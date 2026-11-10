# STM32F407 motion controller

Stock application image: `firmware/Firmware/firmware.supx`, reported as Marlin **V1.3.2-alpha**. The container format and the Ghidra pin / driver-UART notes live in [supx_decompile_report.md](supx_decompile_report.md) and [supx_report.md](supx_report.md). This page is the current map of flash, the update protocol, fans, CAN, and the serial ports.

Tags: **[V]** in the image or the A33 app · **[I]** inferred · **[U]** unknown · **[D]** datasheet.

## Flash map

STM32F407VE is 512 KiB at `0x08000000` **[D]**.

| Range | Sector | Contents | Evidence |
|---|---|---|---|
| `0x08000000`–`0x08007FFF` | 0–1 (32 KiB) | Vendor bootloader. Not inside `.supx`. No dump exists in this repo | **[I]** (the app never executes there; update replies are not in the app) |
| `0x08008000`–`0x0800FFFF` | 2–3 (16 KiB each) | Settings. The app erases and programs these (M500 / M502 / M504 / M2050). Default sector is 3 at `0x0800C000` | **[V]** |
| `0x08010000`–`0x0803779F` | 4 onward | Application, 161696 bytes from `.supx`. VTOR = `0x08010000`. Reset vector `0x08016E2D`, SP `0x20020000` | **[V]** |
| `0x08037800`–`0x0807FFFF` | rest | Expected blank `0xFF` | **[I]** |

The application image contains no writes to `OPTKEYR` or `OPTCR` and no ST option-key constants **[V]**. Whether the bootloader sets readout protection is **[U]** (the bootloader image is not available).

An 8-second independent watchdog is started at boot and kicked from the idle and thermal paths **[V]**.

## Update protocol

Settings → Update Firmware on the touchscreen is the only trigger. The A33 app sends `M997` through the normal G-code sender, closes the port, then opens `/dev/ttyUSB0` itself at 115200 8N1 with RTS false and DTR true **[V]**.

`M997` in the application only executes `NVIC_SystemReset`. It writes no RAM or flash flag **[V]**. The bootloader's rule for staying in update mode is **[U]**.

The host then writes the `.supx` body as-is and waits for 5-byte replies. Checksums are CRC-16/XMODEM, little-endian. `tools/stm32/supx_stream.py` reproduces the frames and checks the CRCs. It sends nothing.

| Step | Bytes | Success reply |
|---|---|---|
| Erase / header | 12 B from file offset 8: `A1 03`, load `0x08010000`, length `0x277C4`, CRC | `C1 ?? E0` (`E2` erase error) |
| Records | 256 B × 652: `A2 40`, address, 248 data, CRC. 100 µs gap | `C2 ?? E0` (`E3` write error) |
| Remainder | 44 B: `A2 0B`, end address `0x080377A0` | `C2 ?? E0` |
| Check | 8 B: `A3 02 0A BA 00 00 DE 3A` (fixed bytes, not the image CRC) | `C3 ?? E0` (`E4` CRC error) |
| Run | `A4 02 AA AA AA AA 9F BD`, sent twice, 300 ms apart | none |

Other errors use `C0 ?? Ex` (E1 unknown command, E6 data). Bootloader entry itself is four tries of the ASCII line `M997\n`, expecting `C4 ?? B0 ?? ??` within about 0.6 s **[V]**.

This is not ST's ROM bootloader (no `0x7F` sync, no ACK `0x79`). The ROM UART bootloader is not reachable on USART2 **[D]**. ROM USB DFU on PA11/PA12 is possible only with BOOT0 high at reset; the BOOT0 pin has not been located **[U]**. With readout protection at level 1, DFU reads are refused, and clearing protection mass-erases the chip. Do not do that.

