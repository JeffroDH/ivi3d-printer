# A33 ivibridge — on-printer Wi-Fi control

`ivibridge` is a static C daemon that runs on the IVI 3D printer's Allwinner A33 (Linux 3.4). It owns the real STM32 serial link, gives the stock touchscreen app a pty in place of `/dev/ttyUSB0`, and serves an OctoPrint-compatible HTTP API plus a web UI on TCP port 5001.

This is not the Mac/PC bridge in [`../bridge/`](../bridge/README.md). That program runs on a computer and streams jobs over USB serial. This daemon runs on the printer, so Orca Slicer can print and monitor over the LAN with no cable and no computer in the middle.

The current version is **0.1.7-a33**. Built binaries and install tarballs are not in this folder; build them with `scripts/build.sh`.

## Architecture

The real CH340 node (`/dev/ttyUSB0`, 115200 8N1) is recreated as `/dev/ivi-stm32` on devtmpfs. The daemon opens that node exclusively and atomically replaces `/dev/ttyUSB0` with a symlink to a pty. The touchscreen app keeps talking to `/dev/ttyUSB0` and does not need to be patched.

The daemon passes the app's traffic through byte for byte and takes turns on the wire. Replies meant for a network command are kept away from the app, because the app treats any line containing `ok` as an acknowledgement. While a network job runs, the firmware status shown to the app is rewritten to `WORKING_PC` so the stock lock page appears. The lock page's Disconnect button (`M108` + `M2001 S1`) is intercepted and turned into a graceful cancel.

Network jobs are streamed with Marlin line numbers, checksums, and resend support. Pause, resume, and cancel use the firmware job words (`M2410`, `M2411 S1`/`S3`/`S4`). Resume waits for `Finish pause` / `Resume complete` before the next job line. A stalled line is probed with `M105` and, if it was dropped, resent with the same `N` so a motion line cannot run twice. The daemon never sends `M3` or `M4`. `M5` is included in the cooldown only when the last head report was a laser.

Uploaded jobs start in `/tmp/ivi_jobs`. Once the internal FAT partition is mounted at `/userdata/WifiFile`, new uploads go to `/userdata/WifiFile/ivibridge_jobs` and earlier RAM copies are moved after a size and SHA-256 check. A file that is currently printing is not moved until the job ends. Logs start in `/tmp/ivibridge/` and are also mirrored to `/userdata/WifiFile/ivibridge_logs/` (rotated at 2 × 1 MB each). Uploads are pre-scanned: embedded job-control words and `M3`/`M4` at `S>100` are rejected. Files that do not already have an IVI header get one on upload (`src/ivi_header.c`; also available as `ivibridge --add-header`).

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
- The console allowlist matches the Mac bridge, except `M3`/`M4` are refused entirely. Temperatures, axis moves, and fans (`M106`/`M107` with optional `P0`/`P1` and `S0–255`) are range-limited. During a job only `M104`, `M140`, `M220`, `M221`, `M106`, `M107`, `M105`, and `M114` are allowed.
- Do not commit or publish the apikey file, SSH keys, Wi-Fi credentials, password hashes, or the printer serial.

## HTTP API (port 5001)

Compatible with Orca's OctoPrint connection and with the repo's Orca plugin client.

| Method | Path | Role |
|---|---|---|
| GET | `/` | Web UI (`www/index.html`) |
| GET | `/api/version`, `/api/server` | OctoPrint version stubs |
| GET | `/api/printer` | Temperatures, state, position, `ivi.head`, `ivi.fan` / `ivi.fans` (percent, once a fan command has been seen) |
| GET | `/api/job` | Active job, progress, resend/stall/lost-line counts |
| GET | `/api/files`, `/api/files/local`, `/api/ivi/files` | Stored jobs (size, mtime, time, filament, thumbnail flag) and the print queue |
| GET | `/api/ivi/files/thumb?name=…`, `/api/files/local/<name>/thumbnail` | Thumbnail extracted from the G-code comments |
| GET | `/api/ivi/console?since=` | Console ring (see quiet M114 below) |
| GET | `/api/ivi/link` | Link state and daemon version |
| POST | `/api/files/local`, `/api/files/sdcard` | Multipart upload; `print=true` starts the job |
| POST | `/api/files/local/<name>` | OctoPrint `select` / `print` of a stored file |
| POST | `/api/ivi/files`, `/api/ivi/queue` | Queue, print, delete, start-next, clear queue |
| DELETE | `/api/files/local/<name>` | Delete a stored job (refused while that file is printing) |
| POST | `/api/job` | `start`, `pause` (`pause` / `resume` / `toggle`), `cancel` |
| POST | `/api/printer/command`, `/api/printer/tool`, `/api/printer/bed`, `/api/printer/printhead` | Allowlisted commands, hotend/bed targets, flow, feedrate |
| POST | `/api/ivi/clear` | Orca plugin "clear stale job" |

