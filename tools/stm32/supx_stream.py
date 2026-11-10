#!/usr/bin/env python3
"""OFFLINE ONLY. Reproduces, from a .supx file, the exact byte frames the A33 app
(Work::startUpgradeFirmware @0x47614, IVI-Main-Controller v1.222) writes to /dev/ttyUSB0,
and checks every CRC the way the host and (presumably) the bootloader do. Sends nothing."""
import struct, sys
def crc16x(b, c=0):
    for x in b:
        c ^= x << 8
        for _ in range(8): c = ((c << 1) ^ 0x1021) & 0xFFFF if c & 0x8000 else (c << 1) & 0xFFFF
    return c
f = open(sys.argv[1] if len(sys.argv) > 1 else 'firmware/Firmware/firmware.supx', 'rb').read()
n, ver, fcrc = struct.unpack_from('<IHH', f, 0)
print(f"file {len(f)} B; len field {n} (= file-8: {n == len(f)-8}); format ver {ver} (host requires 2); "
      f"file CRC 0x{fcrc:04X} vs computed 0x{crc16x(f[8:8+n]):04X}")
frames = []
frames.append(('HDR/erase', f[8:20]))                    # write(12)  -> wait C1 xx E0
off = 20; body = n - 12                                   # host: (n-0x14)>>8 full 256-B blocks
nblk = (n - 0x14) >> 8
for i in range(nblk): frames.append(('REC', f[off:off+256])); off += 256   # write(256) -> wait C2 xx E0
rem = (n - 0x14) & 0xFF
if rem: frames.append(('TRAILER', f[off:off+rem])); off += rem           # write(rem) -> wait C2 xx E0
frames.append(('CHECK', f[off:off+8])); off += 8                          # write(8)  -> wait C3 xx E0
print(f"frames: 1 header + {nblk} records + {'1 trailer' if rem else 'no trailer'} ({rem} B) + 1 check; consumed {off} of {len(f)} B")
bad = 0
for k, (t, fr) in enumerate(frames):
    if t == 'HDR/erase':
        tag, addr, ln, c = struct.unpack('<HIIH', fr)
        ok = c == crc16x(fr[:10]); print(f"  HDR tag {fr[:2].hex()} load 0x{addr:08X} lenfield 0x{ln:X} crc ok={ok}")
    elif t == 'REC':
        ok = struct.unpack('<H', fr[254:256])[0] == crc16x(fr[:254]) and fr[:2] == b'\xa2\x40'
    elif t == 'TRAILER':
        ok = struct.unpack('<H', fr[42:44])[0] == crc16x(fr[:42]); print(f"  TRAILER {fr[:8].hex()} {fr[8:13]} crc ok={ok}")
    else:
        ok = True; print(f"  CHECK {fr.hex()}")
    bad += not ok
recs = [f for t, f in frames if t == 'REC']
a0 = struct.unpack_from('<I', recs[0], 2)[0]; a1 = struct.unpack_from('<I', recs[-1], 2)[0]
contig = all(struct.unpack_from('<I', recs[i], 2)[0] == a0 + 248*i for i in range(len(recs)))
print(f"records 0x{a0:08X}..0x{a1+247:08X}, contiguous={contig}, bad CRCs={bad}")
jta = bytes([0xA4, 2, 0xAA, 0xAA, 0xAA, 0xAA]); jta += struct.pack('<H', crc16x(jta))
print("jumpToApp frame (sent twice):", jta.hex(' '))
print("bootloader-entry text (Work::jumpToBootloader):", repr(b'M997\n'))
