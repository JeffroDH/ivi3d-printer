# A33 ivibridge — on-printer Wi-Fi control

`ivibridge` is a static C daemon that runs on the IVI 3D printer's Allwinner A33 (Linux 3.4). It owns the real STM32 serial link, gives the stock touchscreen app a pty in place of `/dev/ttyUSB0`, and serves an OctoPrint-compatible HTTP API plus a web UI on TCP ports 5001 and 80 (5001 is the main port; Orca should keep using it).

This is not the Mac/PC bridge in [`../bridge/`](../bridge/README.md). That program runs on a computer and streams jobs over USB serial. This daemon runs on the printer, so Orca Slicer can print and monitor over the LAN with no cable and no computer in the middle.

The current version is **0.1.19-a33**. Built binaries and install tarballs are not in this folder; build them with `scripts/build.sh`.

## Architecture

The real CH340 node (`/dev/ttyUSB0`, 115200 8N1) is recreated as `/dev/ivi-stm32` on devtmpfs. The daemon opens that node exclusively and atomically replaces `/dev/ttyUSB0` with a symlink to a pty. The touchscreen app keeps talking to `/dev/ttyUSB0` and does not need to be patched.

The daemon passes the app's traffic through byte for byte and takes turns on the wire. Replies meant for a network command are kept away from the app, because the app treats any line containing `ok` as an acknowledgement. `print=true` stores the file in `/userdata/WifiFile` and posts a `/tmp/ivibridge/print_request` so the touchscreen app can open the stock Status page (assist mode; the user taps Start). It does not start a network stream and does not show the `WORKING_PC` lock page. A persistent Auto-start setting (default off) can skip the plate warning and run the stock RUN path. The web UI shows Z offset as a normal offset (reference H minus effective H: 0.00 after calibration, + when the nozzle is higher). Save permanently queues `M665`+`M500` until idle and keeps the displayed offset. “Set current as zero” updates the reference. A stock paper-test calibration resets it. The Calibration tab runs stock G33, G29, and the paper test (with Run all chaining XYZ into leveling, then the paper test), and saves with M500 only on success. The older stream path is only used when `IVIB_NET_STREAM=1` (tests/debug). While a network job *does* run, the firmware status shown to the app is rewritten to `WORKING_PC`. The lock page's Disconnect button (`M108` + `M2001 S1`) is intercepted and turned into a graceful cancel. During a touchscreen job the API can pause, resume, cancel, and adjust temperature, speed, flow, fan (on/off), and Z-offset through that same request route; manual moves, homing, and arbitrary console G-code stay blocked.

Network jobs are streamed with Marlin line numbers, checksums, and resend support. Pause, resume, and cancel use the firmware job words (`M2410`, `M2411 S1`/`S3`/`S4`). Resume waits for `Finish pause` / `Resume complete` before the next job line. A stalled line is probed with `M105` and, if it was dropped, resent with the same `N` so a motion line cannot run twice. The daemon never sends `M3` or `M4`. `M5` is included in the cooldown only when the last head report was a laser.

Uploaded jobs start in `/tmp/ivi_jobs`. Once the internal FAT partition is mounted at `/userdata/WifiFile`, new uploads go to `/userdata/WifiFile` (the same folder the touchscreen Wi-Fi file list shows) and earlier RAM copies are moved after a size and SHA-256 check. A file that is currently printing is not moved until the job ends. Jobs left in the older `/userdata/WifiFile/ivibridge_jobs` folder are still listed in the Files tab but do not appear on the touchscreen until they are moved into `/userdata/WifiFile`. Logs start in `/tmp/ivibridge/` and are also mirrored to `/userdata/WifiFile/ivibridge_logs/` (rotated at 2 × 1 MB each). Uploads are pre-scanned: embedded job-control words and `M3`/`M4` at `S>100` are rejected. Files that do not already have an IVI header get one on upload (`src/ivi_header.c`; also available as `ivibridge --add-header`).

