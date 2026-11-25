#!/usr/bin/env python3
"""Rebuild the QML resource tree of IVI-Main-Controller and relocate it.

This is the general, reusable alternative to in-place slot squeezing. It
extracts every file from the app's existing Qt resource tree, applies an
overlay (replace or add any path, any size), runs Qt 5.9.6
``rcc --binary --format-version 2``, appends the new ``qres`` blob as a
fresh PT_LOAD segment at a high vaddr, and repoints ``qInitResources_qml`` /
``qCleanupResources_qml`` at a 12-byte pointer table in that segment.

The original ``.rodata`` resource bytes are left in place as dead data, so
the tool is always re-run from the *baseline* (fansync / stock) binary —
never from a previously packed output.

Typical use::

    python3 tools/repack_rcc.py \\
        --input IVI-Main-Controller.fansync \\
        --overlay overlay/ \\
        --output IVI-Main-Controller.rccpack \\
        --rcc /path/to/qt-5.9.6/bin/rcc

    python3 tools/repack_rcc.py --dump IVI-Main-Controller.rccpack /tmp/qrc_out

See tools/README-repack-rcc.md for the ELF / qres layout and how to add
future QML files.
"""
from __future__ import print_function

import argparse
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib

# Baseline (IVI-Main-Controller 1.222 / fansync) resource table file offsets.
# These are also vaddr - 0x8000 (the first PT_LOAD maps file 0 at 0x8000).
BASELINE_TREE_OFF = 0x4DB68
BASELINE_NAME_OFF = 0x4E788
BASELINE_DATA_OFF = 0x4F9FC

# qInitResources_qml / qCleanupResources_qml file offsets (vaddr 0x4a204 / 0x4a238).
QINIT_OFF = 0x42204
QCLEANUP_OFF = 0x42238
# Words we keep so the existing bl (PLT-relocated) stays at a fixed address.
QINIT_BL = 0x4A224
QCLEANUP_BL = 0x4A258
LOAD_BASE = 0x8000

# Signature stored in the unused literal slot after each function's table pointer.
PATCH_MAGIC = 0x31434352  # 'RCC1' little-endian

# New PT_LOAD virtual address: far above .bss (bss ends ~0xb7478).
# 0x20000000 is 64K-aligned. Do not use 0x100000 — it sits only ~300 KiB
# above bss if a mapping is *not* reserved; with the segment mapped, brk
# starts after this blob.
NEW_VADDR = 0x20000000
# ARM Linux 3.4 often uses ELF_EXEC_PAGESIZE 64K (or 32K, matching the
# baseline PT_LOAD p_align of 0x8000). Align the new segment to 64K so
# p_offset ≡ p_vaddr (mod ELF_MIN_ALIGN).
PAGE = 0x10000

# Layout of the new segment (no PH table — see build_packed_elf):
#   0x000  u32 tree_va, name_va, data_va
#   0x00c  u32 'RCC1'
#   0x010  u32 qres_off (0x18), u32 qres_size
#   0x018  qres blob
SEG_TABLE = 0x000
SEG_MAGIC = 0x00C
SEG_META = 0x010
SEG_QRES = 0x018

PT_LOAD = 1
PT_PHDR = 6
PT_GNU_STACK = 0x6474E551
PF_R = 4
PF_X = 1
E_PHOFF = 28
E_PHNUM = 44


def die(msg, code=1):
    sys.stderr.write("repack_rcc: %s\n" % msg)
    sys.exit(code)


def align_up(n, a):
    return (n + a - 1) & ~(a - 1)


def unpack_ph(buf, off):
    return list(struct.unpack_from("<8I", buf, off))


def pack_ph(fields):
    return struct.pack("<8I", *fields)


def parse_elf_ph(data):
    if data[:4] != b"\x7fELF":
        die("not an ELF file")
    if data[4] != 1 or data[5] != 1:
        die("expected ELF32 little-endian")
    e_phoff, = struct.unpack_from("<I", data, E_PHOFF)
    e_phentsize, e_phnum = struct.unpack_from("<HH", data, 42)
    if e_phentsize != 32:
        die("unexpected e_phentsize %d" % e_phentsize)
    phs = [unpack_ph(data, e_phoff + i * 32) for i in range(e_phnum)]
    return e_phoff, phs

def first_load_addr(phs):
    """ET_EXEC load_addr as Linux 3.4 computes it: first PT_LOAD vaddr - offset."""
    for typ, off, va, pa, fsz, msz, fl, aln in phs:
        if typ == PT_LOAD:
            return va - off
    die("no PT_LOAD segment")


