# Orca Slicer Bridge

**Status (2026-11-01): v0.1 implemented in [`bridge/`](../bridge/README.md)** — OctoPrint-compatible service, Wi-Fi upload + USB serial streaming, post-processing/watch-folder CLI for Anycubic Slicer Next. Unit-tested with fakes; not yet run against the printer.

## Goal
Slice in Orca Slicer and send jobs directly to the IVI3D, replacing the discontinued IVI slicer. Runs locally on a Mac, no cloud.

## Core features (v1)
- **Orca printer profile**: delta geometry, build volume, heater/fan settings producing Marlin V1.3.2-compatible G-code.
- **Job start/pause/resume**: over **USB-C serial** (`M2411 S2` start, stream per `ok`, `M2410` pause, `M2411 S1` resume) — the only working path on current firmware. Wi-Fi (`:8080` `upload`) can store files only; print-control endpoints are 404. Future official/custom firmware may enable them over Wi-Fi.
- **Status and control**: from serial (`M105`, line counts); Wi-Fi `status` only reports `IDLE`.
- **G-code translation**: map any IVI-specific commands (tool selection, laser/spindle) to what the firmware expects.

## Later features
- Multi-tool support (FDM, laser, CNC), toolhead detection via CAN.
- Diagnostics: CAN and driver logging.
- Firmware backup/recovery helpers once SWD access is confirmed.

## Design goals
- Local only; read-only and safe by default; never flash without explicit approval.
- Prototype in Python (requests, pyserial, python-can); possibly a Rust/Go standalone build later.

## Blockers
1. ~~Bridge code~~ done (`bridge/`); needs a real-hardware test.
1. ~~Port 8080 API~~ tested 2026-11-01: upload only; start/pause/stop 404 → use USB serial. Laser/CNC header and power scale still unverified.
2. Linux shell via UGUART console pads (CP2102 adapter).
3. Toolhead CAN command map (CANable PRO capture).
4. Full flash backup via SWD (ST-Link V2) before anything risky.
