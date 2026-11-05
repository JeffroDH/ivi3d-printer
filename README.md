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
| Motion controller | STM32F407VET6, **Marlin "V1.3.2-alpha"** (vendor build of Marlin 2.0.x, Mar 2021), 64 KB bootloader + app at `0x08010000` |
| Main board | One combined board, `A33_407MB_200916`: castellated **Allwinner A33** SoM (AXP223, Samsung DDR3L, 4 GB eMMC) for Linux/Qt UI + HTTP, and **STM32F407VET6** for Marlin. AP6236 Wi-Fi/BT + CH340G fitted. SWD + rear `DEBUGUART_*` pads located. See [docs/mainboard.md](docs/mainboard.md) |
| Motors | Smart **closed-loop** drivers (the closed loop lives in the drivers; the STM32 still sends STEP/DIR and reads faults over UART) |
| Tool heads | 3D print (0.15–0.4 mm nozzles; beta shipped 0.3 mm), laser, CNC (BLDC spindle). Each head has its own MCU on **CAN**; hotend heating/sensing, head fan, laser power and spindle are controlled through it |
| Other sensors | Door switch, filament runout, temp/humidity, load cell, probe/auto-level, thermal runaway protection |
| Network | Full TCP scan (2026-10-31): **only port 8080** open (kore HTTP API). No SSH/Telnet/FTP on any port. Many ports filtered (possible firewall). UDP 20050 for discovery. See [docs/network.md](docs/network.md) |
| USB-C | Direct serial link to the STM32 Marlin, **115200 8N1**, plain line G-code |

Saved printer output: [`docs/marlin_M115.txt`](docs/marlin_M115.txt), [`docs/marlin_M503_settings.txt`](docs/marlin_M503_settings.txt).

## Hardware research

**Main board map:** [docs/mainboard.md](docs/mainboard.md) has labeled photos of the combined `A33_407MB_200916` board and a pad/connector table. Highlights:

- Four closed-loop motor drivers (X, Y, Z, F = filament feeder), each wired with step/dir/enable **plus its own UART**, powered from `MTX/MTY/MTZ/MTF_24V`.
- Tool head on **CAN** (`CAN+`/`CAN-`, 3-wire cable) with its own `HEADVCC24V` supply; main input `VCCIN24V`; separate `BEDVCC24V` and `FAN24V`.
- **STM32 SWD pads** (`RST#`, `DIO`, `CLK`, `3V3`, `GND`) for an ST-Link backup or reflash, plus a second SWD set beside a small unidentified MCU.
- **Likely Linux console:** rear `DEBUGUART_RX`/`DEBUGUART_TX` pads (Nov 2026 silk; **measure voltage before attaching a USB-TTL adapter**). Front bottom-left 5-pin is next to a **CH340G** (USB-UART) - trace before use. See [docs/mainboard.md](docs/mainboard.md).
- `INP`/`INN` differential input with its own analog supply, probably the load cell used for probing (firmware has `M2049` load cell), plus SD/eMMC lines, USB host pads, `BUTTON` and `LED_CTL`.

**Tools for SWD and console access:** see [docs/tools.md](docs/tools.md).

**Background research:** board history, magnetic-encoder motors, head ID chips, the 8-pad head connector, and product renders are in [docs/hardware_research.md](docs/hardware_research.md).

## Repo layout

