# A33 ivibridge changelog

Versions are tagged `X.Y.Z-a33`. This log covers the on-printer daemon only, not the Mac/PC bridge in `bridge/`.

## 0.1.19-a33

Print-time Status and Adjust, a round-bed mesh map, heated leveling, and a
console that says why it is unavailable.

  • **Status / Adjust while printing.** During any print (a bridge job, a
    touchscreen job, or a firmware `WORKING_*` status) the Toolhead and
    Filament boxes become **Status** (progress ring, elapsed and remaining
    time, layer and Z, nozzle and bed temperatures, file, Pause / Resume /
    Stop / Clear) and **Adjust** (nozzle and bed targets, Z offset in
    0.01 / 0.02 / 0.05 mm `M290` babysteps, speed `M220`, flow `M221`, fan,
    Save Z offset permanently). The normal boxes return when the print
    ends. `GET /api/printer` adds `ivi.print`
    (`active`, `source`, `paused`, `file`, `speed`, `flow`, `layer`, `z`).
  • **Motion lock.** While a print is active the binary refuses jog, home,
    extrude / retract, and other moving or non-status console commands
    (HTTP 409); only temperature, fan, speed, flow, `M290`, `M105`, and
    `M114` are accepted. Pause / Resume / Stop stay available.
  • Adjust and console commands queued during a bridge job are now sent
    between job lines instead of after the job finished.
  • Touchscreen jobs: fan on/off goes through the hook
    (`sendSetFanOnCMD` / `sendSetFanOffCMD`, request `cmd=fan`). It needs the
    0.1.19 touchscreen app; with an older app the request times out and
    says so.
  • **Round mesh map.** The Auto-level card draws the 7×7 mesh over the
    210 mm print circle with the firmware's bilinear interpolation (grid
    origin (−105, −105), 35 mm spacing, I = X from the left, J = Y from the
    front). Everything outside r = 105 mm is dimmed and the grid points
    outside the circle are drawn hollow (extrapolated). Hover or tap reads
    a value. Rendered client-side, only when the mesh changes.
  • **Heated leveling.** `POST /api/ivi/cal/start {"action":"level","bed":60}`
    heats the bed (40–80 °C, clamped; `true` means 60; absent or 0 is the
    plain cold flow; `bed` is only valid with `level`). Order: build plate
    prompt, home and move up, attach-probe prompt, `M119` probe check,
    `M140 S<t>`, wait until the bed is within 1 °C of the target (20 minute
    limit), `G29`, `M500`, `M503`, `M140 S0`, move up, remove-probe prompt.
    Cancel and any failure also send `M140 S0`. `G29` is not on the console
    allow-list.
  • **Probe gate is the nozzle only.** Every probe flow (XYZ, level, Run all)
    waits for the nozzle actual to be 40 °C or below, as the stock
    `checkTempForWizard` does; the bed temperature no longer matters.
  • `GET /api/ivi/cal` (and `ivi.cal` in `/api/printer`) adds `bed_target`,
    `bed`, and `nozzle` next to the existing `level.grid`.
  • **Console.** A reason line under Send says why the console is off or
    limited: link down, a calibration step waiting (with an Open Calibration
    button), a touchscreen job, or a running print. Refusals from the bridge
    (409 / 400) are shown in the console, including when sent with Enter.
  • **Touchscreen Adjust screen.** The current Z adjustment for this print is
    shown under the “Z offset distance (mm)” label (`Current: −0.03 mm`); the
    text that overlapped the nozzle − / + buttons is gone.

## 0.1.18-a33

www layout (Calibration as its own top-bar view, Z Offset card on the right,
independent stacking columns) plus:

  • Paper-test jog accepts ±5 mm in addition to ±1, ±0.1, ±0.05, and ±0.01.
    `/api/ivi/cal/jog` on 0.1.17 rejected 5 mm (HTTP 400). The allow list and
    the error string were updated; the firmware move is still G91 / G1 Z{dz}
    F500 / G90 / M114.
  • Toolhead Pause / Resume / Stop / Clear sit under the jog pad as a 2×2
    of Home-styled pills. Calibration paper-test buttons include a +5 / −5
    column first.

