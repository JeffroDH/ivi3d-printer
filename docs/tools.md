# Hardware tools

These are the tools for going beyond Wi-Fi (port 8080) and the USB-C Marlin serial link. Pad locations are in [mainboard.md](mainboard.md).

> **Serial port caution (2026-11):** the board has **more than one** serial-looking connector.
> Rear silk: **`DEBUGUART_RX` / `DEBUGUART_TX` / `GND`**. Front **3-pin** by micro-USB is the same nets by **owner continuity [O]** (facing connector L→R: **TX, RX, GND**). **Measure voltage first** (do not assume 3.3 V); which CPU owns the UART **[U]**.
> The front **bottom-left 5-pin** beside **CH340C** is a **third** path (USB-UART bridge) — not the DEBUGUART breakout. Trace to CH340C pins and measure before connecting. Details: [mainboard.md](mainboard.md) §6.
>
> **Two SWD-style 5-pin headers:** **central** → STM32 **[O]**; **lower** near SD top→bottom **1 DIO, 2 3V3, 3 CLK, 4 GND, 5 RST [O]** (pin2 ≠ GND), continuous with rear pads by the **GD32E230F4** **[O]/[P]**. Chip↔header pin continuity **not measured [U]**.


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
- **Readout protection / RDP:** inspect status only. **Never unlock or mass-erase** to force a firmware dump on either MCU.

Software for macOS: `brew install stlink` / OpenOCD. Read-only probe first; write nothing until a full backup is saved when RDP allows.

## USB-TTL listen on debug UART (only after measuring)

1. Measure `DEBUGUART_TX` (and/or the front 3-pin TX candidate) against GND with the printer powered and idle.
2. Only if the levels match your adapter, prepare a listen-first hookup:

| Adapter | Board pad |
|---|---|
| RXD | board TX (`DEBUGUART_TX` if that is the transmitter) |
| GND | `GND` |
| TXD | **leave disconnected for first listen** |
| 3.3V / 5V | **leave unconnected** |

3. Open a serial terminal (e.g. 115200 8N1 as a starting guess **after** levels are known), power on, and capture boot text. Do not use TX/RX swapping or baud thrashing as a substitute for measuring levels. Add adapter TX only once you understand the link.

## Oscilloscope vs CANable

A scope (especially one with a CAN decode option) can confirm the bus is alive and measure the bit rate (~500 kbit/s). It is a poor substitute for hours of frame logging. Prefer the CANable for mapping heater/fan/laser/spindle messages.
