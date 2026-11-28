# Calibration and Z-offset

Current behaviour of the on-printer ivibridge Calibration view and the
stock Marlin V1.3.2-alpha firmware on this machine. Firmware changes are
out of scope; the numbers below were verified against the STM32 dump and
live runs.

## Web UI

On a large screen, Calibration is its own view, opened by a **Calibration**
button in the top bar (State / File / Progress / Link). **Back to control**
returns to the main two-column page. On a phone the same top-bar button
opens the view; the bottom tab bar stays for Toolhead, Filament, Camera,
Files, and Console.

The view has three cards plus **Run all**:

- **XYZ (G33)** — always continues into leveling.
- **Auto-level (G29)** — the firmware's 7×7 bilinear mesh, drawn over the 210 mm print circle, with an optional **Heat the bed first** setting (40–80 °C, default 60).
- **Z-offset paper test** — probe off. Jog, then save or cancel.

**Run all** is G33, then G29 (probe stays on between them), then the
paper test. Settings are saved with `M500` only after a successful
step, never on cancel or failure.

The probe is a clip-on sensor that attaches to the nozzle. It is only
on the toolhead during G33 and G29, which is why the flow has attach and
remove prompts, and why the nozzle (not the bed) has to be cool for them.

## Round-bed mesh map

The firmware mesh is a 7×7 grid with its origin at (−105, −105) and 35 mm
spacing (I = X from the left, J = Y from the front). The Auto-level card
draws it over the 210 mm round print area, interpolated bilinearly the
way the firmware applies it. Everything outside r = 105 mm is dimmed, and
the 20 grid points that lie outside the circle are drawn hollow because
their values are extrapolated. The 29 points inside are filled. Hover or
tap the map to read a value at that spot. The map is drawn in the browser
and only redrawn when the mesh changes. The mesh itself comes from
`GET /api/ivi/cal` as `level.grid[j][i]`.

## Heated leveling

`POST /api/ivi/cal/start {"action":"level","bed":60}` levels with the bed
hot, so the mesh matches the surface at print temperature. `bed` is
clamped to 40–80 °C (`true` means 60). Without `bed` (or with 0) the flow
is the plain cold one. `bed` is rejected with any other action.

Order: confirm the build plate, home and move up, attach-probe prompt,
`M119` probe check, `M140 S<t>`, wait until the bed is within 1 °C of the
target (20 minute limit, then the run fails), `G29`, `M500`, `M503`,
`M140 S0`, move up, remove-probe prompt. Cancel and any failure send
`M140 S0`; nothing sends it before `G29`. `G29` is not on the console
allow-list.

While the bed heats, `GET /api/ivi/cal` reports `phase` `heat_bed`,
`bed_target`, and the live `bed` and `nozzle` temperatures.

### Temperature gate

Attaching or removing the probe needs the **nozzle** actual temperature
at 40 °C or below. The bed is not checked. This matches the stock
`checkTempForWizard`, which looks at the nozzle only. It applies to every
probe flow (XYZ, level, Run all), so a warm bed no longer holds up a
cold-bed run either.

## API

| Method | Path | Body |
|---|---|---|
| GET | `/api/ivi/cal` | — (also present as `ivi.cal` on `GET /api/printer`) |
| POST | `/api/ivi/cal/start` | `{action: "xyz"\|"level"\|"paper"\|"all", bed?: 40..80}` |
| POST | `/api/ivi/cal/confirm` | `{action: "confirm"}` |
| POST | `/api/ivi/cal/cancel` | `{action: "cancel"}` |
| POST | `/api/ivi/cal/jog` | `{dz: <mm>}` |
| POST | `/api/ivi/cal/save` | `{action: "save"}` |

Paper-test jog steps accepted: ±5, ±1, ±0.1, ±0.05, ±0.01 mm. Other values return HTTP 400.

`start` also takes an optional `bed` (°C) with `action: "level"`; see Heated leveling below.

Human prompts (build plate, attach probe, remove probe, paper jog) are
confirmed on the Calibration view. The bridge does not confirm them on
its own.

## Firmware math

**G33** (default `P=4`) solves endstop trim (`M666`), delta height H,
radius R, and tower angle trim (`M665`). It does not change the probe
offset (`M851`). It calls `reset_bed_level`, so a successful G33 always
continues into G29. Typical run is about 15 minutes, with a home at
each iteration. Success is the line `Calibration OK`. Failure lines
include `No convergence` and `Probing Failed`. The firmware does not
write EEPROM itself.

**G29** is bilinear and fixed at 7×7 (no grid-size `P`). The EEPROM mesh
is 0xC4 bytes. Catmull-Rom subdivision factor 3 is used only to display
an interpolant; the stored grid stays 7×7. The probe area is a 210 mm
square starting at (−105, −105) with 35 mm spacing. A 12×12 grid would
need a firmware change; multiple G29 runs cannot be stitched into a
finer mesh.

**Paper test** (probe off): `G28`, `G1 X0 Y0 Z50 F1000`, `G1 Z40 F500`,
`M211 S0` (software endstops off). Jogs are real `G91` / `G1 Z{dz} F500`
/ `G90` / `M114`. **Save:** `new_H = H − Z`, then `M665 H`, `M500`,
`M211 S1`. **Cancel:** `M211 S1` only; no `M665`, no `M500`.

## When M500 is sent

ivibridge sends `M500` only after:

- a G33 `Calibration OK`, or
- a complete `Bilinear Leveling Grid:` (the daemon sends `M500` itself after `G29`; the firmware does not write EEPROM on its own), or
- a paper-test Save.

It does not send `M500` on `Probing Failed`, `No convergence`, timeout,
or cancel. After a successful G33 or G29, the daemon refreshes `M503`.
Last-run times are stored in the settings file as `last_xyz`,
`last_level`, and `last_paper`.

A long post-success settle (default 45 s, `IVIB_CAL_SETTLE_MS`;
`echo:busy` extends it) covers G33's final home and G29's end-script
`G28`.

## Z-offset display

The web UI shows a normal offset, not a raw height:

```
offset = reference_H − effective_H
```

After calibration, or after **Set current as zero**, the displayed
offset is 0.00. Positive means the nozzle is higher than that
reference; negative means closer.

- A paper-test Save or a G33 that changes H resets the reference to the
  new height so the offset reads 0.00 again. Save still writes
  `M665 H` + `M500` but keeps the displayed offset if you saved a mid-
  print baby-step later.
- G29 does not change H and does not reset the reference.
- Mid-print baby steps are `M290`. **Save Z offset permanently** queues
  `M665 H` + `M500` until idle.

`M851` (probe Z offset) is not changed by G33, G29, or the paper test.

## Leveling and start G-code

Firmware fact for the stock Marlin V1.3.2-alpha on this machine: the
stock app never sends `M420 S1`, and `G28` turns bed leveling off. A
saved mesh is therefore not applied after a home unless the job's start
G-code sends `M420 S1` after `G28`. (`M420 V` prints the current state;
`GET /api/ivi/cal` reports `level.enabled`.) Put `M420 S1` after the
`G28` in the slicer's start G-code if you want the mesh used.
