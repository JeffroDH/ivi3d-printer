#!/usr/bin/env python3
"""Rebuild an IVI3D motion-controller firmware.supx from a raw STM32 app image.
Format (reverse engineered, verified byte-identical against firmware.supx V1.3.2-alpha):
  CRC = CRC-16/XMODEM (poly 0x1021, init 0x0000, no reflection, no xorout), stored little-endian.
  off 0  u32  file_len - 8
  off 4  u16  format version (2)
  off 6  u16  CRC over file[8:EOF]
  off 8  "a1 03" header tag, u32 load addr, u32 image-len field, u16 CRC over [8:18]
  then N x 256-byte records: "a2 40" | u32 flash addr | 248 data bytes | u16 CRC over first 254 bytes
  trailer: "a2 0b" | u32 end addr | 00 00 | "ASCII" zero-padded to 42 bytes | u16 CRC(trailer[0:42])
           "a3 02 0a ba 00 00" | u16 CRC(trailer[0:50])
Usage: supx_pack.py raw.bin out.supx [--base 0x08010000] [--verify firmware.supx]
"""
import struct, sys, argparse
def crc16x(data, c=0):
    for b in data:
        c ^= b << 8
        for _ in range(8):
            c = ((c << 1) ^ 0x1021) & 0xFFFF if c & 0x8000 else (c << 1) & 0xFFFF
    return c
def pack(raw, base=0x08010000, lenfield=None):
    if len(raw) % 248: raw += b'\xff' * (248 - len(raw) % 248)
    if lenfield is None: lenfield = len(raw) + 36   # matches original (0x277C4 for 161696 B)
    h = b'\xa1\x03' + struct.pack('<II', base, lenfield)
    h += struct.pack('<H', crc16x(h))
    body = bytearray()
    for i in range(0, len(raw), 248):
        r = b'\xa2\x40' + struct.pack('<I', base + i) + raw[i:i+248]
        body += r + struct.pack('<H', crc16x(r))
    t = b'\xa2\x0b' + struct.pack('<I', base + len(raw)) + b'\x00\x00' + b'ASCII'
    t = t.ljust(42, b'\x00'); t += struct.pack('<H', crc16x(t))
    t += b'\xa3\x02\x0a\xba\x00\x00'; t += struct.pack('<H', crc16x(t))
    rest = h + bytes(body) + t
    return struct.pack('<IHH', len(rest), 2, crc16x(rest)) + rest   # len field = file_len - 8
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('raw'); ap.add_argument('out')
    ap.add_argument('--base', default='0x08010000'); ap.add_argument('--verify')
    a = ap.parse_args()
    out = pack(open(a.raw, 'rb').read(), int(a.base, 0))
    open(a.out, 'wb').write(out); print('wrote', a.out, len(out), 'bytes')
    if a.verify:
        ref = open(a.verify, 'rb').read()
        print('IDENTICAL' if ref == out else 'DIFFERENT (first diff at %d)' % next((i for i,(x,y) in enumerate(zip(ref,out)) if x!=y), min(len(ref),len(out))))
