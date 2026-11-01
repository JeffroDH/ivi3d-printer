# ivi-bridge — Orca Slicer / Anycubic Slicer Next → IVI3D

A small local Python service that looks like an **OctoPrint** server to the slicer and forwards jobs to the IVI3D.

| Mode | Transport | What happens |
|---|---|---|
| `wifi` (default) | kore API `:8080` | `connect` → `upload` (201) → `disconnect`. **Start the job on the touch screen** — `start_print` is 404 on firmware V1.3.2-alpha. Future/custom firmware may enable Wi-Fi start. |
| `serial` | USB-C, 115200 | `M2411 S2` (+`M1001 L` only if fw ≥ 2.4.0) → wait for `PC start work` → stream G-code per `ok`. Pause `M2410`, resume `M2411 S1`, cancel = stop streaming + heaters off. Progress at `/api/job`. **Only one program can own the port — disconnect IVI 3licer.** The Mac must stay awake for the whole print. |

## Install (macOS)
```sh
python3 -m pip install --user pyserial          # only needed for serial mode
mkdir -p ~/.config/ivi-bridge
cp bridge/config.example.json ~/.config/ivi-bridge/config.json   # set printer_token, api_key, mode
python3 bridge/ivi_bridge.py serve               # http://127.0.0.1:5000
```
The token can also come from `IVI_PRINTER_TOKEN`. Never commit your config. To run at login, adapt `com.ivi3d.bridge.plist.example` into `~/Library/LaunchAgents/`. Allow Python under **System Settings → Privacy & Security → Local Network** (else "No route to host").

## Orca Slicer
1. Printer settings → Basic information → enable **Use 3rd-party print host** (or the Wi-Fi/network icon next to the printer).
2. Host type **OctoPrint**, Hostname/IP `127.0.0.1:5000`, API key = `api_key` from the config → **Test**.
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

## CLI
`ivi_bridge.py [--config F] [--mode wifi|serial] serve | send FILE | postprocess FILE | watch DIR`
`send`/`postprocess`/`watch` hand the file to the running service if it is up (required for serial, since streaming outlasts the slicer hook), else upload directly over Wi-Fi.

## Tests
`python3 -m unittest discover -s bridge/tests -v` — fake serial printer and fake kore HTTP printer; nothing touches real hardware.

## Not yet verified on hardware
Whole bridge (written 2026-11-01, unit-tested only); Orca/Next host test against it; serial cancel (no verified stop code — heaters off and stream halts, the printer may need the touch screen to exit PC mode); laser/CNC jobs.
