# A33 ivibridge changelog

Versions are tagged `X.Y.Z-a33`. This log covers the on-printer daemon only, not the Mac/PC bridge in `bridge/`.

## 0.1.7-a33

- Automatic position checks (`M114` with `"quiet": true`) are kept out of the console view. A check typed in the console still appears. Quiet applies only to `M114`.
- The Toolhead tab polls immediately after a jog or Home, and otherwise about every 10 seconds (was every 3 seconds whenever the tab was visible).
- 14 px gap between the jog pad and the Home button.
- `/api/printer` tracks fan state (`ivi.fan`, `ivi.fans`) from fan commands seen on the page, the touchscreen, or a print file. The page fan button follows that state. The touchscreen toggle still does not, as noted in the README.

## 0.1.6-a33

- Port of the Mac bridge web UI to the printer page: Toolhead, Filament, Camera, Files, and Console.
- File list with thumbnails, estimated time and filament, delete, print-from-file, and a manual queue (`/api/ivi/files`, `/api/ivi/queue`, thumbnail routes).
- Camera tab takes a snapshot or MJPEG URL from a separate camera. Snapshot view refreshes at 5 frames/sec in the browser. The printer's OV5640 is not used.

## 0.1.5-a33

- LAN trust: clients on `10/8`, `172.16/12`, and `192.168/16` may use the API and the Device tab without an API key. Loopback and Tailscale `100.x` still need the key. Controls remain disabled when no apikey file is present.

## 0.1.4-a33

- Fixes for the API key entry on the status page so a typed or pasted key is saved in the browser and sent on later requests. The key is not written into the page DOM.

## 0.1.3-a33

- **Hot-restart fix.** 0.1.2 could leave the touchscreen app down after a stop/start: `stop` restarted the app, that process then exited, and the next `start` did not launch it again. `stop` now writes `/tmp/ivibridge/needs_app`. `start` relaunches the app when that marker is present or when uptime is at least 90 seconds, and still leaves the app to `autorun.sh` during early boot.
- Status page API key box: prompt, Save, Forget key, and storage of the key in `localStorage` (`ivi.apikey`). The page itself is served without authentication and never includes the server key.

## 0.1.2-a33

- Adds the IVI file header on upload (`src/ivi_header.c`, also `ivibridge --add-header`), matching the Mac bridge's `prepare_gcode`. Already-headered files are left unchanged.

## 0.1.1-a33

Fixes found in the first hardware RAM run (0.1.0) and in the offline harness, plus the start-at-boot package:

- Wait for `Resume complete` before sending the next job line; a numbered line sent earlier is dropped by the firmware with no reply.
- Stall recovery: after the stall window, one unnumbered `M105` probe; a dropped line is resent with the same `N`. A late `ok` before the probe's `ok T:` is treated as the line's own acknowledgement and is not resent.
- Cancel is never blocked: an outstanding wait is abandoned after 1.5 s and `M2411 S3` is sent. The lock-page Disconnect path does the same.
- Supervisor `status` no longer hangs: it does not open a connection, because the printer's loopback interface is down.
- `M5` is sent in the cooldown only when the reported head is a laser. Console `M106`/`M107` accept `P0`/`P1`.
- HTTP upload body no longer drops a byte when headers and the start of a large body arrive in one read.
- Fair turn-taking so a chatty app cannot starve the network side (250 ms claim; queued console commands go out as one burst).
- `TIOCNXCL` on exit and periodically on the pty, so a later open is not stuck with `EBUSY`.
- SIGTERM during a job stops the job and cools down before exit.
- Persistent start-at-boot: one tagged hook in `/etc/init.d/rcS` (the `ivissh` line and `autorun.sh` are left untouched), `boot.sh` waits for `/dev/ttyUSB0` before starting the bridge, boot-fail counter, off switches (`disable` files and USB `no-bridge`), and job/log persistence under `/userdata/WifiFile` once that partition is mounted.
