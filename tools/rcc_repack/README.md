# repack_rcc.py — relocate the IVI-Main-Controller QML resource tree

Reusable tool for QML patches of the stock touchscreen app. It does not
squeeze replacements into a fixed in-binary slot. A new file can be any
size, and new files can be added.

Always start from the **fansync / stock baseline** ELF
(`IVI-Main-Controller.fansync`, sha256
`eb576ec38cfd28dca01fb704dfaa1dc461fde8bdce6346454abb49eaa37c452c`).
Do not pass a previously packed output as `--input`. Packed app binaries
are not stored in this repository.

## Requirements

- Python 3
- Qt 5.9.6 `rcc` (format-version 2, the same compiler the app was built with)

## Pack

```sh
python3 tools/rcc_repack/repack_rcc.py pack \
  --input IVI-Main-Controller.fansync \
  --overlay tools/ivi_hook \
  --output IVI-Main-Controller.rccpack \
  --rcc /path/to/qt-5.9.6/bin/rcc \
  --work-dir /tmp/repack_work
```

The subcommand name `pack` may be omitted when the first flag is `--input`.

`--overlay` is a directory tree whose paths are rooted at `/` in the
resource filesystem. For the hook sources in this repo that means:

| Overlay path | Resource path | Effect |
|---|---|---|
| `tools/ivi_hook/qml/main.qml` | `/qml/main.qml` | replace (declares `IviHook`) |
| `tools/ivi_hook/qml/IviHook.qml` | `/qml/IviHook.qml` | add |
| `tools/ivi_hook/qml/ControlPageInPrinting.qml` | `/qml/ControlPageInPrinting.qml` | replace |

Hidden files and `__pycache__` are skipped. After `rcc` runs, the tool
round-trips the `qres` blob and refuses to write an output if any overlaid
file is missing or has the wrong bytes.

## Dump

Works on a packed output or a baseline ELF:

```sh
python3 tools/rcc_repack/repack_rcc.py dump IVI-Main-Controller.rccpack /tmp/qrc_out
```

Offline proofs must use this extracted copy, not only the overlay source.

## What the packer changes in the ELF

The baseline is ELF32 little-endian ARM, with 8 program headers. `e_phoff`
points at `0x34`. The resource tree / names / data live in the first
PT_LOAD (`.rodata`) and are registered by `qInitResources_qml`
(vaddr `0x4a204`) and unregistered by `qCleanupResources_qml` (vaddr
`0x4a238`). Both pass format version 2 to `qRegisterResourceData` /
`qUnregisterResourceData`. Those `bl` sites are PLT-relocated and must
stay at the same file offset.

The packer:

1. Extracts every resource (138 files under `/qml` and `/img`).
2. Applies the overlay and writes a `resources.qrc` with `prefix="/"`.
3. Runs `rcc --binary --format-version 2`.
4. Appends a new `PT_LOAD` (PF_R) at vaddr `0x20000000`, far above `.bss`
   (~`0xb7478`). The file offset is padded so
   `p_offset ≡ p_vaddr (mod 64K)` (ARM Linux 3.4 `ELF_EXEC_PAGESIZE`).
5. Does **not** relocate `e_phoff` / `e_phnum` / `PT_PHDR`. Linux 3.4
   sets `AT_PHDR = load_addr + e_phoff` from the first PT_LOAD and ignores
   `PT_PHDR.p_vaddr`. The new PT_LOAD reuses the baseline `PT_GNU_STACK`
   slot so the 8-entry table at `0x34` still fits in the first PT_LOAD.
6. Rewrites the body of `qInitResources_qml` / `qCleanupResources_qml` to
   load a 12-byte pointer table (tree, name, data vaddrs) from the new
   segment, then `mov r0, #2` and the original `bl`. The unused literal
   slot is tagged `RCC1` (`0x31434352`) so a packed file is detectable.
7. Leaves the old `.rodata` resource bytes untouched.

New segment layout (vaddr `0x20000000`):

```
+0x000  u32 tree_va, name_va, data_va
+0x00c  u32 'RCC1'
+0x010  u32 qres_off (0x18), u32 qres_size
+0x018  qres blob  (magic "qres", be32 version=2, tree, data, name)
```

To host an always-live helper, declare it in `main.qml` as a child of
`Window` (see `IviHook { id: iviBridgeHook }`). Do not `createObject` it
from `BusyWindow`: `BusyWindow`'s `root.destroy()` after self-test will
delete a hook that was only visually reparented.

How the hook starts a print from the bridge is in
[docs/native_print.md](../../docs/native_print.md).
