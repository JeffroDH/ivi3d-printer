#!/bin/sh
# IVI3D rescue system init (runs once, from RAM).
# Does NOT fsck, mount, or write anything on the eMMC.
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev 2>/dev/null
mkdir -p /dev/pts && mount -t devpts devpts /dev/pts
mount -t tmpfs -o size=64m tmpfs /tmp
mount -t configfs configfs /sys/kernel/config 2>/dev/null
mkdir -p /mnt/sd /mnt/img
echo 1 > /proc/sys/kernel/printk 2>/dev/null   # keep kernel chatter off the console

. /usr/lib/ivi/common.sh

# Wait up to 15 s for the eMMC to appear.
i=0
while [ $i -lt 15 ]; do
	ivi_find_devices && [ -n "$EMMC" ] && break
	sleep 1; i=$((i+1))
done

{
echo
echo "=============================================================="
echo " IVI3D A33 RESCUE  (kernel $(uname -r), running from RAM)"
echo "=============================================================="
if [ -n "$EMMC" ]; then
	ivi_lock_emmc
	echo " eMMC : /dev/$EMMC  -> READ-ONLY (blockdev --setro, whole disk + partitions)"
else
	echo " eMMC : NOT FOUND"
fi
if [ -n "$SDCARD" ]; then
	if ivi_mount_sd; then
		echo " SD   : /dev/$SDCARD  data partition mounted rw at /mnt/sd"
	else
		echo " SD   : /dev/$SDCARD  (no usable FAT/exFAT/ext4 partition 1; not mounted)"
	fi
else
	echo " SD   : none (FEL/RAM boot without a card is fine)"
fi
echo
echo " READ-ONLY commands : ivi-status  ivi-verify  ivi-image-check  ivi-ums-ro"
echo " SD-ONLY writes     : ivi-backup  ivi-prep-p7"
echo " eMMC WRITES        : ivi-restore-part  ivi-restore-full  ivi-fsck-p7"
echo "                      (each asks for a typed confirmation and checks MD5 first)"
echo " Leave              : ivi-off   (sync + power off; nothing was written unless you ran a write command)"
echo " Docs               : RESCUE.md on the build zip; 'ivi-help' here"
echo "=============================================================="
} > /tmp/ivi-banner.txt
cat /tmp/ivi-banner.txt