def at_phdr_mapped(phs, e_phoff, e_phnum):
    """True if load_addr + e_phoff .. + e_phnum*32 falls inside a PT_LOAD.

    Linux 3.4 sets AT_PHDR to load_addr + e_phoff (not PT_PHDR.p_vaddr).
    If that address is unmapped, ld.so segfaults before main.
    """
    load_addr = first_load_addr(phs)
    va = load_addr + e_phoff
    end = va + e_phnum * 32
    for typ, off, vaddr, pa, fsz, msz, fl, aln in phs:
        if typ == PT_LOAD and vaddr <= va and end <= vaddr + fsz:
            return True
    return False



def is_packed(data):
    """True if qInit already has our RCC1 signature (or a 0x20000000 PT_LOAD)."""
    if len(data) >= QINIT_OFF + 0x34:
        sig, = struct.unpack_from("<I", data, QINIT_OFF + 0x30)  # literal slot 0x4a234
        if sig == PATCH_MAGIC:
            return True
    _, phs = parse_elf_ph(data)
    return any(ph[0] == PT_LOAD and ph[2] == NEW_VADDR for ph in phs)


def walk_tree(data, tree_off, name_off, data_off):
    """Walk a Qt 5.9 format-version-2 resource tree. Returns {path: bytes}."""
    out = {}

    def name(no):
        ln, = struct.unpack(">H", data[name_off + no:name_off + no + 2])
        return data[name_off + no + 6:name_off + no + 6 + 2 * ln].decode("utf-16-be")

    def node(i, path):
        b = tree_off + 22 * i
        no, fl = struct.unpack(">IH", data[b:b + 6])
        nm = name(no) if i else ""
        p = (path + "/" + nm) if i else ""
        if fl & 2:
            cnt, first = struct.unpack(">II", data[b + 6:b + 14])
            for k in range(cnt):
                node(first + k, p)
        else:
            off, = struct.unpack(">I", data[b + 10:b + 14])
            length, = struct.unpack(">I", data[data_off + off:data_off + off + 4])
            raw = data[data_off + off + 4:data_off + off + 4 + length]
            payload = zlib.decompress(raw[4:]) if fl & 1 else raw
            out[p] = payload

    node(0, "")
    return out


def parse_qres(blob):
    if blob[:4] != b"qres" or len(blob) < 20:
        die("not a qres blob")
    version, tree_rel, data_rel, name_rel = struct.unpack(">IIII", blob[4:20])
    if version not in (1, 2):
        die("unsupported qres version %d" % version)
    return walk_tree(blob, tree_rel, name_rel, data_rel), (version, tree_rel, data_rel, name_rel)


def extract_baseline(data, tree_off=BASELINE_TREE_OFF, name_off=BASELINE_NAME_OFF,
                     data_off=BASELINE_DATA_OFF):
    return walk_tree(data, tree_off, name_off, data_off)


def find_packed_qres(data):
    _, phs = parse_elf_ph(data)
    for ph in phs:
        typ, off, va, pa, fsz, msz, fl, aln = ph
        if typ != PT_LOAD or va != NEW_VADDR:
            continue
        if fsz < 20:
            die("packed PT_LOAD is too small")
        seg = data[off:off + fsz]
        # Current layout puts meta at 0x10; the first packer used 0x130.
        for meta in (SEG_META, 0x130):
            if meta + 8 > len(seg):
                continue
            qoff, qsz = struct.unpack_from("<II", seg, meta)
            if 0 <= qoff < len(seg) and qoff + qsz <= len(seg) and seg[qoff:qoff+4] == b"qres":
                return seg[qoff:qoff + qsz]
        pos = seg.find(b"qres")
        if pos >= 0:
            return seg[pos:]
        die("packed PT_LOAD at 0x%x has no qres blob" % NEW_VADDR)
    # Fallback: scan for a qres header in the file tail.
    pos = data.rfind(b"qres")
    if pos >= 0 and pos + 20 <= len(data):
        ver, = struct.unpack(">I", data[pos + 4:pos + 8])
        if ver in (1, 2):
            return data[pos:]
    die("no packed qres blob found (is this a baseline binary? use --dump on a packed output)")