## Fail-safes

- **Watchdog.** If the daemon dies, the supervisor restores the real `/dev/ttyUSB0` node, removes `/dev/ivi-stm32`, clears the stale serial lock, restarts the touchscreen app, and exits. It does not loop restarts.
- **Stop restores stock.** `scripts/ivibridge-ram.sh stop` stops a network job first, then puts the real serial node back and restarts the app on it.
- **Hot restart.** `stop` writes `/tmp/ivibridge/needs_app`. The next `start` relaunches the app if that marker is present or if uptime is at least 90 seconds (`IVIB_BOOT_WINDOW`). During early boot (uptime under that window, no marker) `start` leaves the app for the stock `autorun.sh`.
- **Boot hook.** `scripts/boot.sh` is started by one tagged line in `/etc/init.d/rcS`. It waits up to 30 seconds for the real `/dev/ttyUSB0`, then starts the bridge so the pty can be in place before the app opens the port. On timeout or failure, stock is left alone. The stock `ivissh` line and `autorun.sh` are not edited.
- **Boot-fail counter.** `/userapp/ivibridge/bootfail` is incremented before start and reset to 0 after 60 seconds (`IVIB_HEALTH_WAIT`) of a healthy daemon, watchdog, and link. If it is already ≥ 2 at boot, start is skipped until the file is cleared.
- **Off switches** (then reboot, or `ivibridge-ram.sh stop` if the supervisor is already up):
  - `/userapp/ivibridge/disable`
  - `/userdata/WifiFile/ivibridge.disable` (honoured once that partition is mounted; this script never formats or write-mounts it)
  - a `no-bridge` file at the root of a USB volume (`/dev/sd*`)
- **Mid-job exit.** SIGTERM during a network job sends `M2411 S3` and the cooldown before exiting, so the printer is not left mid-job.
- A reboot with the hook removed or an off switch set returns the printer to stock serial behaviour.

The printer's loopback interface is down, so supervisor `status` never opens a network connection. It reads pids, device nodes, and `/proc/net/tcp` instead.

## Security

- With an API key configured (`-K` file; the install script creates a 128-bit key in a mode-0600 file at `/userapp/ivibridge/apikey`):
  - Clients on RFC 1918 networks — `10/8`, `172.16/12`, and `192.168/16` — are trusted without a key.
  - Loopback and Tailscale `100.x` addresses still need the key (`X-Api-Key` or `?apikey=`).
- With no apikey file, every POST returns 403 and controls are disabled. GET status endpoints still work.
- The console allowlist matches the Mac bridge, except `M3`/`M4` are refused entirely. Temperatures, axis moves, and fans (`M106`/`M107` with optional `P0`/`P1` and `S0–255`) are range-limited. During a print (bridge job, touchscreen job, or a firmware `WORKING_*` status) only `M104`, `M140`, `M220`, `M221`, `M290` (±0.01 / 0.02 / 0.05 mm), `M106`, `M107`, `M105`, and `M114` are allowed; everything that moves the machine returns 409. `G29` is never on the console allow-list; leveling runs only from the Calibration flow.
- Do not commit or publish the apikey file, SSH keys, Wi-Fi credentials, password hashes, or the printer serial.

## HTTP API (ports 5001 and 80)

Compatible with Orca's OctoPrint connection and with the repo's Orca plugin client.

