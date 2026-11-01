# Orca Slicer Bridge (planned, on hold)

## Goal
Slice in Orca Slicer and send jobs directly to the IVI3D, replacing the discontinued IVI slicer. Runs locally on a Mac, no cloud.

## Core features (v1)
- **Orca printer profile**: delta geometry, build volume, heater/fan settings producing Marlin V1.3.2-compatible G-code.
- **Job upload/start**: via the printer's HTTP server on port 8080 (kore), falling back to USB-C Marlin serial streaming.
- **Status and control**: temperatures, progress, position; pause/resume/cancel.
- **G-code translation**: map any IVI-specific commands (tool selection, laser/spindle) to what the firmware expects.

## Later features
- Multi-tool support (FDM, laser, CNC), toolhead detection via CAN.
- Diagnostics: CAN and driver logging.
- Firmware backup/recovery helpers once SWD access is confirmed.

## Design goals
- Local only; read-only and safe by default; never flash without explicit approval.
- Prototype in Python (requests, pyserial, python-can); possibly a Rust/Go standalone build later.

## Blockers
1. Exact port 8080 upload/start-print API (capture old slicer traffic or read it from a Linux shell).
2. Linux shell via UGUART console pads (CP2102 adapter).
3. Toolhead CAN command map (CANable PRO capture).
4. Full flash backup via SWD (ST-Link V2) before anything risky.
