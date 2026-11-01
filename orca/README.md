# OrcaSlicer profile for the IVI3D (FDM, delta)

| File | What |
|---|---|
| `IVI3D.orca_printer` | Bundle: printer + PLA filament + 0.15 mm process (one import) |
| `machine/IVI3D 0.3 nozzle.json`, `filament/IVI3D PLA.json`, `process/IVI3D 0.15mm Standard.json` | Same presets as separate user-preset JSON |
| `ivi_fdm_header.py` | Optional post-processing hook that adds the IVI 3licer `;Header Start … header_type: 3dp` block |
| `build_profiles.py` | Regenerates everything (edit values here) · `tests/` validates JSON, geometry, bundle, header |

## Import
1. OrcaSlicer → **File → Import → Import Configs…** → pick `IVI3D.orca_printer` (or the three `.json` files).
2. Select printer **IVI3D 0.3 nozzle**, filament **IVI3D PLA**, process **IVI3D 0.15mm Standard**.
3. Printer settings → Connection: the host is pre-set to OctoPrint `127.0.0.1:5000`; paste the API key from the
   IVI Bridge installer ([../bridge/README.md](../bridge/README.md)) → Test.
4. Optional header hook: Process → Others → Post-processing scripts:
   `/usr/bin/python3 "/Volumes/14TB/3D Printing Files/IVI3D/orca/ivi_fdm_header.py";`
   Not needed for USB printing through the bridge; may matter for files uploaded over Wi-Fi and started from the touch
   screen (it shows type/material/time from that header). Unverified whether the screen refuses files without it.

The bed is a 105 mm-radius circle with the origin at the centre; the delta homes to the top, so the start G-code homes
then drops to Z15 at the bed edge before the purge line (same as IVI 3licer).

## Values — sourced vs assumed
**Sourced** (IVI 3licer 1.6.2 `resources/CuraEngine/Config/ivi3d.def.json` = *def*, the user's
`~/Library/Application Support/ivi-3licer/Config/active_final.def.json` = *active*, printer `M503` = *M503*):
| Setting | Value | Source |
|---|---|---|
| Bed shape | circle Ø210 (r 105), origin centre | def: width/depth 210, `machine_shape: elliptic`, `machine_center_is_zero: true` |
| Max Z | 220 mm | def `machine_height` (M503 delta height H233.22) |
| Nozzle / filament | 0.3 mm / 1.75 mm | def; printer reports `info:Head 3DP,0.3mm` |
| Flavor / E mode | Marlin, absolute E (M82) | def `RepRap (Marlin/Sprinter)`; end G-code + observed start use M82 |
| Start / end G-code | IVI's, with Orca placeholders | active `machine_start_gcode` / `machine_end_gcode`; `G53` + `M82` from today's observed FDM start |
| Temps PLA | 210 / 215 first layer, bed 60 | active + `material.pla.def.json` |
| Retraction | 6.5 mm @ 25 mm/s, no layer-change retract, no Z-hop | active |
| Layer | 0.15, first 0.3; widths 0.3 / 0.28 | active |
| Shells / infill | 3 walls, 6 top, 4 bottom, 15 % | active |
| Speeds (mm/s) | outer 45, inner 50, infill 60, top/bottom 30, travel 80, first layer 18, first-layer travel 30, skirt 18 | active |
| Accel / jerk | 500 mm/s² print, jerk 15 | active |
| Machine limits | max accel X/Y/E 1000; feed Z 500 | active (firmware M503: M201 3000, M203 500/500/500/100) |
| Skirt | 1 loop, brim width 8 (off) | active |
| Support | off, 50° | active |

**Assumed** (not in IVI's files): max layer 0.24 / min 0.05; deretraction speed = retraction speed; retraction min travel
1.5 mm; max jerk Z 10 / E 5 (M503 M205 has Z10 E5); machine limits not emitted to G-code (firmware keeps its own);
`M107` added to the end G-code; fan 100 % after layer 1; max volumetric speed 8 mm³/s; skirt distance 3 mm; seam
aligned; grid infill; pause G-code `M2410`; PLA range 190–230 °C; thumbnails off. Today's observed start used
`M140 S50` — the profile uses the IVI default bed 60 °C. Firmware delta values (M665 L357.5 R160.31 H233.22, M666, M851
Z-14.29) live in the printer, not in Orca.
