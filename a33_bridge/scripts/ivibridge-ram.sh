#!/bin/sh
# ivibridge-ram.sh {start|stop|status|watchdog}   (for ivibridge 0.1.19-a33)
# RAM-only run of the A33 Wi-Fi bridge (busybox 1.18 ash). Writes only to /tmp (tmpfs) and /dev (devtmpfs);
# nothing on the eMMC changes, and a reboot always returns the printer to stock.
#   start : save the app's env/cwd/stdout, stop IVI-Main-Controller, make /dev/ivi-stm32 (same major:minor as
#           /dev/ttyUSB0), start ivibridge (it swaps /dev/ttyUSB0 for a symlink to its pty), start the watchdog,
#           If the app was running, restart it with its saved environment so it
#           opens the pty. If it was not, then at boot (uptime under IVIB_BOOT_WINDOW,
#           no needs_app marker) leave it for autorun. On a hot restart (stop wrote
#           needs_app, or uptime is past the boot window) start it the same way
#           autorun does, with the stock Qt/tslib environment if no saved env is
#           present. Never start a second copy if one is already running.
#   stop  : stop watchdog + daemon (the daemon stops a running network job first), put the real /dev/ttyUSB0
#           node back, remove /dev/ivi-stm32, restart the app on the real port.
#   status: pids, device nodes and whether the HTTP ports are listening (read from /proc/net/tcp). It never opens a
#           network connection (the printer's loopback interface is down), so it cannot hang.
#   watchdog (internal): if the daemon dies, fail safe to stock (restore node, restart app) and exit. No restart loop.
# Every background process gets stdin/stdout/stderr redirected, so 'ssh printer sh ivibridge-ram.sh start' returns at once.
# Every path can be overridden with IVIB_* variables (used by the box test harness).
D=${IVIB_DIR:-/tmp/ivibridge}
BIN=${IVIB_BIN:-$D/ivibridge}
LINK=${IVIB_LINK:-/dev/ttyUSB0}
REAL=${IVIB_REAL:-/dev/ivi-stm32}
SYSDEV=${IVIB_SYSDEV:-/sys/class/tty/ttyUSB0/dev}
APP=${IVIB_APP:-/userapp/app/IVI-Main-Controller}
UPDIR=${IVIB_UPDIR:-/tmp/ivi_jobs}
PORT=${IVIB_PORT:-5001}
PORT2=${IVIB_PORT2:-80}
KEYFILE=${IVIB_KEYFILE:-$D/apikey}
EXTRA=${IVIB_ARGS:-}
MKNOD=${IVIB_MKNOD:-mknod}
SELF=${IVIB_SELF:-$0}
LCK=${IVIB_LOCKFILE:-/tmp/LCK..$(basename "$LINK")}   # QSerialPort's lock file (tmpfs)
APPNAME=$(basename "$APP")
LOG=$D/ivibridge.log

_rot() {
    [ -f "$1" ] || return 0
    sz=$(wc -c < "$1" 2>/dev/null); sz=${sz:-0}
    [ "$sz" -ge "${IVIB_LOG_MAX:-1048576}" ] 2>/dev/null || return 0
    mv -f "$1" "$1.1" 2>/dev/null
}
say() {
    echo "ivibridge-ram: $*"
    line="$(date '+%Y-%m-%d %H:%M:%S') $*"
    echo "$line" >> "$D/ram.log" 2>/dev/null
    if [ -f "$D/p1.ready" ]; then
        pdir=$(head -n 1 "$D/p1.ready" 2>/dev/null)
        if [ -n "$pdir" ] && [ -d "$pdir/ivibridge_logs" ]; then
            _rot "$pdir/ivibridge_logs/ram.log"
            echo "$line" >> "$pdir/ivibridge_logs/ram.log" 2>/dev/null
            case "$*" in *ERROR*|*"failing safe"*|*"running:"*|*stopped*|*"link lost"*) sync;; esac
        fi
    fi
}
die() { say "ERROR: $*"; exit 1; }
first() { echo "${1:-}"; }
app_pid() { first $(pidof "$APPNAME" 2>/dev/null); }
alive() { [ -n "${1:-}" ] && kill -0 "$1" 2>/dev/null; }
is_node() { { [ -c "$1" ] && [ ! -L "$1" ]; } || { [ "${IVIB_TEST:-0}" = 1 ] && [ -f "$1" ] && [ ! -L "$1" ]; }; }

