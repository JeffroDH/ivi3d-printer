#!/usr/bin/env python3
"""Offline model of the STM32 bootloader update handlers.

Feeds firmware.supx's frames through the rules at USART2 ISR 0x08003350
(and the same USB CDC parser at 0x080054FC): A1 erase 0x080062B4, A2 write
0x08006260, A3 check 0x0800632C. Prints whether every frame is accepted and
whether the resulting image equals the 2026-11-10 SWD dump. Sends nothing.

    python3 tools/stm32/bl_protocol_model.py [flash.bin] [firmware.supx]
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DUMP = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "firmware/stm32_dump/stm32_flash_20261110_a.bin"
SUPX = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "firmware/Firmware/firmware.supx"


def crc(b, c=0):
    for x in b:
        c ^= x << 8
        for _ in range(8):
            c = ((c << 1) ^ 0x1021) & 0xFFFF if c & 0x8000 else (c << 1) & 0xFFFF
    return c


SECT = [(0x08000000, 0x4000), (0x08004000, 0x4000), (0x08008000, 0x4000), (0x0800C000, 0x4000),
        (0x08010000, 0x10000), (0x08020000, 0x20000), (0x08040000, 0x20000), (0x08060000, 0x20000)]


def sector_of(a):  # FUN_08000954
    for i, (b, length) in enumerate(SECT):
        if b <= a < b + length:
            return i
    return 8


def reply(cmd, status, n=4):
    r = bytearray([cmd, 5, status, 0])
    c = crc(r[:n])
    r[3] = c & 0xFF
    r += bytes([c >> 8])
    return bytes(r)


def main():
    dump = DUMP.read_bytes()
    flash = bytearray(dump)
    st = {"load": 0x08010000, "len": 0, "eeprom_flag": False}

    def handle(fr):
        exp = fr[1] * 4  # ISR: expected length = byte1 * 4
        assert len(fr) == exp, (len(fr), exp)
        if crc(fr[:-2]) != struct.unpack("<H", fr[-2:])[0]:
            return reply(0xC0, 0xE4, 3)
        c = fr[0]
        if c == 0xA1:
            load, ln = struct.unpack_from("<II", fr, 2)
            st["load"], st["len"] = load, ln
            if load != 0x08010000:
                return reply(0xC1, 0xE6)
            s0, s1 = sector_of(load), sector_of(load + ln)
            if not 4 <= s0 <= 7:
                return reply(0xC1, 0xE6)
            st["eeprom_flag"] = True  # FUN_08000566: valid record at EEPROM 0x20
            for s in range(s0, s1 + 1):
                if s < 4:
                    return reply(0xC1, 0xE2)  # FUN_08005972 refuses < 4
                b, length = SECT[s]
                flash[b - 0x08000000:b - 0x08000000 + length] = b"\xff" * length
            print("  A1: load 0x%08X len 0x%X -> erased sectors %d..%d" % (load, ln, s0, s1))
            return reply(0xC1, 0xE0)
        if c == 0xA2:
            addr = struct.unpack_from("<I", fr, 2)[0]
            data = fr[6:6 + fr[1] * 4 - 8]
            if not 0x08010000 <= addr <= 0x0807FFFF:
                return reply(0xC2, 0xE6)
            o = addr - 0x08000000
            for i, byte in enumerate(data):
                flash[o + i] &= byte  # NOR program semantics
            return reply(0xC2, 0xE0)
        if c == 0xA3:
            want = struct.unpack_from("<I", fr, 2)[0]
            got = crc(flash[st["load"] - 0x08000000:st["load"] - 0x08000000 + st["len"]])
            print("  A3: CRC16 over 0x%08X+0x%X = 0x%04X, frame wants 0x%04X"
                  % (st["load"], st["len"], got, want))
            if got == want:
                st["eeprom_flag"] = False
                return reply(0xC3, 0xE0)
            return reply(0xC3, 0xE4)
        if c == 0xA0:
            return reply(0xC0, 0xE0)
        return reply(0xC0, 0xE1)

    f = SUPX.read_bytes()
    n = struct.unpack_from("<I", f, 0)[0]
    frames = [f[8:20]]
    off = 20
    for _ in range((n - 0x14) >> 8):
        frames.append(f[off:off + 256])
        off += 256
    rem = (n - 0x14) & 0xFF
    if rem:
        frames.append(f[off:off + rem])
        off += rem
    frames.append(f[off:off + 8])
    print("M997 entry reply (C4 05 B0 + CRC over 3 bytes):", reply(0xC4, 0xB0, 3).hex(" "))
    stats = {}
    for fr in frames:
        r = handle(fr)
        stats[r[:3].hex()] = stats.get(r[:3].hex(), 0) + 1
    same = bytes(flash) == dump
    untouched = flash[:0x10000] == dump[:0x10000]
    print("replies:", stats)
    print("EEPROM pending flag after A3:", st["eeprom_flag"])
    print("flash after model update == SWD dump:", same)
    print("sectors 0-3 untouched:", untouched)
    if not (same and untouched and st["eeprom_flag"] is False):
        return 1
    if stats != {"c105e0": 1, "c205e0": 653, "c305e0": 1}:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
