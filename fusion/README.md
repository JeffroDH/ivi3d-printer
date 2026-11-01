# Autodesk Fusion post processors for the IVI3D (laser + CNC)

| File | For |
|---|---|
| `ivi3d_laser.cps` | Laser (jet / cutting) operations → `.nc`, IVI 3licer **line-mode** format |
| `ivi3d_cnc.cps` | Milling operations → `.cnc`, IVI 3licer CNC format |
| `ivi_header_check.py` | Checks any `.nc`/`.cnc` against the IVI header format (and flags the point-mode dwell bug) |
| `_common.js`, `laser.src.js`, `cnc.src.js`, `build.py` | Sources; run `python3 build.py` to regenerate the `.cps` files |

Format details: [../docs/laser_cnc_gcode.md](../docs/laser_cnc_gcode.md). **Unverified on hardware** — first run
at low power on scrap with laser safety glasses, or with the CNC bit raised above the stock.

## Install
1. In Fusion open the **Manufacture** workspace → **Manage → Post Library**.
2. Import `ivi3d_laser.cps` and `ivi3d_cnc.cps` (into *My Posts* / local folder).
3. When posting (**Actions → Post Process**), pick "IVI3D Laser (line mode)" or "IVI3D CNC" and set the output folder.

## Setup in Fusion
- **Units: mm** (the posts refuse inch output).
- **Origin: centre.** Set the setup WCS X0 Y0 at the centre of the stock / work area (IVI jobs are centre-origin
  and return to X0 Y0 at the end). For CNC put Z0 at the **top** of the stock.
- Arcs are linearized (IVI files contain only G0/G1).
- Laser: create a cutting/laser operation (2D profile etc. with a laser tool). Power is the post property
  **Laser power (%)** → `M3 S<percent>` (first segment), bare `M3` after, `M5` after each segment. `M106 P0` /
  `M107 P0` (fan/air assist) wrap the job; turn off with the *Fan / air assist* property. Feed comes from the
  operation; jog speed from the property (default 1500).
- CNC: spindle is the property **Spindle power (%)** → `M3 P<percent>` (Fusion RPM is ignored). Safe Z 10 and
  retract Z 5 as in IVI 3licer; plunges are capped at 300 mm/min.

## Check a file before printing
```sh
python3 fusion/ivi_header_check.py job.nc
```
Errors = header missing/inconsistent; warnings = cosmetic (e.g. IVI's own off-by-one valid-line count) or
dangerous (absurd `G4` dwell). Send files with the bridge or IVI 3licer as usual.

## Tests
`python3 -m unittest discover -s fusion/tests` — runs both posts under a small mock of the Fusion post API
(`tests/run_post.js`, needs Node) on a synthetic square toolpath and validates the output with the checker.
The mock covers only the calls these posts use; real Fusion behaviour (section types, jet power events) is untested.
