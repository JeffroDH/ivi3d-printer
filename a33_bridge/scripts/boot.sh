#!/bin/sh
# /userapp/ivibridge/boot.sh — started in the background by one tagged hook in
# /etc/init.d/rcS (same style as the ivissh line, which is left untouched).
# Waits for the real /dev/ttyUSB0 (mdev), then starts the bridge so the pty
# link is in place before IVI-Main-Controller opens the port. No app restart
# is needed in that case. On timeout or failure, stock is left untouched. If
# the app is already running when the bridge is ready, the supervisor falls
# back to its restart-app path.
#
# Kill switches (no UART needed):
#   /userapp/ivibridge/disable
#   /userdata/WifiFile/ivibridge.disable  (checked if p1 is already mounted, or
#       as soon as autorun mounts it; p1 is never mounted read-write here, and
#       is not mounted at all, so autorun's mount-or-mkfs.vfat path is not raced)
#   a 'no-bridge' file at the root of any mounted /dev/sd* USB volume; if none
#       is mounted, a brief read-only mount of /dev/sda1 then /dev/sda is tried
#
# Failure counter: /userapp/ivibridge/bootfail is incremented before start and
# reset to 0 after IVIB_HEALTH_WAIT seconds (default 60) of a healthy daemon,
# watchdog and link. If it is already >=2 at boot, start is skipped.
H=${IVIB_HOME:-/userapp/ivibridge}
P1=${IVIB_P1:-/userdata/WifiFile}
MOUNTS=${IVIB_MOUNTS:-/proc/mounts}
LINK=${IVIB_LINK:-/dev/ttyUSB0}
D=${IVIB_DIR:-/tmp/ivibridge}
FAIL=${IVIB_BOOTFAIL:-$H/bootfail}
TTY_TO=${IVIB_TTY_TIMEOUT:-30}
USB_TRY=${IVIB_USB_TRY:-"/dev/sda1 /dev/sda"}
mkdir -p "$D" || exit 0
LOG=$D/boot.log
LOGMAX=${IVIB_LOG_MAX:-1048576}

blog() {
    ts=$(date '+%Y-%m-%d %H:%M:%S' 2>/dev/null)
    line="${ts:-} $*"
    echo "$line" >> "$LOG" 2>/dev/null
    echo "ivibridge-boot: $*"
    pdir=""
    if [ -f "$D/p1.ready" ]; then pdir=$(head -n 1 "$D/p1.ready" 2>/dev/null); fi
    if [ -n "$pdir" ] && [ -d "$pdir/ivibridge_logs" ]; then
        _rot "$pdir/ivibridge_logs/boot.log"
        echo "$line" >> "$pdir/ivibridge_logs/boot.log" 2>/dev/null
        sync
    fi
}
_rot() {
    [ -f "$1" ] || return 0
    sz=$(wc -c < "$1" 2>/dev/null); sz=${sz:-0}
    [ "$sz" -ge "$LOGMAX" ] 2>/dev/null || return 0
    mv -f "$1" "$1.1" 2>/dev/null
}

p1_mounted() {
    [ -r "$MOUNTS" ] || return 1
    while read dev mp typ rest; do
        [ "$mp" = "$P1" ] && return 0
    done < "$MOUNTS"
    return 1
}

# USB off switch: 'no-bridge' at the root of a mounted /dev/sd*, or a brief
# read-only mount of sda1/sda under /tmp if nothing is mounted yet.
usb_off() {
    any=0
    if [ -r "$MOUNTS" ]; then
        while read dev mp typ rest; do
            case "$dev" in
            /dev/sd*)
                any=1
                if [ -f "$mp/no-bridge" ]; then return 0; fi
                ;;
            esac
        done < "$MOUNTS"
    fi
    [ "$any" = 0 ] || return 1
    chk=${IVIB_USBCHK:-/tmp/ivib-usbchk}
    mkdir -p "$chk" 2>/dev/null || return 1
    hit=1
    for dev in $USB_TRY; do
        [ -b "$dev" ] || [ -n "${IVIB_TEST:-}" ] || continue
        if mount -o ro "$dev" "$chk" 2>/dev/null; then
            if [ -f "$chk/no-bridge" ]; then hit=0; fi
            umount "$chk" 2>/dev/null
            [ "$hit" = 0 ] && break
        fi
    done
    rmdir "$chk" 2>/dev/null
    return $hit
}

is_real_tty() {
    if [ -c "$LINK" ] && [ ! -L "$LINK" ]; then return 0; fi
    # box tests use a regular file as the stand-in for a char node
    if [ "${IVIB_TEST:-0}" = 1 ] && [ -f "$LINK" ] && [ ! -L "$LINK" ]; then return 0; fi
    return 1
}

off() {
    [ -f "$H/disable" ] && { blog "disabled by $H/disable"; return 0; }
    if p1_mounted && [ -f "$P1/ivibridge.disable" ]; then
        blog "disabled by $P1/ivibridge.disable"; return 0
    fi
    if usb_off; then blog "disabled by USB no-bridge"; return 0; fi
    return 1
}

if off; then exit 0; fi

n=0
# already-failed count (do not increment yet)
failc=0
[ -f "$FAIL" ] && failc=$(cat "$FAIL" 2>/dev/null)
case "$failc" in *[!0-9]*|"") failc=0;; esac
if [ "$failc" -ge 2 ]; then
    blog "disabled after 2 failed boots"
    exit 0
fi

# wait for mdev to create the real CH340 node; do not start if it never appears
to=$((TTY_TO * 10))
[ "$to" -lt 1 ] && to=1
while [ $n -lt $to ]; do
    is_real_tty && break
    usleep 100000
    n=$((n + 1))
done
if ! is_real_tty; then
    blog "timeout waiting for $LINK; leaving stock untouched"
    exit 0
fi

if off; then exit 0; fi

# increment before start; reset later by the health helper
echo $((failc + 1)) > "$FAIL" 2>/dev/null
sync

export IVIB_DIR="$D" IVIB_BIN=${IVIB_BIN:-$H/ivibridge} IVIB_KEYFILE=${IVIB_KEYFILE:-$H/apikey}
export IVIB_SELF=${IVIB_SELF:-$H/ivibridge-ram.sh} IVIB_HOME="$H" IVIB_P1="$P1" IVIB_MOUNTS="$MOUNTS"
export IVIB_UPDIR=${IVIB_UPDIR:-/tmp/ivi_jobs}
export IVIB_LINK="$LINK" IVIB_BOOTFAIL="$FAIL"
blog "starting supervisor (bootfail=$((failc + 1)))"
# start returns after the daemon/watchdog are up; it does not start the app
# unless the app was already running (restart-app fallback).
if ! sh ${IVIB_SELF:-$H/ivibridge-ram.sh} start; then
    blog "start failed; stock left/restored by the supervisor"
    exit 1
fi
blog "bridge started"
exit 0
