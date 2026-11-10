#!/bin/sh
# ivitap.sh X Y [DEV] [HOLD_US] - BusyBox-only fallback (no binary upload needed).
# Builds 16-byte struct input_event records with printf octal escapes and writes them with
# dd bs=16 so every write() is exactly one event (evdev_write rejects partial events).
# Mirrors gt9xx_ts Type-A frames. Does NOT verify the device name; run
#   cat /proc/bus/input/devices   first and pass the gt9xx node explicitly.
X=$1; Y=$2; DEV=${3:-/dev/input/event3}; HOLD=${4:-100000}
case "$X$Y" in *[!0-9]*|"") echo "usage: $0 X Y [dev] [hold_us]"; exit 2;; esac
[ "$X" -le 799 ] && [ "$Y" -le 479 ] || { echo "refusing: x 0..799 y 0..479"; exit 2; }
o() { printf '\\%03o' $(( $1 & 255 )); }
ev() { # type code value
  printf '\000\000\000\000\000\000\000\000'
  printf "$(o $1)$(o $(($1>>8)))$(o $2)$(o $(($2>>8)))$(o $3)$(o $(($3>>8)))$(o $(($3>>16)))$(o $(($3>>24)))"
}
T=/tmp/ivitap.$$
{ ev 3 53 $X; ev 3 54 $Y; ev 3 48 20; ev 3 50 20; ev 3 57 0; ev 0 2 0; ev 0 0 0; } > $T.down
{ ev 3 48 0; ev 3 50 0; ev 0 2 0; ev 0 0 0; } > $T.up
[ "$(wc -c < $T.down)" -eq 112 ] && [ "$(wc -c < $T.up)" -eq 64 ] || { echo "bad sizes"; rm -f $T.*; exit 1; }
dd if=$T.down of=$DEV bs=16 2>/dev/null
usleep $HOLD
dd if=$T.up of=$DEV bs=16 2>/dev/null
rm -f $T.down $T.up
echo "tapped $X,$Y on $DEV"
