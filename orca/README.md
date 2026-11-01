# OrcaSlicer profile for the IVI3D (FDM, delta)

| File | What |
|---|---|
| `IVI3D.orca_printer` | Bundle: printer + 7 filaments (PLA, ABS, ASA, PETG, PCTG, TPU 95A, SR-30 experimental) + 3 processes: 0.15 Standard, 0.20 Fast, 0.10 High Quality (one import) |
| `machine/IVI3D 0.3 nozzle.json`, `filament/*.json`, `process/IVI3D 0.15mm Standard.json`, `process/IVI3D 0.20mm Fast.json`, `process/IVI3D 0.10mm High Quality.json` | Same presets as separate user-preset JSON |
| `ivi_fdm_header.py` | Optional post-processing hook that adds the IVI 3licer `;Header Start … header_type: 3dp` block |
| `build_profiles.py` | Regenerates everything (edit values here) · `tests/` validates JSON, geometry, bundle, header |

## Import
1. OrcaSlicer → **File → Import → Import Configs…** → pick `IVI3D.orca_printer` (or the three `.json` files).
2. Select printer **IVI3D 0.3 nozzle**, filament **IVI3D PLA**, process **IVI3D 0.15mm Standard** (or **0.20mm Fast** / **0.10mm High Quality**).
3. Printer settings → Connection: the host is pre-set to OctoPrint `127.0.0.1:5000`; paste the API key from the
   IVI Bridge installer ([../bridge/README.md](../bridge/README.md)) → Test.
4. Optional header hook: Process → Others → Post-processing scripts:
   `/usr/bin/python3 "/Volumes/14TB/3D Printing Files/IVI3D/orca/ivi_fdm_header.py";`
   Not needed for USB printing through the bridge; may matter for files uploaded over Wi-Fi and started from the touch
   screen (it shows type/material/time from that header). Unverified whether the screen refuses files without it.

The bed is a 105 mm-radius circle with the origin at the centre; the delta homes to the top, so the start G-code homes
then drops to Z15 at the bed edge before the purge line (same as IVI 3licer).

### Bed texture and model
`bed/IVI_plate.stl` (bed model) is the whole IVI plate outline (~300 mm wide at the front, ~190 mm at the flat back,
~240 mm deep; traced from a photo against the 20 mm grid, so expect a few mm of error), centred on the 210 mm printable
circle with the wide edge at the front. `bed/IVI_plate.svg` (bed texture) covers only the 210 mm printable circle,
because Orca stretches the texture over the printable area. It is transparent (only the IVI logo, text as paths and
the dashed 210 mm circle, plus a solid 200 mm circle), so Orca's bed grid stays visible. The printable area stays a 210 mm circle.
The preset sets `bed_custom_model` and `bed_custom_texture` to the Mac mirror paths
(`/Volumes/14TB/3D Printing Files/IVI3D/orca/bed/IVI_plate.stl` / `.svg`) because Orca keeps absolute paths and config
bundles do not carry them. On another machine, set `IVI3D_BED_MODEL` / `IVI3D_BED_TEXTURE` before running
`build_profiles.py`, or pick the files under Printer settings → Bed shape.

Scale is **estimated**: the only plate image (ivi3d.com product photo `bk11`) is a perspective render with no dimensions.
Its outline is a rounded triangle, modelled as an equilateral triangle (inradius 45 mm) offset by 70 mm (plate inradius
115 mm, so 10 mm of margin around the 105 mm printable circle), with 1.6 mm holes on an 8 mm hex grid kept 18 mm in from
the edge. Measure the real plate and update the constants in `make_bed.py` if precision matters.

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

