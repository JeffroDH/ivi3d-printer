# IVI3D rescue: U-Boot script for the microSD path (compiled to ivi-rescue.scr).
# Loads everything from microSD partition 1 into RAM. Touches nothing on the eMMC.
echo "== IVI3D rescue: loading kernel + initramfs from microSD (mmc 0:1) =="
mmc dev 0
setenv bootargs "console=ttyS0,115200 earlycon regulator_ignore_unused clk_ignore_unused rdinit=/sbin/init loglevel=4 ivi.boot=sd"
load mmc 0:1 ${kernel_addr_r} zImage
load mmc 0:1 ${fdt_addr_r} sun8i-a33-ivi3d-rescue.dtb
load mmc 0:1 ${ramdisk_addr_r} uInitrd
bootz ${kernel_addr_r} ${ramdisk_addr_r} ${fdt_addr_r}
echo "bootz returned: staying at the U-Boot prompt"
