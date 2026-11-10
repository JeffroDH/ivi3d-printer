# GD32E230F4 firmware analysis (IVI3D board), offline only

**Input:** a 16384-byte flash image, base 0x08000000. SHA-256 `540f4967976e390a5a1822347a148b332ee3da78329d03e1880c851ab17f0167`. The image is not in this repo. A second read of the same chip was byte-identical. No hardware was touched for this write-up. See [docs/gd32.md](../../gd32.md).
**Method:** a recursive-descent disassembler (Capstone 5.0.9, Thumb/M-class/ARMv8-M) starting from every vector, call target, code-pointer literal and the scatter-load table. Peripheral literals were annotated from register tables parsed out of the GD32E23x User Manual. Instruction bytes not reached this way are only alignment padding (`c046` nop / `0000`) and five unreferenced `b .` stubs. (`binutils-arm-none-eabi` couldn't be installed because apt had no package, so there was no second-disassembler cross-check.)

## Files
| File | Content |
|---|---|
| `gd32e230_annotated.s` | Full listing, split into vector table / code / LITERAL pools / padding / scatter table / .data. Peripheral literals carry register names, and SRAM variables are named |
| `functions.md` | All 56 functions with addresses, sizes, callers and roles |
| `peripherals.md` | Peripheral, GPIO and pin map with evidence addresses, plus the SRAM map |
| `pseudocode.c` | C-like reconstruction (main state machine, ADC, SysTick) |
| `datasheet_pin_tables_excerpt.txt` | TSSOP20 / LGA20 pin tables from the datasheet |
| `tools/` | Scripts that regenerate the listing (`run.sh`) |

## Flash extent
- **Used: 0x08000000–0x0800113F (4416 bytes, 27% of 16 KiB).** Every byte from 0x08001140 to 0x08003FFF is 0xFF (11968 bytes, erased).
  - 0x08000000–0x080000CB: vector table (51 entries)
  - 0x080000CC–0x08001117: code and literal pools
  - 0x08001118–0x08001137: scatter-load region table
  - 0x08001138–0x0800113F: .data initial values (72000000 and 1)
- There is no second image, no bootloader/application split, no strings, and no configuration or calibration data block.

## Key findings
- **Toolchain:** Arm/Keil C library startup (`__main`, `__scatterload`), GD32E23x SPL/CMSIS helpers, built at -O0. There are **no printable strings**: no version text, protocol tables or command bytes.
- **CPU evidence:** the code uses `udiv` (0x080008FC, 0x080010B8) and `movw`. Both exist on ARMv8-M Baseline (Cortex-M23) and **don't exist on ARMv6-M (Cortex-M0/M0+)**.
- **Clocks:** internal IRC8M → PLL ×18 → 72 MHz. No crystal, 2 flash wait states, SysTick at 1 ms. Nothing is interrupt-driven except SysTick.
- **Peripherals used:** only RCU, FMC_WS, GPIOA, GPIOB, ADC (channel 3), SysTick, NVIC priority and VTOR. **No USART, I2C, SPI, timers, DMA, EXTI, watchdog or RTC.** The chip has no data link of any kind to another processor; its only connections are plain GPIO levels plus one analog input.
- **Behaviour** (see `pseudocode.c`). It's a soft power button / power sequencer:
  1. **Boot:** PA4, PB1 and PA7 go low, and PA2 goes high and then low after 500 ms. The chip then waits in **standby** for a PA1 press (active-low, 50 ms debounce).
  2. **Power on (at press):** PA2, PA4 and PB1 go high, and the chip waits for release.
  3. **While on:**
     - A press toggles PA2.
     - Holding the button toggles PA2 every 500 ms.
     - Holding for about 3 s turns power off, or releasing after about 2.5–3 s does. Power-off means PB1 goes low, then PA4 goes low 10 ms later, and the chip returns to standby.
     - A shorter press just returns PA2 to steady on.
  4. **Low-voltage path:** if the 10-sample average on PA3 falls to ≤1985/4095 (about 1.60 V at a 3.3 V reference), the chip latches PA7 high and keeps PB1 high. After 3000 ms (6000 ms if PA6 is high) it drops PB1, then PA4. It then loops forever, so only a reset or power cycle recovers.

## Likely role
| Claim | Confidence | Basis |
|---|---|---|
| The firmware implements a button-driven soft-power controller with LED feedback and a timed shutdown triggered by an analog level | **High** | Follows directly from the code |
| PA1 = front power button, PA2 = power/status LED | **Medium** | Pull-up input with debounce and long-press logic; a toggled/steady output. The board has `BUTTON` and `LED_CTL` pads on its right edge (mainboard.md), but they aren't traced to the GD32 |
| PA4 and PB1 = enables for power switches or regulators (sequenced off PB1 → 10 ms → PA4) | **Medium** | On/off sequencing pattern only |
| PA3 = supply/brown-out sense through a divider, PA7 = "power-fail" warning to the main CPU, PA6 = "extend hold to 6 s" request from the main CPU | **Low to medium** | Fits a power-loss-save scheme, but nothing in the image names these nets |
| No serial link to the A33 or the STM32, and no stepper, heater, or thermistor drive | **High** | USART, I2C, SPI, timers, and DMA are never clocked. One ADC channel, fixed threshold |

### Pin map and checks that would confirm the role (power off; continuity/diode mode)
The package isn't confirmed. Photos suggest LGA20, so check pin 1 orientation.

| Signal | TSSOP20 | LGA20 | Check |
|---|---|---|---|
| PA1 (button) | 7 | 4 | Continuity to `BUTTON` pad / front switch. Expect a press to pull it to GND |
| PA2 (LED) | 8 | 5 | Continuity to `LED_CTL` / LED driver |
| PA3 (ADC) | 9 | 6 | Find the resistor divider and which rail it senses (24 V in? 5 V?). Measure the ratio |
| PA4 | 10 | 7 | Trace to a MOSFET gate, regulator EN, or the power/switch-PCB connector |
| PB1 | 14 | 11 | Same as PA4 |
| PA6 (input) | 12 | 9 | Trace to an STM32F407 or A33 GPIO |
| PA7 (output) | 13 | 10 | Trace to an STM32F407 or A33 GPIO (power-loss pin?) |
| SWDIO / SWCLK / NRST | 19 / 20 / 4 | 16 / 17 / 1 | Confirms the `DIO`/`CLK`/`RST#` pads belong to this chip |

Live check, only if you want one and it's safe: with the printer on, PA4 and PB1 should read high. After a hold of about 3 s, PB1 should fall first and PA4 about 10 ms later. The GD32 must stay powered from a standby rail; if it doesn't, the design guess is wrong.

## Identity checks in the image

- The code uses `udiv` and `movw`. Both exist on ARMv8-M Baseline (Cortex-M23) and do not exist on ARMv6-M.
- SRAM is 4 KiB. The initial SP `0x20000420` is 0x20 bytes of variables plus a 0x400-byte linker stack.
- Reset vector `0x080000E1` is `Reset_Handler`. The default handler is `b .` at `0x080000F2`. SVC and PendSV are empty `bx lr`. Only SysTick does work.
- `0x40013800` (USART0) does not appear. USART is never clocked.
- The last non-`0xFF` byte is `0x0800113F`. `0xFF` starts at `0x08001140`.

## Caveats
- Two reads of this chip matched byte for byte. Option bytes and readout protection were not read. This listing does not say whether the image can be restored.
- Board-level meanings of all pins are inferred from code behaviour only. No GD32 pin has been continuity-tested.
- The voltage threshold assumes VREF = VDDA = 3.3 V, which isn't measured.
- The exact hold timing depends on the `% 500 == 0` exact-match test and the loop rate, so it's uncertain by about ±1 blink step.
- The datasheet pin tables come from the LCSC-hosted copy of the GD32E230xx datasheet (early revision). The same pin numbers appear in the GigaDevice Rev 3.x search excerpt.
