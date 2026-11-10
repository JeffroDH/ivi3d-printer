# DEBUGUART 3-pin pogo holder (A33_407MB_200916)

Simple **one-piece** handheld / arm-mount contact block for pads
**GND · DEBUGUART_RX · DEBUGUART_TX** (L→R, silkscreen upright).

Source: `uart_pogo_holder.scad`. The pads are the A33 ttyS2 console; see [docs/a33.md](../../docs/a33.md) and [docs/tools.md](../../docs/tools.md). Connect GND, RX, and TX only.

---

## Photo measurements (approximate)

From the ruler photo only — **estimates, not a survey**.

| Item | Approx. value | Notes |
|------|---------------|-------|
| Along-edge pitches | **~1.9 mm** then **~2.8 mm** | Raw image-plane ~1.93 / ~2.79; **rounded**. Unequal neighbors are suspicious (center-pick / perspective / non-grid test points). Do not treat as precise. |
| GND→TX span | **~4.7 mm** | |
| Pad Ø | **~1.0 ± 0.2 mm** | ~0.9 mm in image |
| Edge inset | **~5 mm** image-plane | Foreshortened; real likely ~4–7 mm |
| Image row tilt | ignored as PCB skew | Models use a **straight** row parallel to the board-edge reference |

Coordinates in the SCAD (photo variant), origin at GND bore:

- `+X` along board edge toward RX/TX  
- `+Y` toward board interior (away from edge)  
- `+Z` out of board; tips exit the `z=0` face  
- `photo_x = [0.0, 1.9, 4.7]`, `photo_y = [0, 0, 0]`

See `measurement_annotated.jpg`. Front photos: board on chassis standoffs, dense
SMT (STM32F407, blue Allwinner A33 module, AP6236, JSTs, microSD, micro-USB near
this edge). **No underside/component clamp.** DEBUGUART routing not inferred.

---

## Files

| File | Description |
|------|-------------|
| `stl/holder_photo.stl` | Bores at photo-estimated **~1.9 / ~2.8** spacings (straight row) |
| `stl/holder_2_0.stl` | Equal **2.0 mm** pitch |
| `stl/holder_2_5.stl` | Equal **2.5 mm** pitch |
| `stl/bore_coupon.stl` | Through-holes **1.30 / 1.40 / 1.50 / 1.60** mm (L→R) |
| `renders/assembled.png` | Photo holder over ghost PCB |
| `renders/exploded.png` | All three holders + coupon |
| `renders/holder_photo.png` | Photo holder alone |
| `renders/bore_coupon.png` | Coupon alone |
| `measurement_annotated*.jpg` | Ruler/pad overlay |

Edit `photo_x` / `photo_y` (or pitches) in the `.scad` and re-export if calipers disagree.

```bash
openscad -o stl/holder_photo.stl -D 'part="holder_photo"' uart_pogo_holder.scad
```

---

## Hardware assumptions

- R75-class sockets (prior note: sleeve OD ~1.32 mm) — **unverified for your parts**
- Default printed through-bore `r75_hole = 1.40` — **print the coupon first**
- Retention: **press-fit and/or adhesive on the back (non-contact) face**
- Bores are **through-holes**. There is **no** internal shoulder / retention ledge
- **No metal set screws** between sockets (short risk on 1.9–2.0 mm pitch)
- Leads: solder to socket tails at the back/top; Dupont to USB-UART
- Connect **GND / RX / TX only** — no VCC. Power **off** when seating
- Optional M3 through the **rear tab only** (clear of bores) for probe-arm clamp

Tip protrusion / pogo stroke are **not** modeled as a hard stop — unknown for
your pins. Control compression by hand or arm pose.

At ~1.9 mm pitch with Ø1.4 mm bores, plastic wall between GND–RX is only
**~0.5 mm**. Printable, but delicate; prefer PETG and don’t force sockets.

---

## Use

1. Print `bore_coupon`; pick the hole that fits your sleeve; change `r75_hole` if needed.
2. Print `holder_photo` first (or 2.0 / 2.5 if you measure equal pitch).
3. Mark bores GND / RX / TX (L→R).
4. Seat sleeves from either face; glue at the **back** if the fit is loose.
5. Hold normal to the board or M3-mount the rear tab to the probe arm. Stay clear
   of the microSD can / JSTs / USB on the component side.

---

## Print

- 0.4 mm nozzle (0.3 OK), 0.15–0.20 mm layers, PETG preferred  
- Tip face (`z=0`) on bed; no supports  
- ≥3 walls; 40–60% infill  

---

## Validation (this rebuild)

- Each STL: CGAL **Simple: yes**, **one** connected component  
- Bores do not overlap; wall between photo GND–RX ≈ 0.5 mm  
- M3 mount holes stay on the rear tab, **>11 mm** from every bore center in XY  
- Through-bores (full height) — contact face is open  
- Obsolete rail / carrier / wedge / shim / bare-pin files **removed**
