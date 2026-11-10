#!/bin/bash
# [W1 microSD on the Mac] Make a "FEL entry" card: writes only fel-sdboot.sunxi (8 KiB)
# at offset 8 KiB of the card. If the A33 BootROM boots it from the microSD slot, the
# board drops straight into USB FEL mode (no U-Boot, no Linux, no eMMC access by this code).
# If the BootROM does not take the card, the board boots normally from eMMC.
#   usage: make-fel-sdcard-macos.sh diskN
set -euo pipefail
KIT=$(cd "$(dirname "$0")/.." && pwd); OUT=$KIT/out
D=${1:?usage: make-fel-sdcard-macos.sh diskN}; D=${D#/dev/}
info=$(diskutil info "$D")
echo "$info" | grep -E "Device / Media Name|Disk Size|Removable Media|Device Location"
echo "$info" | grep -q "Whole: *Yes" || { echo "not a whole disk"; exit 1; }
echo "$info" | grep -Eq "Device Location: *External|Removable Media: *(Removable|Yes)" || { echo "not external/removable; refusing"; exit 1; }
bytes=$(echo "$info" | sed -n 's/.*Disk Size:.*(\([0-9]*\) Bytes).*/\1/p')
[ "$bytes" -le $((64*1000*1000*1000)) ] || { echo "larger than 64 GB; refusing"; exit 1; }
read -r -p "Overwrite bytes 8192-16383 of /dev/$D? Type the disk id ($D): " a; [ "$a" = "$D" ] || exit 3
( cd "$OUT" && shasum -a 256 -c <(grep ' fel-sdboot.sunxi$' SHA256SUMS) )
diskutil unmountDisk "/dev/$D"
sudo dd if="$OUT/fel-sdboot.sunxi" of="/dev/r$D" bs=1k seek=8 conv=notrunc
sync; diskutil eject "/dev/$D"
echo "FEL card ready. Note: a card that already has a partition starting before 16 KiB would be damaged; use a spare card."
