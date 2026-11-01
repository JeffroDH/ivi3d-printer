# IVI3D motion controller (firmware.supx, "Marlin V1.3.2-alpha") — decompilation report
Generated 2026-10-31. Image: `supx_raw.bin` loaded in Ghidra 12.1.4 headless (ARM Cortex LE, base 0x08010000,
SRAM/CCM/peripheral blocks added, vector table seeded). 971 functions decompiled → `supx_decomp.c` (on the box).
Literal-pool pointers were resolved to strings/RAM addresses with a helper script. No SVD was applied (peripheral
addresses were resolved by hand from literal pools). **Nothing was sent to the printer.**

Confidence tags: **[V]** verified in code/data · **[I]** inferred, likely · **[?]** open.

## 1. .supx container — fully solved [V]
All checksums are **CRC-16/XMODEM** (poly 0x1021, init 0, no reflection, no xorout), stored little-endian
(the same routine exists in the firmware at 0x080259E6).

| Offset | Field |
|---|---|
| 0 | u32 file_len − 8 |
| 4 | u16 format version = 2 |
| 6 | u16 CRC over file[8:EOF]  (0xDC2A) |
| 8 | header block `A1 03`, u32 load addr 0x08010000, u32 0x000277C4 (= image + 36), u16 CRC of these 10 bytes (0x9A1A) |
| 20 | 652 × 256-byte records: `A2 40`, u32 flash addr, 248 data bytes, u16 CRC of the first 254 bytes |
| end | trailer: `A2 0B`, u32 end addr 0x080377A0, `00 00`, "ASCII" zero-padded to 42 B, u16 CRC(trailer[0:42]); then `A3 02 0A BA 00 00`, u16 CRC(trailer[0:50]) |

(The earlier report mis-framed records by 2 bytes; the CRC sits at the end of each record.) All 652 record CRCs,
the header CRC, trailer CRCs and whole-file CRC verify. `supx_pack.py supx_raw.bin out.supx --verify firmware.supx`
rebuilds a **byte-identical** file. Meaning of `A1/A2/A3` second bytes (03/40/0B/02) and `0A BA` is not fully known
[?] — they are reproduced literally; likely bootloader command codes (A1 = begin/erase, A2 = write, A3 = finish) [I].

## 2. Bootloader / M997 / app layout
- App at 0x08010000, 64 KB bootloader at 0x08000000 (not in the file). SystemInit sets **VTOR = 0x08010000** [V].
- **M997** (handler 0x080226E8): parses an optional numeric arg (discarded), then DSB + `AIRCR = 0x05FA0004`
  (**NVIC_SystemReset**). No RAM magic word / flag is written before reset [V] → the bootloader decides on its own
  (most likely waits briefly for the UI board on serial after every reset) [I].
- The UI board (firmware.bin) drives updates: sends `M997`, waits for "now in bootloader", checks the file
  (size, type, `file crc error %04x %04x` = the header CRC), "update start, erase flash", streams blocks, expects
  status bytes with high nibble `0xC?` (errors: command unknown, flash erase/write error, command crc error, data error,
  check update crc error; success "system update complete…", then `jumpToApp()`) [V strings / I sequence].
- No signature or encryption anywhere; integrity is CRC-16 only [V]. Whether the bootloader checks the app's vector
  table (SP in RAM range) before jumping is unknown [?] (bootloader not available).

## 3. Buses
| Function | Peripheral | Settings | Evidence |
|---|---|---|---|
| Host link to Linux UI board **and** USB-C port | Two Marlin serial ports (objects 0x2000111C and 0x20001378), both 115200 8N1 | `MYSERIAL0/1`; "Current working port is not SCREEN/PC" — the firmware tracks which port owns the job | [V] baud, [I] which UART each is |
| Smart closed-loop drivers X/Y/Z/E0 | **Serial2/3/4/5 = USART2, USART3, UART4, UART5**, one driver per UART, 115200 8N1 | FUN_0802DB8C | [V] |
| Default pins for those UARTs (STM32duino first PinMap match) | USART2 PA2/PA3, USART3 PB10/PB11, UART4 PA0/PA1 or PC10/PC11, UART5 PC12/PD2 | PinMap tables at 0x08034140/0x080340BC | [I] — PB10/PB11 and PA0/PA1 are also used as GPIO below, so actual pins need board check |
| Tool head | **CAN2**, PB5 = RX, PB6 = TX (AF9), IRQ CAN2_RX0 | Prescaler 6, BS1 6 tq, BS2 7 tq → 42 MHz/6/14 = **500 kbit/s**, normal mode; host TX std-ID **0x12** | [V] |
| EEPROM / temp-humidity sensor | Bit-banged I²C-style on D69/D70 (PB10/PB11 per variant table) | FUN_08019C8C etc. | [I] |

