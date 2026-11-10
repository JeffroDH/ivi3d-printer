#!/bin/bash
# Build a small (64 MiB) bootable rescue microSD image on Linux without root.
#   usage: make-sdcard-image.sh OUTDIR IMAGE
# Layout: MBR | U-Boot SPL+FIT at 8 KiB | p1 FAT32 "IVIRESCUE" from 4 MiB to end.
# Writing this image to a card only gives 60 MiB of space: enough to boot and run the
# read-only checks, NOT enough for an eMMC backup. For backups use make-sdcard-macos.sh
# (whole card as FAT32) instead.
set -euo pipefail
export PATH=$PATH:/sbin:/usr/sbin
OUT=$1; IMG=$2
SIZE_MB=64; P1_START=8192   # sectors (4 MiB)
rm -f "$IMG"; truncate -s ${SIZE_MB}M "$IMG"
printf 'label: dos\nunit: sectors\n%s,,c,*\n' $P1_START | sfdisk -q "$IMG"
dd if="$OUT/u-boot-sunxi-with-spl.bin" of="$IMG" bs=1024 seek=8 conv=notrunc status=none
P1=$(mktemp); trap 'rm -f "$P1"' EXIT
truncate -s $(( SIZE_MB*1048576 - P1_START*512 )) "$P1"
/usr/sbin/mkfs.vfat -F 32 -S 512 -s 1 -n IVIRESCUE "$P1" >/dev/null
for f in zImage sun8i-a33-ivi3d-rescue.dtb uInitrd ivi-rescue.scr; do mcopy -i "$P1" "$OUT/$f" ::/; done
[ -f "$OUT/../RESCUE.md" ] && mcopy -i "$P1" "$OUT/../RESCUE.md" ::/
dd if="$P1" of="$IMG" bs=512 seek=$P1_START conv=notrunc status=none
# Sanity: U-Boot must end before p1, and the eGON header must sit at 8 KiB.
end=$(( 8192 + $(stat -c %s "$OUT/u-boot-sunxi-with-spl.bin") ))
[ $end -lt $(( P1_START*512 )) ] || { echo "U-Boot overlaps p1"; exit 1; }
[ "$(dd if="$IMG" bs=1 skip=$((8192+4)) count=8 status=none)" = "eGON.BT0" ] || { echo "no eGON header at 8 KiB"; exit 1; }
echo "SD image: $IMG"
