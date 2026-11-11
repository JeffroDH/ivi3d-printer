#!/usr/bin/env python3
"""Print one decompiled bootloader function and the literal-pool words it names.

Offline. Reads the Ghidra listing and the flash dump; sends nothing.

    python3 tools/stm32/blq.py 08005b4c [08005b08 ...]
"""
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DUMP = ROOT / "firmware/stm32_dump/stm32_flash_20261110_a.bin"
DECOMP = ROOT / "docs/research/stm32/bootloader/disasm/bootloader_ghidra_decompile.c"


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__.strip())
    data = DUMP.read_bytes()
    text = DECOMP.read_text(errors="replace")
    funcs = {}
    for part in re.split(r"(?=// ===== )", text):
        m = re.match(r"// ===== (\S+) @ (\S+)", part)
        if m:
            funcs[m.group(2).lower()] = part

    def word(addr):
        return struct.unpack_from("<I", data, addr - 0x08000000)[0]

    for arg in argv[1:]:
        key = arg.lower().removeprefix("0x").zfill(8)
        part = funcs.get(key, "?? " + arg)
        print(part.strip())
        for lit in sorted(set(re.findall(r"DAT_([0-9a-f]{8})", part))):
            print("   DAT_%s = 0x%08x" % (lit, word(int(lit, 16))))
        print()


if __name__ == "__main__":
    main(sys.argv)