### 3a. Driver protocol (UART, TMC-like) [V]
- CRC-8, poly 0x07, data bytes processed LSB-first (identical to Trinamic TMC22xx UART CRC).
- Read request (4 B): `55 00 REG CRC`. Write (8 B): `55 00 (REG|0x80) D0 D1 D2 D3 CRC` (data little-endian).
- Reply (8 B): `55 00 REG D0..D3 CRC`; a 4-byte reply with valid CRC = "ok" ack.
- Registers seen: `0x00` version (u32) · `0x03` dir/flags (bit0 = Dir; write 0x400000/0x400001) · `0x04` currents:
  hi-u16 = **HDCP**, lo-u16 = **HDCE** (init X/Y/Z = 1100/1500, E0 = 900/1500) · `0x05` mode (low byte: 2 Open,
  3 Close, 4 Servo; bit8 = RS; init writes Close-loop for all) · `0x10` broadcast write 0x100 (M2915, probably save) ·
  `0x14` fault flags: bit0 Overload, bit1 locked rotor (stops), bit2 phase stagger (on E0 = "High extruder pressure",
  pauses 5 s), bit8 Overvoltage, bit9 Undervoltage · `0x15` "Driver location".
- So the "closed loop" lives in the drivers; the MCU still produces STEP/DIR (below).

### 3b. Tool-head protocol (CAN2, ID 0x12, 8-byte frames, byte0 = command) [V cmd bytes, I meaning]
Host → head: `A0` request version/SN · `A3` request head info (type / nozzle) · `A7` query u16 (likely CNC BLDC speed) ·
`B1 n` laser/spindle power % (ramped in 10 % steps, 300 ms apart) · `B2 0/1` hotend heater on/off ·
`B6 u16` hotend target temp (clamped to MAXTEMP−15) · `B3 0/1` fan (head type 3) · `B4 0/1` head fan
(auto on above 40 °C) · `B8 1/2` head power/tool enable on/off.
Head → host: `A0` version/hw/SN fields · `A1` 8-byte status bitfield (7 flags + u32 + byte) · `A2` u32 ·
`A3` 3×u16 head info · `A6` byte · `A7` u16 · `C0` byte. Head serial number is stored in EEPROM as 16 bytes with a
CRC-16/XMODEM over 14 ("serial number check crc error").
→ The **hotend heater, its sensor, the head fan, laser and spindle are all controlled through the head MCU over CAN**,
not by MCU pins.

## 4. Pin map (STM32duino digital pin → port pin, via variant table at 0x080342F0) [V pins, I roles]
| Role | Pin | Notes |
|---|---|---|
| X STEP / DIR / EN | PC4 / PC5 / PB0 | stepper init order (FUN_0802CA34), DIR from set_directions |
| Y STEP / DIR / EN | PB9 / PE0 / PE1 | |
| Z STEP / DIR / EN | PB1 / PE7 / PE8 | |
| E0 STEP / DIR / EN | PE11 / PE12 / PE13 | |
| Endstops (delta homes to MAX) | PE9, PE10, PB8 (INPUT_PULLUP) | X_MAX/Y_MAX/Z_MAX [I]; the probe appears to come via the head/CAN [?] |
| Door switch | PE3 (INPUT_PULLUP) | M2010 reads it |
| Analog inputs | PA0, PA1 | thermistor channels (bed/chamber or hotend backup) [I]; MINTEMP 5 °C, MAXTEMP 299 °C table scan |
| Output, low at temp init | PE4 | bed heater / SSR [I] |
| PWM/analog out | PD3 | fan or light [I] |
| Board power/enable outputs set high at boot | PB13, PB14, PD0, PD1, PC9 (PA6/PA7 outputs) | rails / driver enable [?] |
| Output, low at boot | PD15 | [?] |
| CAN2 | PB5 RX, PB6 TX | tool head |
Timers/ADC/DAC instances referenced are standard STM32duino tables; per-signal timer channel mapping for heaters
was not resolved [?].

## 5. G/M-code dispatcher (FUN_080230F8) — custom codes [V]
| Code | Function |
|---|---|
| M997 | reset into bootloader (see §2) |
| M2001 [S] | re-open host serial at 115200; if S1, stop/hand over job (claims the PC port) |
| M2005 | print firmware version, tool-head FW/HW version + SN |
| M2006 [S0/1] | Auto Fan Switch |
| M2007 | internal (thunk 0x08025D60, not decoded) |
| M2010 [S0/1] | auto door check on/off; no S = report door opened/closed |
| M2049 | load-cell report (" info:weight_0 / weight_1 ") |
| M2050 / M2051 | internal (reset/settings helpers, not decoded) |
| M2055 | read head SN from EEPROM, verify CRC-16, rewrite if bad, prints "OK" |
| M2056 | print head SN ("SN:"), CRC-16 check |
| M2060 / M2061 | self-test strings ("sensor: XMotor:ok …" / "Print:ok …") |
| M2080 | report head type ("info:<n>") via CAN `A3` |
| M2111 S/L | S0 print position_shift + current position; S1/S2 L0–6 set debug/error level |
| M2155 S<sec> | set host-watchdog/timeout, max 60 s |
| M2410 | **no-op** in the motion firmware (pause is handled by the UI host) |
| M2411 S1/S2/S3/S4 | trigger resume / start work / stop / finish (job state machine; errors "Can't … in current status") |
| M2910 [S] | driver info dump (Version/HDCP/HDCE/Sub/Mode/Dir/RS) |
| M2911 X/Y/Z/E | set driver HDCP current (reg 4, HDCE fixed 1500) |
| M2912 X/Y/Z/E | set driver direction (reg 3) |
| M2913 / M2914 | set driver mode Open/Close/Servo (reg 5) / set RS |
| M2915 | broadcast reg 0x10 = 0x100 (save) |
**AA 55 framing is NOT implemented in the STM32 firmware** [V: no 0xAA/0x55 frame parser]; it's the Luban/3licer
protocol to the Linux UI board. The STM32 only speaks line G-code (with N/checksum, M110, resend).

