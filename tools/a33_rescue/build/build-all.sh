#!/bin/bash
# Reproducible offline build of the IVI3D A33 rescue kit.
# Host: Debian 13 (trixie) x86_64. Nothing here talks to the board.
#
# apt deps (Debian names):
#   make bc bison flex cpio bzip2 xz-utils python3-setuptools python3-pyelftools python3-libfdt
#   libssl-dev libgnutls28-dev device-tree-compiler gcc-arm-linux-gnueabihf libc6-dev-armhf-cross
#   mtools dosfstools fdisk kmod libelf-dev lzop u-boot-tools pkg-config libusb-1.0-0-dev
#   zlib1g-dev libfdt-dev rsync file
set -euo pipefail
export PATH=$PATH:/sbin:/usr/sbin
KIT=$(cd "$(dirname "$0")/.." && pwd)
W=${W:-/workspace/a33_build}
SRC=$W/src; OUT=$KIT/out
J=${J:-$(nproc)}
X=arm-linux-gnueabihf-
mkdir -p "$SRC" "$OUT"

UBOOT_TAG=v2026.10
LINUX_VER=6.18.62
BUSYBOX_VER=1.37.0
E2FS_VER=1.47.3
SUNXI_TOOLS_COMMIT=34dfa20f8284273085666436e4cac09af19646c8
declare -A SHA=(
 [linux-$LINUX_VER.tar.xz]=490a7aedf1b355c565d3a6c05333ccccb5da82064eca46b590448a7099d7d651
 [busybox-$BUSYBOX_VER.tar.bz2]=3311dff32e746499f4df0d5df04d7eb396382d7e108bb9250e7b519b837043a4
 [e2fsprogs-$E2FS_VER.tar.xz]=857e6ef800feaa2bb4578fbc810214be5d3c88b072ea53c5384733a965737329
)
UBOOT_COMMIT=5508406582f6f7120dce0c4b3059819a41788db2

fetch() { [ -f "$SRC/$2" ] || curl -fsSL -o "$SRC/$2" "$1"; echo "${SHA[$2]}  $SRC/$2" | sha256sum -c -; }

cd "$SRC"
[ -d u-boot ] || git clone -q --depth 1 -b $UBOOT_TAG https://source.denx.de/u-boot/u-boot.git u-boot
[ "$(git -C u-boot rev-parse HEAD)" = $UBOOT_COMMIT ] || { echo "u-boot commit mismatch"; exit 1; }
[ -d sunxi-tools ] || git clone -q https://github.com/linux-sunxi/sunxi-tools sunxi-tools
git -C sunxi-tools checkout -q $SUNXI_TOOLS_COMMIT
fetch https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-$LINUX_VER.tar.xz linux-$LINUX_VER.tar.xz
fetch https://busybox.net/downloads/busybox-$BUSYBOX_VER.tar.bz2 busybox-$BUSYBOX_VER.tar.bz2
fetch https://cdn.kernel.org/pub/linux/kernel/people/tytso/e2fsprogs/v$E2FS_VER/e2fsprogs-$E2FS_VER.tar.xz e2fsprogs-$E2FS_VER.tar.xz
[ -d linux-$LINUX_VER ] || tar xf linux-$LINUX_VER.tar.xz
[ -d busybox-$BUSYBOX_VER ] || tar xf busybox-$BUSYBOX_VER.tar.bz2
[ -d e2fsprogs-$E2FS_VER ] || tar xf e2fsprogs-$E2FS_VER.tar.xz

