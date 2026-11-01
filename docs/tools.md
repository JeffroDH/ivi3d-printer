# Hardware tools

These are the tools for going beyond Wi-Fi (port 8080) and the USB-C Marlin serial link. Pad locations are in [mainboard.md](mainboard.md).

> **Affiliate disclosure:** the Amazon links below are affiliate links. As an Amazon Associate I earn from qualifying purchases, at no extra cost to you. Any equivalent part works.

| Tool | What it's for | Example |
|---|---|---|
| ST-Link V2 (SWD programmer) | Check STM32 readout protection and back up the full flash, including the 64 KB bootloader that isn't in `firmware.supx` | [AITRIP ST-Link V2 with cable](https://link.amazon/B0dqOexs0) |
| 3.3 V USB-to-TTL serial adapter (CP2102) | Connect to the likely A33 Linux console (`UGUART_RX`/`UGUART_TX`) | [HJHYUL CP2102, 3-pack with jumper wires](https://link.amazon/B03eMUPzG) |
| Multimeter with continuity mode | Map the board pads (driver UARTs, bed, fan, limits) to STM32 pins | Any |
| CAN USB adapter (e.g. CANable), optional | Sniff the toolhead CAN bus (500 kbit/s) for heater, fan, laser, and spindle messages | Not tested yet |

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

## CP2102 to UGUART console
| Adapter | Board pad |
|---|---|
| RXD | `UGUART_TX` |
| TXD | `UGUART_RX` |
| GND | `GND` |
| 3.3V / 5V | **leave unconnected** |

Run `screen /dev/tty.usbserial-* 115200`, then power on the printer. If the output is garbled, try 57600 or 9600, or swap TX and RX.
