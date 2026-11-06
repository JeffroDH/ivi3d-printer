# Motors and display (2026-11-05 photo pass)

Evidence tags match [mainboard.md](mainboard.md):

| Tag | Meaning |
|---|---|
| **[P]** | Read from owner photos by tools this session |
| **[Pᵗ]** | **Parent-transcribed** visible content from owner photos that **agent tools could not open** this pass (claimed attachment hashes / sizes not present under `attachments/` or the cursor store at documentation time). Treat as photo-backed once the files are archived; do not elevate to measured/traced. |
| **[F]** | Firmware / decompile |
| **[D]** | Datasheet |
| **[G]** | Inference |
| **[U]** | Unknown |

**Safety:** power off and disconnect before any continuity or connector work on steppers or display flex. **Never hot-unplug a stepper** under power.

Agent recovery note (this pass): claimed paths  
`…/e8ce01d0….jpg` (motor), `…/d39f4fa4….jpg` (display back), `…/8a93a3a7….jpg` (flex macro), `…/db2820e3….jpg` (small-board macro) were **not found** by Shell or Read. Cursor store newest JPGs remained the earlier mainboard evening set. **No crops were added to `docs/images/`** for this pass.

---

## 1. Closed-loop motor (body / connectors) — [Pᵗ]

### Label

- Motor body marking begins approximately **`BJ42C29-01V…`** with the **suffix incomplete / not fully readable** in the photo transcription **[Pᵗ]**.
- **Do not** publish a finalized full model string until a clear photo or datasheet match is archived.
- No voltage, torque, or encoder rating is claimed from this partial marking **[U]**.

### Connectors (visual only)

| Connector | Visible leads | Notes | Tag |
|---|---|---|---|
| Lower connector | **Four** leads, black/white | Appearance is **consistent with a bipolar stepper phase pair** (two windings). That is a layout consistency note only — not a pinout, phase map, or driver-type proof. | **[Pᵗ]**; function detail **[U]** |
| Upper connector | **Two** red leads on a **distinct** connector | **Function unknown.** Do **not** assume brake, encoder, thermistor, fan, or hall sensor without tracing or a readable silk/datasheet. | **[Pᵗ]**; role **[U]** |

### Relation to main-board docs

- Main board still shows per-axis `*_UART_*` + STEP/DIR/EN and `MT*_24V` feeds to **separate driver boards** **[P][F]** ([mainboard.md](mainboard.md)).
- This motor-body photo does **not** by itself identify which tower (X/Y/Z/F) or prove the closed-loop sensor path **[U]**.

### Safe next steps

1. Power off. Photograph the full label square-on; archive under `docs/images/` with EXIF stripped.
2. Continuity (power removed): map the four-lead connector to the mating driver cable only after labeling both ends; never hot-unplug.
3. Leave the two-red-lead connector unassigned until traced or silk is readable.

---

## 2. Display rear / flex — [Pᵗ]

### Assembly (visible)

- Display rear shows a **broad amber flex** **[Pᵗ]**.
- A **narrow white ribbon** runs to a **small board taped at the glass edge** **[Pᵗ]**.
- **LCD panel vs capacitive-touch roles** for each flex/ribbon are **possible but not proven** from these photos alone **[G/U]**. Main-board silk already has separate **CTP_*** I²C and **LCD*** bias rails **[P]** ([mainboard.md](mainboard.md) §5.2) — that supports a touch+LCD system in general, not a one-to-one assignment of these specific ribbons.

### Broad flex partial marking [Pᵗ]

Legible segment transcribed by parent (trailing characters obscured):

- Approximate text: **`7-48 159P/0.17-50R/0.`** (end cut off / unreadable)
- Also noted: **`RXS`**
- Vertical / right-side marking appears to include **`SD0063F…`** — **uncertain** reading; do not treat as confirmed part number.

**Explicit non-claims**

- Do **not** infer FFC contact count or pitch from artwork or partial text.
- Do **not** infer brand, full model, voltage, or resolution from this flex string.
- Record only the **partial** strings above with **[U]** for the obscured remainder.

### Safe next steps

1. Power off. Flat, glare-free macros of the full flex legend and both connectors.
2. Continuity only when disconnected: which flex lands on main-board LCD ZIF vs CTP ZIF (if either).

---

## 3. Small edge interface board (macro) — [Pᵗ]

Parent-visible macro of the small board at the glass edge (claimed `db2820e3….jpg`, not opened by tools):

- **White/black latch** connector at the top mating a **narrow white FFC** with a **blue stiffener** **[Pᵗ]**.
- **Amber** small PCB **[Pᵗ]**.
- A **long fine-pitch black IC**, partly hidden by the white ribbon and amber tape — **no confidently legible chip ID** **[Pᵗ]/[U]**.
- Possibly another tiny part at upper right — unmarked / unread **[U]**.

**Explicit non-claims**

- Do **not** name a controller chip model, I²C address, or touch protocol from this macro.
- The photo **supports** that a **separate small interface board** exists between glass-edge flex and the narrow FFC **[Pᵗ]**.
- A **touch** role for that board remains **probable in context [G]** (main-board `CTP_*` silk **[P]**), **not proven** for this assembly **[U]**.

---

## 4. Open questions

- Full motor orderable string after `BJ42C29-01V`.
- Role of the two-red-lead upper connector.
- Which flex is LCD vs CTP (or other); complete flex part marking.
- Identity of the fine-pitch IC on the small edge board.
- Archive the four owner JPEGs into `docs/images/` once attachments are readable to tools (strip EXIF/GPS; no printer serials).

---

## Related

- Remote Bowden **extruder gear train / hobs**: [extruder.md](extruder.md) (2026-11-05; largely **[Pᵗ]/[O]** while photos unavailable to tools).
