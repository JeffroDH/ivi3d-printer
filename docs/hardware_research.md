# IVI hardware research

Compiled 2026-10-31 from public sources; board photo pass extended **2026-11-05**. No internal board photos were found online; an owner has photographed the main board — see **[mainboard.md](mainboard.md)** (primary detail page). Labels: **[P]** owner photos, **[O]** owner statement (dated), **[C]** public source, **[F]** firmware, **[D]** datasheet, **[G]** guess, **[U]** unknown.

## Architecture

- **Boards [C][P]:** one **combined main board, `A33_407MB_200916`**, carrying:
  - a **blue castellated SoM** with Allwinner **A33** (**owner-confirmed 2026-11-06 [O]**; photo die text may still be hard to read), **AXP223** PMIC, Samsung **K4B4G1646E**-class **512 MB** DDR3L, and Toshiba/Kioxia **THGBMNG5D1LBAIL 4 GB** eMMC **[P][D]**;
  - carrier **STM32F407VET6** (512 KB flash, LQFP100) for Marlin motion **[P][D][F]**;
  - Ampak **AP6236** Wi-Fi/BT module fitted **[P][D]** (RF path/firmware enablement **[U]**).
  Separately: per-motor closed-loop driver boards and, per the forum's December 2020 update, a "power PCB and switch PCB". Full pad maps, connector caveats, **5-pin + CH340G**, wood-set **Amass** inlet / **GL850G** hub / unassigned black wires are in [mainboard.md](mainboard.md).
- **Software split [F]:** Linux/Qt UI + HTTP `:8080` on the A33 side; Marlin-derived image on the STM32; UI↔motion over internal serial; external USB-C CDC goes to Marlin. See `firmware_report.md`, `network.md`.
- **November 2020 [C]:** first version of the main board finished, with small affiliated PCBs.
- **June 2019 [C]:** control board parts sourced through Allchips.
- **Closed-loop motors [C][F]:** FAQ: magnetic angle sensor + separate drive board per motor; firmware uses a custom UART protocol per driver.
- **Toolhead identification [C][F]:** FAQ: chip on printhead PCB; firmware queries head over CAN2 (ID 0x12) for type, serial, FW version, nozzle size. **Do not put printer/toolhead serials in this repo.**
- **Head connector [C visually / G roles]:** renders show 8 gold pads in 2 staggered rows of 4 (`images/renders/`). Power, GND, CAN-H, CAN-L, detect/ID **guess only**. Pitch/order unknown.
- **Motion [C]:** delta with HIWIN MGN9H rails and belt-driven carriages (`images/archive/IVI-joints.png`). Geometry matches the M503 dump.

## Images

- `images/renders/`: 14 BackerKit product renders. See `SOURCES.md` there.
- `images/board/`: owner photos of the main board (2026-10 and 2026-11). See `SOURCES_2026-11.md` for the newer set.
- Motor body / display flex / glass-edge board: [motors_and_display.md](motors_and_display.md) (2026-11-05; partly **parent-transcribed** while attachments were unavailable to tools).
- Extruder (remote dual-drive geared Bowden layout, hob grip notes): [extruder.md](extruder.md).
- `images/archive/`: Wayback Machine renders.

All images are IVI / owner material, included for preservation. Chip lot codes and `A33_407MB_200916` are **not** printer serials.

## Sources

- IVI forum (archived, ~160 threads): https://web.archive.org/web/2021*/forum.ivi3d.com/*. Beta thread 1877. ~21 beta units Feb 2021.
- BackerKit updates: https://ivi.backerkit.com/hosted_preorders/project_updates. Dec 15, 2020 "inner look" photos deleted.
- ivi3d.com FAQ/assets: https://web.archive.org/web/2020*/ivi3d.com/*
- Chip datasheets cited in [mainboard.md](mainboard.md) §12.
- No useful FCC / Reddit / YouTube / CN hits for board artwork.

## Not yet retrieved (retry later)

Wayback listed `ivi3d.com` images like `mcu-*.jpg`, `closed-loop-stepper-*.jpg`, `Ivi_front_sensors_all-*.jpg`. On 2026-10-31 CDX returned none. Retry:

`https://web.archive.org/cdx/search/cdx?url=ivi3d.com&matchType=domain&filter=original:.*(mcu|closed-loop|sensors).*`

## Open questions

Photos answered the big architecture questions. Still open (detail in [mainboard.md](mainboard.md)):

**Resolved by board photos**

- Hotend heater/fan/laser/spindle on the **toolhead** over **CAN** — no hotend MOSFET expected on the main board
- Labeled rails: `VCCIN24V`, `BEDVCC24V`, `FAN24V`, `HEADVCC24V` + `CAN±`
- `BEDTEMP` bed thermistor; `INP`/`INN` differential (likely load cell / `M2049`)
- Four driver boards with UART + STEP/DIR/EN; SWD found; rear **`DEBUGUART_*`** pads found (Nov 2026 silk); CH340G at front 5-pin
- SoM memory/PMIC markings and AP6236 module marking (2026-11)
- Wood-set stills: Amass brand on yellow 3-pin inlet; GL850G USB hub beside CH340G; black loop wires + Kapton near RF (role unknown); session video not analyzed
- Evening JPEGs: front 3-pin silk RX/TX/GND; rear DEBUGUART pad order GND→RX→TX; external flat antenna + coax at AP6236/Kapton (visual only); Amass series still unknown

**Still open**

- Motor label full string after partial `BJ42C29-01V…`; upper two-red-lead connector role ([motors_and_display.md](motors_and_display.md))
- Display flex complete marking; LCD vs CTP assignment of amber flex / white ribbon / edge board
- Extruder: tooth counts/ratio; hob aggression vs pinch; PLA groove severity ([extruder.md](extruder.md))


- STM32 pin map for driver UARTs, bed/`FAN24V` switching (`supx_decompile_report.md` §8)
- Whether bed heat switches on this board or a power PCB
- Head connector pinout/pitch; full CAN set
- STM32 RDP status (**inspect only** - never unlock/disable); confirm whether `DEBUGUART_*` is a Linux console **after measuring voltage**
- Front 3-pin vs `DEBUGUART_*` vs 5-pin/CH340G net relationships
- Why each axis has both `LIMITSW_` and `LIMIT_`
- SOIC-8 near SWD; QFN by second SWD
- Amass connector series/pitch; GL850G port mapping; black-wire identity; PPTC orderables

## Contributing board photos

If you own an IVI, please open an issue or PR with:

1. Clear top-down photos of each board with chip markings readable
2. Close-ups of connectors, SWD/UART, silkscreen
3. Multimeter continuity results if possible

Remove power first. Strip EXIF/GPS. **Redact printer serials.** Photos go in `docs/images/owners/` or `docs/images/board/`.