save_app() {
    p=$(app_pid); alive "$p" || return 1
    tr '\000' '\n' < /proc/$p/environ > "$D/app.env"
    readlink /proc/$p/cwd > "$D/app.cwd"
    readlink /proc/$p/fd/1 > "$D/app.out"
    return 0
}

stop_app() {
    p=$(app_pid); alive "$p" || return 0
    kill "$p" 2>/dev/null; n=0
    while alive "$p" && [ $n -lt 50 ]; do usleep 100000; n=$((n+1)); done
    alive "$p" && kill -9 "$p" 2>/dev/null
    usleep 300000
    rm -f "$LCK"             # the app is gone, so its serial lock is stale
    return 0
}

# Seconds since boot (IVIB_UPTIME overrides, used by the box tests).
uptime_s() {
    if [ -n "${IVIB_UPTIME:-}" ]; then echo "$IVIB_UPTIME"; return; fi
    read u rest < /proc/uptime 2>/dev/null
    u=${u%%.*}
    case "$u" in *[!0-9]*|"") echo 0;; *) echo "$u";; esac
}

# Qt/tslib environment from stock /etc/profile, without running setup_module.sh,
# timeStartKore.sh, timeCloseKore.sh, or autorun.sh.
apply_stock_env() {
    export TSLIB_TSEVENTTYPE=H3600
    export TSLIB_CONSOLEDEVICE=none
    export TSLIB_FBDEVICE=/dev/fb0
    export TSLIB_CALIBFILE=/etc/pointercal
    export TSLIB_CONFFILE=/etc/ts.conf
    export TSLIB_PLUGINDIR=/usr/lib/ts
    if [ -e /dev/input/event4 ]; then
        export TSLIB_TSDEVICE=/dev/input/event4
        export QT_QPA_EVDEV_TOUCHSCREEN_PARAMETERS=/dev/input/event4
    elif [ -e /dev/input/event3 ]; then
        export TSLIB_TSDEVICE=/dev/input/event3
        export QT_QPA_EVDEV_TOUCHSCREEN_PARAMETERS=/dev/input/event3
    elif [ -e /dev/input/event2 ]; then
        export TSLIB_TSDEVICE=/dev/input/event2
        export QT_QPA_EVDEV_TOUCHSCREEN_PARAMETERS=/dev/input/event2
    elif [ -e /dev/input/event1 ]; then
        export TSLIB_TSDEVICE=/dev/input/event1
        export QT_QPA_EVDEV_TOUCHSCREEN_PARAMETERS=/dev/input/event1
    fi
    export QTDIR=/opt/qt-5.9.6
    export QWS_DISPLAY=LinuxFb:/dev/fb0
    export QWS_SIZE=800x480
    export LD_LIBRARY_PATH=$QTDIR/lib
    export QWS_MOUSE_PROTO=tslib:${TSLIB_TSDEVICE:-}
    export QT_QPA_PLATFORM_PLUGIN_PATH=$QTDIR/plugins
    export QT_QPA_PLATFORM=linuxfb:fb=/dev/fb0
    export QT_QPA_FONTDIR=$QTDIR/lib/fonts/
    export QML2_IMPORT_PATH=$QTDIR/qml
    export PATH=/kore/install-dir/bin:/bin:/sbin:/usr/bin:/usr/sbin:/usr/bin/X11:/usr/local/bin
}

