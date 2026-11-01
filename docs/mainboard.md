# IVI main board: `A33_407MB_200916`

Photos taken by an owner on 2026-10-31 (EXIF/GPS stripped). Labels: **[P]** read from the photo silkscreen, **[F]** matches firmware decompile (`supx_decompile_report.md`), **[G]** guess.

| Center/right view | Left edge (connectors) |
|---|---|
| ![center](images/board/mainboard_center.jpg) | ![left edge](images/board/mainboard_left_edge.jpg) |

## What the board marking tells us
- `A33_407MB_200916` **[P]**: one **combined main board** carrying an **Allwinner A33** (quad Cortex-A7, runs Linux + the Qt UI + the HTTP server) and the **STM32F407** motion MCU (Marlin). `200916` is probably the design date, 2020-09-16 **[G]**.
- The forum's "ARM A7 control board (Related with LCD)" is this A33 side. Earlier notes guessing a Rockchip RK3128 (from `rk312x`/`sinlinx` strings in `firmware.bin`) were wrong; those strings likely come from a reused vendor SDK/toolchain **[G]**.
- The LCD/touch panel, Wi-Fi antenna, and power rails all land on this board. Motor driver boards and the power/switch PCBs are separate.

## Pads and connectors
| Silkscreen | Location | Meaning / status |
|---|---|---|
| `RST#`, `DIO`, `CLK`, `3V3`, `GND` | center, left of logo | **STM32 SWD** debug pads (NRST, SWDIO, SWCLK). ST-Link clips here for flash backup **[P]** |
| `MT1_24V`…`MT4_24V` | left edge, red bundle | 24 V feed to four motor driver boards (3 towers + extruder) **[P]/[G]** |
| `VBAT`, `VBATIN` | left / lower center | battery-backup (power-loss) input **[P]** |
| `F_UART_TX/RX`, `F_EN`, `F_DIR`, `F_STEP` | left edge | per-driver UART + STEP/DIR/EN for driver "F" (feeder/extruder? **[G]**) **[P][F]** |
| `Z_UART_TX/RX`, `Z_EN`, `Z_DIR`, `Z_STEP` | left edge | same for the Z tower driver **[P][F]**; X/Y equivalents appear on the right edge (partly legible) |
| `CHB`, `CHA` | left edge | unknown; CAN-H/L or encoder channels **[G]** |
| `DOOR_STAUS` (sic) | left edge | door switch **[P][F]** |
| `BEDTEMP`, `TMP`, `TMN`, `AGND`, `AVDD_3V3` | left edge | bed thermistor + an analog sensor pair (`TMP/TMN` likely a thermistor ±) **[G]** |
| `LIMITSW_X/Y/Z` | lower left | three tower MAX endstops **[P][F]** |
| `MT_24V`, `MT_12V7` | center | motor 24 V rail and a 12.7 V rail **[P]** |
| `BEDVCC24V`, `VCCIN24V`, `FAN24V`, `HEADVCC24V` | right edge | bed, input, fan and toolhead 24 V rails **[P]** |
| `CAN+`/`CAN-` style pads | right edge | toolhead CAN bus **[P][F]** (CAN2, head ID 0x12) |
| `CTP_SDA/SCL/RST/INT`, `CTPVCC_3V3` | top | capacitive touch controller (I²C) **[P]** |
| `LCDVCCIN`, `VGH_18V`, `VGL_-8V`, `DVDD_3V3`, `AVDD_10V3`, `VCOM_3V5`, `VLED+/-` | top | LCD panel bias and backlight rails **[P]** |
| shielded module + antenna lead | center/bottom | Wi-Fi **[P]** |

The `_TX`/`_RX` fragments seen at the far left of the center photo are the `F_UART`/`Z_UART` pads above, not a separate console. **No A33 Linux UART console header has been identified yet**; look for unpopulated 3–4 pin pads near the A33 (`UART0` on A33 is usually PF2/PF4 via the SD pins or PB0/PB1).

## Confirms vs. decompile
- One UART per closed-loop driver, plus STEP/DIR/EN from the STM32 **confirmed**.
- Three MAX endstops and a door switch **confirmed**.
- Toolhead on CAN with its own 24 V supply **confirmed**; heater/fan/laser power are on the head side, so no hotend MOSFET on this board is expected.
- SWD location found, so the readout-protection check and a full flash backup are now practical.

## Open questions
- Which STM32 pins / USART remap each `*_UART` pad uses (resolves §8 of the decompile report)
- `CHA/CHB`, `TMP/TMN` roles; legible right-edge X/Y labels
- A33 serial console location; boot media (eMMC/NAND/SD)
- STM32 RDP level (read via ST-Link: `st-info --probe`, or STM32CubeProgrammer)

## Multimeter tracing guide (power OFF)
1. Continuity mode. Put one probe on a labeled pad (e.g. `Z_UART_TX`), drag the other along the STM32F407VET6 (LQFP100) pins; pin 1 is at the dot.
2. Map pin number → port with the STM32F407 datasheet LQFP100 pinout (e.g. pin 47 = PB10 = USART3_TX).
3. Record in a table here: pad → pin → port → peripheral. Do the same for `F_*`, X/Y pads, `CHA/CHB`, `TMP/TMN`, `BEDTEMP`, `LIMITSW_*`, `DOOR_STAUS`.
4. For the A33 console: with power ON, measure unknown 3-pin pad groups to GND; a pad idling at 3.3 V that flickers at boot is TX. Use a 3.3 V USB-serial adapter at 115200.
5. Never apply 5 V adapters; SWD and UART are 3.3 V.