Leave Auto-start and the touchscreen app unchanged.

## 0.1.17-a33

- Adds a Calibration tab (own tab on a phone, full-width row on a wide screen) with XYZ (G33), auto-level (G29), and the Z-offset paper test, plus Run all. Flows match the stock prompts: cool below 40 °C, confirm the build plate, home and move to Z100, attach the probe and check M119, then run the command and move back up to remove it. XYZ always continues into leveling because G33 wipes the 7×7 mesh. Run all keeps the probe on between those two, then removes it for the paper test. M500 is sent only after “Calibration OK”, a complete “Bilinear Leveling Grid:”, or a paper-test Save (`new_H = H − Z`, then M665 H + M500 + M211 S1). Failures, timeouts, and Cancel never save. After a successful XYZ or paper-test save the Z-offset reference is reset so the display reads 0.00. The 7×7 bilinear grid is a firmware limit; the tab does not offer a denser mesh.
- API: `GET /api/ivi/cal` and `POST /api/ivi/cal/start` (or `/confirm`, `/cancel`, `/jog`, `/save`). `GET /api/printer` includes `ivi.cal`. Last-run times are stored in the settings file. Other bridge and Orca commands are locked while a calibration runs, and calibration is locked during a print.

## 0.1.16-a33

- The Toolhead Z-offset readout is a normal offset: displayed offset = reference H − effective H (stored H minus this-print babystep). It is 0.00 right after calibration or after “Set current as zero”, + when the nozzle is higher than that reference, and − when closer. The first M503 after install (or when no reference is stored) sets the reference to the current stored height and persists it in `/userapp/ivibridge/settings` as `ref_h=`. A stock paper-test calibration (an M665 H that is not our own save) resets the reference to the new height. Saving a live adjustment still writes `M665`+`M500` when idle but does not change the reference, so the displayed offset stays the same. `POST /api/ivi/zoffset/zero` (or `POST /api/ivi/settings` with `set_zero`) sets the reference to the current effective height.

## 0.1.15-a33

- Auto-start is a persistent bridge setting (default off), toggled from the web UI or `GET`/`POST /api/ivi/settings`. When it is on, Upload and Print skips the plate-warning dialog and runs the stock RUN path (`getGoOrignStatus` / `goOrigin` / `startPrinting`); the hook acks `started`. When it is off, behaviour is unchanged (ack `opened`, user taps OK then RUN). The flag is written into `print_request` as `autostart=0|1`. Settings are stored at `/userapp/ivibridge/settings` (or `$IVIB_DIR/settings`).
- The Toolhead tab and `GET /api/printer` (`ivi.zoffset`) show the stored calibration height (M665 H, the stock paper-test value, not M851), the live M290 babystep accumulated this print, and the effective height `H − babystep`. `POST /api/ivi/zoffset/save` queues a permanent save: mid-print `M665` is not applied; when the printer is idle the daemon sends `M665 H` + `M500`, then a cancelling `M290` so leftover babysteps do not stack. `M665` and `M500` stay off the user console allowlist. Loopback `GET /api/ivi/settings` needs no API key so the hook can read the stored height.

## 0.1.14-a33

- During a touchscreen job, `M290` Z-offset (babystep) uses the same request route as temperature, speed, and flow, so the app can call `zfinetunePlus` / `zfinetuneMinus` instead of the bridge injecting onto the serial link. Only +/-0.01, +/-0.02, and +/-0.05 mm are accepted, matching the patched Adjust-screen steps. `M851` stays refused.
- The Toolhead tab adds a Z Offset control (0.01 / 0.02 / 0.05 mm, Z+ / Z-).
- Loopback `GET /api/ivi/r` (the QML hook poll) is logged once, then at most every 30 s, as `qml hook poll n=…`, so a missing hook is visible in `ivibridge.log` without reading the UART.

