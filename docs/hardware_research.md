# IVI hardware research

Compiled 2026-10-31 from public sources. **No internal board photos of the IVI were found online.** Labels: **[C]** confirmed by a source, **[F]** confirmed in firmware (see `supx_decompile_report.md`), **[G]** guess.

## Architecture
- **At least 4 boards [C]:** the IVI forum's December 2020 update lists an "ARM A7 control board (Related with LCD)" (Linux/Qt UI), "the fourth version of the motion control board" (STM32F407, Marlin), and a separate "power PCB and switch PCB".
- **November 2020 [C]:** the first version of the main board was finished, with small affiliated PCBs.
- **June 2019 [C]:** control board parts were sourced through Allchips.
- **Closed-loop motors [C][F]:** IVI's FAQ says each motor has a magnetic angle sensor and a separate motor drive board. The firmware talks to each driver over its own UART, using a custom protocol.
- **Toolhead identification [C][F]:** the FAQ says a chip on the printhead PCB identifies the head. The firmware queries the head over CAN2 (ID 0x12), and the head reports its type, serial number, firmware version, and nozzle size.
- **Head connector [C visually / G roles]:** every head render shows 8 gold pads in 2 staggered rows of 4 (`images/renders/`). Power, GND, CAN-H, CAN-L, and a detect/ID line is **only a guess**. The pitch and pin order are unknown.
- **Motion [C]:** a delta with HIWIN MGN9H rails and belt-driven carriages (`images/archive/IVI-joints.png`). The delta geometry matches the M503 dump.

## Images
- `images/renders/`: 14 BackerKit product renders (heads, base plate, full printer). See `SOURCES.md` there.
- `images/archive/`: renders retrieved from the Wayback Machine.

All images are IVI's material, included for preservation.

## Sources
- IVI forum (archived, about 160 threads): https://web.archive.org/web/2021*/forum.ivi3d.com/*. The beta thread is 1877, "beta-testers-share-your-experience". About 21 beta testers received units in February 2021.
- BackerKit updates: https://ivi.backerkit.com/hosted_preorders/project_updates. The December 15, 2020 update's "inner look of the printer" photos have been deleted.
- ivi3d.com FAQ and site assets: https://web.archive.org/web/2020*/ivi3d.com/*
- No results from FCC ID searches, Reddit, YouTube, or Chinese-language sources.

## Not yet retrieved (retry later)
The Wayback Machine listed `ivi3d.com` images named like `mcu-*.jpg`, `closed-loop-stepper-*.jpg`, and `Ivi_front_sensors_all-*.jpg`. On 2026-10-31 the Internet Archive had an outage, and CDX queries returned no captures for them. Retry with:
`https://web.archive.org/cdx/search/cdx?url=ivi3d.com&matchType=domain&filter=original:.*(mcu|closed-loop|sensors).*`

## Open questions
- Which pins drive the heater, fans, and outputs, and which pin pairs the driver UARTs are remapped to (see `supx_decompile_report.md` §8)
- The head connector pinout and pitch, and the full CAN message set (needs a CAN capture)
- Whether STM32 readout protection is enabled, and where the SWD pads are
- The ARM A7 board's SoC and its serial console header

## Contributing board photos
If you own an IVI, please open an issue or PR with:
1. Clear, well-lit, top-down photos of each board (motion, ARM/LCD, power, switch, motor driver, and the toolhead PCB), with chip markings readable
2. Close-ups of the connectors, debug headers (SWD, UART), and silkscreen
3. Multimeter continuity results from MCU pins to connectors, if you can

Remove the power cable first. Photos go in `docs/images/owners/`.