def apply_overlay(resources, overlay_dir):
    """Merge overlay_dir into the resource dict.

    Files under overlay_dir are stored at '/'+relative_path. A file at
    overlay/qml/IviHook.qml becomes /qml/IviHook.qml (added if new,
    replaced if it already exists). Directories are created implicitly
    by the path. Hidden files and __pycache__ are skipped.
    """
    overlay_dir = os.path.abspath(overlay_dir)
    added, replaced = [], []
    for root, dirs, files in os.walk(overlay_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]
        for fn in files:
            if fn.startswith("."):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, overlay_dir).replace(os.sep, "/")
            key = "/" + rel
            data = open(full, "rb").read()
            if key in resources:
                if resources[key] != data:
                    replaced.append(key)
                resources[key] = data
            else:
                added.append(key)
                resources[key] = data
    return added, replaced


def write_tree(resources, dest_dir):
    for path, blob in resources.items():
        rel = path.lstrip("/")
        out = os.path.join(dest_dir, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "wb").write(blob)


def write_qrc(resources, qrc_path, tree_dir):
    lines = ['<RCC>', '  <qresource prefix="/">']
    for path in sorted(resources):
        rel = path.lstrip("/")
        # rcc resolves file names relative to the .qrc location.
        lines.append("    <file>%s</file>" % xml_escape(rel))
    lines += ["  </qresource>", "</RCC>", ""]
    open(qrc_path, "w").write("\n".join(lines))