# Same launch as autorun.sh: "/userapp/app/IVI-Main-Controller &" from the login
# shell (cwd /, stdout on ttyS2, profile env). Prefer a previously saved env/cwd/stdout
# when we stopped a running app. Do not start a second copy.
start_app() {
    alive "$(app_pid)" && return 0
    cwd=$(cat "$D/app.cwd" 2>/dev/null)
    if [ ! -d "$cwd" ]; then
        if [ -d / ]; then cwd=/; else cwd=$(dirname "$APP"); fi
    fi
    out=$(cat "$D/app.out" 2>/dev/null)
    if ! { [ -n "$out" ] && [ -w "$out" ]; }; then
        if [ -w /dev/ttyS2 ]; then out=/dev/ttyS2; else out=/dev/null; fi
    fi
    (
        if [ -f "$D/app.env" ]; then
            while IFS= read -r l; do case "$l" in *=*) export "$l";; esac; done < "$D/app.env"
        else
            apply_stock_env
        fi
        cd "$cwd" && exec "$APP" > "$out" 2>&1 < /dev/null
    ) > /dev/null 2>&1 < /dev/null &
    say "app restarted (pid $!)"
}

restore_node() {
    if ! is_node "$LINK"; then
        mm=$(cat "$D/ttyUSB0.dev" 2>/dev/null)
        case "$mm" in [0-9]*:[0-9]*) ;; *) say "no saved major:minor; leaving $LINK"; return 1;; esac
        rm -f "$LINK"; $MKNOD "$LINK" c "${mm%%:*}" "${mm##*:}" && say "restored $LINK ($mm)"
    fi
    rm -f "$REAL"
}

# is anything listening on TCP port $1? (/proc/net/tcp + tcp6, state 0A = LISTEN; no sockets opened)
port_listening() {
    hex=$(printf '%04X' "$1")
    for f in /proc/net/tcp /proc/net/tcp6; do
        [ -r "$f" ] || continue
        while read -r sl la ra st rest; do
            case "$la" in *:$hex) [ "$st" = "0A" ] && return 0;; esac
        done < "$f"
    done
    return 1
}

fail_safe() {          # back to stock: real node, no bridge, app on the real port
    stop_app; restore_node; start_app
    # so a later start (hot) will relaunch the app even if this start_app exits
    touch "$D/needs_app" 2>/dev/null
    rm -f "$D/ivibridge.pid" "$D/watchdog.pid"
}

case "${1:-}" in
start)
    mkdir -p "$D" "$UPDIR" || die "cannot create $D"; rm -f "$D/stopping"
    alive "$(cat "$D/ivibridge.pid" 2>/dev/null)" && die "already running"
    $BIN -V >/dev/null 2>&1 || die "$BIN does not run"
    is_node "$LINK" || die "$LINK is not the real serial node (already bridged?)"
    mm=$(cat "$SYSDEV" 2>/dev/null)
    case "$mm" in [0-9]*:[0-9]*) echo "$mm" > "$D/ttyUSB0.dev";; *) die "cannot read $SYSDEV";; esac
    if [ ! -s "$KEYFILE" ]; then
        (umask 077; head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n' > "$KEYFILE")
        say "new API key written to $KEYFILE (read it with: cat $KEYFILE)"
    fi
    hot=0
    if [ -f "$D/needs_app" ]; then hot=1; rm -f "$D/needs_app"; fi
    up=$(uptime_s)
    if [ "$up" -ge "${IVIB_BOOT_WINDOW:-90}" ]; then hot=1; fi
    app_was_running=0
    if save_app; then
        app_was_running=1
    elif [ "$hot" = 1 ]; then
        say "app not running; will start it (hot restart)"
    else
        say "app not running; will not start it (autorun will)"
    fi
    if [ "$app_was_running" = 1 ]; then say "stopping $APPNAME"; stop_app; fi
    rm -f "$REAL"; $MKNOD "$REAL" c "${mm%%:*}" "${mm##*:}" || { [ "$app_was_running" = 1 ] && start_app; die "mknod $REAL failed"; }
    nohup $BIN -s "$REAL" -L "$LINK" -p "$PORT" -2 "$PORT2" -u "$UPDIR" -l "$LOG" -K "$KEYFILE" $EXTRA \
        > "$D/ivibridge.out" 2>&1 < /dev/null &
    echo $! > "$D/ivibridge.pid"
    n=0; while ! [ -L "$LINK" ] && [ $n -lt 100 ]; do usleep 100000; n=$((n+1)); done
    if ! [ -L "$LINK" ]; then
        say "daemon did not take over $LINK; failing safe"; kill "$(cat "$D/ivibridge.pid")" 2>/dev/null; usleep 500000
        fail_safe; exit 1
    fi
    nohup sh "$SELF" watchdog > /dev/null 2>&1 < /dev/null &
    echo $! > "$D/watchdog.pid"
    if [ "$app_was_running" = 1 ] || [ "$hot" = 1 ]; then start_app
    else say "app was not running; pty link is ready for autorun to start it"; fi
    # persist logs/jobs and the bootfail health reset run in the background; they must not delay start
    nohup sh "$SELF" persist > /dev/null 2>&1 < /dev/null &
    echo $! > "$D/persist.pid"
    if [ -n "$PORT2" ] && [ "$PORT2" != 0 ] && [ "$PORT2" != "$PORT" ]; then
        say "running: daemon pid $(cat "$D/ivibridge.pid"), http ports $PORT and $PORT2, log $LOG"
    else
        say "running: daemon pid $(cat "$D/ivibridge.pid"), http port $PORT, log $LOG"
    fi
    ;;
stop)
    touch "$D/stopping"
    w=$(cat "$D/watchdog.pid" 2>/dev/null); alive "$w" && kill "$w" 2>/dev/null
    x=$(cat "$D/persist.pid" 2>/dev/null); alive "$x" && kill "$x" 2>/dev/null
    p=$(cat "$D/ivibridge.pid" 2>/dev/null)
    if alive "$p"; then
        kill "$p"; n=0; while alive "$p" && [ $n -lt 100 ]; do usleep 100000; n=$((n+1)); done
        alive "$p" && kill -9 "$p"
    fi
    fail_safe; rm -f "$D/stopping"; say "stopped; stock serial path restored"
    # fail_safe already touches needs_app so the next start will relaunch the app
    ;;
