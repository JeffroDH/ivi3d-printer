# Network access

Verified on an owner unit at `192.168.50.85` (home Wi-Fi), 2026-10-31.

## What answers on the LAN

| Path | Result |
|---|---|
| **TCP 8080** | Open. HTTP API served by **kore** (`server: kore …`). This is the only open TCP port. |
| **UDP 20050** | Discovery: broadcast ASCII `discover` → `IVI3D@<ip>|Model:IVI 3D Printer|status:IDLE` |
| TCP 21 / 22 / 23 and all other TCP ports | Closed or filtered. Full `nmap -Pn -p-` found **no** SSH, Telnet, or FTP. |

About 12k ports actively refused; ~53k gave no response. That pattern often means a firewall is dropping traffic (or Wi-Fi is lossy). SSH could still exist on the printer and be blocked from the network — the scan alone cannot prove the binary is gone.

USB-C is **not** a network path: it enumerates as CDC serial (`/dev/cu.usbmodem…`) straight to Marlin at 115200 8N1.

## How to get a shell anyway

1. **`UGUART_RX` / `UGUART_TX`** (likely A33 Linux console) — 3.3 V USB-TTL; see [tools.md](tools.md) and [mainboard.md](mainboard.md).
2. **STM32 SWD** — ST-Link read-only flash backup (includes the 64 KB bootloader missing from `.supx`).
3. Once Linux access exists, re-enabling Dropbear/OpenSSH or a simple listener is usually straightforward if the packages or binaries are still on the rootfs.

## Related docs

- API map: [slicer_report.md](slicer_report.md), README protocol section
- UI ELF notes: [firmware_report.md](firmware_report.md) (the Qt `firmware` binary is not the HTTP server)