| Method | Path | Role |
|---|---|---|
| GET | `/` | Web UI (`www/index.html`) |
| GET | `/api/version`, `/api/server` | OctoPrint version stubs |
| GET | `/api/printer` | Temperatures, state, position, `ivi.head`, `ivi.fan` / `ivi.fans` (percent, once a fan command has been seen) |
| GET | `/api/fan` | Fan state only, `{"on":…,"fan":…,"fans":[…,…]}` (percent; `null` until a fan command has been seen). Public and read-only, no key, for the touchscreen Fan toggle |
| GET | `/api/job` | Active job, progress, resend/stall/lost-line counts |
| GET | `/api/files`, `/api/files/local`, `/api/ivi/files` | Stored jobs (size, mtime, time, filament, thumbnail flag) and the print queue |
| GET | `/api/ivi/files/thumb?name=…`, `/api/files/local/<name>/thumbnail` | Thumbnail extracted from the G-code comments |
| GET | `/api/ivi/console?since=` | Console ring (see quiet M114 below) |
| GET | `/api/ivi/link` | Link state and daemon version |
| POST | `/api/files/local`, `/api/files/sdcard` | Multipart upload; `print=true` stores the file and posts a native-start request |
| POST | `/api/files/local/<name>` | OctoPrint `select` / `print` of a stored file |
| POST | `/api/ivi/files`, `/api/ivi/queue` | Queue, print, delete, start-next, clear queue |
| DELETE | `/api/files/local/<name>` | Delete a stored job (refused while that file is printing) |
| POST | `/api/job` | `start`, `pause` (`pause` / `resume` / `toggle`), `cancel` |
| POST | `/api/printer/command`, `/api/printer/tool`, `/api/printer/bed`, `/api/printer/printhead` | Allowlisted commands, hotend/bed targets, flow, feedrate |
| POST | `/api/ivi/clear` | Orca plugin "clear stale job" |

A touchscreen print restricts the API: network start, uploads that print, and moving console commands return 409 until it finishes. Pause, resume, cancel, and the adjust commands above still work.

`GET /api/printer` includes `ivi.print` (`active`, `source` = `network` / `touchscreen` / `printer`, `paused`, `file`, `speed`, `flow`, `layer`, `z`) and `ivi.cal`. `GET /api/ivi/cal` returns the calibration state, the xyz values, and the current mesh as `level.grid[j][i]` (J rows from the front, I columns from the left).

## Web UI

The page is a port of the Mac bridge UI, served from `www/index.html`.

- **Toolhead:** temperatures, feedrate and flow, fan toggle, jog, Home (with a 14 px gap under the jog pad), and a position bar.
- **Filament:** load and unload wizard.
- **While printing**, Toolhead becomes **Status** and Filament becomes **Adjust** (the web counterparts of the touchscreen Status and Adjust pages). Status shows progress, elapsed and remaining time, layer and Z, temperatures, and the file, with Pause / Resume / Stop / Clear. Adjust has nozzle and bed targets, Z offset (`M290` babysteps and Save permanently), speed, flow, and fan. Jog, Home, extrude / retract, and moving macros are hidden or disabled, and the binary enforces the same lock. The normal boxes return when the print ends. On a phone these are the first two tabs; on a wide screen they take the places of Toolhead and Filament in the left and right columns.
- **Camera:** snapshot or MJPEG URL from a *separate* camera. Snapshot view refreshes at 5 frames/sec in the browser, not on the printer.
- **Files:** list of jobs stored on the printer, thumbnails, print, delete, and a manual queue (a queued job never starts on its own).
- **Console:** allowlisted G-code, plus a few built-in preset buttons (preheat PLA/PETG, cooldown, park, load/unload). A line under Send gives the reason when the console is unavailable or limited (printer link down, a calibration step waiting, a touchscreen job, or a print), and refusals from the bridge are printed in the console.

Automatic position checks (`M114`) are sent only while the Toolhead tab is visible: immediately after a jog or Home, and otherwise about every 10 seconds. Those automatic checks are posted with `"quiet": true` and are kept out of the console view. A check you type yourself still appears.

Intentionally omitted from this port: print history, timelapse, toolpath preview, a temperature graph, user-saved macros, and the printer's own camera.

## Orca Slicer

