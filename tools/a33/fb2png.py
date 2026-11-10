#!/usr/bin/env python3
"""Box-side: convert a raw /dev/fb0 dump to PNG.
Capture on the printer (read-only):
  cat /sys/class/graphics/fb0/virtual_size /sys/class/graphics/fb0/bits_per_pixel /sys/class/graphics/fb0/stride /sys/class/graphics/fb0/pan
  dd if=/dev/fb0 of=/tmp/fb.raw bs=1536000 count=1      # first 800x480x4 page
Usage: fb2png.py fb.raw out.png [width=800] [height=480] [stride=width*4] [yoffset=0]
Assumes 32bpp little-endian BGRA/XRGB8888 (sys_config fb0_format=10 = ARGB8888)."""
import sys
from PIL import Image
raw = open(sys.argv[1], 'rb').read(); out = sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 800; h = int(sys.argv[4]) if len(sys.argv) > 4 else 480
stride = int(sys.argv[5]) if len(sys.argv) > 5 else w * 4; yoff = int(sys.argv[6]) if len(sys.argv) > 6 else 0
buf = b''.join(raw[(yoff + r) * stride:(yoff + r) * stride + w * 4] for r in range(h))
Image.frombytes('RGBA', (w, h), buf, 'raw', 'BGRA').convert('RGB').save(out); print('wrote', out)
