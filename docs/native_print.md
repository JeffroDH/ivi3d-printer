# Native print flow

How a job started from ivibridge (the web UI, Orca, or `ivi-control.sh`)
reaches the stock touchscreen app and the STM32. This is the current
path. The older network stream (`IVIB_NET_STREAM=1`) is tests and debug
only.

## Pieces

- **ivibridge** on the A33 owns `/dev/ivi-stm32` (the real STM32 serial
  node) and gives the stock app a pty in place of `/dev/ttyUSB0`.
- **IviHook.qml**, packed into `IVI-Main-Controller` with the
  [rcc repacker](../tools/rcc_repack/README.md), is a child of the main
  QML `Window`. It polls `http://127.0.0.1:5001` (the printer's loopback;
  `lo` must be up).
- Job files live in `/userdata/WifiFile`, the same folder the
  touchscreen Wi-Fi file list shows.

## Start a job

1. The client uploads a G-code file (`print=true`). ivibridge stores it
   under `/userdata/WifiFile` (after a header check and a pre-scan that
   rejects embedded job-control words and laser `M3`/`M4` at `S>100`).
2. The daemon writes `/tmp/ivibridge/print_request`. It does not start a
   network G-code stream and does not show the stock `WORKING_PC` lock
   page.
3. IviHook picks up the request (`/api/ivi/r` / `/api/ivi/a`), checks
   that the printer is not already printing, the tool head is present,
   the path is under `/userdata/WifiFile`, and calibration is not
   running.
4. It points the stock app at that file (`setSelectFileFullName`) and
   opens `StatusPageNew.qml`.
5. **Auto-start** (persistent setting, default off) comes from the
   request. When it is off, the user confirms the plate warning and taps
   RUN on the screen, the same as a file started from the touchscreen.
   When it is on, the hook skips that dialog and calls the stock RUN
   path (`goOrigin` if needed, then `startPrinting`).
6. The STM32 then receives the job from the app over the pty, as it
   would for any touchscreen start. ivibridge passes that traffic
   through.

## Mid-job

While a touchscreen (or hook-started) job is running, the API can pause,
resume, cancel, and adjust temperature, speed, flow, and Z-offset
through the same request route. Manual moves, homing, and arbitrary
console G-code stay blocked until the job ends.

Z-offset mid-print is `M290`. “Save Z offset permanently” queues
`M665 H` + `M500` until the printer is idle and does not change the
displayed offset. See [calibration.md](calibration.md).

## Locks

- A calibration run (`/api/ivi/cal`) refuses to start while a print or
  touchscreen job is in progress. While calibration is running, other
  bridge / Orca commands that would move the machine are refused, and
  the hook acks a new print start as busy (`pc`).
- The hook is not created with `Component.createObject` from
  `BusyWindow`, because that window's `root.destroy()` after self-test
  would delete it.

## Sources

- Hook and overlay QML: [tools/ivi_hook/](../tools/ivi_hook/README.md)
- Packer: [tools/rcc_repack/](../tools/rcc_repack/README.md)
- Bridge daemon and web UI: [a33_bridge/README.md](../a33_bridge/README.md)
