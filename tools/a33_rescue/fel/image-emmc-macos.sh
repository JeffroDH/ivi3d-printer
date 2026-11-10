#!/bin/bash
# [R0 READ on the board; writes a file on the Mac] Copy the read-only UMS disk to an image file.
#   usage: image-emmc-macos.sh diskN [OUTFILE]
# Refuses any disk whose size is not exactly the IVI eMMC user area (3959422976 bytes).
set -euo pipefail
D=${1:?usage: image-emmc-macos.sh diskN [OUTFILE]}; D=${D#/dev/}
OUTF=${2:-$HOME/IVI_eMMC_$(date +%Y%m%d_%H%M%S).img}
EXPECT=3959422976
info=$(diskutil info "$D")
size=$(echo "$info" | sed -n 's/.*Disk Size:.*(\([0-9]*\) Bytes).*/\1/p')
echo "$info" | grep -E "Device / Media Name|Disk Size|Removable|Protocol|Read-Only Media"
[ "$size" = "$EXPECT" ] || { echo "Size $size != $EXPECT: this is not the IVI eMMC export. Refusing."; exit 1; }
echo "$info" | grep -q "Read-Only Media: *Yes" || echo "NOTE: macOS does not report it read-only; U-Boot still rejects writes."
diskutil unmountDisk "/dev/$D" || true     # unmount any auto-mounted FAT volumes (read-only anyway)
echo "Reading /dev/r$D -> $OUTF"
sudo dd if="/dev/r$D" of="$OUTF" bs=1m
md5 -q "$OUTF" | tee "$OUTF.md5"
echo "Compare with the known backup MD5 400889383907f6a864e65bbea4e27c57 (differs if the board has run since 2026-11-07)."
