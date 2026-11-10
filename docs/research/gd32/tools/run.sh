#!/bin/sh
# Regenerate ../gd32e230_annotated.s
# Needs python3, capstone>=5, and GD32_BIN pointing at a 16 KiB flash image
# (not published in this repo; SHA-256 is in docs/gd32.md).
# GD32_MANUAL is only needed to rebuild regs_raw.json via regmap.py.
cd "$(dirname "$0")" || exit 1
if [ -z "$GD32_BIN" ]; then echo "set GD32_BIN to the 16 KiB flash image" >&2; exit 1; fi
python3 rda.py >/dev/null && python3 listing.py && rm -rf __pycache__ rda.pkl
