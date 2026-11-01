#!/bin/bash
# Double-click to stop and remove the IVI Bridge LaunchAgent. Your config is kept unless you choose otherwise.
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
LABEL=com.ivi3d.bridge
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/$LABEL.plist"
rm -rf "$HOME/Library/Application Support/ivi-bridge/app"
ANS="$(osascript -e 'button returned of (display dialog "IVI Bridge removed. Also delete its settings (API key, printer token) and spooled jobs?" buttons {"Keep settings", "Delete settings"} default button "Keep settings" with title "IVI Bridge")' 2>/dev/null || echo "Keep settings")"
if [ "$ANS" = "Delete settings" ]; then
  rm -rf "$HOME/.config/ivi-bridge" "$HOME/Library/Application Support/ivi-bridge"
fi
echo "IVI Bridge uninstalled ($ANS)."
