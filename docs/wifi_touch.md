# Wi-Fi control and touch injection

Three ways to drive a print exist today. Only the USB-C path can start one without touching the screen.

| Path | Start a job? | Notes |
|---|---|---|
| kore `POST /api/v1/upload` | No | File appears in the on-screen Wi-Fi list. Start is a finger on Make, then the dialogs, then Start |
| [bridge/](../bridge/README.md) on the STM32 USB-C port | Yes | `M2411 S2` and a line-by-line stream. Verified with an FDM print on 2026-11-01. The screen locks on `WORKING_PC` |
| `tools/ivi_touch_nav` | Only if you ask it to tap Start | Drives the stock Qt UI by injecting touch events. Default `goto-print` stops on the status page **before** Start |

Nothing in the stock app starts a print from the network. UDP 20050 only answers `discover`. Patching the QML or the UI binary is not part of this tree.

## Upload names

kore accepts a filename with **exactly one dot** and an extension of `gcode`, `cnc`, or `nc`. `cube.gcode` is stored. `benchy_0.2mm.gcode` returns **412** `File type error`. The bridge forwards the slicer's name unchanged, so a normal Orca name is rejected on Wi-Fi upload. The bridge code is intentionally unchanged; renaming before upload (the navigator's `safe_name()` replaces extra dots) is a follow-up. Full rules: [a33.md](a33.md#kore-upload-api).

## Touch injection

`tools/ivi_touch_nav` (v0.2.0) runs on the computer, not on the printer.

1. An ephemeral sshd on the A33 (keys and pid file in `/tmp` only).
2. SSH with `-T` and a remote command, so `/etc/profile` does not run and a second copy of the UI is not started.
3. Read `/dev/fb0` (the visible page, using the pan offset) and classify the screen.
4. Inject one tap or a slow drag through `/tmp/ivitap2`, which writes gt9xx Type-A events to `/dev/input/event3`.

The helper is a 53008-byte static armel binary, sha256 `4ea4403987136da7936670cdb56781b7914cc03e91b8889b12d714d6baf3c0a8`. Source and the build line are in `tools/ivi_touch_nav/device/ivitap2.c`. It refuses to write unless the input device name contains `gt9xx` and the axis maxima are 800×480. A `-G` guard hashes the framebuffer rectangle under the finger and refuses the tap if the screen changed after the screenshot.

Coordinates are pixels. The table is [data/tap_geometry.csv](data/tap_geometry.csv). Points used most often:

| Target | x, y | Risk |
|---|---|---|
| Home → Files | 122, 209 | none |
| Files → Wi-Fi row | 400, 225 | none |
| Wi-Fi list, Make on row 0 | 552, 132 | selects a file. Do not tap x > 621 (Delete is near 701) |
| Dialog left / right | 215, 345 / 585, 345 | confirms the dialog |
| Status Start | 400, 421 | **high**: `G28`, `M2001 S1`, `M2411 S2` |
| Status Cancel / Stop | 680, 421 | stops |
| Page Home / Back | 740, 29 / 60, 29 | none |
| Wake, below the buttons | 400, 472 | inferred inert |

The classifier will not tap on a provisional or unknown screen, or on printing, paused, homing, or the PC-lock page. `goto-print` also refuses when two file descriptors in the UI process point at the same gcode (that means the file is streaming). Calibration screenshots stay on the computer (`~/.ivi_touch/calib/`). Until calibration, every screen is provisional and no action tap is sent.

`M2001 S1`, which Start sends, force-stops a PC/bridge job. Do not tap Start, and do not let the navigator tap Start, while the bridge is printing.

The tool's own README is [../tools/ivi_touch_nav/README.md](../tools/ivi_touch_nav/README.md). It has been tested against a simulated framebuffer and a fake kore server (49 tests). It has not been run on the printer. The first hardware session is [home_session/RUNBOOK.md](home_session/RUNBOOK.md), with [QUICKREF.md](home_session/QUICKREF.md) and the upload/probe notes in [CHECKS.md](home_session/CHECKS.md).

Holding the front power button for about 3 seconds drops the rails (GD32: PB1, then PA4). That is a hard power cut. The next boot runs `e2fsck -y` on a `barrier=0` rootfs. Use the on-screen Stop first.

## What the bridge should keep doing

Leave print control on the USB-C port. Wi-Fi upload is optional and only for names kore will accept. Do not write `/dev/ttyUSB0` from another process while the Qt app owns it. Do not send `M2155 S0` while the screen is up; that interval is global and `S0` disables reports for both ports.

## Related

[a33.md](a33.md) · [stm32.md](stm32.md) · [network.md](network.md) · [architecture.md](architecture.md) · [../bridge/README.md](../bridge/README.md)
