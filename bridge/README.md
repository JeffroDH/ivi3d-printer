# ivi-bridge — Orca Slicer / Anycubic Slicer Next → IVI3D

A small local Python service that looks like an **OctoPrint** server to the slicer and forwards jobs to the IVI3D.

| Mode | Transport | What happens |
|---|---|---|
| `wifi` (default) | kore API `:8080` | `connect` → `upload` (201) → `disconnect`. **Start the job on the touch screen** — `start_print` is 404 on firmware V1.3.2-alpha. Future/custom firmware may enable Wi-Fi start. |
| `serial` | USB-C, 115200 | `M2411 S2` (+`M1001 L` only if fw ≥ 2.4.0) → wait for `PC start work` → stream G-code per `ok`. Connect: `M2005`, `M2007`, `M105`, `M2155 S4` (like IVI 3licer; a stale PC job is stopped with `M2411 S3`). Laser/CNC: `G53`, `G28`, [`G0 Z<laser_focus_z> F1500`], `G54` before start. Pause `M2410`, resume `M2411 S1`, cancel = `M2411 S3` + heaters off. Progress at `/api/job`. **Only one program can own the port — disconnect IVI 3licer.** The Mac must stay awake for the whole print. |

## Install (macOS) — one time, no Terminal
Double-click **`Install IVI Bridge.command`** (first time: right-click → Open if Gatekeeper complains). It:
- copies the bridge to `~/Library/Application Support/ivi-bridge/app`, no extra packages (built-in termios serial, no pyserial);
- writes `~/.config/ivi-bridge/config.json` (mode 600) if missing: `mode: auto`, printer `192.168.50.85:8080`, stock token, random API key;
- installs/loads the LaunchAgent `com.ivi3d.bridge` (starts at login, restarts on crash; log `~/Library/Logs/ivi-bridge.log`);
- writes the API key into OrcaSlicer for you (`ivi_setup_keys.py`): the IVI3D printer presets (`printhost_apikey`),
  the Device tab's saved connection (`OrcaSlicer.conf` → `local_machines` → `127.0.0.1:5000`) and the IVI3D Bridge
  plugin's config (`orca_plugins/config.json`). Each Orca file is backed up (`*.bak-<date>`) first. Orca must be
  closed — the installer asks you to quit it and retry (or skip);
- shows the Orca settings in a dialog and copies the API key to the clipboard.
Re-run it after updating the repo; the existing key is kept (`"Install IVI Bridge.command" --new-key` from Terminal
makes a new one and updates Orca too).
**After importing `IVI3D.orca_printer` again** (it ships with a placeholder key), quit Orca and double-click
**`Fix IVI Bridge Key.command`** (in this folder or `~/Library/Application Support/ivi-bridge/app`). Same as
`/usr/bin/python3 bridge/ivi_setup_keys.py --wait`; add `--dry-run` to only list what would change. **`Uninstall IVI Bridge.command`** removes it (optionally the settings).
If macOS asks, allow Python under **Privacy & Security → Local Network**.

**Automatic mode:** USB printer plugged in (`/dev/tty.usbmodem*`) → USB print starts immediately (Mac kept awake via `caffeinate -i` for the job); otherwise → Wi-Fi upload, start on the touch screen. Override with `"mode": "wifi"` or `"serial"` in the config.
**Notifications** for upload done / print started / finished / cancelled / errors (`"notify": false` to silence).
**Status page:** http://127.0.0.1:5000/ — state, temperatures, progress, Pause/Resume/Cancel. Temperatures come from the printer's USB reports during a job (the port is released between jobs so IVI 3licer can still use it), and also appear in Orca's device tab via `/api/printer`.

## Orca Slicer
1. Import `IVI3D.orca_printer` (see [../orca/README.md](../orca/README.md)); it pre-sets OctoPrint `127.0.0.1:5000`,
   and the installer / `Fix IVI Bridge Key.command` fills in the API key. Nothing to paste.
2. Optional check: Prepare sidebar → **Printer** title bar → Connection (Wi-Fi) icon → **Test**. (Hidden while the
   experimental "Use printer agents instead of print hosts" option is on.)
3. Slice → **Send** (wifi: upload, then press start on the touch screen) or **Print** (serial: starts now).

Alternative without the service in wifi mode: Process → Others → Post-processing scripts:
`/usr/bin/python3 /PATH/bridge/ivi_bridge.py postprocess;` then use Export G-code.
(The hook is skipped when the slicer itself is uploading to OctoPrint, to avoid double sends.)

## Anycubic Slicer Next
Next is an Orca fork, but its printer connection is built around Anycubic's own cloud/LAN printers; it does not reliably expose the generic OctoPrint print-host option, and its Remote Print reportedly **skips post-processing scripts**. Generic paths that work:
1. **Post-processing script on export** (same line as above) → *Export G-code* triggers the send.
2. **Watch folder**: `python3 bridge/ivi_bridge.py watch ~/IVI-out` and export G-code into `~/IVI-out`.
3. If your Next build does show a 3rd-party/OctoPrint print host for a custom printer, use the Orca steps.
Either way, use a custom (non-Anycubic) printer profile with the IVI delta geometry.

## Printer events handled (USB)
| Printer says | Bridge does |
|---|---|
| `warning:DriveX locked rotor` | pauses (`M2410`, as IVI 3licer does), state *Paused: locked rotor*, notification |
| `PC/SC trigger pause`, `trigger resume: ok` | tracks pause/resume (touch-screen pauses too) |
| `Printer halted. kill() called!` | *Error*, notification — power-cycle the printer |
| `Can't start work in current status: 5` | old job still paused: sends `M2411 S3` and retries once (`auto_clear_stale_job`), else error |
| `Working Status: WORKING_SCREEN` at connect | refuses (touch-screen job running) |
Status page button **Clear stuck job** (`POST /api/ivi/clear`) sends `M2411 S3`.
Laser jobs without a Z move are refused when `home_before_job` is on unless `laser_focus_z` is set: after `G28` a delta sits at the top
and the first sideways move stalls a tower (see docs/laser_cnc_gcode.md).

## CLI
`ivi_bridge.py [--config F] [--mode wifi|serial] serve | send FILE | postprocess FILE | watch DIR`
`send`/`postprocess`/`watch` hand the file to the running service if it is up (required for serial, since streaming outlasts the slicer hook), else upload directly over Wi-Fi.

## Tests
`python3 -m unittest discover -s bridge/tests -v` — fake serial printer and fake kore HTTP printer; nothing touches real hardware.

## Not yet verified on hardware
Whole bridge (written 2026-11-01, unit-tested only); Orca/Next host test against it; serial cancel via `M2411 S3` (decoded, not run), locked-rotor/kill/status-5 handling, laser/CNC prelude (fake-serial tests only; the printer may need the touch screen to exit PC mode); laser/CNC jobs.
