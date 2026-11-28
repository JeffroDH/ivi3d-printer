# Network control, USB-C, and touch injection

Ways to drive a print, from the one in daily use to the ones kept for recovery and research.

| Path | Starts a job? | Notes |
|---|---|---|
| **ivibridge** on the printer, ports **5001** and **80** ([a33_bridge/](../a33_bridge/README.md)) | Yes, through the stock touchscreen path | OctoPrint-compatible API and web UI. Orca **Upload and Print** stores the file in `/userdata/WifiFile` and posts a start request that the touchscreen hook picks up. The stock Status page opens (assist mode: confirm the plate and tap RUN), or the persistent Auto-start setting runs the stock RUN path. The job then runs from the touchscreen app, as a touchscreen start would. Flow: [native_print.md](native_print.md) |
| Stock kore `POST /api/v1/upload`, TCP 8080 | No | The file appears in the on-screen Wi-Fi list. Start is a finger on Make, then the dialogs, then Start. Print-control routes return 404 on V1.3.2-alpha |
| [bridge/](../bridge/README.md) on the STM32 USB-C port | Yes | Optional computer-side service. `M2411 S2` and a line-by-line stream. The screen locks on `WORKING_PC`. The USB port must be free of any other program |
| `tools/ivi_touch_nav` | Only if you ask it to tap Start | Drives the stock Qt UI by injecting touch events over SSH. Default `goto-print` stops on the status page **before** Start |

UDP 20050 only answers `discover`. Nothing in the stock app starts a print from the network; the ivibridge row works because the touchscreen app carries a small QML hook ([tools/ivi_hook/](../tools/ivi_hook/README.md)) that opens the Status page and calls the stock handlers.

## ivibridge in one paragraph

ivibridge owns the real serial node (`/dev/ivi-stm32`) and hands the stock app a pty at `/dev/ttyUSB0`, so the app and the network share the STM32 link without a second process opening it. While a touchscreen or native-start job runs, the bridge never writes onto that link. Pause, resume, cancel, temperature, speed, flow, fan on/off, and Z-offset go through the hook ([native_print.md](native_print.md)). Moves, homing, and other console G-code are refused until the job ends. The page and API are reachable on the LAN without a key; loopback and Tailscale `100.x` need the key. Install and rollback: [a33_bridge/README.md](../a33_bridge/README.md#install-and-rollback).

## Upload names

The stock kore upload keeps the first two non-empty pieces of a filename split on `.`. The second piece must be exactly `gcode`, `cnc`, or `nc`, or the reply is **412** `File type error`. `cube.gcode` is stored. `benchy_0.2mm.gcode` is rejected. ivibridge and the computer-side bridge both rewrite names before storing or sending them: extra dots and characters outside `[A-Za-z0-9_-]` become `-` (`Cube_0.2mm_PLA.gcode` becomes `Cube_0-2mm_PLA.gcode`), the extension is folded to `gcode`, `cnc`, or `nc`, the name is capped at 100 bytes, and a collision between two originals gets `-2`, `-3`, and so on. The navigator's `safe_name()` applies the same shape of rename for its own uploads. Full rules: [a33.md](a33.md#kore-upload-api).

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

## Rules that apply to every path

- Leave print control to one owner at a time. Do not write `/dev/ttyUSB0` from another process while the Qt app owns it, and do not open the USB-C port while a touchscreen or native-start job is streaming (that stalls it).
- Do not send `M2155 S0` while the screen is up. That interval is global, and `S0` disables reports for both ports.

## Related

[native_print.md](native_print.md) · [calibration.md](calibration.md) · [orca_bridge.md](orca_bridge.md) · [a33.md](a33.md) · [stm32.md](stm32.md) · [network.md](network.md) · [architecture.md](architecture.md) · [../bridge/README.md](../bridge/README.md) · [../a33_bridge/README.md](../a33_bridge/README.md)