status)
    p=$(cat "$D/ivibridge.pid" 2>/dev/null); w=$(cat "$D/watchdog.pid" 2>/dev/null)
    alive "$p" && echo "daemon: running (pid $p)" || echo "daemon: not running"
    alive "$w" && echo "watchdog: running (pid $w)" || echo "watchdog: not running"
    a=$(app_pid); echo "app: ${a:-not running}"
    if [ -L "$LINK" ]; then echo "link: $LINK -> $(readlink "$LINK")"
    elif is_node "$LINK"; then echo "link: $LINK is the real node (not bridged)"
    else echo "link: $LINK missing"; fi
    if [ -c "$REAL" ] || [ -L "$REAL" ]; then echo "real: $REAL present"; else echo "real: $REAL absent"; fi
    port_listening "$PORT" && echo "http: listening on port $PORT" || echo "http: port $PORT not listening"
    if [ -n "$PORT2" ] && [ "$PORT2" != 0 ] && [ "$PORT2" != "$PORT" ]; then
        port_listening "$PORT2" && echo "http: listening on port $PORT2" || echo "http: port $PORT2 not listening"
    fi
    v=$($BIN -V 2>/dev/null < /dev/null); echo "version: ${v:-unknown}"
    ;;
watchdog)
    while :; do
        sleep 2
        [ -f "$D/stopping" ] && exit 0
        p=$(cat "$D/ivibridge.pid" 2>/dev/null)
        if ! alive "$p"; then say "daemon gone: failing safe to stock"; fail_safe; exit 0; fi
    done
    ;;
