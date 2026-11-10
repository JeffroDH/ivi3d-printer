#!/bin/bash
# [R1 USB-RO] Boot only U-Boot over FEL and export the eMMC to this computer as a
# write-protected USB disk (U-Boot 'ums'). This U-Boot has no MMC write code and the
# UMS LUN is forced read-only, so the host cannot write the eMMC through it.
set -euo pipefail
. "$(dirname "$0")/fel-common.sh"
sha_check u-boot-sunxi-with-spl.bin fel-ums.scr
require_a33
echo
echo "RISK R1: board RAM only; eMMC exported read-only. Image it with fel/image-emmc-macos.sh."
ask_yes "Start U-Boot UMS (read-only)?"
"$FEL" -v -p uboot "$OUT/u-boot-sunxi-with-spl.bin" write 0x43100000 "$OUT/fel-ums.scr"
echo "Wait ~5 s, then: diskutil list   (look for a ~3.96 GB external disk)"
