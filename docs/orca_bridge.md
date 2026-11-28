# Orca Slicer and the printer

Orca Slicer connects to the printer as an **OctoPrint** host. Two services can answer, and they can be used side by side.

| | On-printer ivibridge (primary) | Computer-side bridge (optional) |
|---|---|---|
| Runs on | The printer's A33 board | A Mac, Linux, or Windows computer |
| Orca host | `http://<printer-ip>:5001` (port 80 also answers) | `127.0.0.1:5001` on the computer |
| Upload and Print | Stores the file on the printer and starts it through the touchscreen hook (assist mode, or Auto-start). No cable and no computer needs to stay awake | Streams the job over USB-C from the computer, which must stay awake and connected |
| Upload | Same as Upload and Print without starting it | Stores the file over Wi-Fi; start it on the touchscreen |
| Docs | [a33_bridge/README.md](../a33_bridge/README.md), [native_print.md](native_print.md) | [bridge/README.md](../bridge/README.md) |

## Connect Orca to the printer (on-printer ivibridge)

1. Install the printer profile: [orca/README.md](../orca/README.md) (File → Import → Import Configs…, `IVI3D.orca_printer`). It is a delta with a 210 mm circular bed.
2. Printer settings → Connection: host type **OctoPrint**, host `<printer-ip>:5001` (use the printer's own address). On an RFC 1918 LAN the Device tab works without an API key. From a Tailscale `100.x` address or any other non-LAN client, enter the key stored at `/userapp/ivibridge/apikey` on the printer.
3. Slice, then **Upload and Print**. The Status page opens on the touchscreen: confirm the plate and tap RUN (or turn Auto-start on in the web UI to skip that dialog). Pause, resume, cancel, temperature, speed, flow, fan, and Z-offset work from the Device tab or the web page while the job runs; moves and homing are refused until it ends.
4. The web page at `http://<printer-ip>:5001/` (or port 80) shows Status and Adjust while printing, the file list and queue, and the Calibration view.

## Start G-code and leveling

Whether a saved bed mesh is used is decided by the job's start G-code, not by Orca. On stock Marlin V1.3.2-alpha the touchscreen app never sends `M420 S1`, and `G28` turns bed leveling off. A mesh is applied to a job only if the start G-code sends `M420 S1` after the `G28`. Leveling itself (G29, optionally with a heated bed) runs from the Calibration view, not from the console and not from G-code the bridge forwards. Details: [calibration.md](calibration.md#leveling-and-start-g-code).

`M106 S0` without `P` turns both head fans on on this firmware, and both Orca and IVI 3licer emit it to mean "fan off". Use `M107` or `M106 P0 S0` for an FDM head ([stm32.md](stm32.md#fans)).

## Anycubic Slicer Next

Slicer Next is an Orca fork whose printer connection is built around Anycubic's own cloud and LAN printers. It does not reliably expose the generic OctoPrint print-host option, and its Remote Print skips post-processing scripts. Paths that work with the computer-side bridge are a post-processing script on export, or a watch folder: [bridge/README.md](../bridge/README.md#anycubic-slicer-next). Use a custom (non-Anycubic) printer profile with the IVI delta geometry.

## Other Orca-side pieces

- The profile bundle, its sourced and assumed values, and the optional IVI header hook: [orca/README.md](../orca/README.md).
- The Orca Python plugin (an **IVI3D Bridge** tab and an automatic IVI header): [orca/plugin/README.md](../orca/plugin/README.md). It talks to the computer-side bridge API.
- Laser and CNC jobs from Fusion: [fusion/README.md](../fusion/README.md) and [laser_cnc_gcode.md](laser_cnc_gcode.md).

## Related

[wifi_touch.md](wifi_touch.md) · [network.md](network.md) · [calibration.md](calibration.md) · [slicer_report.md](slicer_report.md)
