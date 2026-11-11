# IVI 3D Printer — open documentation and tools

Community reverse-engineering notes, firmware archive, and control tools for the **IVI 3D Printer**, a modular
(FDM / laser / CNC) machine from a Kickstarter campaign. Beta units shipped, but **IVI has since gone defunct**:
the Kickstarter pledges were never delivered and the company website is down. Nobody else is supporting these
machines, so this repo collects what's needed to keep them running and to drive them from modern software
(e.g. Orca Slicer) instead of the stock IVI 3licer slicer.

## Hardware summary

| Item | Finding |
|---|---|
| Kinematics | **Delta** — `M665 L357.50 R160.31 H233.22` (rod, radius, height). Homes to MAX endstops. |
| Motion controller | STM32F407VET6 (IDCODE `0x10076413`, RDP level 0), **Marlin "V1.3.2-alpha"**. App at `0x08010000`; bootloader in sectors 0–1; Marlin `V81` settings in sectors 2–3 (sector 3 live). Full 512 KB dump: [firmware/stm32_dump/](firmware/stm32_dump/README.md). See [docs/stm32.md](docs/stm32.md) |
| Main board | One combined board, `A33_407MB_200916`: **Allwinner A33** (Linux/Qt UI + kore HTTP), **STM32F407VET6** (motion), **GD32E230F4** (soft power). CH340C on a GL850G hub links the A33 to STM32 USART2. `DEBUGUART` / front 3-pin is the A33 console (ttyS2, 115200). See [docs/architecture.md](docs/architecture.md) and [docs/mainboard.md](docs/mainboard.md) |
| Motors | Smart **closed-loop** drivers (the closed loop lives in the drivers; the STM32 still sends STEP/DIR and reads faults over UART) |
| Tool heads | 3D print (0.15–0.4 mm nozzles; beta shipped 0.3 mm), laser, CNC (BLDC spindle). Each head has its own MCU on **CAN**; hotend heating/sensing, head fan, laser power and spindle are controlled through it |
| Other sensors | Door switch, filament runout, temp/humidity, load cell, probe/auto-level, thermal runaway protection |
| Network | **TCP 8080** (kore) and **UDP 20050** (discover). Port 22 is closed because `sshd` is installed and not started. Upload names need exactly one dot (`cube.gcode`; `part_0.2mm.gcode` is HTTP 412). See [docs/network.md](docs/network.md) and [docs/a33.md](docs/a33.md) |
| USB-C | Direct serial link to the STM32, **115200 8N1**, plain line G-code. `M997` restarts into the bootloader (`STM32 Virtual ComPort` on the same port); `A4` starts the app again. Stop the Wi-Fi bridge first. See [docs/stm32.md](docs/stm32.md#recovery) |

Saved printer output: [`docs/marlin_M115.txt`](docs/marlin_M115.txt), [`docs/marlin_M503_settings.txt`](docs/marlin_M503_settings.txt).

## Hardware research

**Main board map:** [docs/mainboard.md](docs/mainboard.md) has labeled photos of the combined `A33_407MB_200916` board and a pad/connector table. Highlights:

- Four closed-loop motor drivers (X, Y, Z, F = filament feeder), each wired with step/dir/enable **plus its own UART**, powered from `MTX/MTY/MTZ/MTF_24V`.
- Tool head on **CAN** (`CAN+`/`CAN-`, 3-wire cable) with its own `HEADVCC24V` supply; main input `VCCIN24V`; separate `BEDVCC24V` and `FAN24V`.
- **Two SWD headers:** central → **STM32F407** (owner); lower near SD (1 DIO / 2 3V3 / 3 CLK / 4 GND / 5 RST) ↔ rear pads by **GD32E230F4** (owner continuity; chip-pin nets unmeasured). The STM32 read of 2026-11-10 (RDP level 0, `mem_ap` only) is in `firmware/stm32_dump/`. Later sessions stay read-only — see [docs/tools.md](docs/tools.md).
- **DEBUGUART / front 3-pin:** same nets (facing L→R TX, RX, GND). A33 console ttyS2, 115200 8N1, 3.3 V, adapter VCC unconnected. The front bottom-left 5-pin is a separate connector; the CH340C itself is the A33↔STM32 link. See [docs/mainboard.md](docs/mainboard.md) and [docs/a33.md](docs/a33.md).
- `INP`/`INN` differential input with its own analog supply, probably the load cell used for probing (firmware has `M2049` load cell), plus SD/eMMC lines, USB host pads, `BUTTON` and `LED_CTL`.

**Tools for SWD and console access:** see [docs/tools.md](docs/tools.md).

**Background research:** board history, magnetic-encoder motors, head ID chips, the 8-pad head connector, and product renders are in [docs/hardware_research.md](docs/hardware_research.md). Motor-body / display-flex notes (2026-11-05): [docs/motors_and_display.md](docs/motors_and_display.md). Extruder gears/hobs: [docs/extruder.md](docs/extruder.md).

## Repo layout

| Path | Contents |
|---|---|
| `orca/` | OrcaSlicer FDM profile (printer/filament/process + `.orca_printer` bundle) and optional IVI header hook ([orca/README.md](orca/README.md)) |
| `fusion/` | Autodesk Fusion post processors for the laser and CNC heads + header checker ([fusion/README.md](fusion/README.md)) |
| `docs/laser_cnc_gcode.md` | Laser (line/point) and CNC G-code + header format from IVI 3licer test files |
| `bridge/` | Orca Slicer / Anycubic Next bridge: OctoPrint-compatible service, Wi-Fi upload + USB serial streaming, tests; installers for macOS (launchd), Linux (systemd) and Windows (Task Scheduler) in `bridge/install/` |
| `ivi-control.sh` | Command-line client for the HTTP API (discover, status, print, pause, G-code, …) |
| `docs/README.md` | Index of the topic docs |
| `docs/architecture.md` | Three processors, ports, and how a job starts |
| `docs/stm32.md` | Motion firmware: chip ID, RDP, bootloader, update protocol, fans, CAN, UARTs |
| `docs/a33.md` | Touchscreen board: Qt, sshd, kore upload, update package, boot |
| `docs/gd32.md` | GD32E230 soft-power controller |
| `docs/wifi_touch.md` | Wi-Fi upload, the USB bridge, and touch injection |
| `docs/backups.md` | What has been backed up, and the restore routes |
| `docs/home_session/` | Runbook, quick reference, and upload/probe notes for the touch navigator |
| `tools/` | `ivi_touch_nav` v0.2.0, STM32 dump/probe helpers, framebuffer and tap helpers |
| `hardware/uart-pogo-holder/` | Printable pogo block for the DEBUGUART pads |
| `docs/slicer_report.md` | How IVI 3licer 1.6.2 (a rebranded Snapmaker Luban) talks to the printer |
| `docs/firmware_report.md` | UI-board ELF: discovery, serial link, commands the UI sends |
| `docs/supx_report.md` | `.supx` container notes |
| `docs/supx_decompile_report.md` | Ghidra pass: pins, driver UART protocol, custom M-codes |
| `docs/supx_pack.py` | Packs a raw STM32 image into a `.supx` update file |
| `docs/marlin_M115.txt`, `docs/marlin_M503_settings.txt` | Firmware info and full settings dump from a beta unit |
| `firmware/Firmware/` | Stock firmware: `firmware` (UI app), `firmware.supx` (motion), `config.ini` / `config2.ini` (version + MD5) |
| `firmware/stm32_dump/` | 2026-11-10 read-only SWD dump: 512 KB flash, system ROM, blank OTP, option bytes, MD5SUMS |
| `Beta Test Program/` | IVI's beta-program documents (blank templates and info sheets) |

## Quick start: `ivi-control.sh`

Requires `curl` (and `python3` for `discover`). Set the printer address and token with environment variables:

```bash
export IVI_IP=192.168.50.85          # your printer's IP (default shown)
export IVI_TOKEN=e0cf19a3-e0a4-4740-825f-bdffb49e58b8   # stock default token
./ivi-control.sh discover            # find printers on the LAN
./ivi-control.sh connect             # confirm on the printer screen if asked
./ivi-control.sh status
./ivi-control.sh print part.gcode    # upload + prepare + start (type 3DP)
./ivi-control.sh print logo.nc Laser # laser job; CNC jobs use type CNC
./ivi-control.sh pause | resume | stop
./ivi-control.sh gcode "G28"         # raw G-code via execute_code
./ivi-control.sh upload big.gcode    # store only (chunked for files >= 20 MiB)
```

The token is the default hard-coded in the stock slicer. If your printer rejects it, `connect` with an empty token
(`IVI_TOKEN= ./ivi-control.sh connect`) and use the `token` it returns.

## Protocol summary

**Discovery:** send ASCII `discover` to the broadcast address on **UDP 20050**. Reply:
`IVI3D@<ip>|Model:IVI 3D Printer|status:IDLE`.

**HTTP API** at `http://<ip>:8080/api/v1/` (kore). Endpoint list comes from the stock slicer; **tested against the beta firmware on 2026-11-01**:

| Endpoint | Tested result |
|---|---|
| `POST connect` | ✅ needs `token=` (empty token rejected) → `{"token":…,"readonly":true,"series":"IVI Printer","headType":1,"hasEnclosure":true}` |
| `POST disconnect`, `POST setSystemTime` | ✅ work |
| `GET status?token=` | ⚠️ only ever returns `{"status":"IDLE"}` — no temps/progress, even while printing from the touch screen |
| `POST execute_code` | ✅ `token=&code=<one G-code line>` (e.g. `M503`) |
| `POST upload` | ✅ multipart `token`, `file` → 201 "Upload successfully" (file then started from the touch screen) |
| `POST sliceUpload` | ⚠️ exists; returns 412 `md5 err` unless the md5 field is right. Fields: `index`, `count`, `md5`, `size`, `filename`, `file` (2 MiB chunks) |
| `prepare_print`, `start_print`, `pause_print`, `resume_print`, `stop_print` | ❌ **404 on this firmware** |
| `confirm`, `accept`, `set_readonly`, `readonly` | ❌ 404 |

The session is always `readonly:true`. Adding `readonly=false`, `readOnly=0`, `isReadOnly=false`, `confirm=1` or `accept=1` to
`connect` changes nothing, and no known request clears it (on Snapmaker it clears via an accept prompt on the touch screen).
The slicer never checks the flag. IVI 3licer's Wi-Fi **Run** does `execute_code` (G53/G0/G54/G92) → upload → `prepare_print`
(404) and then silently fails. **Wi-Fi workaround: use Send, then start the job on the touch screen.**

> **Future firmware:** this is a beta unit and the Wi-Fi API looks unfinished. A later official or **custom firmware may
> enable the print-control endpoints over Wi-Fi** — re-test them after any firmware update.

**USB serial (works, verified 2026-11-01):** USB-C CDC at 115200 baud. The printer reports Firmware V1.3.2-alpha, Tool Head
FW V1.1, HW V1, `Head 3DP,0.3mm`. Start a PC job with `M2411 S2` (plus `M1001 L` if firmware ≥ 2.4.0) → `PC start work` /
`trigger work: ok`, state `WORKING_PC`; then stream G-code line by line, one per `ok`. `M2410` pause, `M2411 S1` resume,
`M2411 S3` stop (firmware "trigger stop"; also what IVI 3licer sends on connect if a stale PC job exists). Job states,
locked-rotor and kill handling: [docs/laser_cnc_gcode.md](docs/laser_cnc_gcode.md#firmware-findings-2026-11-01). An FDM print was started this way from IVI 3licer (G53, G28, M82, M104 S215, M140 S50,
M109 S215 with `busy: processing` while heating, then printing). On macOS, allow the slicer under **Privacy & Security →
Local Network**, or Wi-Fi requests fail with "No route to host".

The stock slicer prepends a `;Header Start … ;Header End` block to jobs (see `docs/slicer_report.md`). Laser jobs are `.nc`
(`M3 S<percent>` on / `M5` off per segment), CNC jobs are `.cnc` (`M3 P<percent>` / `M5`), both centre-origin.
Decoded from IVI 3licer test files in [docs/laser_cnc_gcode.md](docs/laser_cnc_gcode.md); Fusion posts in [fusion/](fusion/README.md). Not yet run on hardware.

> **Fan command.** On this firmware `M106 S0` **without `P` turns both head fans on** (`S` is ignored). IVI 3licer and Orca both emit that line meaning "fan off". Use `M107` or `M106 P0 S0` on an FDM head. `M106 P0` is sent only when the head class is FDM, so it does nothing on a laser or CNC head. The auto heatsink-fan rule is on from boot; with a laser head it forces P1 on every second, so `M107` holds that fan off for at most about 1 s. See [docs/stm32.md](docs/stm32.md#fans).

## Firmware findings (summary)

- **Motion firmware is not encrypted or signed** — integrity is CRC-16 only.
- Smart drivers use a TMC-style UART protocol (CRC-8) with Open / Close(d-loop) / Servo modes and fault reporting
  (overload, locked rotor, phase stagger / high extruder pressure, over/undervoltage). Custom codes `M2910`–`M2915` inspect and tune them.
- Tool heads talk on CAN2 (ID 0x12). Custom codes include `M2005` (versions/SN), `M2010` (door check), `M2049` (load cell),
  `M2080` (head type), `M2411 S1–S4` (job state machine), `M997` (reboot to bootloader).
- The STM32 speaks plain line G-code only; the `AA 55` framed protocol in the slicer is for the slicer↔UI-board path.
- Head fans are on/off CAN frames. `M106` with no `P` forces both on.

Details: [`docs/stm32.md`](docs/stm32.md), [`docs/supx_decompile_report.md`](docs/supx_decompile_report.md), [`docs/firmware_report.md`](docs/firmware_report.md),
[`docs/slicer_report.md`](docs/slicer_report.md).

## Update file (`.supx`) format

All checksums are CRC-16/XMODEM, little-endian. Layout: 8-byte file header (length, format version 2, whole-file CRC) →
`A1 03` header block (load address `0x08010000`, length, CRC) → 256-byte records (`A2 40`, u32 flash address, 248 data bytes, CRC) →
`A2 0B` / `A3 02` trailer. `A3`'s `0A BA 00 00` is the CRC-16/XMODEM of the programmed range (`0xBA0A`). The bootloader (sectors 0–1) and the settings sectors (2–3) are not in the file; they are in the SWD dump. Updates rewrite the application from `0x08010000` only and cannot erase the bootloader or the settings.

```bash
python3 docs/supx_pack.py raw.bin out.supx                          # base defaults to 0x08010000
python3 docs/supx_pack.py raw.bin out.supx --verify firmware.supx   # check byte-identical rebuild
```

The 512 KB backup for this unit is [firmware/stm32_dump/](firmware/stm32_dump/README.md) (RDP level 0). A later SWD session is still no reset, halt, erase, program, or option-byte write. Recovery order, gentlest first: [docs/stm32.md](docs/stm32.md#recovery) and [docs/backups.md](docs/backups.md).

## Status and roadmap

- ✅ Discovery, serial link, and update format documented. Wi-Fi API tested: upload/execute_code work; print control is 404 on current firmware (USB serial works).
- ✅ **Orca Slicer / Anycubic Next bridge (v0.1, [`bridge/`](bridge/README.md), untested on hardware):** a small local service that looks like an OctoPrint server to Orca and streams jobs over **USB serial** (`M2411 S2` + line-by-line G-code); Wi-Fi can only upload until firmware enables print control. Orca would use a delta profile built from the M665 values above. Snapmaker Luban can't be used directly: it only connects to Snapmaker machines.
- 🔍 **Modern Marlin:** feasible but a big job. The delta motion, pins and endstops port directly; the smart-driver UART link, CAN tool-head link (including hotend temperature control via the head) and touchscreen compatibility must be written. Estimate **~3–5 weeks for FDM-only, ~2–3 months** for full laser/CNC/UI parity. Open items need hardware: mapping driver UART pads to STM32 pins (multimeter), bed/`FAN24V` switching, full CAN frame meanings (CANable capture). The bootloader and the SWD backup are documented.
- ✅ A33 console (ttyS2), boot chain, kore upload rules, and the GD32 power sequencer are documented ([docs/a33.md](docs/a33.md), [docs/gd32.md](docs/gd32.md)). sshd is present and not started. Touch injection is `tools/ivi_touch_nav` (offline tests only so far); the hardware session is [docs/home_session/RUNBOOK.md](docs/home_session/RUNBOOK.md).

## Contributing

There may only be a few dozen of these printers out there. If you own one, issues and pull requests are welcome —
especially board photos, CAN captures, SWD dumps, working Orca profiles, or laser/CNC workflow notes.

## License

Original work in this repo (documentation, scripts, `supx_pack.py`) is licensed under
[CC BY-NC-SA 4.0](LICENSE).

**Not covered by the license:** the firmware files in `firmware/`, material extracted from IVI's installers, and the
`Beta Test Program/` documents are IVI's material. They are included here for preservation and interoperability
because the company no longer exists.

- Orca Slicer bridge: [bridge/README.md](bridge/README.md), plan [docs/orca_bridge.md](docs/orca_bridge.md)
