#!/bin/bash
# Double-click to install the IVI Bridge as a login item (LaunchAgent). Safe to re-run (updates in place).
# Keeps the existing API key; run with --new-key (from Terminal) to generate a fresh one.
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
NEWKEY=""; [ "${1:-}" = "--new-key" ] && NEWKEY="--new-key"
cp "$HERE/ivi_bridge.py" "$HERE/ivi_setup_keys.py" "$APP/"
cp "$HERE/Fix IVI Bridge Key.command" "$APP/" && chmod +x "$APP/Fix IVI Bridge Key.command"
INFO="$("$PY" "$APP/ivi_bridge.py" --config "$CFG" init-config)"
HOSTPORT="$("$PY" -c 'import json,sys; print(json.loads(sys.argv[1])["host"])' "$INFO")"
# Create/keep the key in the bridge config (Orca files are patched further down, after the plugin copy)
KEY="$("$PY" "$APP/ivi_setup_keys.py" --config "$CFG" --key-only $NEWKEY --print-key)"
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

# Optional: OrcaSlicer 2.5 plugin (each plugin lives in its own folder under orca_plugins/)
PLUGIN_SRC="$HERE/../orca/plugin/ivi3d_bridge_plugin.py"
PLUGIN_NOTE="OrcaSlicer plugin: not installed"
if [ -f "$PLUGIN_SRC" ]; then
  ANS=$(osascript -e 'button returned of (display dialog "Also copy the IVI3D Bridge plugin into OrcaSlicer 2.5 (orca_plugins)? Enable it afterwards in the Orca Plugins dialog." buttons {"Skip", "Copy plugin"} default button "Copy plugin" with title "IVI Bridge")' 2>/dev/null || echo Skip)
  if [ "$ANS" = "Copy plugin" ]; then
    # Same layout Orca's own "Install local plugin" uses: orca_plugins/<entry file name>/<entry file>
    # (PluginLoader.cpp local_plugin_install_dir). A single .py has no OS/arch suffix; that only applies to .whl tags.
    ROOT="$HOME/Library/Application Support/OrcaSlicer/orca_plugins"
    DEST="$ROOT/ivi3d_bridge_plugin.py"
    OLD="$ROOT/ivi3d_bridge"   # pre-0.1.1 location; same plugin key, so remove it to avoid a duplicate
    if [ -d "$OLD" ] && [ "$(ls -A "$OLD" | grep -v '^\.' | grep -vx 'ivi3d_bridge_plugin.py' || true)" = "" ]; then rm -rf "$OLD"; fi
    mkdir -p "$DEST" && cp "$PLUGIN_SRC" "$DEST/ivi3d_bridge_plugin.py" && PLUGIN_NOTE="OrcaSlicer plugin copied to $DEST (restart Orca and enable it; its API key is filled in for you)"
  fi
fi
# Write the key into Orca: printer presets, Device tab connection, plugin config
ORCA_NOTE="Orca: API key filled in automatically (presets, Device tab, plugin)"
while :; do
  set +e; "$PY" "$APP/ivi_setup_keys.py" --config "$CFG"; RC=$?; set -e
  [ $RC -ne 3 ] && break
  ANS=$(osascript -e 'button returned of (display dialog "OrcaSlicer is open. Quit it (Cmd-Q) so the API key can be written into its settings, then click Retry." buttons {"Skip", "Retry"} default button "Retry" with title "IVI Bridge")' 2>/dev/null || echo Skip)
  if [ "$ANS" != "Retry" ]; then ORCA_NOTE="Orca: NOT updated (Orca was open). Quit Orca and double-click \"Fix IVI Bridge Key.command\" in $APP"; break; fi
done
[ "${RC:-0}" -ne 0 ] && [ "${RC:-0}" -ne 3 ] && ORCA_NOTE="Orca: key update failed (see Terminal); run Fix IVI Bridge Key.command"

MSG="IVI Bridge is installed and starts automatically at login.

$ORCA_NOTE
Orca connection (Printer bar → Connection icon), already set by the IVI3D profile:
  Host type: OctoPrint
  Hostname/IP: $HOSTPORT
  API key: $KEY   (already copied to the clipboard)
After importing IVI3D.orca_printer again, quit Orca and run Fix IVI Bridge Key.command.

USB printer: $USB
Status page: http://$HOSTPORT/
Anycubic Next post-processing line:
  /usr/bin/python3 \"$APP/ivi_bridge.py\" postprocess;
$PLUGIN_NOTE
Running now: $OK   (log: ~/Library/Logs/ivi-bridge.log)"
echo "$MSG" | tee "$HOME/.config/ivi-bridge/orca-settings.txt"
osascript - "$MSG" <<'AS' >/dev/null || true
on run argv
  display dialog (item 1 of argv) buttons {"Open status page", "Done"} default button "Done" with title "IVI Bridge"
  if button returned of result is "Open status page" then do shell script "open http://127.0.0.1:5000/"
end run
AS