persist)
    # Background helper (started by 'start'). Waits for p1 to be mounted by
    # autorun — never mounts it. Seeds persist logs, writes p1.ready so the
    # daemon can send new uploads to p1 and migrate idle RAM jobs, honours a
    # late p1 disable file, and after IVIB_HEALTH_WAIT seconds of a healthy
    # daemon+watchdog+link resets /userapp/ivibridge/bootfail to 0.
    P1=${IVIB_P1:-/userdata/WifiFile}
    MOUNTS=${IVIB_MOUNTS:-/proc/mounts}
    H=${IVIB_HOME:-/userapp/ivibridge}
    FAIL=${IVIB_BOOTFAIL:-$H/bootfail}
    HEALTH=${IVIB_HEALTH_WAIT:-60}
    P1WAIT=${IVIB_P1_WAIT:-1500}
    MIGROUNDS=${IVIB_MIGRATE_ROUNDS:-30}
    p1_mounted() {
        [ -r "$MOUNTS" ] || return 1
        while read dev mp typ rest; do [ "$mp" = "$P1" ] && return 0; done < "$MOUNTS"
        return 1
    }
    seed_log() {
        [ -f "$1" ] || return 0
        if [ ! -f "$2" ]; then cp "$1" "$2" && sync; fi
    }
    migrate_jobs() {
        ram=${IVIB_UPDIR:-/tmp/ivi_jobs}
        dest="$P1"
        mkdir -p "$dest" || return 1
        cur=""; [ -f "$D/current_job" ] && cur=$(cat "$D/current_job" 2>/dev/null)
        for f in "$ram"/*; do
            [ -f "$f" ] || continue
            base=$(basename "$f")
            case "$base" in .*|*.part) continue;; *.gcode|*.GCODE|*.gco|*.GCO) ;; *) continue;; esac
            [ "$f" = "$cur" ] && continue
            # copy, verify size and sha256, then delete the RAM copy
            tmp="$dest/.$base.part"
            if ! cp "$f" "$tmp"; then rm -f "$tmp"; continue; fi
            sync
            s1=$(wc -c < "$f"); s2=$(wc -c < "$tmp")
            if [ "$s1" != "$s2" ]; then rm -f "$tmp"; say "persist: size mismatch migrating $base"; continue; fi
            h1=$(sha256sum "$f" | cut -d' ' -f1); h2=$(sha256sum "$tmp" | cut -d' ' -f1)
            if [ -z "$h1" ] || [ "$h1" != "$h2" ]; then rm -f "$tmp"; say "persist: checksum mismatch migrating $base"; continue; fi
            mv -f "$tmp" "$dest/$base" && rm -f "$f" && say "persist: migrated $base to p1"
        done
    }
    # health reset is independent of p1 (a single sleep, not a poll loop)
    (
        sleep "$HEALTH"
        [ -f "$D/stopping" ] && exit 0
        p=$(cat "$D/ivibridge.pid" 2>/dev/null); w=$(cat "$D/watchdog.pid" 2>/dev/null)
        if alive "$p" && alive "$w" && [ -L "$LINK" ]; then
            echo 0 > "$FAIL" 2>/dev/null
            sync
            say "persist: healthy for ${HEALTH}s; bootfail reset"
        else
            say "persist: not healthy after ${HEALTH}s; bootfail left as-is"
        fi
    ) &
    health_pid=$!
    # wait for autorun to mount p1 (up to ~5 min, 0.2 s steps); never mount it ourselves
    n=0
    while [ $n -lt "$P1WAIT" ]; do
        [ -f "$D/stopping" ] && exit 0
        p1_mounted && break
        usleep 200000
        n=$((n + 1))
    done
    if ! p1_mounted; then say "persist: p1 never mounted; logs/jobs stay in RAM"; wait; exit 0; fi
    # late kill switch, now that p1 is visible — stop and restore stock if asked
    if [ -f "$P1/ivibridge.disable" ]; then
        say "persist: $P1/ivibridge.disable present; stopping"
        kill "$health_pid" 2>/dev/null
        sh "$SELF" stop
        exit 0
    fi
    mkdir -p "$P1/ivibridge_logs" || { say "persist: cannot create p1 dirs"; wait; exit 0; }
    seed_log "$D/boot.log" "$P1/ivibridge_logs/boot.log"
    seed_log "$D/ram.log" "$P1/ivibridge_logs/ram.log"
    seed_log "$LOG" "$P1/ivibridge_logs/ivibridge.log"
    # announce p1 so the daemon dual-writes logs and prefers p1 for new uploads
    echo "$P1" > "$D/p1.ready"
    sync
    migrate_jobs
    # retry idle migration a few times so a job that was printing can move after it ends
    r=0
    while [ $r -lt "$MIGROUNDS" ]; do
        [ -f "$D/stopping" ] && break
        migrate_jobs
        usleep 2000000
        r=$((r + 1))
    done
    wait
    ;;
*) echo "usage: $0 {start|stop|status}"; exit 2;;
esac