**Fast / High Quality** — IVI 3licer built-in quality defs for the 0.3 nozzle, `resources/CuraEngine/Config/test/quality.(0.3).fast_print.def.json` / `quality.(0.3).high_quality.def.json` (*fast* / *hq*). Everything not listed equals Standard (first layer 0.3 @ 18 mm/s, skirt 1, brim 8 off, support off 50°, retraction 6.5 @ 25 no Z-hop, accel 500 / jerk 15 — identical in both files).
| Setting | 0.20mm Fast | 0.10mm High Quality | Source |
|---|---|---|---|
| Layer / first | 0.2 / 0.3 | 0.1 / 0.3 | fast/hq `layer_height`, `layer_height_0` — match the requested heights |
| Walls | 3 (0.8 mm) | 3 (0.8 mm) | `wall_thickness 0.8` ÷ 0.28 width (files' stale `wall_line_count` 4 / 8 ignored, as Standard) |
| Top / bottom | 5 (0.9 mm) / 3 (0.6 mm) | 12 (1.2 mm) / 6 (0.6 mm) | `top/bottom_thickness` ÷ layer, rounded up (files' stale 4/3, 10/6) |
| Infill | 15 % | 20 % | `infill_sparse_density` |
| Speeds outer / inner / infill / top-bottom / travel | 50 / 60 / 80 / 40 / 100 | 30 / 45 / 50 / 30 / 60 | `speed_wall_0`, `speed_wall_x`, `speed_infill`, `speed_topbottom`, `speed_travel` |
| Line widths | 0.3 / 0.28 | 0.3 / 0.28 | hq sets 0.28 everywhere; fast inherits def (same as Standard) |

**Assumed** (not in IVI's files; applies to all three processes): internal solid infill speed = infill speed; gap/support/bridge speeds as Standard; max layer 0.24 / min 0.05; deretraction speed = retraction speed; retraction min travel
1.5 mm; max jerk Z 10 / E 5 (M503 M205 has Z10 E5); machine limits not emitted to G-code (firmware keeps its own);
`M107` added to the end G-code; fan 100 % after layer 1; max volumetric speed 8 mm³/s; skirt distance 3 mm; seam
aligned; grid infill; pause G-code `M2410`; PLA range 190–230 °C; thumbnails off. Today's observed start used
`M140 S50` — the profile uses the IVI default bed 60 °C. Firmware delta values (M665 L357.5 R160.31 H233.22, M666, M851
Z-14.29) live in the printer, not in Orca.

## Extra filament presets

Baseline: Anycubic's own OrcaSlicer vendor profiles (`resources/profiles/Anycubic/filament/`, the "Anycubic ABS/ASA/PETG @Anycubic Kobra S1 0.4 nozzle" and "Anycubic TPU 95A @Anycubic Kobra S1 Max 0.4 nozzle" JSONs). Max volumetric speed is scaled ~0.55x for the 0.3 nozzle (area ratio (0.3/0.4)^2 = 0.56) and capped at the PLA preset's 8 mm³/s. Retraction is inherited from the machine preset (6.5 mm @ 25 mm/s, from IVI 3licer) except TPU. All values are starting points; calibrate temperature, flow, and retraction per spool.

| Preset | Nozzle (1st layer) °C | Bed °C | Fan min–max (off first n layers) | Retraction | Max vol. mm³/s | Source |
|---|---|---|---|---|---|---|
| IVI3D ABS | 250 (250) | 90 | 10–80 % (5) | machine 6.5 mm | 8 (AC 15) | Anycubic ABS |
| IVI3D ASA | 260 (260) | 100 | 10–60 % (5) | machine 6.5 mm | 7 (AC 12) | Anycubic ASA |
| IVI3D PETG | 240 (245) | 70 | 30–90 % (3) | machine 6.5 mm | 7 (AC 12) | Anycubic PETG (250 °C, lowered 10 °C for this slower printer) |
| IVI3D PCTG (Tangled TUFF) | 260 (260) | 80 | 10–25 % (3) | machine 6.5 mm | 6 | Tangled TUFF Pro PCTG label: nozzle 250–280, bed 70–90, fan ≤25 %, 30–60 mm/s |
| IVI3D TPU 95A | 215 (220) | 35 | 100 % (1) | 1.0 mm @ 20 mm/s | 1.5 (AC 3.2) | Anycubic TPU 95A (205/215, retract 1 mm @ 30) |
| IVI3D SR-30 Soluble (EXPERIMENTAL) | 255 (260) | 100 | 0–20 % (3) | machine 6.5 mm | 4 | Stratasys / MakerBot SR-30 docs (support for ABS/ASA, ~250–260 °C class); assumed values |

Caveats:
- **ABS / ASA / SR-30:** enclosure strongly recommended (warping, fumes; ventilate). Bed 90–100 °C (the IVI supports bed up to 100 °C and nozzle up to 270 °C per its touchscreen presets; `build_profiles.py` clamps all filament temps to these limits).
- **PCTG / PETG:** stick very hard to smooth PEI/glass; use glue stick as a release agent.
- **TPU 95A:** keep slow (≈15–20 mm/s; 1.5 mm³/s cap enforces this). If the extruder path is Bowden, TPU may buckle — test first.
- **SR-30:** NOT PVA. Stratasys alkaline-soluble terpolymer, dissolved in a heated NaOH bath (~70 °C, Stratasys/MakerBot). Single nozzle means it can't be support under another material here; whole-part tests only. Hygroscopic: dry before use. Values are untested guesses.
