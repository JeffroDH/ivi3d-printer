# IVI 3D Printer — Interface / Protocol Spec

> Current map of the whole machine: [architecture.md](architecture.md), [a33.md](a33.md), [stm32.md](stm32.md). This file is the UI-ELF protocol note.
>
> The printer is a **delta** (M665 L357.50 R160.31 H233.22). The closed loop lives in the smart stepper drivers. The STM32 speaks plain line G-code; `AA 55` framing is the slicer↔UI path. `M2005` is the firmware/serial query and `M2051` is the head-type query. `M106` with no `P` turns both head fans on.

**Target:** `/workspace/ivi/firmware.bin` (ELF32 ARM Qt5 touchscreen/controller UI)  
**Also used:** IVI 3licer 1.6.2 macOS app (from DMG), `firmware.supx`, `config.ini` / `config2.ini`  
**Method:** strings + Ghidra/REA decompilation of `networkManager`, `Sender`, print CMD helpers; client JS from the slicer  
**Scope:** authorized interoperability analysis for an Orca Slicer plugin. Nothing was flashed or modified on the device.

---

## Executive summary

| Layer | Role | Port / path | Protocol |
|-------|------|-------------|----------|
| **UDP discovery** | Printer announces itself; slicer finds it | **UDP 20050** | ASCII `discover` → reply `NAME@IP\|Model:…\|status:…` |
| **HTTP control API** | Connect, upload G-code, start/pause/stop, status | **TCP 8080** `http://IP:8080/api/v1/…` | Snapmaker-Luban-compatible REST + token |
| **Serial (internal)** | Touchscreen UI ↔ motion controller | `/dev/ttyUSB0` **115200 8N1**, no flow control | Marlin-like G/M-code (line-oriented, `ok` replies) |
| **`.supx`** | Motion-controller firmware package | paired with `config*.ini` MD5 | STM32 vector-table image (not the Qt ELF) |

**Important architecture note:** `firmware.bin` is the **Qt LCD/UI process**. It implements UDP discovery and drives the controller over serial. It constructs a `QTcpSocket` but **never connects, listens, or reads/writes TCP** (`networkManager::sendMessage` is an empty stub). The **HTTP API on :8080 is a separate process** on the printer (Snapmaker-style server). The slicer talks to that HTTP server after UDP discovery. For an Orca plugin, implement **UDP 20050 discovery + HTTP :8080 `/api/v1`**, not a custom TCP framing protocol inside this Qt binary.

---

## 1. Network

### 1.1 UDP discovery — port **20050** (`0x4e52`)

**Evidence (printer):** `networkManager::networkManager` @ `0x4a054`:

```c
*(undefined2 *)(this + 8) = 0x4e52;   // 20050
QUdpSocket::QUdpSocket(this + 0xc, …);
QTcpSocket::QTcpSocket(this + 0x14, …);  // constructed only; unused for I/O
*(this + 0x1c) = "IVI3D-Zoom-Mammoth";   // default name/model field
*(this + 0x28) = "IDLE";                 // default status
```

`networkManager::initUdpListen` @ `0x49e44`:

```c
QAbstractSocket::bind(this + 0xc, *(uint16_t*)(this + 8), 0);  // bind UDP 20050
// connect readyRead → readPendingDatagrams
```

**Evidence (slicer):** `server/index.js` broadcasts and parses:

```js
r.client.send(Buffer.from("discover"), 20050, broadcastAddr, …);
r.client.on("message", (e) => {
  const t = e.toString("utf8").split("|");
  if (t.length && t[0].indexOf("@") !== -1) {
    const n = t[0].split("@");
    const i = { name: n[0], address: n[1] };
    for (let o = 1; o < t.length; o++) {
      if (t[o].indexOf(":") !== -1) {
        const [l, f] = t[o].split(":");
        i[l.toLowerCase()] = f;  // model, status, …
      }
    }
    r.devices.push(i);
  }
});
```

**Request (PC → printer):** UDP datagram, payload exactly ASCII:

```
discover
```

sent to the subnet broadcast address on port **20050**.

**Reply (printer → PC):** built in `readPendingDatagrams` @ `0x49208` when payload contains `"discover"`. Wire format (matches user capture and slicer parser):

```
IVI3D@192.168.50.85|Model:IVI 3D Printer|status:IDLE
```

Field rules:

