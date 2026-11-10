# IVI3D rescue: FEL script that only exports the eMMC over USB from U-Boot (compiled to fel-ums.scr).
# This U-Boot build has no MMC write support and the UMS LUN is forced write-protected.
echo "== IVI3D rescue: U-Boot UMS, eMMC exported READ-ONLY over the OTG port. Ctrl-C to stop. =="
mmc list
ums 0 mmc 1
echo "ums ended: staying at the U-Boot prompt"
