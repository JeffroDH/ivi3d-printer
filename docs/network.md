# Network access

Verified on an owner unit (home Wi-Fi), 2026-10-31, and extended by the 2026-11-07 rootfs and UART work. The table below is the **stock boot**; the on-printer bridge adds two ports (next section). Addresses stay off this page; use the printer's DHCP address.

## What answers on the LAN

| Path | Result |
|---|---|
| **TCP 8080** | Open. HTTP API served by **kore** (`server: kore …`). This is the only open TCP port on stock boot. |
| **UDP 20050** | Discovery: broadcast ASCII `discover` → `IVI3D@<ip>|Model:IVI 3D Printer|status:IDLE` |
| TCP 21 / 22 / 23 and all other TCP ports | Closed or filtered on stock boot. `sshd` is installed and **not started** (see [a33.md](a33.md#sshd)). |

About 12k ports actively refused; ~53k gave no response. That pattern often means a firewall is dropping traffic (or Wi-Fi is lossy). SSH could still exist on the printer and be blocked from the network — the scan alone cannot prove the binary is gone.

## With ivibridge installed

| Path | Result |
|---|---|
| **TCP 5001** and **TCP 80** | ivibridge: OctoPrint-compatible API (`/api/version`, `/api/printer`, `/api/job`, `/api/files/local`, and the `/api/ivi/*` routes) plus the web UI. Both ports serve the same content |

Clients on RFC 1918 addresses (`10/8`, `172.16/12`, `192.168/16`) need no key. Loopback and Tailscale `100.x` clients need the API key (`X-Api-Key`), which is stored on the printer. Stock kore on 8080 and UDP 20050 discovery are unchanged. Install and rollback: [a33_bridge/README.md](../a33_bridge/README.md#install-and-rollback). The computer-side [bridge/](../bridge/README.md) also uses port 5001, on the computer's own loopback.

USB-C is **not** a network path: it enumerates as CDC serial (`/dev/cu.usbmodem…`) straight to Marlin at 115200 8N1.

## HTTP API test results (2026-11-01)

- Works: `connect` (token required; returns `readonly:true`, `series:"IVI Printer"`, `headType:1`, `hasEnclosure:true`), `setSystemTime`, `status` (only `{"status":"IDLE"}`), `execute_code`, `disconnect`, `upload` (201 for a name with exactly one dot and extension `gcode`, `cnc`, or `nc`). A name such as `benchy_0.2mm.gcode` returns **412** `File type error`. See [a33.md](a33.md#kore-upload-api).
- `sliceUpload` exists (412 `md5 err` without a correct md5; fields `index,count,md5,size,filename,file`, 2 MiB chunks).
- **404:** `prepare_print`, `start_print`, `pause_print`, `resume_print`, `stop_print`, `confirm`, `accept`, `set_readonly`, `readonly`.
- No known request clears read-only (extra `readonly=false`/`readOnly=0`/`isReadOnly=false`/`confirm=1`/`accept=1` on connect do nothing).
- IVI 3licer 1.6.2 Wi-Fi Run: `execute_code` (G53/G0/G54/G92) → upload → `prepare_print` 404 → silent failure. Workaround: Send, then start on the touch screen.
- macOS: allow the slicer in **Local Network** privacy settings, otherwise "No route to host".
- Beta firmware likely ships an unfinished API. **Future official or custom firmware may enable these endpoints over Wi-Fi** — re-test after updates. Starting a job from the network today goes through ivibridge and the touchscreen hook instead ([native_print.md](native_print.md)).

USB serial is the direct control path: `M2411 S2` (+ `M1001 L` if fw ≥ 2.4.0) starts a PC job (`WORKING_PC`), G-code streamed per `ok`; `M2410` pause, `M2411 S1` resume, `M2411 S3` stop (decoded 2026-11-01). Verified with an FDM print on 2026-11-01. See README.

## How to get a shell

1. **`DEBUGUART` / front 3-pin** is the A33 console, ttyS2, 115200 8N1, root with no login. See [a33.md](a33.md) and [tools.md](tools.md).
2. **sshd** is on the rootfs and is not started. The ephemeral `/tmp` procedure is [home_session/RUNBOOK.md](home_session/RUNBOOK.md). A login shell with no remote command starts a second copy of the UI.
3. **STM32 SWD** is not a Linux shell. This unit is readout-protection level 0, and the 2026-11-10 read-only image is in [firmware/stm32_dump/](../firmware/stm32_dump/README.md). A later session is still no reset, halt, erase, program, or option-byte write. See [stm32.md](stm32.md).

## Related docs

- API map: [slicer_report.md](slicer_report.md), [a33.md](a33.md), README protocol section
- UI ELF notes: [firmware_report.md](firmware_report.md) (the Qt `firmware` binary is not the HTTP server; kore is `printer_http_api.so`)
- Driving a print over the network, USB-C, and touch injection: [wifi_touch.md](wifi_touch.md)
- On-printer bridge: [a33_bridge/README.md](../a33_bridge/README.md), [native_print.md](native_print.md)