# ---------- U-Boot ----------
cd "$SRC/u-boot"
git checkout -q -- drivers/usb/gadget/f_mass_storage.c
git apply "$KIT/patches/u-boot-0001-ums-force-read-only.patch"
rm -rf "$W/uboot-out"
make -s O="$W/uboot-out" CROSS_COMPILE=$X Sinlinx_SinA33_defconfig
scripts/kconfig/merge_config.sh -m -O "$W/uboot-out" "$W/uboot-out/.config" "$KIT/configs/u-boot-ivi3d-rescue.fragment" >/dev/null
make -s O="$W/uboot-out" CROSS_COMPILE=$X olddefconfig
make -s O="$W/uboot-out" CROSS_COMPILE=$X DTC=/usr/bin/dtc -j$J
cp "$W/uboot-out/u-boot-sunxi-with-spl.bin" "$OUT/"
# Raw disk devices on macOS need whole-sector writes: pad to a 1 KiB multiple.
cp "$OUT/u-boot-sunxi-with-spl.bin" "$OUT/u-boot-sunxi-with-spl.padded.bin"
truncate -s %1024 "$OUT/u-boot-sunxi-with-spl.padded.bin"
cp "$W/uboot-out/.config" "$KIT/configs/u-boot-ivi3d-rescue.config.full"
# Safety audit: no MMC write/erase, no env save, no fastboot, no EFI in the binary.
if ${X}nm "$W/uboot-out/u-boot" | grep -E ' (mmc_bwrite|mmc_berase|env_save|efi_set_variable_int|fastboot_init|mmc_set_part_conf)$'; then
	echo "AUDIT FAILED: write-capable symbol present"; exit 1; fi
grep -q '^# CONFIG_MMC_WRITE is not set' "$W/uboot-out/.config"
grep -q '^CONFIG_PREBOOT=""' "$W/uboot-out/.config"

# ---------- Linux ----------
cd "$SRC/linux-$LINUX_VER"
cp "$KIT/dts/sun8i-a33-ivi3d-rescue.dts" arch/arm/boot/dts/allwinner/
grep -q ivi3d-rescue arch/arm/boot/dts/allwinner/Makefile || \
	echo 'dtb-$(CONFIG_MACH_SUN8I) += sun8i-a33-ivi3d-rescue.dtb' >> arch/arm/boot/dts/allwinner/Makefile
make -s O="$W/linux-out" ARCH=arm CROSS_COMPILE=$X sunxi_defconfig
scripts/kconfig/merge_config.sh -m -O "$W/linux-out" "$W/linux-out/.config" "$KIT/configs/linux-ivi3d-rescue.fragment" >/dev/null
make -s O="$W/linux-out" ARCH=arm CROSS_COMPILE=$X olddefconfig
make -s O="$W/linux-out" ARCH=arm CROSS_COMPILE=$X -j$J zImage dtbs
make -s O="$W/linux-out" ARCH=arm CROSS_COMPILE=$X usr/gen_init_cpio >/dev/null 2>&1 || true
cp "$W/linux-out/arch/arm/boot/zImage" "$OUT/"
cp "$W/linux-out/arch/arm/boot/dts/allwinner/sun8i-a33-ivi3d-rescue.dtb" "$OUT/"
cp "$W/linux-out/.config" "$KIT/configs/linux-ivi3d-rescue.config.full"
for k in USB_SERIAL DRM NET USB_EHCI_HCD USB_OHCI_HCD; do
	grep -q "^# CONFIG_$k is not set" "$W/linux-out/.config" || { echo "AUDIT FAILED: CONFIG_$k enabled"; exit 1; }
done

# ---------- busybox (static, armhf) ----------
cd "$SRC/busybox-$BUSYBOX_VER"
make -s defconfig >/dev/null
sed -i -e 's/^# CONFIG_STATIC is not set/CONFIG_STATIC=y/' \
       -e 's/^CONFIG_TC=y/# CONFIG_TC is not set/' \
       -e 's/^CONFIG_FEATURE_TC_INGRESS=y/# CONFIG_FEATURE_TC_INGRESS is not set/' \
       -e 's/^CONFIG_SHA1_HWACCEL=y/# CONFIG_SHA1_HWACCEL is not set/' \
       -e 's/^CONFIG_SHA256_HWACCEL=y/# CONFIG_SHA256_HWACCEL is not set/' .config
