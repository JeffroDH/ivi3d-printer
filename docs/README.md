# Documentation index

Current knowledge of the IVI 3D Printer. Photo evidence and older decompile notes stay in the files that already held them; the pages below are the place to start.

Confidence tags used throughout: **[V]** read in firmware, a boot log, or a live capture · **[I]** inferred · **[O]** owner observation · **[U]** / **[?]** not yet measured · **[D]** datasheet.

## System

| Doc | What it covers |
|---|---|
| [architecture.md](architecture.md) | The three processors, the ports, and how a job actually starts |
| [mainboard.md](mainboard.md) | `A33_407MB_200916` photos, silkscreen, connectors |
| [network.md](network.md) | What answers on the LAN, with and without ivibridge |
| [tools.md](tools.md) | SWD and the debug UART, with the hard limits |

## Controllers

| Doc | What it covers |
|---|---|
| [stm32.md](stm32.md) | Motion firmware: chip ID, RDP, flash map, bootloader, update protocol, fans, laser head, CAN, UARTs |
| [a33.md](a33.md) | Touchscreen board: Qt app, touch, sshd, kore upload, update package, boot, where ivibridge sits |
| [gd32.md](gd32.md) | GD32E230 soft-power controller |
| [backups.md](backups.md) | What has been backed up, the restore routes, and the A33 rescue kit |

## Driving the printer

| Doc | What it covers |
|---|---|
| [wifi_touch.md](wifi_touch.md) | The ways to drive a print (ivibridge, kore upload, USB-C, touch injection), upload names, and rules for sharing the serial link |
| [calibration.md](calibration.md) | Calibration view and API, verified G33 / G29 / paper-test math, Z-offset display |
| [native_print.md](native_print.md) | How ivibridge starts a job through the stock touchscreen hook |
| [../a33_bridge/README.md](../a33_bridge/README.md) | The on-printer bridge: API, web UI, fail-safes, install and rollback |
| [home_session/RUNBOOK.md](home_session/RUNBOOK.md) | Step-by-step sshd + touch-navigator session |
| [home_session/QUICKREF.md](home_session/QUICKREF.md) | One-page version of that session |
| [laser_cnc_gcode.md](laser_cnc_gcode.md) | Laser and CNC G-code |
| [orca_bridge.md](orca_bridge.md) | Connecting Orca: on-printer ivibridge vs the computer-side bridge, start G-code and fan notes, Anycubic Slicer Next |
| [slicer_report.md](slicer_report.md) | How IVI 3licer 1.6.2 talks to the printer |

## Firmware notes already in the tree

| Doc | What it covers |
|---|---|
| [firmware_report.md](firmware_report.md) | Qt UI ELF: discovery, serial, the commands the UI sends |
| [supx_decompile_report.md](supx_decompile_report.md) | Ghidra pass on `firmware.supx` (pins, driver UART protocol, custom M-codes) |
| [supx_report.md](supx_report.md) | First-pass `.supx` container notes |
| [../tools/README.md](../tools/README.md) | `ivi_touch_nav`, `supx_stream.py`, framebuffer and tap helpers, the touchscreen hook and its packer |

Machine-readable tables: [data/stm32_app_commands.csv](data/stm32_app_commands.csv) (141 commands the touchscreen app sends), [data/tap_geometry.csv](data/tap_geometry.csv).

Annotated disassembly and the redacted A33 boot log: [research/README.md](research/README.md).

Mechanical notes: [motors_and_display.md](motors_and_display.md), [extruder.md](extruder.md), [hardware_research.md](hardware_research.md).