| Path | Contents |
|---|---|
| `orca/` | OrcaSlicer FDM profile (printer/filament/process + `.orca_printer` bundle) and optional IVI header hook ([orca/README.md](orca/README.md)) |
| `fusion/` | Autodesk Fusion post processors for the laser and CNC heads + header checker ([fusion/README.md](fusion/README.md)) |
| `docs/laser_cnc_gcode.md` | Laser (line/point) and CNC G-code + header format from IVI 3licer test files |
| `bridge/` | Orca Slicer / Anycubic Next bridge: OctoPrint-compatible service, Wi-Fi upload + USB serial streaming, tests; installers for macOS (launchd), Linux (systemd) and Windows (Task Scheduler) in `bridge/install/` |
| `ivi-control.sh` | Command-line client for the HTTP API (discover, status, print, pause, G-code, …) |
| `docs/slicer_report.md` | How IVI 3licer 1.6.2 (a rebranded Snapmaker Luban) talks to the printer — best map of the API |
| `docs/firmware_report.md` | Analysis of the UI-board app (`firmware`): discovery, serial link to the motion board, update flow |
| `docs/supx_report.md` | First-pass decode of `firmware.supx` (container, features) |
| `docs/supx_decompile_report.md` | Full Ghidra decompile of the motion firmware: .supx format, buses, pin map, custom M-codes, Marlin-port feasibility |
| `docs/supx_pack.py` | Packs a raw STM32 image into a `.supx` update file |
| `docs/marlin_M115.txt`, `docs/marlin_M503_settings.txt` | Firmware info and full settings dump from a beta unit |
| `firmware/Firmware/` | Stock firmware: `firmware` (UI app), `firmware.supx` (motion), `config.ini` / `config2.ini` (version + MD5) |
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
(`M3 S<percent>` on / `M5` off per segment; `M106 P0`/`M107 P0` = fan), CNC jobs are `.cnc` (`M3 P<percent>` / `M5`), both
centre-origin. Decoded from IVI 3licer test files in [docs/laser_cnc_gcode.md](docs/laser_cnc_gcode.md) (point mode has a
bogus-dwell slicer bug); Fusion posts in [fusion/](fusion/README.md). Not yet run on hardware.

## Firmware findings (summary)

- **Motion firmware is not encrypted or signed** — integrity is CRC-16 only.
- Smart drivers use a TMC-style UART protocol (CRC-8) with Open / Close(d-loop) / Servo modes and fault reporting
  (overload, locked rotor, phase stagger / high extruder pressure, over/undervoltage). Custom codes `M2910`–`M2915` inspect and tune them.
- Tool heads talk on CAN2 (ID 0x12). Custom codes include `M2005` (versions/SN), `M2010` (door check), `M2049` (load cell),
  `M2080` (head type), `M2411 S1–S4` (job state machine), `M997` (reboot to bootloader).
- The STM32 speaks plain line G-code only; the `AA 55` framed protocol in the slicer is for the slicer↔UI-board path.

Details: [`docs/supx_decompile_report.md`](docs/supx_decompile_report.md), [`docs/firmware_report.md`](docs/firmware_report.md),
[`docs/slicer_report.md`](docs/slicer_report.md).

## Update file (`.supx`) format

All checksums are CRC-16/XMODEM, little-endian. Layout: 8-byte file header (length, format version 2, whole-file CRC) →
`A1 03` header block (load address `0x08010000`, length, CRC) → 256-byte records (`A2 40`, u32 flash address, 248 data bytes, CRC) →
`A2 0B` / `A3 02` trailer. The bootloader (`0x08000000`–`0x0800FFFF`) is not in the file and is never overwritten by updates.

```bash
python3 docs/supx_pack.py raw.bin out.supx                          # base defaults to 0x08010000
python3 docs/supx_pack.py raw.bin out.supx --verify firmware.supx   # check byte-identical rebuild
```

Before flashing anything custom: check the STM32 read-protection level and back up the full 512 KB flash (including the
bootloader) with an ST-Link on the SWD pads.

## Status and roadmap

- ✅ Discovery, serial link, and update format documented. Wi-Fi API tested: upload/execute_code work; print control is 404 on current firmware (USB serial works).
- ✅ **Orca Slicer / Anycubic Next bridge (v0.1, [`bridge/`](bridge/README.md), untested on hardware):** a small local service that looks like an OctoPrint server to Orca and streams jobs over **USB serial** (`M2411 S2` + line-by-line G-code); Wi-Fi can only upload until firmware enables print control. Orca would use a delta profile built from the M665 values above. Snapmaker Luban can't be used directly: it only connects to Snapmaker machines.
- 🔍 **Modern Marlin:** feasible but a big job. The delta motion, pins and endstops port directly; the smart-driver UART link, CAN tool-head link (including hotend temperature control via the head) and touchscreen compatibility must be written. Estimate **~3–5 weeks for FDM-only, ~2–3 months** for full laser/CNC/UI parity. Open items need hardware: mapping driver UART pads to STM32 pins (multimeter), bed/`FAN24V` switching, full CAN frame meanings (CANable capture), bootloader behaviour (SWD backup).
- ❓ The HTTP server binary on the Linux side hasn't been recovered yet. Next step: measure `DEBUGUART_*` levels, listen with adapter RX+GND only, then decide on a matching USB-serial hookup (see [docs/mainboard.md](docs/mainboard.md)).

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
