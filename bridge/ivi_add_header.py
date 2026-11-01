#!/usr/bin/env python3
"""Add IVI 3licer's ';Header Start' block to one G-code file (what the bridge does on upload).
Usage: ivi_add_header.py IN [OUT] [--nozzle 0.3]      (no OUT = IN.ivi.gcode)"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ivi_bridge as B

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("src"); ap.add_argument("dst", nargs="?"); ap.add_argument("--nozzle", type=float, default=0.3)
    a = ap.parse_args(argv)
    dst = a.dst or os.path.splitext(a.src)[0] + ".ivi.gcode"
    if not B.add_ivi_header(a.src, dst, nozzle=a.nozzle):
        print(f"{a.src} already has an IVI header; copied unchanged to {dst}"); return 0
    with open(dst, encoding="utf-8", errors="replace") as f:
        for line in f:
            print(line, end="")
            if line.startswith(";Header End"): break
    print(f"-> {dst}"); return 0

if __name__ == "__main__": sys.exit(main())
