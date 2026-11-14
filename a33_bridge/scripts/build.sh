#!/bin/sh
# Rebuild on a Debian/Ubuntu box with gcc-arm-linux-gnueabihf (static, so the A33's soft-float userland is irrelevant).
set -e; cd "$(dirname "$0")/.."
mkdir -p bin
arm-linux-gnueabihf-gcc -static -Os -Wall -Wno-format-truncation -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=hard \
    -o bin/ivibridge-armv7-static src/ivibridge.c
arm-linux-gnueabihf-strip bin/ivibridge-armv7-static
gcc -O2 -Wall -Wno-format-truncation -o /tmp/ivibridge_x86 src/ivibridge.c      # native build for quick tests
