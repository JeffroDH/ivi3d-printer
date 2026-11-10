#!/bin/bash
# [W1 microSD on the Mac] Turn a whole microSD card into the IVI rescue card.
#   usage: make-sdcard-macos.sh diskN
# Layout: MBR | U-Boot at 8 KiB | p1 FAT32 "IVIRESCUE" from 4 MiB to the end of the card.
# The whole card is erased. UNTESTED on macOS (layout verified on Linux with the same files).
set -euo pipefail
KIT=$(cd "$(dirname "$0")/.." && pwd); OUT=$KIT/out
D=${1:?usage: make-sdcard-macos.sh diskN}; D=${D#/dev/}
info=$(diskutil info "$D")
echo "$info" | grep -E "Device / Media Name|Disk Size|Removable Media|Device Location|Internal|Protocol"
echo "$info" | grep -q "Whole: *Yes" || { echo "$D is not a whole disk"; exit 1; }
echo "$info" | grep -Eq "Device Location: *External|Removable Media: *(Removable|Yes)" || { echo "$D is not external/removable; refusing"; exit 1; }
bytes=$(echo "$info" | sed -n 's/.*Disk Size:.*(\([0-9]*\) Bytes).*/\1/p')
[ "$bytes" -le $((64*1000*1000*1000)) ] || { echo "Card is larger than 64 GB; refusing (guard against picking a backup drive)"; exit 1; }
[ "$bytes" -ge $((8*1000*1000*1000)) ] || echo "NOTE: card under 8 GB: too small for a full eMMC backup (needs ~4 GB free)."
diskutil list "$D" | grep -qi "14TB" && { echo "This looks like the 14TB drive; refusing"; exit 1; }
sectors=$((bytes/512))
read -r -p "ERASE ALL DATA on /dev/$D ($bytes bytes)? Type the disk id ($D) to continue: " a
[ "$a" = "$D" ] || { echo aborted; exit 3; }
( cd "$OUT" && shasum -a 256 -c <(grep -E ' (u-boot-sunxi-with-spl.padded.bin|zImage|sun8i-a33-ivi3d-rescue.dtb|uInitrd|ivi-rescue.scr)$' SHA256SUMS) )
diskutil unmountDisk "/dev/$D"
# One MBR entry: start 8192, rest of card, type 0x0C (FAT32 LBA), active.
echo "8192,$((sectors-8192)),0x0C,*" | sudo fdisk -y -r "/dev/r$D"
sudo dd if="$OUT/u-boot-sunxi-with-spl.padded.bin" of="/dev/r$D" bs=1k seek=8 conv=notrunc
diskutil unmountDisk "/dev/$D" || true
sudo newfs_msdos -F 32 -v IVIRESCUE "/dev/r${D}s1"
diskutil mount "/dev/${D}s1"
MP=$(diskutil info "${D}s1" | sed -n 's/.*Mount Point: *//p')
cp "$OUT/zImage" "$OUT/sun8i-a33-ivi3d-rescue.dtb" "$OUT/uInitrd" "$OUT/ivi-rescue.scr" "$KIT/RESCUE.md" "$MP/"
mkdir -p "$MP/backups"
sync; diskutil eject "/dev/$D"
echo "Rescue card ready. To restore later, copy mmcblk0.img (+ .md5 if not the 2026-11-07 image) into backups/."
