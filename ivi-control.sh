#!/bin/zsh
# ivi-control.sh — Full control of IVI printer (upload, status, telemetry)
# ---------------------------------------------------------------
# Usage: ./ivi-control.sh <command> [args]
#   status      → Show current printer status
#   upload <file> → Upload .gcode file
#   listen      → Listen to live UDP telemetry (Ctrl+C to stop)
#   connect     → Authenticate session
#   disconnect  → End session
#   help        → Show this help

set -euo pipefail

TOKEN="e0cf19a3-e0a4-4740-825f-bdffb49e58b8"
BASE="http://192.168.50.85:8080"
HEADERS=(
  "Origin: http://127.0.0.1:62446"
  "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 26_0_1) AppleWebKit/537.36 (KHTML, like Gecko) ivi-3licer/1.6.2 Chrome/61.0.3163.100 Electron/2.0.18 Safari/537.36"
)

# === Helper: curl with common headers ===
curl_api() {
  local method="$1"; shift
  local url="$1"; shift
  curl -s -X "$method" "$url" \
    "${HEADERS[@]/#/-H }" \
    "$@"
}

# === Commands ===
cmd_status() {
  echo "Getting printer status..."
  curl_api POST "$BASE/api/v1/status" -d "token=$TOKEN"
  echo
}

cmd_connect() {
  echo "Connecting..."
  curl_api POST "$BASE/api/v1/connect" -d "token=$TOKEN"
  echo
}

cmd_disconnect() {
  echo "Disconnecting..."
  curl_api POST "$BASE/api/v1/disconnect" -d "token=$TOKEN"
  echo
}

cmd_upload() {
  local file="$1"
  [[ -f "$file" ]] || { echo "File not found: $file"; exit 1; }
  local name=$(basename "$file")
  echo "Uploading $name..."
  curl_api POST "$BASE/api/v1/upload" \
    -F "token=$TOKEN" -F "file=@$file"
  echo
  echo "Upload complete. Use printer LCD or SD to start print."
}

cmd_listen() {
  echo "Listening on UDP 20050 (live telemetry)... (Ctrl+C to stop)"
  echo "------------------------------------------------------------"
  nc -u -l 20050
}

cmd_help() {
  sed -n '3,/^$/p' "$0" | grep -v "^#"
}

# === Main ===
case "${1:-}" in
  status)     cmd_status ;;
  upload)     [[ -n "${2:-}" ]] && cmd_upload "$2" || echo "Usage: $0 upload <file.gcode>" ;;
  listen)     cmd_listen ;;
  connect)    cmd_connect ;;
  disconnect) cmd_disconnect ;;
  help|"")    cmd_help ;;
  *)          echo "Unknown command: $1"; cmd_help ;;
esac