make -s oldconfig </dev/null >/dev/null 2>&1 || true
make -s -j$J CROSS_COMPILE=$X >/dev/null
make -s CROSS_COMPILE=$X busybox.links >/dev/null
cp .config "$KIT/configs/busybox.config"

# ---------- e2fsprogs (static e2fsck + dumpe2fs, armhf) ----------
cd "$SRC/e2fsprogs-$E2FS_VER"; mkdir -p build-arm; cd build-arm
[ -f Makefile ] || ../configure -q --host=arm-linux-gnueabihf --disable-shared --enable-static --disable-nls \
	--disable-fuse2fs --disable-defrag --disable-imager --disable-uuidd --disable-e2initrd-helper \
	--without-libarchive LDFLAGS=-static >/dev/null
make -s -j$J libs >/dev/null 2>&1; make -s -j$J -C e2fsck e2fsck >/dev/null 2>&1; make -s -j$J -C misc dumpe2fs >/dev/null 2>&1

# ---------- initramfs ----------
R=$W/initramfs-root; rm -rf "$R"; mkdir -p "$R"
cp -a "$KIT/initramfs/rootfs/." "$R/"
mkdir -p "$R"/{bin,sbin,usr/bin,proc,sys,dev,tmp,mnt/sd,mnt/img,root}
install -m755 "$SRC/busybox-$BUSYBOX_VER/busybox" "$R/bin/busybox"
${X}strip -o "$R/sbin/e2fsck"   "$SRC/e2fsprogs-$E2FS_VER/build-arm/e2fsck/e2fsck"
${X}strip -o "$R/sbin/dumpe2fs" "$SRC/e2fsprogs-$E2FS_VER/build-arm/misc/dumpe2fs"
LIST=$W/initramfs.list
{
	echo "dir /dev 0755 0 0"; echo "nod /dev/console 0600 0 0 c 5 1"; echo "nod /dev/null 0666 0 0 c 1 3"
	(cd "$R" && find . -mindepth 1 -type d | sed 's#^\./##' | sort | while read -r d; do [ "$d" = dev ] || echo "dir /$d 0755 0 0"; done)
	(cd "$R" && find . -type f | sed 's#^\./##' | sort | while read -r f; do
		m=$(stat -c %a "$R/$f"); echo "file /$f $R/$f $m 0 0"; done)
	# Applet symlinks at busybox's own install paths (busybox.links), all -> /bin/busybox.
	while read -r a; do
		[ "$a" = /bin/busybox ] && continue
		echo "slink $a /bin/busybox 0777 0 0"
	done < "$SRC/busybox-$BUSYBOX_VER/busybox.links"
	echo "slink /init /sbin/init 0777 0 0"
} > "$LIST"
grep -q " /sbin/init " "$LIST"
"$W/linux-out/usr/gen_init_cpio" "$LIST" | gzip -9n > "$OUT/initramfs.cpio.gz"
mkimage -A arm -O linux -T ramdisk -C none -n "IVI3D rescue initramfs" -d "$OUT/initramfs.cpio.gz" "$OUT/uInitrd" >/dev/null

# ---------- U-Boot scripts ----------
for s in ivi-rescue fel-boot fel-ums; do
	mkimage -A arm -O linux -T script -C none -n "IVI3D $s" -d "$KIT/bootscripts/$s.cmd" "$OUT/$s.scr" >/dev/null
done

# ---------- sunxi-tools (host Linux build for testing; FEL-forcing SD image) ----------
make -s -C "$SRC/sunxi-tools" sunxi-fel >/dev/null
cp "$SRC/sunxi-tools/bin/fel-sdboot.sunxi" "$OUT/fel-sdboot.sunxi"

# ---------- prebuilt 64 MiB microSD image (boot test; FAT32 p1 at 4 MiB) ----------
"$KIT/sdcard/make-sdcard-image.sh" "$OUT" "$OUT/ivi-rescue-sd-64M.img"

(cd "$OUT" && sha256sum $(ls | grep -v SHA256SUMS) > SHA256SUMS)
echo "BUILD OK -> $OUT"