## 0.1.13-a33

- `print=true` (and the other API start paths) no longer start a network stream and no longer rewrite the firmware status to `WORKING_PC`. The file is stored in `/userdata/WifiFile` and a start request is written to `/tmp/ivibridge/print_request` for the touchscreen app patch to open StatusPageNew plus the stock plate warning. The user taps Start on the screen (phase 1 assist mode). Unattended auto-start is a disabled flag in the app patch, not enabled here.
- The HTTP start call waits up to 8 s for the app to ack. A timeout or refusal still keeps the uploaded file and returns `effectivePrint: false`. A start is refused if a network job, a touchscreen job, a WORKING_* report, or another pending/open start is already active.
- While a touchscreen job (or an assist-mode page) is active, API pause/resume/cancel and nozzle/bed/speed/flow changes go through the same request route so the app can run its own handlers (`isPause`, `stopPrinting`, `setTargetTemperature`, `setBedTargetTemperature`, `setWorkSpeed`, `setFlowrate`). Manual moves, homing, and arbitrary console G-code stay blocked. The bridge does not inject M104/M140/M220/M221 onto the serial link during a screen job, which would desync the app's Sender.
- `GET /api/ivi/r` (alias `/api/ivi/request`) and `GET /api/ivi/a` (alias `/api/ivi/request/ack`) are the loopback poll/ack endpoints the app uses, same idea as `GET /api/fan`.
- `IVIB_NET_STREAM=1` restores the old stream/`WORKING_PC` start path for tests and debug only. It is not used on the printer.

## 0.1.12-a33

- Persistent uploads now go to `/userdata/WifiFile`, the folder the touchscreen Wi-Fi file list shows, instead of `/userdata/WifiFile/ivibridge_jobs`. Logs stay in `ivibridge_logs/`. Upload and migrate temps stay hidden as dotfiles.
- The Files tab and `/api/ivi/files` list `.gcode` files in that folder, plus any leftover jobs still in `ivibridge_jobs`, and skip logs, `tmp_files`, and other non-job entries.
- Existing jobs left in `ivibridge_jobs` need a one-time move into `/userdata/WifiFile` before they appear on the touchscreen. Do that only while the printer is idle.

## 0.1.11-a33

- New `GET /api/fan`: fan state only, as `{"on":true|false|null,"fan":0-100|null,"fans":[P0,P1]}` (percent, the same record as `ivi.fan` / `ivi.fans` in `/api/printer`; `on` is true when either fan is above 0, and everything is `null` until a fan command has been seen since the daemon started). It needs no API key from any address, including loopback, because it is read-only and reports nothing else. Other methods on the path still need the key. Responses are `Cache-Control: no-store`.
- This is what the optional touchscreen app patch (`IVI-Main-Controller.fansync`) polls from `127.0.0.1:5001` so the Fan toggle follows the fan, whoever changed it.

## 0.1.10-a33

- The daemon also listens on port 80, with the same page, API, and auth rules as 5001, so the printer can be opened as `http://<address>/` with no port. 5001 stays the main port and is what Orca should use. If port 80 cannot be bound, the daemon logs that and keeps serving on 5001. `status` reports both ports.

## 0.1.9-a33

- On a phone-sized portrait view, the tab bar stays fixed at the bottom of the screen (taller touch targets, with room for the iOS home indicator) so it no longer moves with the content. Landscape and desktop are unchanged.
- Opening the page from the iPhone home screen now shows the Toolhead tab immediately. The earlier blank view was caused by an unquoted `class=panel on` in the HTML, which browsers read as class `panel` only, so no panel was visible until a tab was tapped.
- The status page header shows the IVI logo mark, the same mark the Mac/PC bridge uses for its home-screen icon, served at `/logo.svg` without an API key.

## 0.1.8-a33

- The status page now serves the same home-screen and favicon icons as the Mac/PC bridge, plus the web app manifest, without an API key.

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
