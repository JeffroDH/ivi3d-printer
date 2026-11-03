#!/usr/bin/env bash
# Stop and remove the IVI Bridge (Linux). Settings are kept unless --purge is given.
set -u
DATA="${XDG_DATA_HOME:-$HOME/.local/share}/ivi-bridge"; UNIT=ivi3d-bridge.service
if command -v systemctl >/dev/null; then
  systemctl --user disable --now "$UNIT" >/dev/null 2>&1
  rm -f "${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user/$UNIT"; systemctl --user daemon-reload >/dev/null 2>&1
  if [ -f "/etc/systemd/system/$UNIT" ]; then
    sudo systemctl disable --now "$UNIT"; sudo rm -f "/etc/systemd/system/$UNIT"; sudo systemctl daemon-reload
  fi
fi
rm -rf "$DATA/app" "$DATA/venv" "$DATA/run.sh" "$DATA/fix-key.sh"
if [ "${1:-}" = "--purge" ]; then
  rm -rf "$HOME/.config/ivi-bridge" "$DATA"; echo "IVI Bridge uninstalled (settings deleted)."
else
  rm -f "$DATA/uninstall.sh"; echo "IVI Bridge uninstalled (settings kept in ~/.config/ivi-bridge; --purge deletes them)."
fi