- First segment: `NAME@IPv4`
- Further segments: `key:value` joined by `|` (keys lowercased by client: `model`, `status`, …)
- Binary strings used while building: `"@"`, `"|Model:"`, `"|status:"`, trailing `"\n"` @ `0x55a84`
- Default status string in ctor: `"IDLE"`
- Status / machine-state strings also present in UI: `IDLE`, `WORKING_PC`, `WORKING_SCREEN`, `Printing`, `Paused`, `Complete`, `Ready`, `Stop`, `Operational`
- Model / name strings in binary: `"IVI3D"`, `"IVI 3D Printer"`, `"IVI3D-Zoom-Mammoth"` (ctor default for field at `this+0x1c`; runtime can overwrite via `setUdpInfo`)
- Reply is sent with `QUdpSocket::writeDatagram` back to the **source port** of the discover packet (`local_8a`), to `QHostAddress::Broadcast` (SpecialAddress `1` in decompile) — i.e. broadcast response path as implemented

**Log line format** (debug only): `"receive:"` + payload + `",ip:"` + `", port:"` + port.

### 1.2 TCP / HTTP — port **8080**

**Not implemented in `firmware.bin`.** Only `QTcpSocket` ctor/dtor are imported; no `connectToHost`, `listen`, `read`, or `write` on TCP.

**Slicer default** (`Server` ctor in app bundle):

```js
s.port = a || 8080;
s.host = "http://" + this.address + ":" + this.port;
this.token = "e0cf19a3-e0a4-4740-825f-bdffb49e58b8";  // default until connect returns one
```

Camera helpers also hardcode `:8080`.

### 1.3 HTTP API (`/api/v1/…`) — print-job control path for Orca

> **Tested 2026-11-01:** on the beta firmware `prepare_print`, `start_print`, `pause_print`, `resume_print` and `stop_print` return **404**, and `status` only returns `{"status":"IDLE"}`. Only connect/disconnect/setSystemTime/execute_code/upload work over Wi-Fi; use USB serial (`M2411 S2`) to run jobs. Future official or custom firmware may enable these endpoints. See README.


Auth: session **token** query/body field. Default bootstrap token above; `POST /api/v1/connect` returns `{ token, series, headType, … }`. Reuse returned token. `403` on connect with a stale token → retry connect with empty token. `POST /api/v1/disconnect` with `token=…`.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/connect` | body `token=` (optional); start session |
| POST | `/api/v1/disconnect` | body `token=` |
| GET | `/api/v1/status?token=` | poll ~1 Hz: status, x/y/z, temps, print progress lines |
| POST | `/api/v1/prepare_print` | multipart: `token`, `type`=`3DP`\|`Laser`\|`CNC`, `file` |
| POST | `/api/v1/upload` | multipart: `token`, `file` (direct; used if size &lt; 20 MiB) |
| POST | `/api/v1/sliceUpload` | chunked upload FormData: `index`, `count`, `md5`, `size`, `filename`, `file` |
| GET | `/api/v1/print_file?token=` | fetch current print file |
| POST | `/api/v1/start_print` | body `token=` |
| POST | `/api/v1/pause_print` | body `token=` |
| POST | `/api/v1/resume_print` | body `token=` |
| POST | `/api/v1/stop_print` | body `token=` |
| POST | `/api/v1/execute_code` | body `token=` + `code=` (single G-code line) |
| POST | `/api/v1/setSystemTime` | body `token=` + `timestamp=` (unix seconds) |

Chunked upload: files ≥ **20971520** (20 MiB) use MD5 + chunks; success text includes `"silce upload success"` (sic) or `"file upload complete"`.

**Recommended Orca plugin flow:**

1. UDP broadcast `discover` → :20050 → parse `NAME@IP|Model:…|status:…`
2. `POST http://IP:8080/api/v1/connect`
3. Upload G-code (`upload` or `prepare_print` with `type=3DP`)
4. `POST …/start_print`
5. Poll `GET …/status?token=`
6. pause / resume / stop as needed; `disconnect` when done

This is the same stack as Snapmaker Luban / “sac” HTTP API (IVI 3licer is clearly a fork).

### 1.4 No other listen ports found in `firmware.bin`

No HTTP server, no second TCP command port, no WebSocket strings tied to control. Discovery is UDP-only in this binary.

---

## 2. Serial (UI ↔ motion controller)

### 2.1 Settings

From `Sender::Sender` @ `0x25e48` and `Sender::openPort` @ `0x1f410`:

| Setting | Value | Evidence |
|---------|-------|----------|
| Device | `ttyUSB0` (string @ `0x551d4`) | preferred USB-serial name |
| Baud | **115200** (`0x1c200` stored at `this+0x78`) | ctor |
| Data bits / parity / stop | Qt defaults (8N1) | no custom setters beyond baud/flow |
| Flow control | **0** = `NoFlowControl` (`this+0x7c`) | ctor end |
| Modem lines | RTS + DTR asserted on open | `setRequestToSend` / `setDataTerminalReady` |
| Open mode | ReadWrite (`open(…, 3)`) | openPort |