The `.supx` path rewrites the application only. It does not restore the bootloader or the settings sectors. A same-version controller re-flash is offered when `firmware.supx` and `config2.ini` MD5 match; the touchscreen half of a package is applied only when its version float is greater than the **1.222 compiled into the running UI binary** **[V]**. Package rules: [a33.md](a33.md#update-package).

Pack or check a file with `docs/supx_pack.py` (load address `0x08010000`).

### SWD

A full 512 KiB read is the only way to capture the bootloader and the settings. It is allowed only when readout protection is level 0, and only under a separate authorization. Until then: no reset, no halt, no erase, no program, no option-byte writes. See [tools.md](tools.md).

## Serial ports and USB

| Object | Peripheral | Pins | Baud | Role |
|---|---|---|---|---|
| `MYSERIAL0` | USB OTG FS | PA11 / PA12 | CDC | **PC port** (USB-C) **[V]** wiring to the connector **[I]** |
| `MYSERIAL1` | USART2 | TX PD5 / RX PD6 | 115200 8N1 | **Screen port**, CH340 → A33 `ttyUSB0` **[V]** pins, **[I]** wiring |
| `Serial3` | USART3 | TX PD8 / RX PD9 | 115200 | X closed-loop driver |
| `Serial4` | UART5 (pins) | TX PC12 / RX PD2 | 115200 | Y driver. The object is named UART4; the pin map selects UART5 |
| `Serial5` | UART4 (pins) | TX PC10 / RX PC11 | 115200 | Z driver |
| `Serial6` | USART6 | TX PC6 / RX PC7 | 115200 | Extruder (F) driver |

A second USART2 object exists and is never `begin()`'d **[V]**. Driver frames are the TMC-style UART protocol in [supx_decompile_report.md](supx_decompile_report.md) (CRC-8, registers `0x00`–`0x15`).

Both host ports share one 6-deep command FIFO, tagged with the source port, strict arrival order **[V]**.

- `ok` and command replies go to the originating port only.
- `CMD buffer: N` (the screen app's pacing ack) goes to USART2 only.
- `M108`, `M112`, `M410`, and `M2410` are handled by a per-port emergency parser and are not queued.
- `M2001 S1` restarts the USB CDC object only. If a job is active it force-stops it, with no check of which port owns the job.
- `M2155 S<seconds>` (0–60) is one global auto-report interval. `S0` turns reports off for both ports. The touchscreen enables `M2155 S5` after it sees a head. The app never sends `M2007`; `M2007` and the `M2155` block both broadcast `Working Status:` (`IDLE`, `WORKING_PC`, `WORKING_SCREEN`, `ERROR`) to both ports.

`Working Status: WORKING_PC` makes the touchscreen open a full-screen lock. The only button on it sends `M108` and `M2001 S1`.

## Fans

Head fans are **on/off**, not PWM. Both channels are CAN frames, not mainboard pins **[V]**.

| Command | Effect |
|---|---|
| `M106` with **no `P`** | **Both fans on. `S` is ignored.** `M106 S0` turns both fans **on** |
| `M106 P0 S<n>` | FDM head only: fan 0 on when `S` ≠ 0, off when `S` = 0. On a laser or CNC head, P0 sends nothing |
| `M106 P1 S<n>` | Fan 1, any head class. `S` = 0 is off, any other `S` is on |
| `M106 P2` or higher | Ignored |
| `M107` | Both fans off. **`P` is ignored**, so `M107 P0` still turns both off |
| `M2006 S1` | Enables a thermostatic rule (not saved by M500, not sent by the app or by stock slicer samples): FDM turns P1 on above 40 °C reported by the head; laser forces P1 on; CNC does nothing |

IVI 3licer and Orca both emit `M106 S0` where a stock Marlin profile means "fan off". On this firmware that line turns the head fans on, and they stay on until an `M107`. Prefer **`M107`** or **`M106 P0 S0`**.

The touchscreen fan switch sends bare `M106` / `M107` (both channels). Laser samples from IVI 3licer use `M106 P0`, which does not drive a fan unless the installed head is FDM.

No `M106` / `M107` / `M2006` path drives a mainboard MOSFET **[V]**. The two unused `FAN24V` headers cannot be selected with `P` ≥ 2. They may be always-on 24 V **[U]** until measured. `M42` can toggle a free GPIO only after that pin is traced, and not on stepper or endstop pins.

## CAN toolhead

CAN2, PB5 RX / PB6 TX, 500 kbit/s, standard TX id **0x12** only. RX filter is accept-all and the id of the head's own frames is **[U]** **[V]**. The connector, owner-measured **[O]**: pin 1 `HEADVCC24V`, 2 `CAN+`, 3 `CAN−`, 4 GND.

Controller → head, byte 0 **[V]**:

| Byte | Payload | Meaning |
|---|---|---|
| `A0` | — | Type and version query |
| `A3` | — | Info query (`M2080`) |
| `A7` | — | CNC BLDC speed query |
| `B1` | byte | Laser / spindle power (`M3` / `M5`) |
| `B2` | 0/1 | Tool enable |
| `B6` | u16 LE | Hotend target °C **[I]** |
| `B3` | 0/1 | Fan P0, FDM class only |
| `B4` | 0/1 | Fan P1, any class |
| `B8` | 1/2 | Tool power enable / disable |

Head → controller **[V]**:

| Frame | Contents |
|---|---|
| `A0` | b1 type code, b2/b3 firmware major/minor, b4 hardware version |
| `A1` | b1 bits 0 and 1 = fan state, bit 4 = probe, bit 6 = probe present; b2 tool on/off; b4–b7 float hotend °C |
| `A2` | float32 hotend °C |
| `A6` / `C0` | probe state |
| `A7` | u16 big-endian CNC speed |

There is no PID on the wire and no head-firmware update command. Reported temperatures and fan bits do not time out if the head stops sending **[V]**. A stuck high reading cannot be distinguished from a real one on the controller side **[I]**.

### Head type codes (`A0` byte 1)

| Code | `M2051` text | Class |
|---|---|---|
| 0 | `error:No Print Head` | unchanged |
| 1 | `info:Head Laser` | 1 |
| 2 | `info:Head CNC` | 2 |
| 3, 4, 5, 6, 7, 8 | `info:Head 3DP,0.3mm`, `0.15mm`, `0.2mm`, `0.25mm`, `0.35mm`, `0.4mm` | 3 FDM |
| other | `error:No Print Type Unknown` | unchanged |

Codes 3–8 change the display string only. Motion, extrusion, and temperature limits do not scale with the diameter **[V]**. The head serial number is in controller EEPROM, not on CAN. `M2056` prints it. `M2055` checks the CRC-16 and rewrites the record if the check fails. `M2005` prints controller firmware plus the head firmware, hardware, and that serial. The class is refreshed at boot and on every `M2051`.

## Commands the touchscreen sends

141 literals are listed in [data/stm32_app_commands.csv](data/stm32_app_commands.csv) (`feature`, `command_literal`, `function`, `function_addr`, `ref_addr`, `evidence`, `notes`). The app streams the file, strips comments, and injects UI lines ahead of file lines. It does not send M20–M30, M105, M2007, M600/M701/M702, or `N…*cs` framing **[V]**.

Job control from the UI:

| Action | Lines |
|---|---|
| Start | `M2001 S1`, then `M2411 S2` |
| Pause / resume / stop | `M2410` / `M2411 S1` / `M2411 S3` |
| Stop cleanup | `M108`, `M104 S0`, `M140 S0` |
| End of file | `M2411 S3`, plus `M5` for laser/CNC |

`M2411 S2` is accepted only in the idle state. The UI does not look at `Can't start work` and will still stream the file. Unknown G-code hits an empty handler and still returns `ok` **[V]**.

The dispatcher table for vendor M-codes (M2001, M2005–M2007, M2010, M2049, M2050, M2051, M2055, M2056, M2080, M2111, M2155, M2410, M2411, M2910–M2915, M997) is in [supx_decompile_report.md](supx_decompile_report.md). `M2051` is the head-type query. `M2050` is a settings helper and is not sent by the app.

## Related

[architecture.md](architecture.md) · [a33.md](a33.md) · [laser_cnc_gcode.md](laser_cnc_gcode.md) · [tools.md](tools.md) · [research/stm32](research/stm32/README.md)
