# IVI 3D Printer — open documentation and tools

Community reverse-engineering notes, firmware archive, and control tools for the **IVI 3D Printer**, a modular FDM / laser / CNC delta from a Kickstarter campaign. Beta units shipped, but **IVI has since gone defunct**: the pledges were never delivered and the company website is down. Nobody else is supporting these machines, so this repo collects what is needed to keep them running and to drive them from modern software (Orca Slicer and a browser) instead of the stock IVI 3licer slicer.

The current way to run the printer over the network is the **on-printer A33 bridge**, ivibridge **0.1.19-a33**. It lives on the printer's Linux board, shares the motion serial link with the touchscreen, and serves an OctoPrint-compatible API and a web UI on ports **5001** and **80**.

## Hardware

| Item | Finding |
|---|---|
| Kinematics | **Delta** — `M665 L357.50 R160.31 H233.22` (rod, radius, height). Homes to MAX endstops. Printable area is a 210 mm circle (origin at the centre). |
| Motion controller | STM32F407VET6 (IDCODE `0x10076413`, RDP level 0), **Marlin "V1.3.2-alpha"**. App at `0x08010000`; bootloader in sectors 0–1; Marlin `V81` settings in sectors 2–3 (sector 3 live). Full 512 KB dump: [firmware/stm32_dump/](firmware/stm32_dump/README.md). See [docs/stm32.md](docs/stm32.md). |
| Main board | One combined board, `A33_407MB_200916`: **Allwinner A33** (Linux 3.4 / Qt 5.9.6 UI + kore HTTP), **STM32F407VET6** (motion), **GD32E230F4** (soft power). A CH340C on a GL850G hub links the A33 to STM32 USART2. `DEBUGUART` / the front 3-pin is the A33 console (ttyS2, 115200). See [docs/architecture.md](docs/architecture.md) and [docs/mainboard.md](docs/mainboard.md). |
| Motors | Smart **closed-loop** drivers (the closed loop lives in the drivers; the STM32 still sends STEP/DIR and reads faults over UART). |
| Tool heads | 3D print (0.15–0.4 mm nozzles; beta shipped 0.3 mm), laser, and CNC (BLDC spindle). Each head has its own MCU on **CAN**; hotend heating and sensing, the head fans, the probe, the laser, and the spindle are controlled through it. |
| Other sensors | Door switch, filament runout, temp/humidity, load cell, clip-on nozzle probe for auto-level, thermal runaway protection. |
| USB-C | Direct serial link to the STM32, **115200 8N1**, plain line G-code. `M997` restarts into the bootloader (`STM32 Virtual ComPort` on the same port); `A4` starts the app again. Stop any USB bridge first. See [docs/stm32.md](docs/stm32.md#recovery). |

Saved printer output: [`docs/marlin_M115.txt`](docs/marlin_M115.txt), [`docs/marlin_M503_settings.txt`](docs/marlin_M503_settings.txt). Mechanical notes: [docs/motors_and_display.md](docs/motors_and_display.md), [docs/extruder.md](docs/extruder.md), [docs/hardware_research.md](docs/hardware_research.md).

## Architecture

Three processors share one carrier. The STM32 runs motion. The A33 runs the 800×480 touchscreen, Wi-Fi, and (when installed) ivibridge. The GD32 sequences the power button and rails. How they are wired, and how a stock job starts, is in [docs/architecture.md](docs/architecture.md).

```
Orca / phone / laptop
        │  HTTP  (LAN or Tailscale)
        ▼
 ivibridge  :5001 and :80   ←  on the A33
        │                      owns /dev/ivi-stm32 (the real CH340)
        ├─ pty ── /dev/ttyUSB0 ── stock touchscreen app  (+ IviHook)
        └─ serial ── STM32 Marlin ── delta / heads / heaters
```

**ivibridge** ([a33_bridge/](a33_bridge/README.md)) is a static C daemon. It recreates the CH340 node as `/dev/ivi-stm32`, opens it exclusively, and replaces `/dev/ttyUSB0` with a symlink to a pty so the stock app keeps talking to the same path. It passes the app's traffic through and takes turns on the wire. Replies meant for a network command are kept away from the app (the app treats any line containing `ok` as an acknowledgement).

**Touchscreen hook.** A QML overlay ([tools/ivi_hook/](tools/ivi_hook/README.md)), packed into the app with [tools/rcc_repack/](tools/rcc_repack/README.md), polls `http://127.0.0.1:5001`. Upload-and-print from Orca or the web UI stores the file in `/userdata/WifiFile` and posts a start request. The hook opens the stock Status page (assist mode: you confirm the plate and tap RUN). A persistent **Auto-start** setting can skip that dialog and run the stock RUN path. Mid-job, the same hook handles pause, resume, cancel, temperature, speed, flow, fan on/off, and Z-offset. The bridge never injects those commands onto the serial link while the app owns the job. Details: [docs/native_print.md](docs/native_print.md).

**Who can talk to the API.** On an RFC 1918 LAN (`10/8`, `172.16/12`, `192.168/16`) the page and Orca's Device tab work without pasting a key. Loopback and Tailscale `100.x` still need the key from `/userapp/ivibridge/apikey` (`X-Api-Key` or `?apikey=`). The printer's loopback interface is down in a stock boot; the Tailscale start script brings `lo` up so userspace Tailscale can forward to the bridge, and so the hook can reach `127.0.0.1:5001`.

**Other paths** still exist and are documented:

| Path | Role |
|---|---|
| [bridge/](bridge/README.md) | Optional **Mac / Linux / Windows** service. Looks like OctoPrint on the computer and streams jobs over **USB-C**. Wi-Fi **Upload** through this service still uses the stock kore API and must be started on the touchscreen. The Mac build has been used on hardware; the Linux and Windows installers have not. |
| Stock kore API, TCP **8080** | Upload, discovery, and `execute_code`. Print start / pause / stop return **404** on V1.3.2-alpha. Client: [`ivi-control.sh`](ivi-control.sh). See [docs/network.md](docs/network.md) and [docs/a33.md](docs/a33.md#kore-upload-api). |
| UDP **20050** | Answers ASCII `discover` only. |
| USB-C CDC, 115200 | Full G-code, including `M2411` job control. Opening that port during a job that is already streaming from the touchscreen (or from ivibridge's native-start path) stalls the print. |
| TCP **22** | Closed on a stock boot. `sshd` is on the rootfs and is not started. An ephemeral `/tmp` procedure is in [docs/home_session/RUNBOOK.md](docs/home_session/RUNBOOK.md). A login shell with no remote command starts a second copy of the UI, so every SSH command must be non-login (`ssh -T … -- 'command'`). |

## Feature summary (ivibridge 0.1.19)

- **Web UI** on `:5001` and `:80`: Toolhead, Filament, Files, Console, Webcam (a separate camera), Calibration. Two independent columns from 1100 px; a phone layout below that.
- **While a print is running** (a bridge job, a touchscreen job, or a firmware `WORKING_*` status) those first two boxes become **Status** and **Adjust**: progress, times, layer and Z, temperatures, file, Pause / Resume / Stop; and nozzle / bed targets, Z offset (`M290` babysteps), speed, flow, fan, and Save Z offset. Jog, Home, and other moves are hidden, and the daemon refuses them (HTTP 409).
- **Orca Slicer** treats the printer as an OctoPrint host on port 5001. Upload and Print stores the file and uses the hook; there is no computer in the middle and no USB cable.
- **Calibration**: XYZ (G33, always followed by leveling, because G33 wipes the mesh), auto-level (G29), and the Z-offset paper test, plus Run all. Optional **heated leveling** (`POST /api/ivi/cal/start` with `action: "level"` and `bed` 40–80 °C) heats the bed after the probe is checked, runs G29, saves, then turns the bed off. Cancel and any failure also turn the bed off. The probe is a **clip-on nozzle sensor**, so only the nozzle actual temperature has to be 40 °C or below (the same rule as the stock `checkTempForWizard`). The bridge sends **`M500` itself** after a successful G29 or G33; the firmware does not write EEPROM on its own. A round-bed **mesh map** on the Auto-level card draws the 7×7 grid over the 210 mm circle. The mesh is also in `GET /api/ivi/cal` as `level.grid`. See [docs/calibration.md](docs/calibration.md).
- **Console**: only allow-listed commands are sent. A line under Send says why the console is off or limited (link down, a calibration step waiting, a touchscreen job, or a print), and refusals from the bridge are shown there.
- Mid-print baby steps, a persistent Auto-start flag, a file queue, and a Z-offset readout (reference height minus effective height) are in [a33_bridge/README.md](a33_bridge/README.md) and [a33_bridge/CHANGELOG.md](a33_bridge/CHANGELOG.md).

## Firmware facts that affect slicing

These are properties of stock Marlin V1.3.2-alpha on this machine, not of a particular slicer profile:

- The stock touchscreen app never sends `M420 S1`, and **`G28` turns bed leveling off**. A saved mesh is not applied after a home unless the job's start G-code sends `M420 S1` after `G28`. (`GET /api/ivi/cal` reports `level.enabled`.)
- On this firmware, `M106 S0` **without `P` turns both head fans on** (`S` is ignored). Use `M107` or `M106 P0 S0` on an FDM head. See [docs/stm32.md](docs/stm32.md#fans).
- `G29` is not on the console allow-list. Leveling runs only from the Calibration flow.
- Motion firmware is not encrypted or signed (integrity is CRC-16 only). Head fans are on/off CAN frames. Tool heads talk on CAN2 (controller TX id `0x12`). Custom codes include `M2005`, `M2010`, `M2049`, `M2080`, `M2411 S1–S4`, and `M997`. Details: [docs/stm32.md](docs/stm32.md), [docs/supx_decompile_report.md](docs/supx_decompile_report.md).

## Repo map

A longer index, including older decompile notes, is [docs/README.md](docs/README.md).

| Path | Contents |
|---|---|
| [a33_bridge/](a33_bridge/README.md) | On-printer ivibridge 0.1.19: daemon sources, web UI, tests, install scripts. Changelog: [a33_bridge/CHANGELOG.md](a33_bridge/CHANGELOG.md). Built binaries are not in the tree; use `scripts/build.sh`. |
| [bridge/](bridge/README.md) | Optional computer-side OctoPrint service (USB stream + kore upload), with macOS, Linux, and Windows installers in `bridge/install/`. |
| [orca/](orca/README.md) | Orca Slicer FDM delta profile (printer / filament / process + `.orca_printer` bundle) and an optional IVI header hook. |
| [fusion/](fusion/README.md) | Autodesk Fusion post processors for the laser and CNC heads. Decoded from IVI 3licer test files; not yet run on hardware. Format notes: [docs/laser_cnc_gcode.md](docs/laser_cnc_gcode.md). |
| [ivi-control.sh](ivi-control.sh) | Command-line client for the **stock** kore API on port 8080 (discover, upload, `execute_code`). It is not the ivibridge client. |
| [docs/architecture.md](docs/architecture.md) | The three processors, the ports, and how a stock job starts. |
| [docs/stm32.md](docs/stm32.md) | Motion firmware: chip ID, RDP, flash map, bootloader, update protocol, fans, CAN, UARTs, recovery. |
| [docs/a33.md](docs/a33.md) | Touchscreen board: Qt app, touch, sshd, kore upload, boot chain, console. |
| [docs/gd32.md](docs/gd32.md) | GD32E230 soft-power controller. |
| [docs/mainboard.md](docs/mainboard.md) | Board photos, silkscreen, connectors. |
| [docs/network.md](docs/network.md) | What answers on the LAN. |
| [docs/calibration.md](docs/calibration.md) | Calibration view and API, G33 / G29 / paper-test math, heated leveling, mesh map, Z-offset display, `M420` after `G28`. |
| [docs/native_print.md](docs/native_print.md) | How ivibridge starts a job through the touchscreen hook, and mid-job control. |
| [docs/wifi_touch.md](docs/wifi_touch.md) | The ways to drive a print: ivibridge, stock kore upload, USB-C streaming, and the touch navigator. |
| [docs/orca_bridge.md](docs/orca_bridge.md) | Connecting Orca: the on-printer bridge vs the computer-side bridge, start G-code and fan notes. |
| [docs/slicer_report.md](docs/slicer_report.md) | How IVI 3licer 1.6.2 (a rebranded Snapmaker Luban) talks to the printer. |
| [docs/backups.md](docs/backups.md) | What has been backed up, and the restore routes. |
| [docs/tools.md](docs/tools.md) | SWD and the debug UART, with the hard limits. |
| [docs/home_session/](docs/home_session/RUNBOOK.md) | Runbook, quick reference, and checks for an ephemeral sshd + touch-navigator session. |
| [docs/firmware_report.md](docs/firmware_report.md) | Qt UI ELF: discovery, serial link, commands the UI sends. |
| [docs/supx_report.md](docs/supx_report.md), [docs/supx_decompile_report.md](docs/supx_decompile_report.md), [docs/supx_pack.py](docs/supx_pack.py) | `.supx` container, Ghidra pass (pins, driver UART, custom M-codes), and a packer for a raw STM32 image. |
| [docs/marlin_M115.txt](docs/marlin_M115.txt), [docs/marlin_M503_settings.txt](docs/marlin_M503_settings.txt) | Firmware info and a settings dump from a beta unit. |
| [firmware/Firmware/](firmware/Firmware/) | Stock firmware: `firmware` (UI app), `firmware.supx` (motion), `config.ini` / `config2.ini`. |
| [firmware/stm32_dump/](firmware/stm32_dump/README.md) | 2026-11-10 read-only SWD dump: 512 KB flash, system ROM, blank OTP, option bytes. |
| [tools/](tools/README.md) | Touch navigator, STM32 dump/probe helpers, framebuffer and tap helpers, A33 rescue kit, rcc QML packer, IviHook sources, command-map regenerators. |
| [tools/ivi_hook/](tools/ivi_hook/README.md) | QML overlay sources (IviHook, in-print Adjust page, main window). Packed app binaries are not stored here. |
| [tools/rcc_repack/](tools/rcc_repack/README.md) | Relocate the app's QML resource tree so patches can be any size. |
| [tools/a33_rescue/](tools/a33_rescue/README.md) | FEL and microSD rescue kit. See Recovery below. |
| [tools/ivi_touch_nav/](tools/ivi_touch_nav/README.md) | v0.2.0 touchscreen navigator (injects taps over SSH). Tested against a simulated framebuffer; the hardware session is the runbook above. |
| [calibration/motion_test/](calibration/motion_test/) | A small generated motion-test G-code. |
| [docs/research/](docs/research/README.md) | Annotated disassembly and a redacted A33 boot log. |
| [Beta Test Program/](<Beta Test Program/>) | IVI's beta-program documents (blank templates and info sheets). |

## Install and rollback

ivibridge writes to the A33 eMMC under `/userapp/ivibridge` (and, when the hook is installed, `/userapp/app/IVI-Main-Controller`). Only do this when the printer is idle: home screen, no job, no calibration, nothing heating. The exact steps, hash checks, and rollback copies are in [a33_bridge/README.md](a33_bridge/README.md#install-and-rollback). In short:

1. Build with `a33_bridge/scripts/build.sh` (static ARMv7 daemon). Pack the hook from the fansync / stock baseline with [tools/rcc_repack/](tools/rcc_repack/README.md), never from a previously packed output.
2. Copy the previous `ivibridge`, `www/index.html`, and `IVI-Main-Controller` aside as named backups.
3. Install the new daemon and page together (the page uses fields only 0.1.19 provides). The hook can be installed on its own; touchscreen fan on/off from the web page needs it.
4. Restart with `ivibridge-ram.sh stop` then `boot.sh`. Confirm `ivibridge -V` / `GET /api/ivi/link`, that the page loads on `:5001` and `:80`, that the app is back, and that the log shows `qml hook poll`.
5. Roll back by restoring the backup copies, then the same stop / `boot.sh`.

The computer-side USB bridge, if you want it, is a separate install: [bridge/README.md](bridge/README.md).

## Recovery tools

None of the write routes is authorized until a later, explicit decision. Routes and their limits: [docs/backups.md](docs/backups.md).

- **STM32.** The 2026-11-10 read-only SWD image is [firmware/stm32_dump/](firmware/stm32_dump/README.md) (RDP level 0, `mem_ap` only: no reset, no halt, no program). Gentlest recovery first: a same-version A33 update package (rewrites application sectors only), then USB-C entry with `M997` (`tools/stm32/bootloader_probe.py` checks the greeting and can send `A4` to start the app; it never sends a write frame). `A4` writes no flash. SWD programming is last. [docs/stm32.md](docs/stm32.md#recovery).
- **`.supx` packer.** `python3 docs/supx_pack.py raw.bin out.supx` builds an update file for the application at `0x08010000`. The bootloader and the settings sectors are not in the file. Offline CRC helpers: [tools/stm32/supx_stream.py](tools/stm32/supx_stream.py).
- **A33.** [tools/a33_rescue/](tools/a33_rescue/README.md) is a FEL and microSD kit. The safest path is FEL plus a RAM boot, which writes nothing to the eMMC. Risk labels run from read-only to a full user-area write. The userspace was checked under QEMU; the hardware verification list in [RESCUE.md](tools/a33_rescue/RESCUE.md) is still open. Built binaries that fit are in `tools/a33_rescue/out/` (the 64 MiB card image is omitted; rebuild it from [BUILD.md](tools/a33_rescue/BUILD.md)). No eMMC image is in this repo.
- A live eMMC image exists off-repo on the owner's drive and is not published here (it contains credential material).

## Safety

The STM32 on this board is **irreplaceable**.

- Over SWD: no reset, no halt, no erase, no program, and no option-byte writes. Never clear readout protection (unprotecting mass-erases the chip). This unit is already RDP level 0; leave the option bytes alone anyway. The same SWD limits apply to the GD32 until a separate decision says otherwise.
- Do not write `/dev/ttyUSB0` while the Qt app is running. Do not open the USB-C port while a touchscreen or native-start job is streaming.
- The debug UART is a root shell with no login (the UI's stdout also goes there). Open a 3.3 V USB-TTL with **VCC unconnected**. Do not type on that shell unless you mean to; do not type `exit` (it is the session that started the touchscreen app).
- Every SSH session must be non-login (`-T`, and override `RequestTTY` / `RemoteCommand` if the host entry sets them).
- Do not commit eMMC images, rootfs dumps, API keys, SSH keys, serial numbers, MAC addresses, SSIDs, password hashes, or Wi-Fi PSKs.
- Installs and hardware tests run only when the printer is idle, and each write path needs its own authorization.

## Status and known limits

- ivibridge **0.1.19-a33** is the current on-printer release in this tree: web UI, Orca over the LAN, native start through the hook, print-time Status / Adjust, motion lock, calibration including heated leveling, and the round mesh map.
- The board never reports fan state. The bridge records every `M106` / `M107` it forwards, starting unknown after a restart. The page follows that record. The stock Fan toggle does not, unless the optional fansync / hook-era app is installed (it polls `GET /api/fan`).
- There is no `M112` emergency stop in the bridge. Stop (cancel) is the stop control while printing.
- The A33 Linux tree is set up for an OV5640 on the CSI port (YUV). There is no ffmpeg on the printer, so the on-board camera is unused. The Camera tab takes a snapshot or MJPEG URL from a separate camera, capped at 5 fps in the browser.
- Laser and CNC Fusion posts, and laser/CNC jobs from Orca, have not been run on hardware.
- `tools/ivi_touch_nav` and the A33 rescue kit have been tested offline (simulator / QEMU). The first hardware sessions are the runbooks linked above; the rescue kit has not been run on the board.
- A port of modern Marlin is feasible but unstarted: delta motion and endstops would port, while the smart-driver UART link, the CAN tool-head link, and touchscreen compatibility would have to be written. Open hardware items include driver-UART pin mapping, bed / `FAN24V` switching, and a full CAN frame map.

## Contributing

There may only be a few dozen of these printers out there. If you own one, issues and pull requests are welcome — especially board photos, CAN captures, SWD dumps, working Orca profiles, or laser/CNC workflow notes.

## License

Original work in this repo (documentation, scripts, `supx_pack.py`) is licensed under [CC BY-NC-SA 4.0](LICENSE).

**Not covered by the license:** the firmware files in `firmware/`, material extracted from IVI's installers, and the `Beta Test Program/` documents are IVI's material. They are included here for preservation and interoperability because the company no longer exists.
