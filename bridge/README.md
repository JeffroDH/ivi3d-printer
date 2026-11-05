# ivi-bridge — Orca Slicer / Anycubic Slicer Next → IVI3D

A small local Python service that looks like an **OctoPrint** server to the slicer and forwards jobs to the IVI3D.

| Mode | Transport | What happens |
|---|---|---|
| Wi-Fi (Orca **Upload**) | kore API `:8080` | `connect` → `upload` (201) → `disconnect`. **Start the job on the touch screen** — `start_print` is 404 on firmware V1.3.2-alpha. Future/custom firmware may enable Wi-Fi start. |
| USB (Orca **Upload and Print**) | USB-C, 115200 | `M2411 S2` (+`M1001 L` only if fw ≥ 2.4.0) → wait for `PC start work` → stream G-code per `ok`. Connect: `M2005`, `M2007`, `M105`, `M2155 S4` (like IVI 3licer; a stale PC job is stopped with `M2411 S3`). Laser/CNC: `G53`, `G28`, [`G0 Z<laser_focus_z> F1500`], `G54` before start. Pause `M2410`, resume `M2411 S1`, cancel = `M2411 S3` + heaters off. Progress at `/api/job`. **Only one program can own the port — disconnect IVI 3licer.** The Mac must stay awake for the whole print. |

## Folder layout
| Path | What |
|---|---|
| `ivi_bridge.py`, `ivi_setup_keys.py`, `ivi_add_header.py` | core code (stdlib only on macOS/Linux; pyserial on Windows) |
| `install/macos/` | `Install IVI Bridge.command`, `Uninstall IVI Bridge.command`, `Fix IVI Bridge Key.command`, plist example |
| `install/linux/` | `install.sh`, `uninstall.sh`, `fix-key.sh` (systemd) |
| `install/windows/` | `Install IVI Bridge.bat` → `install.ps1`, `Uninstall IVI Bridge.bat` → `uninstall.ps1`, `Fix IVI Bridge Key.bat` |
| `examples/config.example.json` | annotated config (`"serial_port": "auto"` = per-OS default) |
| `tests/` | unit tests |

## Install (macOS) — one time, no Terminal
Double-click **`install/macos/Install IVI Bridge.command`** (first time: right-click → Open if Gatekeeper complains). It:
- copies the bridge to `~/Library/Application Support/ivi-bridge/app`, no extra packages (built-in termios serial, no pyserial);
- writes `~/.config/ivi-bridge/config.json` (mode 600) if missing: `mode: auto`, printer `192.168.50.85:8080`, stock token, random API key;
- installs/loads the LaunchAgent `com.ivi3d.bridge` (starts at login, restarts on crash; log `~/Library/Logs/ivi-bridge.log`);
- writes the API key into OrcaSlicer for you (`ivi_setup_keys.py`): the IVI3D printer presets (`printhost_apikey`),
  the Device tab's saved connection (`OrcaSlicer.conf` → `local_machines` → `127.0.0.1:5001`) and the IVI3D Bridge
  plugin's config (`orca_plugins/config.json`). Each Orca file is backed up (`*.bak-<date>`) first. Orca must be
  closed — the installer asks you to quit it and retry (or skip);
- shows the Orca settings in a dialog and copies the API key to the clipboard.
Re-run it after updating the repo; the existing key is kept (`"Install IVI Bridge.command" --new-key` from Terminal
makes a new one and updates Orca too).
**After importing `IVI3D.orca_printer` again** (it ships with a placeholder key), quit Orca and double-click
**`Fix IVI Bridge Key.command`** (in `install/macos/` or `~/Library/Application Support/ivi-bridge/app`). Same as
`/usr/bin/python3 bridge/ivi_setup_keys.py --wait`; add `--dry-run` to only list what would change. **`install/macos/Uninstall IVI Bridge.command`** removes it (optionally the settings).
If macOS asks, allow Python under **Privacy & Security → Local Network**.

