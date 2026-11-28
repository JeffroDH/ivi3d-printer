# Touch-app hook sources (IviHook)

QML overlay used to pack a native-print hook into the stock
`IVI-Main-Controller` app. These are sources only; packed app binaries
are not stored here.

| File | Role |
|---|---|
| `qml/IviHook.qml` | Always-live poller. Declared as a child of the main `Window`. Talks to ivibridge at `http://127.0.0.1:5001`. Starts jobs through the stock Status page / RUN path, and handles mid-job pause, resume, cancel, temperature, speed, flow, fan on/off, and Z-offset requests. Honours Auto-start from the request (default off). Refuses a new start while calibration is running. |
| `qml/main.qml` | Stock main window with `IviHook { id: iviBridgeHook }` declared as a child, so a later `BusyWindow` `root.destroy()` cannot delete it. |
| `qml/ControlPageInPrinting.qml` | In-print Adjust page, including Z-offset jog steps. Shows the current Z adjustment for the print (`Current: ±0.00 mm`) under the “Z offset distance (mm)” label. |

Build a new app binary with [../rcc_repack/README.md](../rcc_repack/README.md),
always from the fansync / stock baseline, never from a previously packed
output.

The end-to-end request flow is documented in
[docs/native_print.md](../../docs/native_print.md).
