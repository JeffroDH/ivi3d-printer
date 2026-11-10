#!/usr/bin/env python3
"""Disassemble a slice of a raw ARM Thumb image. Offline. Needs capstone.

    python3 tools/stm32/thumbdis.py IMAGE ADDR LENGTH [BASE]

ADDR and LENGTH are hexadecimal. BASE is the address of byte 0 of IMAGE
(default 0). For the motion application taken out of firmware.supx, BASE is
0x08010000 and ADDR is the flash address. A PC-relative LDR literal is
printed when the target falls inside the file.
"""
import sys

try:
    import capstone
except ImportError:
    sys.exit("thumbdis.py needs the capstone module")


def main(argv):
    if len(argv) not in (4, 5):
        sys.exit(__doc__.strip())
    path, addr, length = argv[1], int(argv[2], 16), int(argv[3], 16)
    base = int(argv[4], 16) if len(argv) == 5 else 0
    data = open(path, "rb").read()
    start = addr - base
    if start < 0 or start + length > len(data):
        sys.exit("slice is outside %s (base %#x, %d bytes)" % (path, base, len(data)))
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    for ins in md.disasm(data[start:start + length], addr):
        extra = ""
        if ins.mnemonic.startswith("ldr") and "pc" in ins.op_str and "#" in ins.op_str:
            try:
                off = int(ins.op_str.split("#")[1].rstrip("]"), 16)
                la = ((ins.address + 4) & ~3) + off
                rel = la - base
                if 0 <= rel <= len(data) - 4:
                    extra = " ; =0x%08x" % int.from_bytes(data[rel:rel + 4], "little")
            except ValueError:
                pass
        print("%08x: %-8s %s%s" % (ins.address, ins.mnemonic, ins.op_str, extra))


if __name__ == "__main__":
    main(sys.argv)
