#!/usr/bin/env python3
"""Add IVI 3licer's ';Header Start' block to one G-code file (what the bridge does on upload).
Also drops M204/M205/M73/G21 command lines like the bridge (--strip "" to keep them).
Usage: ivi_add_header.py IN [OUT] [--nozzle 0.3] [--strip M204,M205,M73,G21]   (no OUT = IN.ivi.gcode)"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ivi_bridge as B

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("src"); ap.add_argument("dst", nargs="?"); ap.add_argument("--nozzle", type=float, default=0.3)
    ap.add_argument("--strip", default=",".join(B.DEFAULT_STRIP), help="comma-separated first words to drop")
    a = ap.parse_args(argv)
    dst = a.dst or os.path.splitext(a.src)[0] + ".ivi.gcode"
    r = B.prepare_gcode(a.src, dst, nozzle=a.nozzle, strip=[c for c in a.strip.split(",") if c.strip()])
    print(f"removed {r['removed']} line(s)", file=sys.stderr)
    if not r["header"]:
        print(f"{a.src} already has an IVI header; written to {dst}"); return 0
    with open(dst, encoding="utf-8", errors="replace") as f:
        for line in f:
            print(line, end="")
            if line.startswith(";Header End"): break
    print(f"-> {dst}"); return 0

if __name__ == "__main__": sys.exit(main())
