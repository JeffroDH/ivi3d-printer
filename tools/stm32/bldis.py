#!/usr/bin/env python3
"""Disassemble a slice of the STM32 bootloader, with PC-relative literals filled in.

Offline. Needs the capstone module.

    python3 tools/stm32/bldis.py ADDR LENGTH [IMAGE]

ADDR and LENGTH are hexadecimal flash addresses. IMAGE defaults to the
2026-11-10 dump; byte 0 of that file is 0x08000000.
"""
import struct
import sys
from pathlib import Path

try:
    import capstone
except ImportError:
    sys.exit("bldis.py needs the capstone module")

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x08000000


def dis(data, addr, length):
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
    out = []
    for ins in md.disasm(data[addr - BASE:addr - BASE + length], addr):
        extra = ""
        if ins.mnemonic.startswith("ldr") and "[pc" in ins.op_str:
            try:
                off = int(ins.op_str.split("#")[1].rstrip("]"), 16)
                la = ((ins.address + 4) & ~3) + off
                word = struct.unpack_from("<I", data, la - BASE)[0]
                extra = " ; [0x%08x]=0x%08x" % (la, word)
            except (ValueError, IndexError, struct.error):
                pass
        out.append("%08x: %-8s %s%s" % (ins.address, ins.mnemonic, ins.op_str, extra))
    return out


def main(argv):
    if len(argv) not in (3, 4):
        sys.exit(__doc__.strip())
    addr, length = int(argv[1], 16), int(argv[2], 16)
    image = Path(argv[3]) if len(argv) == 4 else ROOT / "firmware/stm32_dump/stm32_flash_20261110_a.bin"
    data = image.read_bytes()
    if addr < BASE or addr - BASE + length > len(data):
        sys.exit("slice is outside %s" % image)
    print("\n".join(dis(data, addr, length)))


if __name__ == "__main__":
    main(sys.argv)
