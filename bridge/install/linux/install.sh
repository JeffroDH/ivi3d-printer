#!/usr/bin/env bash
# IVI Bridge installer for Linux. Safe to re-run (updates in place, keeps config and API key).
#   ./install.sh                 install + systemd --user service (default)
#   ./install.sh --system        system-wide service (/etc/systemd/system, runs as you; needs sudo)
#   ./install.sh --no-service    install only; start it yourself with ~/.local/share/ivi-bridge/run.sh
#   ./install.sh --new-key       generate a fresh API key
#   ./install.sh --no-orca       don't write the key into OrcaSlicer
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; SRC="$(cd "$HERE/../.." && pwd)"   # bridge/ (core code)
SERVICE=user; NEWKEY=""; ORCA=yes
for a in "$@"; do case "$a" in
  --system) SERVICE=system;; --no-service) SERVICE=none;; --user) SERVICE=user;;
  --new-key) NEWKEY="--new-key";; --no-orca) ORCA=no;;
  -h|--help) sed -n '2,8p' "$0"; exit 0;; *) echo "unknown option: $a" >&2; exit 2;; esac; done

DATA="${XDG_DATA_HOME:-$HOME/.local/share}/ivi-bridge"; APP="$DATA/app"; VENV="$DATA/venv"
CFG="${IVI_BRIDGE_CONFIG:-$HOME/.config/ivi-bridge/config.json}"
UNIT=ivi3d-bridge.service

command -v python3 >/dev/null || { echo "python3 is required (e.g. sudo apt install python3 python3-venv)" >&2; exit 1; }
python3 -c 'import sys; assert sys.version_info >= (3, 8)' || { echo "Python 3.8+ is required" >&2; exit 1; }

mkdir -p "$APP" "$(dirname "$CFG")"
# venv preferred; the bridge itself is stdlib-only, pyserial just adds port listing
PY=python3
if [ -x "$VENV/bin/python" ] || python3 -m venv "$VENV" >/dev/null 2>&1; then
  PY="$VENV/bin/python"
  "$PY" -m pip install -q --disable-pip-version-check pyserial 2>/dev/null || echo "note: pyserial not installed (offline?); the bridge works without it on Linux"
else
  echo "note: python3-venv missing; using system python3 (sudo apt install python3-venv to get a venv)"
fi
PY="$(command -v "$PY" || echo "$PY")"

cp "$SRC/ivi_bridge.py" "$SRC/ivi_setup_keys.py" "$SRC/ivi_add_header.py" "$APP/"
cp "$HERE/uninstall.sh" "$HERE/fix-key.sh" "$DATA/" && chmod +x "$DATA/uninstall.sh" "$DATA/fix-key.sh"
cat > "$DATA/run.sh" <<RUN
#!/bin/sh
exec "$PY" "$APP/ivi_bridge.py" --config "$CFG" serve
RUN
chmod +x "$DATA/run.sh"

INFO="$("$PY" "$APP/ivi_bridge.py" --config "$CFG" init-config)"   # never overwrites an existing config
HOSTPORT="$("$PY" -c 'import json,sys; print(json.loads(sys.argv[1])["host"])' "$INFO")"
KEY="$("$PY" "$APP/ivi_setup_keys.py" --config "$CFG" --key-only $NEWKEY --print-key)"
USB="$("$PY" -c 'import json,sys; print(json.loads(sys.argv[1])["usb_port"] or "not plugged in (Wi-Fi will be used)")' "$INFO")"

# Serial access: /dev/ttyACM* is group dialout (Debian/Ubuntu/Fedora) or uucp (Arch)
GRP=""; for g in dialout uucp; do getent group "$g" >/dev/null 2>&1 && { GRP=$g; break; }; done
SERIAL_NOTE="Serial access: OK"
if [ -n "$GRP" ] && ! id -nG | tr ' ' '\n' | grep -qx "$GRP"; then
  SERIAL_NOTE="Serial access: run  sudo usermod -aG $GRP $USER  then log out and back in (needed for USB printing)"
fi

LOGNOTE="journalctl --user -u $UNIT -f"
case "$SERVICE" in
user)
  if ! command -v systemctl >/dev/null || ! systemctl --user show-environment >/dev/null 2>&1; then
    echo "systemd --user is not available here; re-run with --no-service or --system" >&2; SERVICE=none
  else
    D="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"; mkdir -p "$D"
    cat > "$D/$UNIT" <<U
