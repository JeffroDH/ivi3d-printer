# IVI 3D Printer — reverse-engineering notes

Authorized interoperability notes for Dr. Hogan's beta IVI 3D printer, aimed at talking to it from Orca Slicer (or a small plugin) instead of the stock IVI 3licer app.

## Contents

| File | What it is |
|------|------------|
| `slicer_report.md` | How **IVI 3licer 1.6.2** (rebranded Snapmaker Luban / Snapmakerjs) discovers the printer, authenticates, uploads G-code, and controls prints. Best map of the HTTP API. |
| `firmware_report.md` | REA/Ghidra notes on `firmware.bin` (ARM Qt5 UI ELF) and `firmware.supx` (STM32 motion-controller image). Covers UDP discovery, serial, and what is / isn't in the UI binary. |
| `config.ini` / `config2.ini` | Firmware package metadata (`version=` + `MD5=`). |
| Source binaries (elsewhere in this folder) | `firmware`, `firmware.supx`, `ivi-3licer-….dmg`, `IVI.dmg`. |

## Protocol cheat sheet

### Discovery
- PC → UDP broadcast port **20050**, payload ASCII `discover`
- Printer reply: `IVI3D@<ip>|Model:IVI 3D Printer|status:IDLE` (pipe-delimited fields; may have a binary prefix)

### Wi-Fi control (primary path for Orca)
- Base URL: `http://<printer-ip>:8080`
- Default bootstrap token: `e0cf19a3-e0a4-4740-825f-bdffb49e58b8`
- `POST /api/v1/connect` → session `token` (may require on-screen approval; status can 204 until approved)
- `GET /api/v1/status?token=`
- `POST /api/v1/prepare_print` multipart: `token`, `type=3DP`, `file=<gcode>`
- `POST /api/v1/start_print` / `pause_print` / `resume_print` / `stop_print`
- `POST /api/v1/execute_code` for raw G-code
- Large files: `/api/v1/upload` (<20 MiB) or `/api/v1/sliceUpload` (2 MiB chunks + MD5)

### USB serial
- `/dev/ttyUSB0` (on the printer), **115200 8N1**, RTS/DTR on
- Plain Marlin-like G-code, or Snapmaker-style `AA 55` framed packets
- Custom M-codes seen in UI: `M2001`, `M2410`, `M2411 S1–S3` (start/pause/resume/stop family)

### Slicer output
- Plain `.gcode` (Marlin), with a `;Header Start` … `;Header End` block that the stock app always adds
- Build volume from bundled profile: **210 × 210 × 220 mm**, 0.3 mm nozzle, origin at bed center
- `.supx` is the **STM32 firmware update image**, not slicer output

## Orca Slicer path
1. Try Orca's built-in **Snapmaker** machine connection first (same Luban-family API).
2. Otherwise a small HTTP client: discover → connect → prepare_print → start_print → poll status.
3. Keep the `;Header Start` block until proven unnecessary.

## What is still unverified on-device
- That port 8080 is live on this beta unit (HTTP server is a **separate process** from the Qt UI ELF).
- Whether the default token works, or an on-screen confirm is required.
- Which serial framing mode USB-C actually uses.
- Exact closed-loop / encoder control loop (see "Sensors" below).

## Sensors (what we found so far)

**Not found:** dedicated closed-loop encoder drivers, ABZ encoder strings, or a step-loss recovery protocol in either `firmware.bin` (Qt UI) or the strings we pulled from `firmware.supx` (STM32 image). Marketing "closed loop" may mean something else on this machine, or it may live only in the motion firmware as opaque binary logic.

**What *is* in the firmware:**
- **Bed leveling sensor** UI hooks in the Qt app: `checkLevelingSensorInstalled`, `goInstallLevelSensorPos`, `sensorInstalled`, plus endstop on/off (`switchOnEndStop` / `switchOffEndStop`, `setEndstopStatus`).
- **Self-test / health strings** in the STM32 image listing: `XMotor`/`YMotor`/`ZMotor`, `XLimit`/`YLimit`/`ZLimit`, `Fans`, `Door`, `TempHumi`, `ToolHead`, `Print`/`PrintHeat`/`Bed`/`BedHeat`/`Extruder`, `Filament`, `Auto`, and a `Filament runout sensor:` label. Also a bare `Servo` string (likely toolhead / laser / CNC actuator, not axis closed-loop).
- Custom motion M-codes (`M2001`, `M2005`, `M2051`, `M2410`, `M2411 S1–S3`, etc.) whose full semantics aren't decoded yet — some of these *could* interact with sensing, but that is not confirmed.

**To pin closed-loop down next:** SSH into the printer and inspect what process owns `:8080`, dump axis / motor config from the motion board, and/or capture serial traffic while jogging with a deliberate mechanical bind. Hardware photos of the motor ends (encoders vs open-loop steppers) would settle it fast.

## Quick test (from a Mac on the same LAN)
```bash
# Replace IP if needed
curl -s -X POST "http://192.168.50.85:8080/api/v1/connect" \
  -d "token=e0cf19a3-e0a4-4740-825f-bdffb49e58b8"
```

Analyzed: 2026-10-31.

## Laser and CNC toolheads

The machine is a Snapmaker-style modular toolhead platform. The stock slicer and firmware both treat three head types as first-class:

| Mode | API `type=` | File suffix | Notes |
|------|-------------|-------------|-------|
| FDM print | `3DP` | `.gcode` | Nozzle sizes mentioned in STM32: 0.15–0.4 mm (beta shipped 0.3 mm) |
| Laser | `Laser` | `.nc` | Status reports `laserPower`, `laserFocalLength`; override via `POST /api/v1/override_laser_power` |
| CNC | `CNC` | `.cnc` | UI has V-bit / ball / flat end-mill tool images; STM32 string `CNC BLCD Speed:` (BLDC spindle) |

**How the printer knows which head is on:** `/api/v1/connect` returns `headType`. The Qt UI has `setPrintHeadType` / `checkGcodePrinterHeadType`, and the motion firmware self-test reports `ToolHead:ok` plus `info:Head Laser` / `info:Head CNC` / `info:Head 3DP,…`.

**Laser-specific UI commands in the Qt binary:** `sendLaserLightOnCMD` → `M3 S5`, `setCNCorLaserStrength`, `goLaserFinetunePos`, `laserBlockSetWorkOrign`, sample job `Laser/tigger_head.nc`.

**CNC-specific:** `sendCNCMoveOnCMD` → `M3 S70`, `cncMoveOnFinished` / `cncMoveOffFinished`, sample `CNC/owl.cnc`, shared off command `sendLaserOrCNCOffCMD`. Spindle/laser power is Marlin-style `M3 S…` (and presumably `M5` off).

**Slicer assets:** test cases `Laser_test_A150.jpg`, `CNC_test_A150.svg`; instruction images under `app/images/laser/` and `app/images/cnc/`. Same Luban/Snapmaker workflow as A150/A250 machines.

For Orca: FDM is the easy win. Laser/CNC need a toolpath generator (Orca doesn't do laser/CNC CAM the way Luban does), so those heads are better served by keeping Luban/IVI 3licer for CAM, or a separate laser/CNC CAM that emits `.nc`/`.cnc` and uses the same HTTP upload with `type=Laser` or `type=CNC`.