def xml_escape(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def run_rcc(rcc, qrc_path, out_path, compress=None, verbose=False):
    cmd = [rcc, "--binary", "--format-version", "2", "-o", out_path, qrc_path]
    if compress is not None:
        if compress < 0:
            cmd.append("--no-compress")
        else:
            cmd.extend(["--compress", str(compress)])
    if verbose:
        cmd.append("--verbose")
        print("repack_rcc: running", " ".join(cmd), file=sys.stderr)
    try:
        subprocess.check_call(cmd)
    except OSError as e:
        die("failed to execute rcc (%s): %s" % (rcc, e))
    except subprocess.CalledProcessError as e:
        die("rcc failed with exit status %d" % e.returncode)
    blob = open(out_path, "rb").read()
    if blob[:4] != b"qres":
        die("rcc output is missing the qres magic")
    return blob


def patch_register_fn(buf, fn_off, bl_vaddr, table_va, expected_bl):
    """Rewrite qInit / qCleanup, leaving the bl and the push/pop in place."""
    # Original:
    #   push {r3, lr}
    #   ... load tree/name/data via pc-relative literals ...
    #   mov r0, #2
    #   bl qRegisterResourceData / qUnregisterResourceData
    #   mov r0, #1
    #   pop {r3, pc}
    #   .word lit, lit
    #
    # Rewritten (bl stays at the same address so the existing REL32 is valid):
    #   push {r3, lr}
    #   ldr ip, [pc, #0x20]          # literal = table_va
    #   ldr r1, [ip]
    #   ldr r2, [ip, #4]
    #   ldr r3, [ip, #8]
    #   mov r0, #2
    #   nop
    #   nop
    #   bl  ...
    #   mov r0, #1
    #   pop {r3, pc}
    #   .word table_va
    #   .word 'RCC1'
    bl_off = fn_off + (bl_vaddr - (LOAD_BASE + fn_off))
    if bl_off != fn_off + 0x20:
        die("internal error: bl offset mismatch")
    orig_bl, = struct.unpack_from("<I", buf, bl_off)
    if orig_bl != expected_bl:
        die("unexpected bl at 0x%x: got 0x%08x want 0x%08x (not a fansync baseline?)"
            % (bl_off, orig_bl, expected_bl))
    # ldr ip, [pc, #0x20] at fn+4: pc = fn_vaddr+4+8, +0x20 = fn_vaddr+0x2c
    # file literal is at fn_off+0x2c, which is the first original literal slot.
    body = struct.pack(
        "<8I",
        0xE92D4008,  # push {r3, lr}
        0xE59FC020,  # ldr ip, [pc, #0x20]
        0xE59C1000,  # ldr r1, [ip]
        0xE59C2004,  # ldr r2, [ip, #4]
        0xE59C3008,  # ldr r3, [ip, #8]
        0xE3A00002,  # mov r0, #2
        0xE1A00000,  # nop
        0xE1A00000,  # nop
    )
    buf[fn_off:fn_off + 0x20] = body
    # bl already in place
    tail = struct.pack(
        "<4I",
        0xE3A00001,  # mov r0, #1
        0xE8BD8008,  # pop {r3, pc}
        table_va,
        PATCH_MAGIC,
    )
    buf[fn_off + 0x24:fn_off + 0x34] = tail


def expected_bl_words(data):
    init_bl, = struct.unpack_from("<I", data, QINIT_OFF + 0x20)
    clean_bl, = struct.unpack_from("<I", data, QCLEANUP_OFF + 0x20)
    return init_bl, clean_bl


def build_packed_elf(baseline, qres):
    if is_packed(baseline):
        die("input is already packed; pass the fansync/stock baseline instead")

    version, tree_rel, data_rel, name_rel = struct.unpack(">IIII", qres[4:20])
    if version != 2:
        die("rcc produced format version %d, expected 2" % version)

    e_phoff, phs = parse_elf_ph(baseline)
    if len(phs) != 8:
        die("expected 8 program headers in the baseline, found %d" % len(phs))
    if not at_phdr_mapped(phs, e_phoff, len(phs)):
        die("baseline AT_PHDR (load_addr + e_phoff) is not inside a PT_LOAD")

    # Linux 3.4 sets AT_PHDR = first_PT_LOAD.vaddr - offset + e_phoff, and
    # does *not* use PT_PHDR.p_vaddr. Moving e_phoff out of the first PT_LOAD
    # made AT_PHDR = 0x8000 + 0xbe000 = 0xC6000 (unmapped) and the printer
    # process died as soon as ld.so walked the headers. Keep e_phoff / e_phnum
    # / PT_PHDR unchanged, and reuse the PT_GNU_STACK slot for the new LOAD
    # (the table at 0x34 only has room for the original 8 entries).
    stack_i = next((i for i, p in enumerate(phs) if p[0] == PT_GNU_STACK), None)
    if stack_i is None:
        die("baseline has no PT_GNU_STACK slot to reuse for the new PT_LOAD")

    # 64K congruence: p_offset ≡ p_vaddr (mod ELF_MIN_ALIGN).
    seg_off = align_up(len(baseline), PAGE)
    if (seg_off % PAGE) != (NEW_VADDR % PAGE):
        die("internal error: segment alignment mismatch")
    seg_size = SEG_QRES + len(qres)
    table_va = NEW_VADDR + SEG_TABLE
    qres_va = NEW_VADDR + SEG_QRES
    tree_va = qres_va + tree_rel
    name_va = qres_va + name_rel
    data_va = qres_va + data_rel

    new_phs = [list(p) for p in phs]
    new_phs[stack_i] = [PT_LOAD, seg_off, NEW_VADDR, NEW_VADDR,
                        seg_size, seg_size, PF_R, PAGE]

    if not at_phdr_mapped(new_phs, e_phoff, len(new_phs)):
        die("internal error: AT_PHDR would not be covered by a PT_LOAD")

    # New file: baseline + pad + segment. ELF header / e_phoff stay put.
    out = bytearray(seg_off + seg_size)
    out[:len(baseline)] = baseline

    struct.pack_into("<III", out, seg_off + SEG_TABLE, tree_va, name_va, data_va)
    struct.pack_into("<I", out, seg_off + SEG_MAGIC, PATCH_MAGIC)
    struct.pack_into("<II", out, seg_off + SEG_META, SEG_QRES, len(qres))
    out[seg_off + SEG_QRES:seg_off + SEG_QRES + len(qres)] = qres

    # Overwrite the original program-header table in place (still at e_phoff).
    for i, ph in enumerate(new_phs):
        out[e_phoff + i * 32:e_phoff + (i + 1) * 32] = pack_ph(ph)

    init_bl, clean_bl = expected_bl_words(baseline)
    patch_register_fn(out, QINIT_OFF, QINIT_BL, table_va, init_bl)
    patch_register_fn(out, QCLEANUP_OFF, QCLEANUP_BL, table_va, clean_bl)

    info = dict(
        seg_off=seg_off,
        seg_size=seg_size,
        table_va=table_va,
        qres_va=qres_va,
        tree_va=tree_va,
        name_va=name_va,
        data_va=data_va,
        qres_size=len(qres),
        tree_rel=tree_rel,
        name_rel=name_rel,
        data_rel=data_rel,
        file_size=len(out),
    )
    return bytes(out), info


def dump_resources(path, dest, baseline_ok=True):
    data = open(path, "rb").read()
    if is_packed(data):
        blob = find_packed_qres(data)
        resources, hdr = parse_qres(blob)
        src = "packed qres v%d tree=+0x%x name=+0x%x data=+0x%x" % (hdr[0], hdr[1], hdr[3], hdr[2])
    else:
        if not baseline_ok:
            die("%s is not a packed binary" % path)
        resources = extract_baseline(data)
        src = "baseline tree @ 0x%x" % BASELINE_TREE_OFF
    write_tree(resources, dest)
    print("dumped %d files from %s (%s) -> %s" % (len(resources), path, src, dest))
    return resources


def cmd_pack(args):
    rcc = args.rcc or os.environ.get("RCC") or shutil.which("rcc")
    if not rcc or not os.path.isfile(rcc):
        die("rcc not found; pass --rcc /path/to/qt-5.9.6/bin/rcc")

    baseline = open(args.input, "rb").read()
    if is_packed(baseline):
        die("input %s is already packed; pass the fansync/stock baseline" % args.input)

    resources = extract_baseline(baseline)
    n_base = len(resources)
    added, replaced = [], []
    if args.overlay:
        added, replaced = apply_overlay(resources, args.overlay)

    work = args.work_dir or tempfile.mkdtemp(prefix="repack_rcc_")
    cleanup_work = not args.work_dir
    try:
        tree_dir = work if args.work_dir else work
        # Keep the resource tree at the work dir root (paths like qml/main.qml).
        write_tree(resources, tree_dir)
        qrc_path = os.path.join(tree_dir, "resources.qrc")
        rcc_out = os.path.join(tree_dir, "resources.rcc")
        write_qrc(resources, qrc_path, tree_dir)
        qres = run_rcc(rcc, qrc_path, rcc_out, compress=args.compress, verbose=args.verbose)
        packed, info = build_packed_elf(baseline, qres)
        # Confirm the new blob contains every overlay path with matching bytes.
        dumped, _ = parse_qres(qres)
        missing = [p for p in resources if p not in dumped]
        mismatch = [p for p in resources if p in dumped and dumped[p] != resources[p]]
        if missing or mismatch:
            die("rcc round-trip failed: missing=%s mismatch=%s" % (missing[:8], mismatch[:8]))
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
        open(args.output, "wb").write(packed)
        os.chmod(args.output, 0o755)
    finally:
        if cleanup_work:
            shutil.rmtree(work, ignore_errors=True)

    print("packed %s -> %s" % (args.input, args.output))
    print("  files: %d baseline + %d added, %d replaced" % (n_base, len(added), len(replaced)))
    if added:
        print("  added: %s" % ", ".join(added))
    if replaced:
        print("  replaced: %s" % ", ".join(replaced))
    print("  qres:  %d bytes (data +0x%x name +0x%x tree +0x%x)" % (
        info["qres_size"], info["data_rel"], info["name_rel"], info["tree_rel"]))
    print("  segment: file 0x%x size 0x%x vaddr 0x%x" % (
        info["seg_off"], info["seg_size"], NEW_VADDR))
    print("  table vaddr 0x%x -> tree 0x%x name 0x%x data 0x%x" % (
        info["table_va"], info["tree_va"], info["name_va"], info["data_va"]))
    print("  output size %d (0x%x)" % (info["file_size"], info["file_size"]))
    return info


def cmd_dump(args):
    dump_resources(args.input, args.dest)


def make_parser():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("pack", help="extract, overlay, rcc, append PT_LOAD, patch qInit")
    sp.add_argument("--input", "-i", required=True, help="baseline ELF (fansync/stock)")
    sp.add_argument("--overlay", "-O", help="directory of replacement/new resource files")
    sp.add_argument("--output", "-o", required=True, help="packed ELF path")
    sp.add_argument("--rcc", help="Qt 5.9.6 rcc binary")
    sp.add_argument("--work-dir", help="keep the extracted tree / .qrc / .rcc here")
    sp.add_argument("--compress", type=int, default=None,
                    help="rcc --compress level (0-9), or -1 for --no-compress")
    sp.add_argument("--verbose", "-v", action="store_true")
    sp.set_defaults(func=cmd_pack)

    sd = sub.add_parser("dump", help="extract resources from a baseline or packed ELF")
    sd.add_argument("input", help="ELF path")
    sd.add_argument("dest", help="output directory")
    sd.set_defaults(func=cmd_dump)

    return p


def main(argv=None):
    # Also allow a flag-only invocation without a subcommand for the common pack case:
    #   repack_rcc.py -i in -o out -O overlay --rcc ...
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] not in ("pack", "dump", "-h", "--help") and not argv[0].startswith("dump"):
        argv = ["pack"] + argv
    args = make_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
