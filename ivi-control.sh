#!/usr/bin/env bash
# ivi-control.sh - command-line control of an IVI 3D printer over its Wi-Fi HTTP API.
# Endpoints match the stock IVI 3licer 1.6.2 slicer (Snapmaker-2.0-style API on :8080).
# Works under bash or zsh (run as: bash ivi-control.sh ...).
#
# Usage: ivi-control.sh <command> [args]
#   discover                 Broadcast UDP "discover" on port 20050 and print replies
#   connect                  POST /api/v1/connect (may need confirming on the printer screen)
#   disconnect               POST /api/v1/disconnect
#   status                   GET  /api/v1/status
#   print <file> [type]      prepare_print (uploads the file) then start_print; type = 3DP|Laser|CNC (default 3DP)
#   prepare <file> [type]    prepare_print only (upload + load, do not start)
#   start|pause|resume|stop  start_print / pause_print / resume_print / stop_print
#   upload <file>            Store a file on the printer: /api/v1/upload (<20 MiB) or chunked sliceUpload (2 MiB chunks)
#   gcode "<G-code>"         POST /api/v1/execute_code, one line per request (use \n-separated or quote several)
#   help                     Show this help
#
# Environment: IVI_IP (default 192.168.50.85), IVI_PORT (8080), IVI_TOKEN (default stock token).

set -eu

IVI_IP="${IVI_IP:-192.168.50.85}"
IVI_PORT="${IVI_PORT:-8080}"
IVI_TOKEN="${IVI_TOKEN:-e0cf19a3-e0a4-4740-825f-bdffb49e58b8}"
BASE="http://${IVI_IP}:${IVI_PORT}/api/v1"
CHUNK=$((2 * 1024 * 1024))
SMALL_LIMIT=$((20 * 1024 * 1024))

die() { echo "error: $*" >&2; exit 1; }
need_file() { [ -f "${1:-}" ] || die "file not found: ${1:-<none>}"; }
post() { local ep="$1"; shift; curl -sS -X POST "$BASE/$ep" "$@"; echo; }

md5_of() {
  if command -v md5sum >/dev/null 2>&1; then md5sum "$1" | cut -d' ' -f1; else md5 -q "$1"; fi
}
size_of() { wc -c < "$1" | tr -d ' '; }

cmd_discover() {
  command -v python3 >/dev/null 2>&1 || die "discover needs python3"
  python3 - <<'PY'
import socket, time
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.settimeout(0.5)
s.sendto(b"discover", ("255.255.255.255", 20050))
end = time.time() + 3
while time.time() < end:
    try:
        data, addr = s.recvfrom(1024)
        print(addr[0], data.decode(errors="replace").strip())
    except socket.timeout:
        pass
PY
}

cmd_prepare() {
  need_file "${1:-}"
  local type="${2:-3DP}"
  case "$type" in 3DP|Laser|CNC) ;; *) die "type must be 3DP, Laser or CNC";; esac
  echo "prepare_print ($type): $(basename "$1")"
  post prepare_print -F "token=$IVI_TOKEN" -F "type=$type" -F "file=@$1"
}

cmd_upload() {
  need_file "${1:-}"
  local f="$1" name size md5 count i tmp
  name="$(basename "$f")"; size="$(size_of "$f")"
  if [ "$size" -lt "$SMALL_LIMIT" ]; then
    echo "upload: $name ($size bytes)"
    post upload -F "token=$IVI_TOKEN" -F "file=@$f;filename=$name"
    return
  fi
  md5="$(md5_of "$f")"; count=$(( (size + CHUNK - 1) / CHUNK ))
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  i=0
  while [ "$i" -lt "$count" ]; do
    dd if="$f" of="$tmp/chunk" bs="$CHUNK" skip="$i" count=1 2>/dev/null
    echo "sliceUpload chunk $((i + 1))/$count"
    # index is 1-based; the part's filename is the 0-based chunk number (stock-slicer behaviour)
    post sliceUpload -F "index=$((i + 1))" -F "count=$count" -F "md5=$md5" \
      -F "size=$size" -F "filename=$name" -F "file=@$tmp/chunk;filename=$i"
    i=$((i + 1))
  done
}

cmd_gcode() {
  [ -n "${1:-}" ] || die 'usage: gcode "G28"'
  printf '%b\n' "$1" | while IFS= read -r line; do
    [ -n "$line" ] || continue
    echo "> $line"
    post execute_code --data-urlencode "token=$IVI_TOKEN" --data-urlencode "code=$line"
  done
}

cmd_help() { sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'; }

case "${1:-help}" in
  discover)   cmd_discover ;;
  connect)    post connect -d "token=$IVI_TOKEN" ;;
  disconnect) post disconnect -d "token=$IVI_TOKEN" ;;
  status)     curl -sS "$BASE/status?token=$IVI_TOKEN"; echo ;;
  prepare)    cmd_prepare "${2:-}" "${3:-3DP}" ;;
  print)      cmd_prepare "${2:-}" "${3:-3DP}"; post start_print -d "token=$IVI_TOKEN" ;;
  start|pause|resume|stop) post "${1}_print" -d "token=$IVI_TOKEN" ;;
  upload)     cmd_upload "${2:-}" ;;
  gcode)      cmd_gcode "${2:-}" ;;
  help|-h|--help) cmd_help ;;
  *)          echo "unknown command: $1" >&2; cmd_help; exit 1 ;;
esac
