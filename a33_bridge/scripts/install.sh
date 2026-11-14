#!/bin/sh
# install.sh [srcdir] - persistent start-at-boot install (run only after the RAM test passed).
# WRITES to the eMMC p7:
#   /userapp/ivibridge/  (ivibridge ~0.5 MB, scripts, apikey, rcS.before_bridge)
#   ONE line appended to /etc/init.d/rcS (tagged '# ivibridge-hook'), same style as the
#   existing ivissh line. The ivissh hook is left untouched.
# Nothing else (autorun.sh is not edited). Undo with: sh /userapp/ivibridge/uninstall.sh
R=${IVIB_ROOT:-}
SRC=${1:-$(dirname "$0")}
H=$R/userapp/ivibridge
A=$R/etc/init.d/rcS
TAG='# ivibridge-hook'
die() { echo "install: ERROR: $*"; exit 1; }
[ -f "$A" ] || die "$A not found"
grep -q "$TAG" "$A" && { echo "install: already installed (hook present); nothing changed"; exit 0; }
for f in ivibridge ivibridge-ram.sh boot.sh uninstall.sh; do [ -f "$SRC/$f" ] || die "missing $SRC/$f"; done
if [ -f "$SRC/SHA256SUMS" ]; then
    want=$(grep ' ivibridge$' "$SRC/SHA256SUMS" | cut -d' ' -f1); got=$(sha256sum "$SRC/ivibridge" | cut -d' ' -f1)
    [ -n "$want" ] && [ "$want" != "$got" ] && die "ivibridge checksum mismatch"
fi
"$SRC/ivibridge" -V > /dev/null 2>&1 || [ -n "$R" ] || die "ivibridge does not run here"
mkdir -p "$H" || die "cannot create $H"
for f in ivibridge ivibridge-ram.sh boot.sh uninstall.sh; do cp "$SRC/$f" "$H/$f" || die "copy $f"; chmod 755 "$H/$f"; done
cp -p "$A" "$H/rcS.before_bridge" || die "backup of rcS failed"
if [ ! -s "$H/apikey" ]; then
    if [ -s /tmp/ivibridge/apikey ] && [ -z "$R" ]; then cp /tmp/ivibridge/apikey "$H/apikey"      # keep the RAM-test key
    else (umask 077; head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n' > "$H/apikey"); fi
    chmod 600 "$H/apikey"
fi
# same style as: /bin/sh /userapp/ivissh/boot.sh </dev/null >/dev/null 2>&1 &
printf '%s\n' "/bin/sh /userapp/ivibridge/boot.sh </dev/null >/dev/null 2>&1 &  $TAG" >> "$A"
if ! sh -n "$A"; then
    cp -p "$H/rcS.before_bridge" "$A"
    die "rcS failed sh -n; restored backup, nothing left installed"
fi
sync
echo "install: done. Hook added to $A; files in $H. API key: cat $H/apikey"
