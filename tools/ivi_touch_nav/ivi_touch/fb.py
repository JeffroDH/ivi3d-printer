"""Framebuffer frames (32 bpp BGRA/XRGB little-endian as on the A33 sunxi fb0), hashing, signatures, PNG."""
import struct, zlib

FNV_OFFSET, FNV_PRIME = 2166136261, 16777619


def fnv1a(data, h=FNV_OFFSET):
    for b in data:
        h ^= b
        h = (h * FNV_PRIME) & 0xFFFFFFFF
    return h


class Frame:
    """One visible fb0 page. `data` holds `height` rows of `stride` bytes, 4 bytes/pixel B,G,R,A."""

    def __init__(self, data, width=800, height=480, stride=None):
        self.width, self.height = width, height
        self.stride = stride or width * 4
        if len(data) < self.stride * height:
            raise ValueError("frame too short: %d < %d" % (len(data), self.stride * height))
        self.data = bytes(data[: self.stride * height])

    # --- pixel access -------------------------------------------------------------
    def rgb(self, x, y):
        o = y * self.stride + x * 4
        b, g, r = self.data[o], self.data[o + 1], self.data[o + 2]
        return r, g, b

    def lum(self, x, y):
        r, g, b = self.rgb(x, y)
        return (299 * r + 587 * g + 114 * b) // 1000

    def region_mean(self, x, y, w, h, step=2):
        n = sr = sg = sb = 0
        for yy in range(y, y + h, step):
            for xx in range(x, x + w, step):
                r, g, b = self.rgb(xx, yy)
                sr += r; sg += g; sb += b; n += 1
        return (sr // n, sg // n, sb // n) if n else (0, 0, 0)

    def region_hash(self, x, y, w, h):
        """FNV-1a 32 over raw row bytes; identical to ivitap2 -G/-H on the device."""
        hsh = FNV_OFFSET
        for r in range(h):
            o = (y + r) * self.stride + x * 4
            hsh = fnv1a(self.data[o:o + w * 4], hsh)
        return hsh

    def grid(self, x=0, y=0, w=None, h=None, cell=20, step=5):
        """Grayscale signature: list of rows of mean luminance per `cell`x`cell` block (sampled every `step`)."""
        w = w or self.width - x; h = h or self.height - y
        out = []
        for cy in range(y, y + h - cell + 1, cell):
            row = []
            for cx in range(x, x + w - cell + 1, cell):
                s = n = 0
                for yy in range(cy, cy + cell, step):
                    for xx in range(cx, cx + cell, step):
                        s += self.lum(xx, yy); n += 1
                row.append(s // n)
            out.append(row)
        return out

    def is_blank(self):
        """True if the visible page is (near) uniformly dark - e.g. never drawn / panel content cleared."""
        mx = 0
        for yy in range(0, self.height, 16):
            for xx in range(0, self.width, 16):
                mx = max(mx, self.lum(xx, yy))
                if mx > 24:
                    return False
        return True

    def to_png(self, path):
        raw = bytearray()
        for y in range(self.height):
            raw.append(0)
            row = self.data[y * self.stride: y * self.stride + self.width * 4]
            for i in range(0, len(row), 4):
                raw += bytes((row[i + 2], row[i + 1], row[i]))
        def chunk(t, d):
            c = struct.pack(">I", len(d)) + t + d
            return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
        png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0))
        png += chunk(b"IDAT", zlib.compress(bytes(raw), 6)) + chunk(b"IEND", b"")
        with open(path, "wb") as f:
            f.write(png)


def color_close(c1, c2, tol=40):
    return all(abs(a - b) <= tol for a, b in zip(c1, c2))


def hexrgb(s):
    s = s.lstrip("#")
    if len(s) == 8:  # AARRGGBB
        s = s[2:]
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def grid_distance(a, b, mask=None, top=None):
    """Absolute difference of two grids (same shape); mask[r][c] True = ignore cell.
    top=None: mean over all cells (global layout). top=0.1: mean of the largest 10% cell differences
    (min 3 cells) - used for discriminator regions so a one-word change ('Pause' vs 'Continue') is not
    diluted by the surrounding identical pixels."""
    diffs = []
    for r, (ra, rb) in enumerate(zip(a, b)):
        for c, (va, vb) in enumerate(zip(ra, rb)):
            if mask and mask[r][c]:
                continue
            diffs.append(abs(va - vb))
    if not diffs:
        return 255.0
    if top:
        k = max(3, int(len(diffs) * top))
        diffs.sort(reverse=True)
        diffs = diffs[:k]
    return sum(diffs) / len(diffs)