**Updating an existing Mac install** (from before the `install/` move): `git pull`, then double-click
`bridge/install/macos/Install IVI Bridge.command` once. Same LaunchAgent label (`com.ivi3d.bridge`), app folder, config
and key; it just re-copies the core files and reloads. Your existing `"serial_port": "/dev/tty.usbmodem*"` keeps working.

## Install (Linux)
`bridge/install/linux/install.sh` (re-runnable; keeps config + key). Options: `--system` (system service, sudo), `--no-service`, `--new-key`, `--no-orca`.
- needs `python3` (3.8+); makes a venv in `~/.local/share/ivi-bridge/venv` with pyserial (optional on Linux; falls back to system python3);
- copies the core files to `~/.local/share/ivi-bridge/app`, writes `~/.config/ivi-bridge/config.json` if missing (port 5001, filtering off);
- installs a **systemd --user** unit `ivi3d-bridge.service` (logs: `journalctl --user -u ivi3d-bridge -f`). For a headless box run
  `sudo loginctl enable-linger $USER` so it runs without a login, or use `--system`. `--no-service` writes `~/.local/share/ivi-bridge/run.sh` instead;
- serial: the printer appears as `/dev/ttyACM*` (default pattern `/dev/ttyACM*,/dev/ttyUSB*`); you need group `dialout` (Debian/Ubuntu/Fedora) or `uucp` (Arch): `sudo usermod -aG dialout $USER`, then log out/in;
- Orca: key written into `~/.config/OrcaSlicer` (Flatpak: `~/.var/app/io.github.softfever.OrcaSlicer/config/OrcaSlicer`). After re-importing the profile, quit Orca and run `fix-key.sh`.
Uninstall: `~/.local/share/ivi-bridge/uninstall.sh [--purge]`.

