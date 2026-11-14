#!/bin/sh
# Needs: python3, qemu-arm, /tmp/a33root (ld-linux.so.3 + libc.so.6 + busybox + stock_rcS from the p7 image),
# fake app built: gcc -O2 -o /tmp/IVI-Main-Controller tests/fake_app.c
cd "$(dirname "$0")"
python3 -W ignore test_header.py && python3 -W ignore test_ivibridge.py && python3 -W ignore test_supervisor.py && python3 -W ignore test_install.py && python3 -W ignore test_boot.py
