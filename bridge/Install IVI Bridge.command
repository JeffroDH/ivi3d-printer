#!/bin/bash
# Double-click to install the IVI Bridge as a login item (LaunchAgent). Safe to re-run (updates in place).
set -euo pipefail
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
HERE="$(cd "$(dirname "$0")" && pwd)"
APP="$HOME/Library/Application Support/ivi-bridge/app"
CFG="$HOME/.config/ivi-bridge/config.json"
PLIST="$HOME/Library/LaunchAgents/com.ivi3d.bridge.plist"
LOG="$HOME/Library/Logs/ivi-bridge.log"
PY=/usr/bin/python3
LABEL=com.ivi3d.bridge

if ! "$PY" -c 'import sys; assert sys.version_info >= (3, 8)' 2>/dev/null; then
  osascript -e 'display dialog "Python 3 is needed. macOS will offer to install the Command Line Tools; accept, then run this installer again." buttons {"OK"} with title "IVI Bridge"' >/dev/null || true
  xcode-select --install 2>/dev/null || true; exit 1
fi

mkdir -p "$APP" "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
cp "$HERE/ivi_bridge.py" "$APP/ivi_bridge.py"
INFO="$("$PY" "$APP/ivi_bridge.py" --config "$CFG" init-config)"
HOSTPORT="$("$PY" -c 'import json,sys; print(json.loads(sys.argv[1])["host"])' "$INFO")"
KEY="$("$PY" -c 'import json,sys; print(json.loads(sys.argv[1])["api_key"])' "$INFO")"
USB="$("$PY" -c 'import json,sys; print(json.loads(sys.argv[1])["usb_port"] or "not plugged in (Wi-Fi will be used)")' "$INFO")"

cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array>
    <string>$PY</string><string>$APP/ivi_bridge.py</string>
    <string>--config</string><string>$CFG</string><string>serve</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>10</integer>
  <key>ProcessType</key><string>Interactive</string>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict></plist>
PL

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"

OK=no
for i in 1 2 3 4 5 6 7 8 9 10; do
  if curl -fsS -H "X-Api-Key: $KEY" "http://$HOSTPORT/api/version" >/dev/null 2>&1; then OK=yes; break; fi
  sleep 1
done
printf '%s' "$KEY" | pbcopy
MSG="IVI Bridge is installed and starts automatically at login.

Orca Slicer → Printer settings → Connection (Use 3rd-party print host):
  Host type: OctoPrint
  Hostname/IP: $HOSTPORT
  API key: $KEY   (already copied to the clipboard)

USB printer: $USB
Status page: http://$HOSTPORT/
Anycubic Next post-processing line:
  /usr/bin/python3 \"$APP/ivi_bridge.py\" postprocess;
Running now: $OK   (log: ~/Library/Logs/ivi-bridge.log)"
echo "$MSG" | tee "$HOME/.config/ivi-bridge/orca-settings.txt"
osascript - "$MSG" <<'AS' >/dev/null || true
on run argv
  display dialog (item 1 of argv) buttons {"Open status page", "Done"} default button "Done" with title "IVI Bridge"
  if button returned of result is "Open status page" then do shell script "open http://127.0.0.1:5000/"
end run
AS