### 2.2 Framing

- Outbound: UTF-8 G-code lines via `QIODevice::write` + `QSerialPort::flush` (`Sender::sendLine` @ `0x22b38`). Lines are queued; `sendNext` paces them.
- Inbound: line-oriented (`readLine`); replies contain Marlin-style **`ok`**, temps `T:` / `B:`, and custom `work: ok` / `pause: ok` / `stop: ok`.
- `injectCommand` splits on `\n` and pushes into the command queue.

### 2.3 Command set (Marlin-like + IVI custom)

**Standard / Marlin-family (subset used by UI):**  
`G0`/`G1`/`G28`/`G29`/`G33`/`G53`/`G54`/`G90`/`G91`/`G92`,  
`M3` (laser/CNC spindle), `M104`/`M109` (hotend), `M140` (bed), `M106`/`M107` (fan),  
`M114` (position), `M119` (endstops), `M155` (auto-report temp), `M220`/`M221` (feed/flow %),  
`M290` (babystep Z), `M500`/`M502`/`M503`, `M665` (delta/geometry), `M997` (reset/bootloader), `M108`, `M144`, `M211`.

**IVI / Snapmaker-style custom (print job control over serial from the UI):**

| Code | Meaning in this UI |
|------|--------------------|
| `M2001 S1` | Part of start / reclaim control (`sendPrintStartCMD`, also after disconnect) |
| `M2411 S2` | Start print (with `M2001 S1`) |
| `M2410` | Pause |
| `M2411 S1` | Resume |
| `M2411 S3` | Stop |
| `M2005` | Controller firmware string, tool-head firmware/hardware, head serial from EEPROM |
| `M2051` | Head type (`info:Head 3DP,…` / Laser / CNC). Codes in [stm32.md](stm32.md) |
| `M210 S0/S1`, `M2155 S0/S5` | `M2155 S<n>` = motion-board auto status report interval (see laser_cnc_gcode.md) |

`GlobalFuntions::sendPrintStartCMD` @ `0x2a60c`:

```c
injectCommand("M2001 S1");
injectCommand("M2411 S2");
```

Pause / resume / stop @ `0x2a56c` / `0x2a5bc` / `0x2a68c` inject `M2410` / `M2411 S1` / `M2411 S3`.

**PC-side trigger words** (seen by `printTriggerHandle` @ `0x430b0` on a newline-split string):  
`trigged`, `work`, `pause`, `resume`, `stop` — then loads G-code via `cachegcodeFromFile` / `Sender::startPrinting`. These are **internal UI / workflow** strings (also mirrored in HTTP start/pause/stop), not a separate network framing protocol in this ELF.

Controller ack strings: `work: ok`, `pause: ok`, `stop: ok`, `Error:Printer halted`, `CMD buffer`, `ok`.

---

## 3. Print-job transfer flow

### 3.1 Over the network

The slicer issues the Luban sequence below. On this firmware the print-control routes return **404**. What actually works is discovery, connect, `execute_code` (one line), and upload. Start the job on the touchscreen or over USB-C. See [network.md](network.md) and [wifi_touch.md](wifi_touch.md).

1. Discover via UDP 20050.
2. HTTP connect on **8080**, obtain token.
3. Upload `.gcode` to `/upload`. The name must contain exactly one dot and end in `gcode`, `cnc`, or `nc`, or kore returns 412. Large files: `/sliceUpload` with an MD5.
4. `/prepare_print`, `/start_print`, `/pause_print`, `/resume_print`, `/stop_print` are **404** on this unit.
5. `/status` returns only `{"status":"IDLE"}`.

### 3.2 Inside the Qt UI (local / USB path)

1. G-code file selected; lines loaded into a `QVector`/`QList` (`Sender::setFile`).  
2. `startPrinting` → `cachegcodefile` → `sendNext` streams lines over serial.  
3. Progress = bytes/lines accounting in `sendNext`; finish → `printgcodefilefinish`.  
4. Expected G-code comment headers (parsed by UI):

```
;Generated by IVI 3licer
;max_x(mm): …
;max_y(mm): …
;min_x(mm): …
;min_y(mm): …
;header_type: 3dp | laser | …
;material_type: …
;estimated_time(s): …
; md5: …
```

Extensions recognized: `.gcode`, `.nc`, `.cnc`.

### 3.3 Firmware update path (serial bootloader — not for print jobs)