## 6. Machine config
- Delta, FIX_MOUNTED_PROBE, bilinear ABL + G33 auto-calibrate, M48, linear advance, runout + M600, thermal runaway,
  1 extruder, chamber temp, SOFTWARE_POWER, BINARY_FILE_TRANSFER, EMERGENCY_PARSER, babystepping, arcs.
- From M503 (earlier session): diagonal rod 357.5 mm, radius 160.3 mm, height 233 mm; steps/PID/mesh in
  `marlin_M503_settings.txt`.
- Hotend MAXTEMP 299 °C (target clamped to 284), MINTEMP 5 °C; bed plausibility 40–…; thermistor table type not
  identified [?] (sensor read happens partly on the head).
- Drivers: smart closed-loop, current 1100 mA-units X/Y/Z, 900 E (HDCE 1500), close-loop mode.

## 7. Modern Marlin 2.1.x on this board — feasibility
**Ports directly (a few days):** STM32F407VE env (`STM32F407VE_black`-like), delta kinematics + G33, probe/ABL,
endstops, STEP/DIR/EN pins above, door, runout, PA0/PA1 thermistors, EEPROM (bit-bang I²C → `I2C_EEPROM` soft), dual
serial at 115200, `VECT_TAB_OFFSET 0x10000` / `board_build.offset = 0x10000`, then `supx_pack.py` to package.

**Must be written (the real work):**
1. Driver link (~300–500 LOC): 4 UARTs, the 55-frame/CRC-8 protocol, init currents + close-loop mode, fault polling
   (reg 0x14) → Marlin kill/pause, M2910–M2915. Moderate — protocol is now known.
2. Tool-head CAN link (~800–1500 LOC): CAN2 500k driver, A0/A3/A7 queries, head-type detection, **hotend temperature
   control through the head** (custom TEMP_SENSOR / heater backend — Marlin assumes local ADC + PWM, so this is the
   most invasive change), head fan, laser (B1/B2/B8 mapped onto Marlin's SPINDLE_LASER / M3/M4/M5), CNC spindle +
   speed readback. Head frame semantics are partly inferred and need sniffing with a CAN adapter.
3. UI-board compatibility (~500 LOC): reproduce M2001, M2005/M2055/M2056/M2080, M2010, M2155 watchdog, M2411 S1–S4 job state
   machine, M2049 weights, exact response strings the Qt UI parses ("info:Head 3DP,0.4mm", "trigger work: ok", "ok",
   etc.). Without this the touchscreen/HTTP job path breaks. (No AA 55 needed on the STM32.)

**Risks:** the update path only rewrites 0x08010000+; the bootloader stays, so a bad app is normally recoverable by
re-sending a good .supx (if the bootloader enters update mode without a working app [?]). Worst case recovery =
SWD (ST-Link, ~$10) to reflash, *if* RDP is not set — check RDP level first and **back up the full 512 KB flash incl.
bootloader over SWD before any experiment**. Also: laser/spindle safety (door interlock must be kept), thermal
runaway now depends on CAN temp reports (must fault on CAN loss), driver fault handling.

**Effort (one experienced firmware dev):** FDM-only, UI-compatible, no laser/CNC: ~3–5 weeks. Full parity incl.
laser + CNC + all UI codes: ~2–3 months incl. CAN sniffing and testing. **Verdict: feasible but not cheap**; the
benefit over stock is small unless a specific feature/bug matters. A middle path — keep stock firmware and only drive it
better from Orca/Luban — remains far cheaper.

## 8. Unresolved
- Exact UART TX/RX pins (needs board photo/continuity), role of PB13/PB14/PD0/PD1/PC9/PD15/PE4/PD3.
- Heater/fan timer-channel mapping; thermistor table type.
- Full CAN head-frame field meanings (needs live CAN sniff); probe signal path.
- Bootloader behaviour (entry window, app validity check, RDP level) — needs SWD read.
- Meaning of the A1/A3 control-block bytes in the .supx (reproduced exactly, so not blocking).
