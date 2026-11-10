#!/bin/bash
# [R1 RAM] Boot the rescue system entirely from RAM over FEL.
# Loads U-Boot SPL (initialises DRAM), U-Boot, the kernel, DTB, initramfs and a boot script
# into DRAM and runs them. Nothing is read from or written to the eMMC or microSD by this step.
# The rescue system then sets the eMMC read-only at startup. Power-cycle to leave.
set -euo pipefail
. "$(dirname "$0")/fel-common.sh"
sha_check u-boot-sunxi-with-spl.bin zImage sun8i-a33-ivi3d-rescue.dtb uInitrd fel-boot.scr
require_a33
echo
echo "RISK R1: writes ONLY board RAM. Watch the debug UART (115200 8N1) for the rescue banner."
ask_yes "Load and start the rescue system in RAM?"
"$FEL" -v -p uboot "$OUT/u-boot-sunxi-with-spl.bin" \
	write 0x42000000 "$OUT/zImage" \
	write 0x43000000 "$OUT/sun8i-a33-ivi3d-rescue.dtb" \
	write 0x43400000 "$OUT/uInitrd" \
	write 0x43100000 "$OUT/fel-boot.scr"
echo "Started. Expect on UART: '(FEL boot)' then the 'IVI3D A33 RESCUE' banner; press Enter there."
