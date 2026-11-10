#!/bin/bash
# [R0 READ] Identify the SoC in FEL mode. Read-only: asks the BootROM for its version.
# Does not load or run anything on the board.
set -euo pipefail
. "$(dirname "$0")/fel-common.sh"
echo "== FEL devices on USB =="
"$FEL" --list --verbose || true
echo "== BootROM version =="
"$FEL" version
# Expected on the IVI board: "AWUSBFEX soc=00001667(A33) ..." (0x1667 = A33/R16 family)
# Optional and NOT run by default: '$FEL sid' prints the chip's unique ID (treat like a serial number;
# keep it out of reports and the repo).