## Install (Windows)
Double-click `bridge\install\windows\Install IVI Bridge.bat` (runs `install.ps1` with `-ExecutionPolicy Bypass`; no admin). Options: `-NewKey`, `-NoTask`, `-NoOrca`.
- needs Python 3.8+ from python.org (`py` launcher; the Store stub is skipped); makes a venv and installs **pyserial** (required on Windows);
- copies everything to `%LOCALAPPDATA%\IVI3D Bridge` (`app\`, `venv\`, `config.json`, jobs/history under `data\`);
- registers a per-user Scheduled Task **IVI3D Bridge** at logon running `pythonw.exe` (no window, restarts on failure);
- serial: `"serial_port": "COM*"` picks the lowest COM port (set e.g. `"COM5"` if you have several; see Device Manager → Ports);
- firewall: none needed on `127.0.0.1`; for `0.0.0.0` (OctoApp) allow TCP 5001 once as admin (command printed by the installer);
- Orca: key written into `%APPDATA%\OrcaSlicer`; after re-importing the profile, quit Orca and run `Fix IVI Bridge Key.bat`.
Uninstall: `Uninstall IVI Bridge.bat` (add `-Purge` from a prompt to delete settings).

## Two ways to print (Orca's buttons, default `"mode": "auto"`)

| Orca button | Where the file goes | Who runs the print | USB / Device page |
|---|---|---|---|
| **Upload and Print** | Streamed from the Mac over **USB serial** (`M110 N0`, then `N<n> <cmd>*<checksum>` per `ok`, resend handled; `strip_commands` applied if set) | The bridge, starting now | Live status + progress bar, Pause/Resume/Cancel on the Device page. **The Mac must stay awake (caffeinate runs) and the USB cable must stay connected until it finishes.** |
| **Upload** | Stored on the printer over **Wi-Fi** | You, from the **touch screen** (the job runs from the printer's own storage, so the Mac can sleep) | **USB controls are turned off for that print**: opening the USB port during a stored-file print stalls it (cable plugged in alone is fine). The Device page shows a banner; press **Printer idle, re-enable USB** when the print is done or cancelled. Pause/cancel on the touch screen. |

`"mode": "wifi"` sends both buttons over Wi-Fi; `"mode": "serial"` streams both over USB (Upload then only spools).

**USB status + controls** (`"serial_monitor": true`, default): when the USB port is plugged in and free, the bridge holds it and polls `M105` + `M2007` every `monitor_interval_s` (and asks for `M2155 S<report_interval_s>` auto-reports). Orca's Device tab then shows live temps (`/api/printer`) and job state (`/api/job`; M2007 status 5 = paused). If the port is missing or owned by IVI 3licer, the bridge keeps retrying and the status page shows "USB: not connected (…)"; uploads are unaffected. Set `"serial_monitor": false` to leave the port free for IVI 3licer.
Controls (USB only): `POST /api/printer/tool` (`target`, `flowrate`), `/api/printer/bed` (`target`), `/api/printer/printhead` (`feedrate`), `/api/printer/command` (whitelist: `M104/M140/M220/M221 S<n>`, `M105`, `M2007`, `M106/M107`, `M2410`, `M2411 S1/S3`; limits nozzle ≤300 °C, bed ≤120 °C, speed 10–300 %, flow 10–200 %). `/api/job` pause/resume/cancel also works for a touch-screen-started job (`M2410`, `M2411 S1`, `M2411 S3`).
**`M104`/`M140`/`M220`/`M221` are standard Marlin and not yet verified on firmware V1.3.2-alpha.**
**Notifications** for upload done / print started / finished / cancelled / errors (`"notify": false` to silence).
**Status page:** http://127.0.0.1:5001/ — styled like the printer's *Control* screen. **Toolhead**: X/Y/Z readout (M114), Home (G28), jog pad X±/Y±/Z± (G91 · G1 · G90; X/Y = move to X0 Y0, Z = home), jog speed 200/500/1500/3000 mm/min and distance 0.05/1/10/50 mm, plus speed %, flow %, Pause/Resume/Cancel/Clear. **Filament**: Load/Unload like the touch screen: pick the loaded filament (`"filaments"`: PLA 210, PETG 240, ABS 250, TPU 225, PCTG 250, or Custom °C) → `M104` and *Heating…* with live temperature (polled, no blocking `M109`; continues once within `filament_tolerance_c` = 3 °C, Cancel available, timeout `filament_heat_timeout_s`) → `M83`, unload `G1 E10 F300` + `G1 E-<filament_load_mm> F1500`, load `G1 E<filament_load_mm> F300`, `M82`, then *Filament coming out of the nozzle?* (Yes, done / No, extrude more = `G1 E<filament_retry_mm=20> F300`, asks again; nozzle stays hot) → `M104 S0` after Yes, after Unload and on Cancel (like the touch screen) → Done/Error (`GET/POST /api/ivi/filament`). `"filament_load": "m701"` sends `M701`/`M702` instead, but **firmware V1.3.2-alpha ignores them**, nozzle 210/240/270 °C and bed 60/80/100 °C presets with −/+ 5 °C, Fan (M106 S255/M107), Cooldown, Extrude/Retract (M83 · G1 E · M82; the firmware refuses cold extrusion, so if the nozzle target is <170 °C or not yet reached it first heats to `jog_extrude_temp` = 235 °C with the same Heating dialog/Cancel — Cancel restores the previous target — and leaves the nozzle hot afterwards: "Nozzle left at 235°C – Cooldown to turn off") using jog speed 100–1000 mm/min and distance 10–100 mm. Controls are disabled while USB is not connected. Side by side at ≥1100 px, tabs below. G1 limits: |X|,|Y| ≤150, |Z| ≤300, |E| ≤150 mm, F ≤6000. Tested on the printer: bed/nozzle temp, jogs, Home, fan, extrude. M701/M702 are ignored by the firmware.

**Live toolpath** (Device page, Upload and Print only): a top-down view of the streamed file — current layer printed (bright) / still to print (faint), earlier layers dimmed, orange nozzle marker, bed circles (dashed 210 mm, solid 200 mm) and a Z-height layer bar, redrawn every 2 s. The page fetches the job's G-code once (`GET /api/ivi/job/gcode`, API key required; the stripped lines exactly as streamed, 404 without a USB job), parses the moves in the browser (~20 MB for a 100k-line file) and frees the text. `/api/job` → `ivi` adds `line` (lines acknowledged), `layer`, `layers` and `gcode`. Wi-Fi **Upload** prints show a note instead (the printer runs the file itself, so there is no line position).

## Orca Slicer
1. Import `IVI3D.orca_printer` (see [../orca/README.md](../orca/README.md)); it pre-sets OctoPrint `127.0.0.1:5001`,
   and the installer / Fix-key helper (`install/<os>/`) fills in the API key. Nothing to paste.
2. Optional check: Prepare sidebar → **Printer** title bar → Connection (Wi-Fi) icon → **Test**. (Hidden while the
   experimental "Use printer agents instead of print hosts" option is on.)
3. Slice → **Upload and Print** = stream over USB now with live monitoring (keep the Mac awake and connected), or
   **Upload** = store on the printer and start it on the touch screen (USB controls stay off during that print).

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

## IVI file header (touch-screen time / material)
On every upload (Wi-Fi and USB spool), if the file has no `;Header Start`, the bridge prepends IVI 3licer's block (format from its `server/index.js`): `;header_type: 3dp,<nozzle>mm`, `;file_total_lines`, `;file_valid_lines`, `;estimated_time(s)` (Orca's `; estimated printing time (normal mode)`, else `M73 P0 R<min>`), `;material_type` (`; filament_type`), nozzle/bed temps, `;work_speed(mm/minute)` (`sparse_infill_speed`×60), min/max X/Y/Z of extruding moves (else `max_z_height`). Unverified extras: `;filament_used(m)`, `;filament_weight(g)`. Streams in two passes (fine for 17 MB+). Toggle `"ivi_header"`; nozzle default `"nozzle_diameter": 0.3`. Test one file: `python3 bridge/ivi_add_header.py IN [OUT]`.
**G-code filtering is off by default** (`"strip_commands": []`). Stall tests showed `M204`, `M205`, `M73` and `G21` were not the cause of the earlier stalls (the prime was), so nothing is dropped. To re-enable, set `"strip_commands": ["M204","M205","M73","G21"]`; matching command lines (comments after them included) are then dropped, the log shows how many, and the header's line counts describe the output file. `M73 P0 R<min>` is still read for the time estimate. CLI: `--strip M204,M205,M73,G21`.

## Device page extras (Fluidd/Mainsail-style)
All of these live on the bridge's Device page (Orca's Device tab, or `http://<mac>:5001/`) and use the same API key as everything else. On a phone the page has tabs: Toolhead, Filament, Camera, Files, Console.

- **Webcam**: off until you configure one in `~/.config/ivi-bridge/config.json`:
  - `"webcam_stream_url": "http://<camera>/video.mjpg"` shows an IP camera's MJPEG stream directly.
  - `"webcam_snapshot_url": "http://<camera>/snapshot.jpg"` refreshes a still every 3 s. Timelapse uses this.
  - `"webcam_usb_device": "0"` uses a USB camera plugged into the Mac. This needs ffmpeg (`brew install ffmpeg`). The first time, macOS asks for camera permission for Python.
  - `"webcam_usb_fps": 10` (default) is the live MJPEG output rate after capture. Capture requests 30 fps from the camera, then ffmpeg throttles with `-vf fps=N`. Raise this (for example 15–24) for smoother live video; higher values cost CPU and Tailscale/Wi‑Fi bandwidth.
- **Timelapse**: `"timelapse": true` grabs one frame at each layer change during **Upload and Print** (USB) jobs. When the job ends, ffmpeg turns the frames into an MP4 in `~/Library/Application Support/ivi-bridge/timelapse/`, and it's linked under the camera. Without ffmpeg, the frames are kept as JPEGs. Upload (Wi-Fi) prints can't have a timelapse, because the bridge doesn't know the layer.
- **Temperature graph**: nozzle and bed, actual and dashed target, for the last 30 minutes (`temp_history_s`). It needs USB, so it pauses during Upload (Wi-Fi) prints.
- **Files**: every job you've sent to the bridge, from `~/Library/Application Support/ivi-bridge/jobs/`, with Orca's embedded thumbnail, the slicer's time estimate and filament use. **Print (USB)** reprints a file through the Upload and Print path. **Queue** adds it to the queue, and **Delete** removes the file from the Mac.
- **Queue**: jobs never start on their own, because the finished part has to be taken off the bed first. Press **Start next** when the bed is clear.
- **History**: every USB job (finished, cancelled or error, with time, estimate and filament) and every Wi-Fi upload, plus totals. It's stored in `~/Library/Application Support/ivi-bridge/history.json`.
- **Console**: a G-code terminal that shows the printer's replies, with the routine temperature polling hidden. Commands go through the bridge's safety list (temperatures, fan, speed/flow, jogging, homing, `M105 M114 M115 M119 M503 M2007`, …). Anything else is refused. During a USB print only temperature, fan, speed, flow and status commands are allowed. During an Upload (Wi-Fi) print the console is **off**, because opening USB would stall the print. Cancel always stays available.
- **Macros**: one-click G-code sequences stored by the bridge in `~/.config/ivi-bridge/macros.json`, not in the firmware, which has no user macros. The defaults are Preheat PLA, Preheat PETG, Cooldown, Park (home), Load filament, Unload filament, and Settings backup (M503). You can edit them on the page ("Edit macros", one per line: `Name | M104 S210; M140 S60`). They follow the same safety rules as the console. Special steps: `@load` / `@unload` open the filament picker (or `@load PLA`, `@load 215`), and `@backup` saves the M503 settings dump.
- **Settings backup**: the macro writes `~/.config/ivi-bridge/backups/m503-YYYYMMDD-HHMMSS.txt` (only you can read it). It only runs while the printer is idle on USB. Keep these files out of git.
- **Phone notifications**: on top of the macOS notifications, set `"ntfy_url": "https://ntfy.sh/<a-long-secret-topic>"` and subscribe to that topic in the ntfy app. You get pushes for print started, finished, cancelled or failed, and for pauses. It's off by default. Anyone who knows the topic name can read it, so pick a hard-to-guess one.

**Port 5001 (not 5000):** macOS's AirPlay Receiver (ControlCenter) holds port 5000 on every address, so the bridge defaults to **5001**. Orca (`127.0.0.1:5001`) and **OctoApp (`http://<mac-ip>:5001`) must use 5001**. Older installs on 5000: set `"listen_port": 5001` in config.json and update Orca/OctoApp. With `"listen_host": "0.0.0.0"` the bridge still falls back to `127.0.0.1` plus the Mac's LAN address if the wildcard bind fails; restart it if the Mac's IP changes.

## CLI
`ivi_bridge.py [--config F] [--mode wifi|serial] serve | send FILE | postprocess FILE | watch DIR`
`send`/`postprocess`/`watch` hand the file to the running service if it is up (required for serial, since streaming outlasts the slicer hook), else upload directly over Wi-Fi.

## Tests
`python3 -m unittest discover -s bridge/tests -v` — fake serial printer and fake kore HTTP printer; nothing touches real hardware.

## Not yet verified on hardware
USB monitor/controls (M2007 status line format is a guess: `status: <n>`; M104/M140/M220/M221 untested); whole bridge (written 2026-11-01, unit-tested only); Orca/Next host test against it; serial cancel via `M2411 S3` (decoded, not run), locked-rotor/kill/status-5 handling, laser/CNC prelude (fake-serial tests only; the printer may need the touch screen to exit PC mode); laser/CNC jobs.

**Time left (USB stream):** uses Orca's `M73 P<pct> R<min>` lines as they are streamed (R = slicer minutes left, counted down since that line), scaled by 100/FR from a bare `M220` sent every `feedrate_poll_s` (45 s) while printing (`"poll_feedrate": false` turns that off; no reply is tolerated). Files without M73 fall back to the line-rate estimate. The Device page shows the source next to *Left*.