1. Printer settings → Connection: host type **OctoPrint**.
2. Host is the printer on port 5001, for example `http://192.168.50.85:5001` on a typical LAN. Use your printer's own address.
3. On a RFC 1918 LAN the Device tab works without pasting an API key (LAN trust). From a Tailscale `100.x` address, or any other non-LAN client, enter the key from `/userapp/ivibridge/apikey` on the printer.

## Install and rollback

These steps write to the A33's eMMC (`/userapp/ivibridge` on the rootfs). Only run them when the printer is idle (home screen, no job, nothing heating). Use `&&` between the steps so a failed check stops the rest. Verify hashes against the package `SHA256SUMS` and check that `-V` prints the version you expect before replacing files. Keep the previous package so you can roll back.

### Update an existing install

The package tarball contains `ivibridge`, `ivibridge-ram.sh`, `www/index.html`, `www/logo.svg`, and `SHA256SUMS`. From the directory that holds it, with `PRINTER` set to the printer's SSH host. Use a non-login SSH command (`-T`, and if the host entry sets `RequestTTY` or `RemoteCommand`, override them). Only run this when the printer is idle (home screen, no job, nothing heating):

```sh
scp -O ivibridge_X.Y.Z.tar "$PRINTER:/tmp/" &&
ssh -T -o RequestTTY=no -o RemoteCommand=none "$PRINTER" 'set -e
  d=/tmp/ivibridge_update
  rm -rf "$d" && mkdir -p "$d" &&
  tar -C "$d" -xf /tmp/ivibridge_X.Y.Z.tar &&
  cd "$d" && sha256sum -c SHA256SUMS &&
  ./ivibridge -V &&
  cp -p /userapp/ivibridge/ivibridge /userapp/ivibridge/ivibridge.bak &&
  cp -p /userapp/ivibridge/ivibridge-ram.sh /userapp/ivibridge/ivibridge-ram.sh.bak &&
  sh /userapp/ivibridge/ivibridge-ram.sh stop &&
  cp ivibridge /userapp/ivibridge/ivibridge &&
  cp ivibridge-ram.sh /userapp/ivibridge/ivibridge-ram.sh &&
  chmod 755 /userapp/ivibridge/ivibridge /userapp/ivibridge/ivibridge-ram.sh &&
  mkdir -p /userapp/ivibridge/www &&
  cp www/index.html /userapp/ivibridge/www/index.html &&
  cp www/logo.svg /userapp/ivibridge/www/logo.svg &&
  sh /userapp/ivibridge/boot.sh'
```

Then confirm `sh /userapp/ivibridge/ivibridge-ram.sh status` shows the new version, the touchscreen is back, and `http://<printer-ip>:5001/` or `http://<printer-ip>/` serves the page.

If any jobs remain in `/userdata/WifiFile/ivibridge_jobs`, move them into `/userdata/WifiFile` only after the printer is idle and no file from that folder is printing. Quote names (some have spaces). The Files tab lists those leftovers until they are moved; the touchscreen list only shows files in `/userdata/WifiFile` itself:

```sh
ssh -T -o RequestTTY=no -o RemoteCommand=none "$PRINTER" 'set -e
  P1=/userdata/WifiFile
  cur=$(cat /tmp/ivibridge/current_job 2>/dev/null || true)
  for f in "$P1/ivibridge_jobs/"*.gcode; do
    [ -f "$f" ] || continue
    [ "$f" = "$cur" ] && { echo "skip live job $f"; continue; }
    mv -f "$f" "$P1/$(basename "$f")"
  done
  rmdir "$P1/ivibridge_jobs" 2>/dev/null || true
  ls -la "$P1"'
```

To roll back to the previous package, stop the supervisor, copy the `.bak` files (or the previous tarball) back over `ivibridge` and `ivibridge-ram.sh`, and start with `boot.sh`. Jobs already moved into `/userdata/WifiFile` can stay there.

### First-time persistent install

