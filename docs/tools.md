# Hardware tools

These are the tools for going beyond Wi-Fi (port 8080) and the USB-C Marlin serial link. Pad locations are in [mainboard.md](mainboard.md).

> **Hard limits.** The STM32 on this board is irreplaceable, and the GD32 is held to the same rule until a separate decision says otherwise. Over SWD: no reset, no halt, no erase, no program, no option-byte writes. Never clear readout protection (unprotecting mass-erases the chip). Every hardware test is individually authorized.
>
> **Serial ports.** Rear silk **`DEBUGUART_RX` / `DEBUGUART_TX` / `GND`** and the front **3-pin** (facing the connector, left→right **TX, RX, GND**) are the same nets **[O]** and are the A33 console **ttyS2 at 115200 8N1** **[V]**. Use a 3.3 V USB-TTL with **VCC unconnected**, and open the terminal before power-on. The front **bottom-left 5-pin** beside **CH340C** is a different connector; its pinout is **[U]**. The CH340 itself sits on the A33 USB hub and is `/dev/ttyUSB0` to the STM32. Details: [mainboard.md](mainboard.md), [a33.md](a33.md).
>
> **Two SWD-style 5-pin headers:** **central** → STM32 **[O]**; **lower** near SD, top→bottom **1 DIO, 2 3V3, 3 CLK, 4 GND, 5 RST [O]** (pin 2 is not GND), continuous with the rear pads by the **GD32E230F4** **[O]/[P]**. Chip-to-header continuity is **[U]**. The GD32 firmware is a soft-power sequencer: [gd32.md](gd32.md).
>
> A printable contact block for the three DEBUGUART pads is [../hardware/uart-pogo-holder/README.md](../hardware/uart-pogo-holder/README.md). Photo pitch is approximate; print the bore coupon and check with calipers.


> **Affiliate disclosure:** the Amazon links below are affiliate links. As an Amazon Associate I earn from qualifying purchases, at no extra cost to you. Any equivalent part works.

| Tool | What it's for | Example |
|---|---|---|
| ST-Link V2-style SWD programmer | Inspect STM32 (and conditionally GD32) SWD; read-only RDP check / backup when allowed. **Never unlock/erase to dump.** | Owner ordered [AITRIP ST-Link V2-style ASIN B0FJXL5X5P](https://www.amazon.com/dp/B0FJXL5X5P) |
| USB-to-TTL serial adapter (set to match measured rail) | Candidate console on rear `DEBUGUART_*` (or front 3-pin) **after measuring levels**; do not assume the CH340C 5-pin is a safe TTL breakout | [HJHYUL CP2102, 3-pack with jumper wires](https://link.amazon/B03eMUPzG) |
| Multimeter with continuity mode | Map the board pads (driver UARTs, bed, fan, limits) to STM32 pins | Any |
| CAN USB adapter (CANable), optional | Sniff the toolhead CAN bus (500 kbit/s) for heater, fan, laser, and spindle messages. Listen-only; tap `CAN+`/`CAN-` and GND | [CANable PRO V2.0](https://link.amazon/B0d0s4BOo) |

Remove the power cable before you attach any wires.

## ST-Link to SWD pads

There are **two** SWD-style headers — pick the target deliberately:

| Header | Target (evidence) |
|---|---|
| **Central** (by STM32 LQFP) | **STM32F407** — owner traces **[O]** |
| **Lower** (near SD; top→bottom DIO, 3V3, CLK, GND, RST) | Rear pads continuous **[O]**; **likely GD32E230F4 [G]** (chip-pin continuity **[U]**) |

| Probe wire | Board pad |
|---|---|
| SWDIO | `DIO` |
| SWCLK | `CLK` |
| GND | `GND` |
| NRST / RST | `RST` / `RST#` |
| **3V3 / 5V on clone “ST-Link V2” dongles** | **Leave unconnected** when the board is already powered. On common AITRIP/clone pinouts those pins are **power outputs**, **not** a `VTref` sense input. Do **not** feed them into board `3V3` on a live printer. |

**Ordered probe:** AITRIP ST-Link V2-style **ASIN B0FJXL5X5P**. Electrical SWD (DIO/CLK/GND/RST) can work on both STM32 and many GD32 parts, but:

- Vendor / ST software is **STM32-centric**; GD32 often needs **OpenOCD `gd32e23x`** (or vendor ISP) rather than assuming ST utilities.
- Clone fidelity varies; treat as a cheap SWD adapter, not a guaranteed ST authentic probe.
- **Readout protection:** this unit is level 0 (`FLASH_OPTCR` `0x0FFFAAED`). **Never unlock, and never mass-erase**, on either MCU. No reset, halt, program, or option-byte write.

Software for macOS: `brew install stlink` / OpenOCD. The 2026-11-10 STM32 image (512 KB flash, system ROM, OTP, option bytes) is [firmware/stm32_dump/](../firmware/stm32_dump/README.md). Two flash reads matched. The read that produced it is [tools/stm32/openocd_readonly.cfg](../tools/stm32/openocd_readonly.cfg):

```
adapter driver st-link
transport select dapdirect_swd
reset_config none
swd newdap …
dap create …
target create … mem_ap -ap-num 0
init
mdw / dump_image
```

That session created no `cortex_m` target, because `cortex_m` examine writes DHCSR, DEMCR and the FPB, and it did not reset or halt. A later session uses the same pattern. See [stm32.md](stm32.md) and [backups.md](backups.md).

## USB-C bootloader check

`tools/stm32/bootloader_probe.py` sends `M997\n`, checks for `C4 05 B0 19 A2`, then sends `A4 02 AA AA AA AA 9F BD` to start the app. It never sends A1, A2, or A3, so it does not erase or program. Verified on the printer 2026-11-10 over `/dev/cu.usbmodem*` **[V]**.

Stop `ivi_bridge.py` first (LaunchAgent `com.ivi3d.bridge` on macOS). It holds the USB serial port while it runs, including when a print is going over Wi-Fi. Start it again after the probe exits.

```
python3 tools/stm32/bootloader_probe.py /dev/cu.usbmodem*          # prints the sequence
python3 tools/stm32/bootloader_probe.py /dev/cu.usbmodem1234 --go  # sends it
```

## USB-TTL on the debug UART

On this unit the link is 3.3 V, 115200 8N1, ttyS2. For a different board, measure `DEBUGUART_TX` against GND before trusting that.

1. Set the adapter to 3.3 V if it has a jumper. Leave VCC unconnected.
2. Hookup:

| Adapter | Board pad |
|---|---|
| RXD | board TX (`DEBUGUART_TX` if that is the transmitter) |
| GND | `GND` |
| TXD | **leave disconnected for first listen** |
| 3.3V / 5V | **leave unconnected** |

3. Open the terminal **before** power-on, 115200 8N1, no flow control. On this unit the boot log ends in a `#` root prompt; the return path (adapter TX to board RX) is required to type. A printable pogo block for the three pads is in [../hardware/uart-pogo-holder/README.md](../hardware/uart-pogo-holder/README.md).

## Oscilloscope vs CANable

A scope (especially one with a CAN decode option) can confirm the bus is alive and measure the bit rate (~500 kbit/s). It is a poor substitute for hours of frame logging. Prefer the CANable for mapping heater/fan/laser/spindle messages.
