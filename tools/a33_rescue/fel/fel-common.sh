# shellcheck shell=bash
# Shared helpers for the FEL scripts (macOS or Linux host).
KIT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
OUT=$KIT/out
FEL=${SUNXI_FEL:-$(command -v sunxi-fel || echo "$KIT/fel/sunxi-tools/sunxi-fel")}
[ -x "$FEL" ] || { echo "sunxi-fel not found. Run fel/build-sunxi-fel-macos.sh or set SUNXI_FEL."; exit 1; }
sha_check() {   # verify listed out/ files against out/SHA256SUMS
	( cd "$OUT" && for f in "$@"; do
		exp=$(awk -v f="$f" '$2==f{print $1}' SHA256SUMS)
		got=$( (command -v sha256sum >/dev/null && sha256sum "$f" || shasum -a 256 "$f") | cut -d' ' -f1)
		[ -n "$exp" ] && [ "$exp" = "$got" ] || { echo "SHA256 mismatch for $f"; exit 1; }
	done ) || exit 1
	echo "SHA256 OK: $*"
}
require_a33() {
	v=$("$FEL" version 2>&1) || { echo "$v"; echo "No FEL device answered. Is the board in FEL and the USB cable on the OTG port?"; exit 1; }
	echo "$v"
	echo "$v" | grep -q "A33" || { echo "Device is not reported as A33; refusing."; exit 1; }
}
ask_yes() { read -r -p "$1 [y/N] " a; [ "$a" = y ] || [ "$a" = Y ] || { echo "aborted"; exit 3; }; }
