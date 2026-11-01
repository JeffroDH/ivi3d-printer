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
| Main board | One combined board, `A33_407MB_200916`: **Allwinner A33** (Cortex-A7) Linux running a Qt touchscreen app (`firmware`, v1.222) plus a separate HTTP server, and the STM32F407 on the same PCB. SWD pads located. See [docs/mainboard.md](docs/mainboard.md) |
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
- **Likely Linux console:** `UGUART_RX`/`UGUART_TX` pads near the A33 (3.3 V, probably 115200 8N1, untested). This is the most promising way to get a shell and back up the Linux side.
- `INP`/`INN` differential input with its own analog supply, probably the load cell used for probing (firmware has `M2049` load cell), plus SD/eMMC lines, USB host pads, `BUTTON` and `LED_CTL`.

**Tools for SWD and console access:** see [docs/tools.md](docs/tools.md).

**Background research:** board history, magnetic-encoder motors, head ID chips, the 8-pad head connector, and product renders are in [docs/hardware_research.md](docs/hardware_research.md).

## Repo layout

| Path | Contents |
|---|---|
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

**HTTP API** at `http://<ip>:8080/api/v1/` (form-encoded or multipart; HTTP 200/201/203/204 = OK, 204 on status = waiting for on-screen confirm):

| Endpoint | Use |
|---|---|
| `POST connect` / `disconnect` | `token=` → JSON with `token`, `series`, `headType` |
| `GET status?token=` | state, position, temps, `laserPower`, `currentLine`/`totalLines`, `estimatedTime` |
| `POST prepare_print` | multipart `token`, `type`=`3DP`/`Laser`/`CNC`, `file` — uploads and loads the job |
| `POST start_print`, `pause_print`, `resume_print`, `stop_print` | `token=` |
| `POST execute_code` | `token=&code=<one G-code line>` |
| `POST upload` | multipart `token`, `file` — store a file (< 20 MiB) |
| `POST sliceUpload` | chunked store: `index` (1-based), `count`, `md5` (whole file), `size`, `filename`, `file` (2 MiB chunk) |
| `POST override_nozzle_temperature`, `override_bed_temperature`, `override_work_speed`, `override_z_offset`, `override_laser_power` | live adjustments |
| other | `setSystemTime`, `print_file`, `filament_load`/`filament_unload`, camera endpoints |

The stock slicer prepends a `;Header Start … ;Header End` block to jobs (see `docs/slicer_report.md`). Laser jobs are `.nc`
(`M3 S…` power), CNC jobs are `.cnc` (`M3 S…` spindle).

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

- ✅ Wi-Fi API, discovery, serial link, and update format documented; command-line client working from the same endpoints the stock slicer uses.
- ⏳ **Orca Slicer bridge (idea):** a small local service that looks like an OctoPrint server to Orca and forwards jobs to `prepare_print` + `start_print`. Orca would use a delta profile built from the M665 values above. Snapmaker Luban can't be used directly: it only connects to Snapmaker machines.
- 🔍 **Modern Marlin:** feasible but a big job. The delta motion, pins and endstops port directly; the smart-driver UART link, CAN tool-head link (including hotend temperature control via the head) and touchscreen compatibility must be written. Estimate **~3–5 weeks for FDM-only, ~2–3 months** for full laser/CNC/UI parity. Open items need hardware: mapping driver UART pads to STM32 pins (multimeter), bed/`FAN24V` switching, full CAN frame meanings (CANable capture), bootloader behaviour (SWD backup).
- ❓ The HTTP server binary on the Linux side hasn't been recovered yet. Next step: try the `UGUART` console pads with a 3.3 V USB-serial adapter (see [docs/mainboard.md](docs/mainboard.md)).

## Contributing

There may only be a few dozen of these printers out there. If you own one, issues and pull requests are welcome —
especially board photos, CAN captures, SWD dumps, working Orca profiles, or laser/CNC workflow notes.

## License

Original work in this repo (documentation, scripts, `supx_pack.py`) is licensed under
[CC BY-NC-SA 4.0](LICENSE).

**Not covered by the license:** the firmware files in `firmware/`, material extracted from IVI's installers, and the
`Beta Test Program/` documents are IVI's material. They are included here for preservation and interoperability
because the company no longer exists.

- Orca Slicer bridge plan: see [docs/orca_bridge.md](docs/orca_bridge.md)
