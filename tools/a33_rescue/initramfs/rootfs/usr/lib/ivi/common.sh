# shellcheck shell=sh
# IVI3D rescue common helpers (busybox ash).
KNOWN=${IVI_TEST_KNOWN:-/etc/ivi/known-good.txt}   # IVI_TEST_KNOWN: off-target tests only
EMMC_EXPECT_BYTES=3959422976     # user area of the IVI eMMC (= mmcblk0.img size)
SD_MNT=/mnt/sd
EMMC=""; SDCARD=""

say()  { echo "$*"; ivi_log "$*"; }
die()  { echo "ERROR: $*" >&2; ivi_log "ERROR: $*"; exit 1; }
ivi_log() {
	_d=/tmp; mountpoint -q "$SD_MNT" 2>/dev/null && _d="$SD_MNT/ivi-rescue-logs"
	mkdir -p "$_d" 2>/dev/null
	echo "[$(cat /proc/uptime | cut -d' ' -f1)s] $*" >> "$_d/session.log" 2>/dev/null
}
risk() { echo; echo "---- RISK: $1 ----"; echo; }

# Locate the eMMC (type MMC) and the microSD (type SD) by what they are,
# never by name, because numbering differs between stock and rescue kernels.
ivi_find_devices() {
	EMMC=""; SDCARD=""
	# Off-target test hook only (never set on the board): pretend these are the devices.
	if [ -n "$IVI_TEST_EMMC" ]; then
		echo "TEST MODE: IVI_TEST_EMMC=$IVI_TEST_EMMC" >&2
		EMMC=$IVI_TEST_EMMC; SDCARD=$IVI_TEST_SD; return 0
	fi
	for b in /sys/block/mmcblk*; do
		[ -e "$b" ] || continue
		n=${b##*/}
		case "$n" in *boot*|*rpmb*) continue;; esac
		t=$(cat "$b/device/type" 2>/dev/null)
		case "$t" in
			MMC) [ -n "$EMMC" ] && { echo "ERROR: more than one eMMC found" >&2; return 2; }
			     EMMC=$n ;;
			SD)  SDCARD=$n ;;
		esac
	done
	return 0
}

ivi_parts() { for p in /sys/block/$1/$1p*; do [ -e "$p" ] && echo "${p##*/}"; done; }
ivi_bytes() { echo $(( $(cat /sys/class/block/$1/size) * 512 )); }
ivi_start() { cat /sys/class/block/$1/start 2>/dev/null || echo 0; }

ivi_lock_emmc() {
	[ -n "$EMMC" ] || return 1
	for p in $(ivi_parts "$EMMC"); do blockdev --setro "/dev/$p"; done
	blockdev --setro "/dev/$EMMC"
	for bp in ${EMMC}boot0 ${EMMC}boot1; do
		[ -e "/dev/$bp" ] || continue
		blockdev --setro "/dev/$bp"
		[ -w "/sys/block/$bp/force_ro" ] && echo 1 > "/sys/block/$bp/force_ro"
	done
}
ivi_ro_state() { blockdev --getro "/dev/$1" 2>/dev/null; }

ivi_mounted() {  # $1 = device name prefix (e.g. mmcblk1) ; true if any part is mounted/swapped
	grep -q "^/dev/$1" /proc/mounts && return 0
	grep -q "^/dev/$1" /proc/swaps 2>/dev/null && return 0
	return 1
}

ivi_mount_sd() {
	[ -n "$SDCARD" ] || return 1
	mountpoint -q "$SD_MNT" && return 0
	dev=/dev/${SDCARD}p1; [ -b "$dev" ] || return 1
	for fs in vfat exfat ext4; do
		mount -t $fs -o rw "$dev" "$SD_MNT" 2>/dev/null && return 0
	done
	return 1
}

known_size() { awk -v n="$1" '$1==n{print $2}' "$KNOWN"; }
known_md5()  { awk -v n="$1" '$1==n{print $3}' "$KNOWN"; }

# md5 of the first $2 bytes of a file or device (whole file if $2 empty).
md5_of() {
	if [ -z "$2" ]; then md5sum "$1" | cut -d' ' -f1; return; fi
	if [ $(( $2 % 1048576 )) -eq 0 ]; then
		dd if="$1" bs=1M count=$(( $2 / 1048576 )) 2>/dev/null | md5sum | cut -d' ' -f1
	else
		dd if="$1" bs=512 count=$(( $2 / 512 )) 2>/dev/null | md5sum | cut -d' ' -f1
	fi
}
file_bytes() { stat -c %s "$1" 2>/dev/null || wc -c < "$1"; }

# Typed confirmation. The phrase must be typed exactly; anything else aborts.
confirm_typed() {
	phrase="$1"
	[ -t 0 ] || die "refusing: no interactive terminal for confirmation"
	echo
	echo "To continue, type exactly:   $phrase"
	printf "> "
	read -r answer
	[ "$answer" = "$phrase" ] || { say "Aborted (confirmation did not match). Nothing was written."; exit 3; }
	ivi_log "CONFIRMED: $phrase"
}

# Loop-attach an image read-only with partition scan. Prints loop device name.
loop_ro() {
	l=$(losetup -f) || die "no free loop device"
	losetup -r -P "$l" "$1" || die "losetup failed on $1"
	sleep 1
	echo "${l##*/}"
}

# Compare partition starts/sizes of an attached image with the eMMC.
same_layout() {  # $1 loop name, $2 emmc name
	ok=0
	for n in 1 2 5 6 7; do
		a="$(ivi_start ${1}p$n) $(cat /sys/class/block/${1}p$n/size 2>/dev/null)"
		b="$(ivi_start ${2}p$n) $(cat /sys/class/block/${2}p$n/size 2>/dev/null)"
		if [ "$a" != "$b" ]; then echo "  p$n  image: $a   eMMC: $b   <-- DIFFERENT"; ok=1
		else echo "  p$n  start/size (sectors): $a  (match)"; fi
	done
	return $ok
}

needs_recovery() { dumpe2fs -h "$1" 2>/dev/null | grep -q '^Filesystem features:.*needs_recovery'; }

# Restore read-only flags no matter how a write command exits.
_relock() { ivi_find_devices >/dev/null 2>&1; ivi_lock_emmc; sync; }
relock_on_exit() {
	trap '_relock' EXIT
	trap '_relock; echo "Interrupted. eMMC set read-only again. A partial write may have happened: re-run the verify step." >&2; exit 130' INT TERM HUP
}