Only after a RAM test (`scripts/ivibridge-ram.sh` from `/tmp`, nothing written to the eMMC) has already passed. `scripts/install.sh` copies the daemon and scripts to `/userapp/ivibridge/`, creates the key file if needed, backs up `/etc/init.d/rcS` as `rcS.before_bridge`, and appends one tagged hook line. It does not copy the web UI, so copy `www/` as well:

```sh
scp -O ivibridge_boot.tar "$PRINTER:/tmp/" &&
ssh "$PRINTER" 'set -e
  d=/tmp/ivibridge
  mkdir -p "$d" && tar -C "$d" -xf /tmp/ivibridge_boot.tar &&
  chmod 755 "$d/ivibridge" "$d"/*.sh &&
  cd "$d" && sha256sum -c SHA256SUMS &&
  ./ivibridge -V &&
  sh "$d/ivibridge-ram.sh" stop &&
  sh "$d/install.sh" "$d"'
```

Then copy `www/index.html` to `/userapp/ivibridge/www/` (same hash check as above) and power-cycle, or start with `sh /userapp/ivibridge/boot.sh`.

Uninstall: `sh /userapp/ivibridge/uninstall.sh`. That removes only the tagged hook line, leaves the stock `ivissh` line alone, and deletes `/userapp/ivibridge/`. Jobs and logs on `/userdata/WifiFile` are kept.

## Building and tests

On a Debian/Ubuntu host with `gcc-arm-linux-gnueabihf`:

```sh
./scripts/build.sh
```

This produces a static ARMv7 hard-float binary at `bin/ivibridge-armv7-static` (the A33 userland is soft-float glibc 2.18; a static link avoids that ABI) and a native binary at `/tmp/ivibridge_x86` for the tests.

```sh
# header comparison plus the bridge suite (native or qemu-arm)
python3 -W ignore tests/test_header.py
python3 -W ignore tests/test_ivibridge.py

# supervisor, install, and boot tests need qemu-arm and the printer's
# busybox 1.18.3 plus glibc 2.18 staged under /tmp/a33root
python3 -W ignore tests/test_supervisor.py
python3 -W ignore tests/test_install.py
python3 -W ignore tests/test_boot.py
```

`tests/run_all.sh` runs all five suites. The Orca plugin client test is skipped if `orca/plugin` is not present. A `SHA256SUMS` for a release package should list `ivibridge`, `ivibridge-ram.sh`, `www/index.html`, and `www/logo.svg`.

## Known limitations

- The board never reports fan state, so the bridge keeps its own record from every `M106`/`M107` it forwards (page, Orca, touchscreen, or job file). That record starts unknown (`null`) after every restart, until the first fan command. The page's fan button follows it. The stock touchscreen Fan toggle does not; the optional app patch `IVI-Main-Controller.fansync` (Filament page and print status page) polls `GET http://127.0.0.1:5001/api/fan` every 2 s while the page is shown and moves the toggle to match, without sending a command. While the state is unknown, the toggle keeps its stock behaviour.
- Automatic `M114` polls are hidden from the console, as described above.
- The A33 Linux tree is set up for an OV5640 on the CSI camera port, outputting YUV. There is no ffmpeg on the printer, so the on-printer camera is not used. The Camera tab takes a snapshot or MJPEG URL from a separate camera, with the snapshot view capped at 5 fps in the browser.
- `lo` is down in the stock boot. The Tailscale `boot.sh` brings it up (Tailscale's userspace forwarding to the bridge needs it), and the touchscreen fan sync relies on it to reach `127.0.0.1:5001`. Without `lo`, the sync fails silently and the toggle behaves as stock.

## See also

- [Calibration view, API, firmware math, and Z-offset display](../docs/calibration.md)
- [Native print flow (hook, Auto-start, mid-job)](../docs/native_print.md)
- [IviHook QML sources](../tools/ivi_hook/README.md)
- [rcc QML repacker](../tools/rcc_repack/README.md)

## License

Original work here is under the same [CC BY-NC-SA 4.0](../LICENSE) license as the rest of this repository.