Settings → Update Firmware sends `M997`, then the `.supx` body as CRC-16 frames on `ttyUSB0`. The bootloader answers `C4 05 B0 19 A2`, erases sectors 4–5 only, and checks the image CRC. The same entry works over USB-C (confirmed 2026-11-10). Frame table, brick protection, and recovery order: [stm32.md](stm32.md#update-protocol). Package rules: [a33.md](a33.md#update-package).

---

## 4. Authentication

| Mechanism | Detail |
|-----------|--------|
| HTTP token | Default `e0cf19a3-e0a4-4740-825f-bdffb49e58b8`; connect may mint/return a session token |
| UDP discovery | **No auth** — anyone on LAN can discover |
| Serial | **No auth** — physical/USB access |
| Wi-Fi | Standard WPA (`wpa_cli`); not part of the print API |

No password/HMAC on the discovery datagram. Treat LAN trust as the boundary (same as stock slicer).

---

## 5. File formats: `.supx` vs raw `firmware.bin`

| Artifact | MD5 (matches config) | Role |
|----------|----------------------|------|
| `firmware.bin` | `1339cf97f887753b618c6cf7f2af1e73` → `config.ini` `version=1.222` | ELF32 ARM Qt5 UI (`INTERP /lib/ld-linux.so.3`), contains `sinlinx` / `rk312x` / `RK3128` strings, but the board photos show an **Allwinner A33** (see mainboard.md); these are SDK leftovers |
| `firmware.supx` | `f83207e8cafffcd0a4d955f37631d702` → `config2.ini` `version=1.3.2` | Motion-controller image: LE size word `0x28c40` (166976) at offset 0; vector table with `0x0800xxxx` Thumb addresses (STM32-style). **Not** an ELF. |

Update packaging names in UI: `IVI3DPrinterFirmware`, `IVI3DPrinterFirmwarePack`, scripts `/userapp/script/unzipFirmware.sh`, `CpIVI-Main-Controller.sh`. UI verifies MD5 (`checkFileMD5`) against `config.ini` / `config2.ini` before applying.

---

## 6. Uncertainties / next steps on-device

> Hardware cross-reference: [hardware_research.md](hardware_research.md) covers the board architecture (combined `A33_407MB` main board with Allwinner A33 + STM32F407, driver boards, power and switch PCBs; see [mainboard.md](mainboard.md)), the per-motor magnetic encoders and driver boards, the toolhead ID chip, and the 8-pad head connector (pin roles guessed).


1. kore is `printer_http_api.so`, not this Qt ELF. On stock boot only TCP 8080 and UDP 20050 answer. `sshd` is on disk and is not started. The console is ttyS2 on `DEBUGUART`. See [a33.md](a33.md) and [network.md](network.md).
2. Exact mapping of every `setUdpInfo` field → discovery `NAME` vs `Model:` under all firmware builds (ctor default is `IVI3D-Zoom-Mammoth`; live capture shows `IVI3D` / `IVI 3D Printer`). Wire format is solid; field provenance can vary by version.
3. `M2005` / `M2051` / `M210` / `M2155` are traced in [stm32.md](stm32.md) and [data/stm32_app_commands.csv](data/stm32_app_commands.csv).
4. `/prepare_print` and `/start_print` return 404 here. Upload plus a touchscreen start, or the USB-C bridge, are the working paths.
5. The slicer can also open the printer's USB-C port directly. That port is the STM32 CDC interface, not this Linux board.

---

## 7. Key symbol / address index (`firmware.bin`)

| VA | Symbol |
|----|--------|
| `0x4a054` | `networkManager::networkManager` (port 20050) |
| `0x49e44` | `networkManager::initUdpListen` |
| `0x49208` | `networkManager::readPendingDatagrams` |
| `0x49f18` | `networkManager::setUdpInfo` |
| `0x4a050` | `networkManager::sendMessage` (**empty**) |
| `0x25e48` | `Sender::Sender` (baud 115200) |
| `0x1f410` | `Sender::openPort` |
| `0x22b38` | `Sender::sendLine` |
| `0x23ef8` | `Sender::injectCommand` |
| `0x2a60c`/`0x2a56c`/`0x2a5bc`/`0x2a68c` | print start/pause/resume/stop CMDs |
| `0x430b0` | `GlobalFuntions::printTriggerHandle` |

---

## 8. Bottom line for the Orca plugin

Implement a **Snapmaker/IVI HTTP client**:

1. Discover: UDP broadcast `"discover"` → **20050**, parse `NAME@IP|Model:…|status:…`.  
2. Control: HTTP **`IP:8080`**, token auth, `/api/v1/{connect,upload|prepare_print,start_print,status,pause_print,resume_print,stop_print,disconnect}`.  
3. Optional: USB-C serial **115200** G-code straight to the STM32 Marlin (bypasses the UI board and its job tracking).

Do **not** invent a proprietary TCP binary protocol based on this Qt binary — the control plane the official slicer uses is HTTP on 8080 after UDP discovery.
