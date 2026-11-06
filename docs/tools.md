# Hardware tools

These are the tools for going beyond Wi-Fi (port 8080) and the USB-C Marlin serial link. Pad locations are in [mainboard.md](mainboard.md).

> **Serial port caution (2026-11):** the board has **more than one** serial-looking connector.
> Rear silk on the current photos reads **`DEBUGUART_RX` / `DEBUGUART_TX` / `GND`** (older docs said `UGUART_*` - unverified against these photos). Front **3-pin** by micro-USB is another candidate. **Measure voltage first** (do not assume 3.3 V).
> The front **bottom-left 5-pin** sits next to a **WCH CH340C** USB-UART bridge (earlier RS-232 guess superseded). Trace the header to CH340C pins and measure before connecting anything. Details: [mainboard.md](mainboard.md) §6.


> **Affiliate disclosure:** the Amazon links below are affiliate links. As an Amazon Associate I earn from qualifying purchases, at no extra cost to you. Any equivalent part works.

| Tool | What it's for | Example |
|---|---|---|
| ST-Link V2 (SWD programmer) | Check STM32 readout protection and back up the full flash, including the 64 KB bootloader that isn't in `firmware.supx` | [AITRIP ST-Link V2 with cable](https://link.amazon/B0dqOexs0) |
| USB-to-TTL serial adapter (set to match measured rail) | Candidate console on rear `DEBUGUART_*` (or front 3-pin) **after measuring levels**; do not assume the CH340C 5-pin is a safe TTL breakout | [HJHYUL CP2102, 3-pack with jumper wires](https://link.amazon/B03eMUPzG) |
| Multimeter with continuity mode | Map the board pads (driver UARTs, bed, fan, limits) to STM32 pins | Any |
| CAN USB adapter (CANable), optional | Sniff the toolhead CAN bus (500 kbit/s) for heater, fan, laser, and spindle messages. Listen-only; tap `CAN+`/`CAN-` and GND | [CANable PRO V2.0](https://link.amazon/B0d0s4BOo) |

Remove the power cable before you attach any wires.

## ST-Link to SWD pads
| ST-Link | Board pad |
|---|---|
| SWDIO | `DIO` |
| SWCLK | `CLK` |
| GND | `GND` |
| RST | `RST#` |
| 3.3V | `3V3`, only as a voltage reference if your tool needs one. **Never connect 5V.** |

Software for macOS: `brew install stlink` (`st-info --probe`) or OpenOCD. Do a read-only check and a backup first, and don't write anything until the full flash has been saved.

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
