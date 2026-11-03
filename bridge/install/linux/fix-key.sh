#!/usr/bin/env bash
# Linux equivalent of "Fix IVI Bridge Key.command": quit OrcaSlicer, then run this after importing the IVI3D profile.
DATA="${XDG_DATA_HOME:-$HOME/.local/share}/ivi-bridge"; HERE="$(cd "$(dirname "$0")" && pwd)"
H="$HERE/../../ivi_setup_keys.py"; [ -f "$H" ] || H="$DATA/app/ivi_setup_keys.py"
PY="$DATA/venv/bin/python"; [ -x "$PY" ] || PY=python3
exec "$PY" "$H" --wait "$@"
