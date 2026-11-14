#!/bin/sh
# uninstall.sh - remove the persistent install. Removes only the tagged hook line
# from /etc/init.d/rcS and verifies the result matches rcS.before_bridge. The
# ivissh hook is left untouched. Deletes /userapp/ivibridge/. Jobs and logs on p1
# are kept; delete them yourself if wanted.
R=${IVIB_ROOT:-}
H=$R/userapp/ivibridge
A=$R/etc/init.d/rcS
TAG='# ivibridge-hook'
if [ -z "$R" ] && [ -f /tmp/ivibridge/ivibridge.pid ]; then
    IVIB_DIR=/tmp/ivibridge IVIB_BIN=$H/ivibridge IVIB_KEYFILE=$H/apikey sh "$H/ivibridge-ram.sh" stop
fi
if grep -q "$TAG" "$A" 2>/dev/null; then
    grep -v "$TAG" "$A" > /tmp/rcS.ivib-check
    if [ -f "$H/rcS.before_bridge" ] && cmp -s /tmp/rcS.ivib-check "$H/rcS.before_bridge"; then
        cp -p "$H/rcS.before_bridge" "$A.ivib-tmp" && mv "$A.ivib-tmp" "$A" && echo "uninstall: rcS hook removed; matches backup"
    else
        # still remove only the tagged line (do not clobber later rcS edits with the backup)
        if sed -i "/$TAG/d" "$A"; then
            echo "uninstall: rcS was edited since install; removed only the hook line (does not match backup)"
        else
            echo "uninstall: ERROR: failed to remove hook line"; rm -f /tmp/rcS.ivib-check; exit 1
        fi
    fi
    rm -f /tmp/rcS.ivib-check
else
    echo "uninstall: no hook in $A"
fi
rm -rf "$H"
sync
echo "uninstall: done (reboot or 'sh ivibridge-ram.sh stop' leaves the printer fully stock)"