A touchscreen print makes the API read-only: network start, uploads that print, console commands, and job control return 409 until it finishes.

## Web UI

The page is a port of the Mac bridge UI, served from `www/index.html`.

- **Toolhead:** temperatures, feedrate and flow, fan toggle, jog, Home (with a 14 px gap under the jog pad), and a position bar.
- **Filament:** load and unload wizard.
- **Camera:** snapshot or MJPEG URL from a *separate* camera. Snapshot view refreshes at 5 frames/sec in the browser, not on the printer.
- **Files:** list of jobs stored on the printer, thumbnails, print, delete, and a manual queue (a queued job never starts on its own).
- **Console:** allowlisted G-code, plus a few built-in preset buttons (preheat PLA/PETG, cooldown, park, load/unload).

Automatic position checks (`M114`) are sent only while the Toolhead tab is visible: immediately after a jog or Home, and otherwise about every 10 seconds. Those automatic checks are posted with `"quiet": true` and are kept out of the console view. A check you type yourself still appears.

Intentionally omitted from this port: print history, timelapse, toolpath preview, a temperature graph, user-saved macros, and the printer's own camera.

## Orca Slicer

1. Printer settings → Connection: host type **OctoPrint**.
2. Host is the printer on port 5001, for example `http://192.168.50.85:5001` on a typical LAN. Use your printer's own address.
3. On a RFC 1918 LAN the Device tab works without pasting an API key (LAN trust). From a Tailscale `100.x` address, or any other non-LAN client, enter the key from `/userapp/ivibridge/apikey` on the printer.

## Install and rollback

These steps write to the A33's eMMC (`/userapp/ivibridge` on the rootfs). Only run them when the printer is idle (home screen, no job, nothing heating). Use `&&` between the steps so a failed check stops the rest. Verify hashes against the package `SHA256SUMS` and check that `-V` prints the version you expect before replacing files. Keep the previous package so you can roll back.

### Update an existing install

The package tarball contains `ivibridge`, `www/index.html`, and `SHA256SUMS`. From the directory that holds it, with `PRINTER` set to the printer's SSH host:

```sh
scp -O ivibridge_X.Y.Z.tar "$PRINTER:/tmp/" &&
ssh "$PRINTER" 'set -e
  d=/tmp/ivibridge_update
  rm -rf "$d" && mkdir -p "$d" &&
  tar -C "$d" -xf /tmp/ivibridge_X.Y.Z.tar &&
  cd "$d" && sha256sum -c SHA256SUMS &&
  ./ivibridge -V &&
  sh /userapp/ivibridge/ivibridge-ram.sh stop &&
  cp ivibridge /userapp/ivibridge/ivibridge &&
  chmod 755 /userapp/ivibridge/ivibridge &&
  mkdir -p /userapp/ivibridge/www &&
  cp www/index.html /userapp/ivibridge/www/index.html &&
  sh /userapp/ivibridge/boot.sh'
```

Then confirm `sh /userapp/ivibridge/ivibridge-ram.sh status` shows the new version, the touchscreen is back, and `http://<printer-ip>:5001/` serves the page.

To roll back, run the same commands with the previous package tarball.

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

`tests/run_all.sh` runs all five suites. The Orca plugin client test is skipped if `orca/plugin` is not present. A `SHA256SUMS` for a release package should list `ivibridge` and `www/index.html`.

## Known limitations

- The touchscreen fan toggle does not follow fan changes made from the page, Orca, or a network job. The board never reports fan state, and the stock app only remembers its own button presses (and fan commands in files it is printing). The page's fan button does follow fan commands from either side, once the first command has been seen after a restart. Fixing the touchscreen toggle would mean patching the Qt app; that is not done here.
- Automatic `M114` polls are hidden from the console, as described above.
- The A33 Linux tree is set up for an OV5640 on the CSI camera port, outputting YUV. There is no ffmpeg on the printer, so the on-printer camera is not used. The Camera tab takes a snapshot or MJPEG URL from a separate camera, with the snapshot view capped at 5 fps in the browser.
- `lo` is down on the printer; nothing on the board can use `127.0.0.1`.

## License

Original work here is under the same [CC BY-NC-SA 4.0](../LICENSE) license as the rest of this repository.
