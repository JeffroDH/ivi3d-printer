#!/bin/bash
# Build sunxi-fel natively on macOS (Apple silicon or Intel). UNTESTED on macOS (built and
# exercised only on Linux x86_64 from the same commit). Installs nothing system-wide: the
# binary is left at ./sunxi-tools/sunxi-fel.
# Homebrew has no sunxi-tools formula (formulae.brew.sh/formula/sunxi-tools -> 404, 2026-11-10),
# so it is built from source. Deps: libusb, dtc (libfdt), pkg-config; zlib comes with macOS.
set -euo pipefail
COMMIT=34dfa20f8284273085666436e4cac09af19646c8   # sunxi-tools master, 2026-11-05 ("v1.4.2-221-g34dfa20")
command -v brew >/dev/null || { echo "Homebrew is required: https://brew.sh"; exit 1; }
brew install libusb dtc pkg-config
[ -d sunxi-tools ] || git clone https://github.com/linux-sunxi/sunxi-tools
cd sunxi-tools
git fetch -q origin && git checkout -q $COMMIT
DTC=$(brew --prefix dtc)
make sunxi-fel CFLAGS="-I$DTC/include" LDFLAGS="-L$DTC/lib"
./sunxi-fel -? 2>&1 | head -1
file sunxi-fel
echo "Built: $(pwd)/sunxi-fel   (export SUNXI_FEL=$(pwd)/sunxi-fel)"
