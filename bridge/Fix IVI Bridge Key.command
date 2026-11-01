#!/bin/bash
# Double-click after importing IVI3D.orca_printer (or whenever Orca says the bridge is offline / 401).
# Quit OrcaSlicer first; this waits for it. Writes the bridge API key into every Orca location.
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
HERE="$(cd "$(dirname "$0")" && pwd)"
H="$HERE/ivi_setup_keys.py"
[ -f "$H" ] || H="$HOME/Library/Application Support/ivi-bridge/app/ivi_setup_keys.py"
/usr/bin/python3 "$H" --wait "$@"
echo; read -r -p "Done. Press Return to close." _
