# IVI3D rescue: U-Boot script for the FEL (USB, RAM-only) path (compiled to fel-boot.scr).
# sunxi-fel has already written zImage, DTB and uInitrd into DRAM at these addresses.
echo "== IVI3D rescue: FEL RAM boot (nothing is read from or written to storage) =="
setenv bootargs "console=ttyS0,115200 earlycon regulator_ignore_unused clk_ignore_unused rdinit=/sbin/init loglevel=4 ivi.boot=fel"
bootz 0x42000000 0x43400000 0x43000000
echo "bootz returned: staying at the U-Boot prompt"
