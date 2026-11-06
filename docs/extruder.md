# Extruder mechanism (remote / Bowden feeder)

Evidence tags (same spirit as [mainboard.md](mainboard.md)):

| Tag | Meaning |
|---|---|
| **[P]** | Agent opened owner photos this session |
| **[Pᵗ]** | **Parent-transcribed** visible content from owner photos **not opened by tools** this pass (claimed attachment hashes absent under `attachments/` / store). Photo-backed once archived; not measured. |
| **[O]** | **Owner report** (subjective / operational observation; not a lab measurement) |
| **[F]** | Firmware / saved dump |
| **[G]** | Inference |
| **[U]** | Unknown |

**Access (this pass):** claimed paths  
`bd92a292….jpg`, `2d65ee94….jpg`, `9727b940….jpg` were **not found** by Shell or Read; store had no newer extruder batch. **No crops** were added under `docs/images/extruder/`. Re-archive when files are readable (strip EXIF/GPS; no printer serials).

**Safety:** power off before poking gears, pinch, or filament path. Never hot-unplug a driven extruder under load.

Owner note that started this pass: interest in **more refined extruder gears** — documented below as refinement *opportunities* and measurement prerequisites, not a shopping list or CAD job.

---

## 1. Layout (visual) — [Pᵗ]

Orthogonal motor → bevel stage → spur train → dual hobbed feed looks like a **geared dual-drive Bowden** feeder (remote of the toolhead).

| Stage | Visible parts | Tag |
|---|---|---|
| Motor pinion | Small **brass** bevel / face pinion on the stepper shaft; **radial grub screw** | **[Pᵗ]** |
| Bevel driven | Large **ivory plastic** face/bevel gear on a **transverse** shaft; **hub screw** | **[Pᵗ]** |
| Spur train | Two **smaller ivory spur gears** on **parallel** shafts, appear meshed | **[Pᵗ]** |
| Filament drive | **Metal toothed / hobbed rollers** at the filament path by a **brass tube fitting** | **[Pᵗ]** |

**Distinguish:** ivory/brass **transmission gears** ≠ metal **filament hobs**. Refining one does not automatically fix the other.

**Not measured [U]:** tooth counts, ratios, module, center distance, bevel pitch-cone geometry, shaft bores/flats, axial stack-up, hob effective diameter, bearing fit, endplay, unloaded runout, pinch force.

**Materials [U]:** ivory parts look like engineering plastic; **nylon vs POM (or other) not known** from photos/transcription.

**Damage / backlash [U]:** static photos do **not** prove backlash, missing teeth, or wear. One view was noted as *possible* tooth irregularity — **do not diagnose** wear or broken teeth without clearer evidence **[Pᵗ]/[U]**.

---

## 2. Filament grip (owner report) — [O]

> Owner: “The filament gripping teeth are very aggressive, leaving grooves in the PLA even when they don’t slip.”

| Item | Status |
|---|---|
| Grooves in PLA after feed without slip | **Owner report [O]** — severity (light indent vs deep gouge / ridge / flattening) **not graded** |
| Over-tension proven? | **No [U]** — grooves + no slip ≠ proof of excessive pinch or wrong tooth profile alone |
| Light surface marks | Common on many hobbed feeders; not automatically a defect **[G]** |
| Deep gouges / raised ridges / flattening | *Could* raise Bowden drag downstream **[G]** — still unproven here |

### Priority vs gear redesign

If drag or feed reliability is the concern, treat **hob geometry / pinch pressure** as **higher priority** than a transmission-gear redesign **[G]** (owner symptom is about **gripping teeth**, not bevel noise/ratio).

### Safe checks (powered off)

1. Compare **untouched** filament diameter vs filament that has been through the hobs, in **two orientations** (mark axes) — look for ovalization / deep ridges **[U]** until measured.
2. Inspect hobs for **debris** packed in teeth.
3. With power off, feel **Bowden drag** (path clear) — qualitative only.
4. If the mechanism has a **pinch/tension adjuster** (presence **not proven [U]**), use the **lowest** pressure that still feeds reliably — do not invent an adjuster that isn’t there.
5. A future matched hob set with **rounded / less aggressive** teeth is a possible redesign direction **[G]**; **avoid smooth rollers** that lose grip. No manufacturing in this pass.

---

## 3. Refinement notes (transmission) — opportunities, not a build plan

Grounded in the transcribed layout; **no purchases, CAD, or printer commands**.

**Higher-value mechanical targets than “more teeth”**

1. **Concentricity** of pinion and large bevel to their shafts (grub/hub seating).
2. **Matching bevel geometry** (cone angle / offset) — do **not** substitute a generic spur pair for the bevel stage.
3. **Shaft support and axial retention** (endplay at bevel and spur shafts).
4. **Mesh / backlash** at bevel and spur stages (measurable once opened).
5. Only then: material or tooth-quality upgrades **keeping the same tooth counts / ratio** if a prototype set is desired later.

**Not automatically better**

- Smaller module / more teeth without measured center distance and cones.
- Helical substitution on these shafts — adds **axial** force and needs thrust support / housing redesign **[G]**.

**If a matched replacement gear set is ever designed:** prefer **retaining current tooth counts and overall ratio** as the first prototype goal so firmware E-steps stay in the same ballpark — still requires extrusion calibration after any change (below).

---

## 4. Firmware / print settings context (do not retune from photos)

| Item | Value / note | Tag |
|---|---|---|
| `M92` E steps | **`E1150.00`** in saved Marlin `M503` snapshot | **[F]** — [marlin_M503_settings.txt](marlin_M503_settings.txt); **not** a new measurement from these photos |
| Changing gear ratio or effective hob Ø | Needs **extrusion calibration**; may need **pressure-advance** retune | **[G]** — photos do **not** prove gears/hobs cause any specific artifact |
| Owner print context | **0.3 mm** nozzle; Bowden **~6–8 in**; PA **K0.86**; retract **6.2** | **[O]** — **do not change** these from documentation alone; only after controlled tests |

---

## 5. Measurement checklist before any printable replacement

Power off. Record before cutting plastic or metal:

1. Tooth counts: motor bevel pinion, large bevel, both spurs (both stages).
2. Shaft bores, flats, and set-screw sizes; hub lengths.
3. Center distances (bevel axes; spur pair).
4. Bevel pitch-cone geometry (angles / offset) or careful photos with scale.
5. Axial space / stack clearance for each gear.
6. Hob effective diameter (and whether dual hobs match).
7. Bearing type/fit and endplay.
8. Unloaded runout; pinch range if adjustable.
9. Archive clear macros into `docs/images/extruder/` (EXIF stripped).

Until those exist: **document and observe only** — no manufacturing.

---

## 6. Open questions

- Full photo archive of the three owner JPEGs.
- Tooth counts and ratio; plastic resin of ivory gears.
- Whether pinch is adjustable; hob tooth form / OD.
- Severity of PLA grooving (diameter before/after).
- Link of any extrusion artifact to gears vs hobs vs Bowden drag vs PA — **unproven**.

Related: remote feeder is the **F** (filament) axis on the main board (`F_*` pads, `MTF_24V`) **[P][F]** — [mainboard.md](mainboard.md). Motor-body / display notes: [motors_and_display.md](motors_and_display.md).
