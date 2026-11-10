# STM32F407 motion controller

Stock application image: `firmware/Firmware/firmware.supx`, reported as Marlin **V1.3.2-alpha**. The container format and the Ghidra pin / driver-UART notes live in [supx_decompile_report.md](supx_decompile_report.md) and [supx_report.md](supx_report.md). This page is the current map of flash, the update protocol, fans, the laser head, CAN, and the serial ports.

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

Head fans are **on/off**, not PWM. Both channels are CAN frames, not mainboard pins **[V]**. The firmware has no air-assist output. The only fan frames are `B3` (P0) and `B4` (P1).

The auto heatsink-fan rule is **on from boot**. Head init stores `1.0` in the auto-fan flag at boot (`FUN_08026420` at `0x0802642C`, flag at struct +8, RAM `0x200063C8`) **[V]**. `M2006` is the command that changes it. It is not saved by M500, and the touchscreen app and the stock slicer samples do not send it. `M2006 S1` is the boot state. `M2006 S0` turns the rule off.

With the rule on, a 1 s tick (`FUN_08026254` → `FUN_0802620c`) applies it **[V]**:

- FDM (class 3): P1 on when the head reports above 40 °C, off at or below that.
- Laser (class 1): P1 forced on (`B4 01`) every second, for as long as a laser head is installed.
- CNC (class 2): the tick does nothing.

`M107` turns the fans off at once. On a laser head the next tick turns P1 back on, so the off lasts at most about 1 s. The laser-head fan stays off only after `M2006 S0`. On an FDM head the same tick turns P1 back on once the reported temperature is above 40 °C.

| Command | Effect |
|---|---|
| `M106` with **no `P`** | **Both fans on. `S` is ignored.** `M106 S0` turns both fans **on** |
| `M106 P0 S<n>` | FDM head only: fan 0 on when `S` ≠ 0, off when `S` = 0. On a laser or CNC head, P0 sends nothing |
| `M106 P1 S<n>` | Fan 1, any head class. `S` = 0 is off, any other `S` is on. On a laser head the 1 s tick forces it back on while the auto-fan rule is on |
| `M106 P2` or higher | Ignored |
| `M107` | Both fans off at once. **`P` is ignored**, so `M107 P0` still turns both off. The tick above can turn P1 back on |
| `M2006 S0` | Auto-fan rule off |
| `M2006 S1` | Auto-fan rule on. This is also the state after boot |

IVI 3licer and Orca both emit `M106 S0` where a stock Marlin profile means "fan off". On this firmware that line turns the head fans on. For an FDM head, **`M107`** or **`M106 P0 S0`** is the off command. On a laser head `M106 P0` sends nothing, and `M107` does not hold P1 off.

The touchscreen fan switch sends bare `M106` / `M107` (both channels). Laser samples from IVI 3licer use `M106 P0`. That line is not air assist, and it drives a fan only when the installed head is FDM.

No `M106` / `M107` / `M2006` path drives a mainboard MOSFET **[V]**. The two unused `FAN24V` headers cannot be selected with `P` ≥ 2. They may be always-on 24 V **[U]** until measured. `M42` can toggle a free GPIO only after that pin is traced, and not on stepper or endstop pins.

## CAN toolhead

CAN2, PB5 RX / PB6 TX, 500 kbit/s, standard TX id **0x12** only. RX filter is accept-all and the id of the head's own frames is **[U]** **[V]**. The connector, owner-measured **[O]**: pin 1 `HEADVCC24V`, 2 `CAN+`, 3 `CAN−`, 4 GND.

Controller → head, byte 0 **[V]**:

| Byte | Payload | Meaning |
|---|---|---|
| `A0` | — | Type and version query |
| `A3` | — | Info query (`M2080`) |
| `A7` | — | CNC BLDC speed query |
| `B1` | byte | Laser power from the 101-entry table, or CNC spindle power (`M3` / `M5`). See [Laser](#laser) |
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

## Laser

This is the motion firmware's laser behaviour **[V]**, plus the host where noted. It has not been run on a laser head. Power the printer on with the laser already attached.

### Identification and arming

Boot setup calls head init (`FUN_08026420`). That sends CAN `A0` (controller standard id 0x12, 500 kbit/s) and reads byte 1 of the head's `A0` reply. Type code 1 sets class 1. `M2051` then prints `info:Head Laser`, `Current Status: ON/OFF` (head `A1` byte 2), and `Current Power:` of the last S **[V]**. The controller's receive filter accepts every frame. The head's own CAN id is **[U]**.

Only that boot path arms a laser (`FUN_080261c0`, taken when the class is 1). It sends CAN `B2 01` (tool enable) and sets the power-ceiling byte to `0xFF`. `M2051` refreshes the class and does neither **[V]**. Plug the laser in after power-on and the ceiling stays 0, so every `M3 S…` maps to power 0. How the head itself treats a later plug-in is **[U]**.

No G-code or M-code exists only to arm the laser. `M104` and `M109` share the `B2` frame. `M104 S0` sends `B2 00` to a laser head. Whether the head treats that as disabled is **[U]**. The touchscreen's stop cleanup sends `M104 S0` anyway. Leave `M104` out of laser files. Whether the laser still fires after a stopped job is **[U]**.

### Commands

| Code | What the firmware does |
|---|---|
| `M3 S<n>` | Waits until queued moves finish, then `power = table[min(n, 255)]` and CAN `B1 <power>`. Stores n as the last S |
| `M3` with no S | Re-sends the last S |
| `M4` | Same handler as `M3`. The M3/M4 distinction is not read. There is no dynamic or inline mode |
| `M5` | Waits for queued moves, then `B1 00`. The last S is kept, so a later bare `M3` restores it |
| `G4 P<ms> L<n>` | Waits for queued moves, sends `B1` for table entry n, dwells, then `B1 00`. A bare `L` re-uses the last S. `L` is honoured only on a laser head |
| `G0` / `G1` with `S` | `S` is not parsed (X/Y/Z/E/F only). Planner blocks copy the last S and the stepper ISR recomputes the table value, and that path sends no CAN frame. There is no inline power |
| `M3` just after pause | Ignored for 3 s once a pause starts (status 3–5) |

Pause (`FUN_08026bd0`) and stop (`FUN_08026708`) send `B1 00`. Resume (`FUN_08026aa8`) re-sends the last S when the laser was on. `M2411 S3` and the touchscreen's end-of-file `M5` both turn the laser off **[V]**.

Each `M3` and `M5` drains the planner, so the head stops briefly on every segment boundary. IVI 3licer files do the same.

### Power table

S is a percent, 0–100. It indexes a 101-byte table at `0x08035D34`. The byte is the `B1` payload **[V]**:

| S | `B1` |
|---|---|
| 0 | 0 |
| 1 | 50 |
| 5 | 108 |
| 6 | 77 |
| 10 | 129 |
| 20 | 153 |
| 50 | 204 |
| 80 | 237 |
| 90 | 254 |
| 96–100 | 255 |

The curve is steep at the low end and is not monotonic (S5 is 108, S6 is 77). What the head does with the byte is **[U]**. A PWM duty out of 255 is the reading the table suggests **[I]**.

**Never send S above 100.** The index is clamped to 255, and a negative or oversized value becomes 255. S101–S255 read past the table into the bytes that follow it: S101 → 101, S128 → 0, S200 → 32, S255 → 101 **[V]**.

### Door

The door input is PE3 (`DOOR_STAUS` on the board). The check is enabled at boot. `M2010 S0` turns it off and `M2010 S1` turns it on (`Auto door check on` / `off`). For every head except FDM, the idle loop prints `warning:Door opened` or `warning:Door closed` when the pin changes. Pin high means opened **[V]**.

A door-open prints that warning and leaves laser power where it is. `B1` stays set until `M5`, pause, stop, or the end of a `G4`. There is no enclosure-fan check, no tube check, and no watchdog that clears laser power when the host goes quiet. The 8 s IWDG resets the MCU when the firmware stops kicking it **[V]**.

The host has to act on the warning. IVI 3licer maps `warning:Door opened` to a pause (`M2410`, which sends `B1 00`) **[V]**. The touchscreen app has a door-warning path; whether that path pauses a job is **[U]**. The Mac bridge does not watch for the warning.

### Posts

IVI 3licer laser files, and the Fusion post in [../fusion/](../fusion/README.md), emit `M106 P0` at the start and `M107 P0` at the end. On a laser head the first sends nothing. The second turns P1 off until the next 1 s tick. Proposed post changes are pending a hardware test and are not in this tree: clamp S to an integer 0–100, assert `M2010 S1` and `M2006 S1`, turn P1 on with `M106 P1`, and leave the heatsink fan running at the end (no `M107`, no air-assist property).

### Still to measure on the machine

Low power, scrap, laser safety glasses, door closed. Each item is its own decision.

1. Laser installed at power-on. `M2051` should print `info:Head Laser` and `Current Power: 0`. `M107` should stop the head fan, and the fan should restart within about 1 s. `M2006 S0` followed by `M107` should leave it off. Then `M2006 S1`.
2. Open and close the door at idle and look for the warning lines on USB. Whether the touchscreen pauses a job is a separate dry run at S0.
3. Short burns at S1, S5, S10, and S20. S1 maps to 50/255, so a mark at S1 is expected if the head treats `B1` as duty.
4. After a touchscreen stop (`M104 S0` → `B2 00`), one S5 segment, to see whether the laser still fires.
5. Optional listen-only CAN capture of boot, `M3`, `M5`, and `M107`, for the `B1` / `B4` frames and the head's id.

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