[Unit]
Description=IVI3D Bridge (OctoPrint-compatible API for the IVI 3D printer)
After=network-online.target

[Service]
ExecStart="$PY" "$APP/ivi_bridge.py" --config "$CFG" serve
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
U
    systemctl --user daemon-reload
    systemctl --user enable "$UNIT" >/dev/null 2>&1
    systemctl --user restart "$UNIT"
    if command -v loginctl >/dev/null && [ "$(loginctl show-user "$USER" -p Linger --value 2>/dev/null)" != "yes" ]; then
      echo "tip: to keep the bridge running when you're logged out (headless box):  sudo loginctl enable-linger $USER"
    fi
  fi;;
system)
  LOGNOTE="journalctl -u $UNIT -f"
  sudo tee "/etc/systemd/system/$UNIT" >/dev/null <<U
[Unit]
Description=IVI3D Bridge (OctoPrint-compatible API for the IVI 3D printer)
After=network-online.target
Wants=network-online.target

[Service]
User=$USER
${GRP:+SupplementaryGroups=$GRP}
Environment=HOME=$HOME
ExecStart="$PY" "$APP/ivi_bridge.py" --config "$CFG" serve
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
U
  sudo systemctl daemon-reload && sudo systemctl enable --now "$UNIT" && sudo systemctl restart "$UNIT";;
esac
if [ "$SERVICE" = none ]; then
  LOGNOTE="(no service) start it with: $DATA/run.sh"
  # stop an old user service if switching to --no-service
  command -v systemctl >/dev/null && systemctl --user disable --now "$UNIT" >/dev/null 2>&1 || true
fi

OK=no
if [ "$SERVICE" != none ]; then
  for i in $(seq 1 10); do
    if "$PY" - "$HOSTPORT" "$KEY" <<'P' 2>/dev/null; then OK=yes; break; fi
import sys, urllib.request
r = urllib.request.Request("http://%s/api/version" % sys.argv[1], headers={"X-Api-Key": sys.argv[2]})
urllib.request.urlopen(r, timeout=2).read()
P
    sleep 1
  done
fi

PLUGIN_NOTE="OrcaSlicer plugin: not installed"
ORCA_NOTE="Orca: skipped (--no-orca)"
if [ "$ORCA" = yes ]; then
  ORCA_DIR="$("$PY" -c 'import sys; sys.path.insert(0, sys.argv[1]); import ivi_setup_keys as k; print(k.default_orca_dir())' "$APP")"
  if [ -f "$SRC/../orca/plugin/ivi3d_bridge_plugin.py" ] && [ -d "$ORCA_DIR" ]; then
    DEST="$ORCA_DIR/orca_plugins/ivi3d_bridge_plugin.py"; mkdir -p "$DEST"
    cp "$SRC/../orca/plugin/ivi3d_bridge_plugin.py" "$DEST/" && PLUGIN_NOTE="OrcaSlicer plugin copied to $DEST (restart Orca and enable it)"
  fi
  set +e; "$PY" "$APP/ivi_setup_keys.py" --config "$CFG" --orca-dir "$ORCA_DIR"; RC=$?; set -e
  case $RC in
    0) ORCA_NOTE="Orca: API key filled in ($ORCA_DIR)";;
    3) ORCA_NOTE="Orca: NOT updated (Orca was open). Quit Orca and run $DATA/fix-key.sh";;
    *) ORCA_NOTE="Orca: key update failed; run $DATA/fix-key.sh";;
  esac
fi

MSG="IVI Bridge is installed (service: $SERVICE).

$ORCA_NOTE
Orca connection: Host type OctoPrint, Hostname/IP $HOSTPORT
API key: in $CFG  (\"api_key\")
USB printer: $USB
$SERIAL_NOTE
Status page: http://$HOSTPORT/
Running now: $OK   Log: $LOGNOTE
$PLUGIN_NOTE
Firewall: only needed if you set listen_host to 0.0.0.0 for other devices (e.g. sudo ufw allow 5001/tcp)"
echo "$MSG" | tee "$(dirname "$CFG")/orca-settings.txt" >/dev/null; echo "$MSG"
