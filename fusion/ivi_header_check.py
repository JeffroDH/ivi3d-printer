#!/usr/bin/env python3
"""Validate an IVI3D laser/CNC G-code file against the IVI 3licer header format.
Usage: ivi_header_check.py FILE [FILE...]   exit 0 = no errors (warnings allowed)."""
import re, sys

KEYS = ["header_type", "renderMethod", "file_total_lines", "file_valid_lines", "estimated_time(s)",
        "max_x(mm)", "max_y(mm)", "max_z(mm)", "min_x(mm)", "min_y(mm)", "min_z(mm)",
        "work_speed(mm/minute)", "jog_speed(mm/minute)", "power(%)"]
NUM = KEYS[2:]
MAX_SANE_DWELL_MS = 60_000        # IVI 3licer 1.6.2 point mode emitted P896745231 (slicer bug)

def check(text):
    errs, warns = [], []
    lines = text.split("\n")
    if lines and lines[-1] == "": lines_count = len(lines) - 1
    else: lines_count = len(lines)
    if not lines or lines[0].strip() != ";Header Start":
        return ["first line must be ';Header Start'"], warns, {}
    try: end = next(i for i, l in enumerate(lines) if l.strip() == ";Header End")
    except StopIteration: return ["missing ';Header End'"], warns, {}
    hdr = {}
    for l in lines[1:end]:
        m = re.match(r";\s*([^:]+):\s*(.*)$", l.strip())
        if m: hdr[m.group(1).strip()] = m.group(2).strip()
    order = [k for k in hdr if k in KEYS]
    for k in KEYS:
        if k not in hdr: errs.append(f"missing header key {k}")
    if order != [k for k in KEYS if k in hdr]: warns.append("header keys not in IVI 3licer order")
    for k in NUM:
        if k in hdr:
            try: hdr[k] = float(hdr[k])
            except ValueError: errs.append(f"{k} is not a number: {hdr[k]!r}")
    if errs: return errs, warns, hdr
    if hdr["header_type"] not in ("laser", "cnc", "3dp"): errs.append(f"unknown header_type {hdr['header_type']}")
    if hdr["renderMethod"] not in ("line", "point"): errs.append(f"unknown renderMethod {hdr['renderMethod']}")
    if abs(hdr["file_total_lines"] - lines_count) > 1:
        errs.append(f"file_total_lines {hdr['file_total_lines']:.0f} != actual {lines_count}")
    valid = [l.strip() for l in lines if l.strip() and not l.strip().startswith(";")]
    if abs(hdr["file_valid_lines"] - len(valid)) > 1:
        errs.append(f"file_valid_lines {hdr['file_valid_lines']:.0f} != actual {len(valid)}")
    elif hdr["file_valid_lines"] != len(valid):
        warns.append(f"file_valid_lines off by one ({hdr['file_valid_lines']:.0f} vs {len(valid)}; IVI 3licer counts a whitespace-only line)")
    xs, ys, zs, dwells = [], [], [], []
    for l in valid:
        c = l.split(";")[0]
        for a, arr in (("X", xs), ("Y", ys), ("Z", zs)):
            m = re.search(a + r"(-?\d+(?:\.\d+)?)", c)
            if m and re.match(r"G[01]\b", c): arr.append(float(m.group(1)))
        m = re.match(r"G4\s+P(\d+)", c)
        if m: dwells.append(int(m.group(1)))
    for ax, arr in (("x", xs), ("y", ys)):
        if arr:
            if abs(min(arr) - hdr[f"min_{ax}(mm)"]) > 0.02 or abs(max(arr) - hdr[f"max_{ax}(mm)"]) > 0.02:
                errs.append(f"{ax} bounds header [{hdr[f'min_{ax}(mm)']}, {hdr[f'max_{ax}(mm)']}] != moves [{min(arr)}, {max(arr)}]")
    if zs and (min(zs) < hdr["min_z(mm)"] or max(zs) > hdr["max_z(mm)"]):
        warns.append(f"Z moves span [{min(zs)}, {max(zs)}] but header z is [{hdr['min_z(mm)']}, {hdr['max_z(mm)']}] (IVI 3licer always writes 0)")
    if dwells and max(dwells) > MAX_SANE_DWELL_MS:
        warns.append(f"G4 dwell P{max(dwells)} ms ({len(dwells)} dwells) is absurd - IVI 3licer point-mode bug; do not run as-is")
    if hdr["estimated_time(s)"] > 7 * 86400: warns.append(f"estimated_time {hdr['estimated_time(s)']:.0f} s is implausible (dwell bug?)")
    if not 0 <= hdr["power(%)"] <= 100: errs.append("power(%) outside 0-100")
    return errs, warns, hdr

def main(argv):
    bad = 0
    for f in argv:
        errs, warns, hdr = check(open(f, errors="replace").read())
        print(f"{f}: {'OK' if not errs else 'FAIL'} ({hdr.get('header_type', '?')}/{hdr.get('renderMethod', '?')})")
        for e in errs: print("  ERROR", e)
        for w in warns: print("  warn ", w)
        bad |= bool(errs)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
