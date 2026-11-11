# STM32 bootloader (0x08000000–0x08007FFF)

Boot flow, update protocol, settings sectors, and recovery for the motion controller. The image is the read-only SWD dump of 2026-11-10 in [firmware/stm32_dump/](../../../../firmware/stm32_dump/README.md). Listings are in this directory. The short form is [docs/stm32.md](../../../stm32.md).

**Tags:** **[V]** verified in the dump, in disassembly, by computation, or on the printer · **[I]** inferred · **[?]** needs a hardware check.

## Inputs

| File | MD5 | Notes |
|---|---|---|
| `firmware/stm32_dump/stm32_flash_20261110_a.bin` | `f6ad34c24a230dd2e6337ea7ed14a127` | 512 KB at `0x08000000`. A second read the same night matched |
| `bl_0x08000000_32k.bin` | slice of that dump | Sectors 0–1. Code and data end at `0x08006933`; the rest of the 32 KB is `0xFF` |
| `firmware/stm32_dump/stm32_otp_20261110.bin` | `3aa259ba5fbccbc52ca9a121964045b7` | 528 B, all `0xFF` (blank, no locks) **[V]** |
| `firmware/stm32_dump/stm32_optbytes_20261110.bin` | `9c4a2b3a2e0fb62a6e4d0a31105d1d1e` | RDP `0xAA` = level 0, `nWRP` `0x0FFF` (no sector write protection) **[V]** |
| `firmware/stm32_dump/stm32_sysmem_20261110.bin` | `283f8615e8cc33301c2afec942ac57c9` | ST ROM at `0x1FFF0000`. The bootloader does not call it |

`FLASH_OPTCR` was `0x0FFFAAED`. DBGMCU_IDCODE `0x10076413` (STM32F405/407/415/417 family), CPUID `0x410FC241`, DPIDR `0x2BA01477`.

The read used [tools/stm32/openocd_readonly.cfg](../../../../tools/stm32/openocd_readonly.cfg): ST-Link, `dapdirect_swd`, `reset_config none`, `swd newdap`, `dap create`, `target create` `mem_ap` `-ap-num 0`, then `init` and `dump_image` / `mdw`. No `cortex_m` target, so nothing wrote DHCSR, DEMCR or the FPB. No reset, halt, erase, or program.

Tools that reproduce the listings and the protocol check, all offline:

- Ghidra headless (raw binary, ARM Cortex, base `0x08000000`). Full decompile: `disasm/bootloader_ghidra_decompile.c`. Script: `ghidra/DecompAll.java`.
- `tools/stm32/bldis.py` (Capstone, PC-relative literals filled in) produced `disasm/*.s`.
- `tools/stm32/blq.py` prints one decompiled function and its literal-pool words.
- `tools/stm32/bl_protocol_model.py` feeds `firmware.supx` through the handlers. Output: `bl_protocol_model_output.txt`.

The bootloader is a Keil/ARM build (`__scatterload`, compressed RW) on the ST HAL and the ST USB CDC middleware.

## 1. Boot flow

1. **Reset** at `0x080001A4` calls `SystemInit` at `0x08002F48`. That enables the FPU (`CPACR |= 0xF00000`) and sets **VTOR = `0x08000000`** **[V]**. `__main` / `__scatterload` at `0x080002F0` decompresses `.data` (0x1BC bytes → `0x20000000`) and zeroes `.bss`. `main` is at `0x08005B4C` **[V]**.
   - Initial RAM, decompressed in `ram_init_0x20000000.bin` **[V]**: status `0x20000000 = 0xE0`, app base `0x20000004 = 0x08010000`, length `0x20000008 = 0`.
2. **Init** **[V]**:
   - `HAL_Init` (flash ACR prefetch and I/D caches, NVIC grouping 3, SysTick).
   - **Clock:** HSE + PLL, M=4, N=168, P=2, Q=7 → **168 MHz from an 8 MHz HSE** **[V]** for the register values, **[I]** for the 8 MHz crystal. Flash latency 5 wait states, APB1 /4, APB2 /2, PWR VOS scale 1.
   - **GPIO:** PC1, PC2, PC6, PC7 and PA6, PA7 are outputs driven low. PE3 and PE4 are inputs; the boot decision never reads them. PB10 and PB11 are a bit-banged I²C bus. **PD0 is an output driven high.**
     - **[I]** The low outputs hold heater and fan MOSFETs off while the bootloader runs. PD0 is an enable. What each pin switches is **[?]**.
   - **USART2 on PD5 (TX) / PD6 (RX), AF7, 115200 8N1, RXNE interrupt** (IRQ 38, ISR `0x08003350`). This is the update link.
   - USART1 on PA9/PA10 at 115200 is initialized. Its RX interrupt is not enabled and the IRQ handler at `0x0800334C` is empty, so it is unused **[V]**.
   - UART4 on PA0/PA1 at 115200 is initialized through the HAL and unused **[V]**.
   - **USB OTG FS CDC** (`STM32 Virtual ComPort`, VID:PID `0483:5740`). The serial string is derived from the 96-bit UID at `0x1FFF7A10`, which is read and not written **[V]**. That UID is not inside these dump files.
3. **Decision** at `0x08005B6E`–`0x08005BDE` **[V]**, in this order:
   1. **EEPROM "update pending" record.** `FUN_0800036A` reads 16 bytes from **address 0x20 of an external I²C EEPROM** (device `0xA0`/`0xA1`, bit-banged, PB10 = SCL, PB11 = SDA). CRC-16/XMODEM over bytes 0–13 must match bytes 14–15, little-endian.
      - A match stays in the bootloader with no timeout.
   2. Otherwise it **listens for 1 s** (10 × 100 ms) for `M997` plus any one byte on **USART2 or USB CDC**. A hit stays in the bootloader.
   3. Otherwise, if **RCC_CSR.SFTRSTF (bit 28)** is set (the last reset was a software reset), it clears the reset flags (`RMVF`), prints ` software reset, now in bootloader` on USART2 and USB, and **stays in the bootloader**.
   4. Otherwise it **jumps to the app** through `FUN_08005B08`, using `*(uint32_t *)0x20000004`, which is `0x08010000`.
4. **Jump** at `0x08005B08` **[V]**:
   - It prints ` stack: %x` (SP masked with `0x2FFE0000`) on USART2. The print is the whole check: **there is no stack-pointer test, no app-validity test, and no app CRC at boot**.
   - It stops USB (`USBD_Stop` at `0x08003942`) and loads the reset vector from base+4.
   - It sets **MSP = `*(base)`** (`0x0800019C`, `msr msp`) and branches to the reset vector.
   - **The bootloader does not change VTOR.** The app's own `SystemInit` sets VTOR = `0x08010000`.
   - UART, GPIO, and the USART2 NVIC enable are left as they are. If the app returns, the bootloader prints `jump to app failed` and enters the command loop.
5. **Command loop** at `0x08005BE8` **[V]**. USART2 (`0x08005E28`) and USB CDC (`0x08006368`) share the same handlers. There is no watchdog and no timeout.

**Not used [V]:** BOOT0, any GPIO or button in the decision, RTC or backup registers, backup SRAM, a flag in flash sectors 2–3, and the IWDG.

The only persistent input is the external EEPROM record. The only volatile one is `RCC_CSR.SFTRSTF`.

On the printer, 2026-11-10 **[V]**: `M997\n` on USB-C to the running app (product `BLACK_F407VE CDC in FS Mode`, node `/dev/cu.usbmodem*`) restarted into this bootloader. It re-enumerated on the same port as `STM32 Virtual ComPort` in about 0.9 s, and a second `M997\n` received `C4 05 B0 19 A2`. That is the software-reset path staying in the command loop long enough to answer.

## 2. Update protocol

The frames match the A33 `firmware.supx` stream.

**Framing [V]**, from the USART2 ISR at `0x08003350` and the same USB parser at `0x080054FC`:

- After 4 bytes, if byte 0 is in `A0..A4`, the frame length is **byte1 × 4**. So `A1 03` is 12 bytes, `A2 40` is 256, `A2 0B` is 44, `A3 02` is 8, `A4 02` is 8.
- Otherwise the first 4 bytes must be `M997`. A fifth byte (any value, including `\n`) completes the entry request.
- Anything else gets status `E1`.
- The frame CRC is CRC-16/XMODEM over the frame except its last 2 bytes, stored little-endian. A bad CRC is answered `C0 05 E4`.

**Replies [V]:** 5 bytes, `Cx 05 status crcLo crcHi`.

- The CRC covers 3 bytes for the `C4` entry reply and for error replies, and 4 bytes (including a `0x00`) for the C1–C3 replies. The host does not appear to check it **[I]**.
- **M997 entry reply = `C4 05 B0 19 A2`.** Seen on USB-C on 2026-11-10 **[V]**.
- A command that left a non-`E0` status makes the next frame get `C0 05` plus that old status, and the status is then cleared.

| Cmd | Handler | Action **[V]** | Reply |
|---|---|---|---|
| `A0` | — | ping | `C0 05 E0` |
| `A1` load, len | `0x080062B4` | Requires **load == `0x08010000`** and its sector in 4..7, else `E6`. **Writes the EEPROM pending record first** (`FUN_08000566`: `55 AA 63 … 6E` + CRC `C3 2B`), then erases sectors from `sector(load)` through `sector(load+len)`. The stock file erases **sectors 4–5**. The write result is ignored | `C1 05 E0`, `E2` on erase failure |
| `A2` addr, data | `0x08006260` | **addr must be `0x08010000`..`0x0807FFFF`**, else `E6`. Word-programs `len×4−8` bytes. No read-back | `C2 05 E0`, `E3` on program failure |
| `A3` crc | `0x0800632C` | **CRC-16/XMODEM over flash `[load, load+len)`**, compared with frame bytes 2..5. The stock file's `0A BA 00 00` is **`0xBA0A`, the CRC of the dumped app region** **[V]**. On a match it overwrites the EEPROM record with `FF 00` × 15 (CRC no longer valid), which clears pending | `C3 05 E0`, `C3 05 E4` on mismatch |
| `A4` | dispatcher | jump to **`0x08010000`** (a constant), same jump routine. The frame is `A4 02 AA AA AA AA 9F BD` | none |

`tools/stm32/bl_protocol_model.py` runs these rules on the real `firmware.supx` frames. Every frame gets `E0` (1 × C1, 653 × C2, 1 × C3). The resulting image is **byte-identical to the dump**, and sectors 0–3 are untouched **[V]** inside the model. `A3 02 0A BA 00 00 DE 3A` is that whole-image CRC plus the frame CRC.

**Entry from a running printer:**

1. The host sends `M997\n`. The app executes `NVIC_SystemReset` and writes no flag **[V]**.
2. The bootloader either catches another `M997\n` inside its 1 s window, or SFTRSTF keeps it in the bootloader anyway **[V]** in the image.
3. The next `M997\n` is answered `C4 05 B0 19 A2`.

USB-C on 2026-11-10 followed that sequence **[V]**. The A33's own update path sends `M997` on `ttyUSB0` and then the same frames; that host path is **[V]** in the UI binary. `M997` is also accepted when the command loop is already running **[V]**.

**Interrupted update [V]:**

- The pending record is written **before** the erase and cleared **only** after a good A3.
- Power or the link lost anywhere from A1 until a successful A3 leaves **every later boot in the bootloader**, with USART2 and USB CDC listening, and **a full re-send works**.
- That depends on the EEPROM write having succeeded. The I²C write's ACK is ignored, and the erase runs anyway **[V]**.

**What it cannot erase [V]:**

- A1 refuses a load address other than `0x08010000`.
- The sector-erase wrapper at `0x08005972` refuses any sector below 4.
- The program wrapper at `0x080059B8` refuses addresses below `0x08010000`.
- The sector helper returns 8 for an address past `0x0807FFFF`, and the HAL then rejects it (`E2`).

Sectors 0–3 (bootloader and settings) stay in place across an update.

Residual cases **[V]** for the mechanism, **[I]** for how likely they are:

- **(a)** The EEPROM write fails silently and power is lost mid-update. The record stays invalid, the bootloader jumps to a blank app (SP/PC = `0xFFFFFFFF`), and the core faults into the HardFault loop at `0x08001F6C`. Recovery is the 1 s window after power-on, or SWD.
- **(b)** The EEPROM is missing or NACKs. The read buffer stays zero, and CRC of 14 zero bytes is `0x0000`, which matches the stored `0x0000`. **Every boot stays in the bootloader and the app never starts.** `A4`, or a re-flash, still works. The same happens if address `0x20..0x2F` ever reads as all `0x00`.
- **(c)** Any software reset of the app (`M997` or any other `NVIC_SystemReset`) leaves the printer in the bootloader until a power cycle or `A4`.

`A4` on USB-C, 2026-11-10 **[V]**: the frame started the app, no reply bytes came back, the app re-enumerated as `BLACK_F407VE CDC` within 4 s, the touchscreen showed no errors, and no flash was written.

## 3. Option bytes, RDP, OTP, ST system bootloader [V]

A literal scan of the bootloader shows:

- **No reference** to OPTCR `0x40023C14`, OPTKEYR `0x40023C08`, the option keys `0x08192A3B` / `0x4C5D6E7F`, OTP `0x1FFF7800`–`0x1FFF7A0F`, or system memory `0x1FFF0000`.
- No BOOT0 handling and no DFU class. USB is CDC only.
- The FLASH registers it uses are ACR, KEYR (keys `0x45670123` / `0xCDEF89AB` at `0x08000BC8`), SR, and CR.
- **The bootloader never sets RDP or writes option bytes.** The application image has no option-key writes either. No stock code on this board touches RDP or the option bytes.
- The only read of the system-memory region is the 96-bit UID at `0x1FFF7A10`, for the USB serial string.
- Measured state: RDP level 0, no write protection, BOR off, OTP blank.

## 4. Sectors 2–3 (0x08008000–0x0800FFFF)

Each sector holds one **Marlin settings image, version `V81`**, at offset `0x64` (Marlin's `EEPROM_OFFSET` of 100). Each image is `0x3CA` bytes and the rest of the sector is `0xFF`.

Both copies' Marlin CRC-16 (over `0x6A..0x3C9`) verify **[V]**: sector 2 = `0xE7FE`, sector 3 = `0xAB71`.

The app code that reads and writes them is the same map as the application decompile: sector select at `0x0801A2FC` / `0x0801A318` (default sector 3), flush at `0x0801A368`, from M500 / M501 / M502 / M504 / M2050. The bootloader never touches these sectors **[V]**.

**Sector 3 is the live copy.** It matches [docs/marlin_M503_settings.txt](../../../marlin_M503_settings.txt) **[V]**:

- **M92** X/Y/Z 800, E 1150.
- **M203** 500/500/500/100.
- **M201** 3000/3000/3000/1000.
- **M204** P1000 R1000 T3000.
- **M205** B20000, X/Y/Z jerk 10, E jerk 5, plus 0.02 (junction deviation).
- **M851** Z −14.29 at offset `0x10E`.
- **Delta:** H 233.22 at `0x21F`; M666 −0.03/−0.13/0 at `0x223`; R 160.31 at `0x22F`; L 357.5 at `0x233`; S 200 at `0x237`; tower trims 0.11/−0.07/−0.04 at `0x23B`.
- **M301** P22.2 I1.08 D114 at `0x253`.
- **7 × 7 bilinear mesh** at `0x136`: grid_max 7,7; spacing 35 mm; start (−105, −105); 49 z-values at `0x148` matching the G29 W list.

**Sector 2 is an older copy.** The same settings, except H = 233.32 and **no mesh** (all NaN, spacing 0).

Full decode: `settings_decode.txt`. `settings_0x08008000_32k.bin` is the same bytes as the dump at `0x08008000`.

**No unit id in these sectors [V]:**

- No serial number, ID string, or MAC. The only ASCII is `V81`.
- What differs per machine is the **calibration**: delta height and trims, endstop adjustments, probe Z offset, bed mesh, and PID.
- The OTP block is blank **[V]**.
- The factory UID at `0x1FFF7A10` (not in these dumps) is the per-chip id, and only the USB serial-number descriptor uses it.

## 5. Recovery, gentlest first

Stop `ivi_bridge.py` before any direct USB-C session. It holds the port while it runs. Start it again afterwards.

1. **Same-version re-flash through the A33 (USB-stick package)** **[V]** for the STM32 side, **[I]** for the A33 UI offering it when the MD5s match:
   - Rewrites application sectors 4–5 only.
   - Works on a healthy board, and also after an interrupted update, because the pending record then keeps the bootloader up.
   - Does not restore sectors 0–3. Settings survive because this path never erases them.
2. **Send the `.supx` stream from a computer over USB-C** **[V]** that the port and the bootloader are reachable, stream itself not sent:
   - The bootloader speaks this protocol on USB CDC (`0483:5740`, product `STM32 Virtual ComPort`).
   - 2026-11-10 **[V]**: `M997\n` to the app on `/dev/cu.usbmodem*` brought that product up in about 0.9 s, and the second `M997\n` returned `C4 05 B0 19 A2`.
   - Entry after a software reset is what that USB session showed **[V]**. The pending-record path is in the image **[V]**; this printer was already running the app, so that record was not set. The 1 s window after a cold power-on has not been timed on the hardware **[?]**.
   - Replaying A1/A2/A3 would write the application. That stream has not been sent. It needs its own approval.
   - `tools/stm32/bootloader_probe.py` does the enter, reply check, and A4 return, and refuses A1, A2, and A3.
3. **Start the app** when the board is sitting in the bootloader (EEPROM fault, or any software reset): send `A4 02 AA AA AA AA 9F BD` over USB CDC or USART2 **[V]** in the image. On USB-C, 2026-11-10, that frame started the app, produced no reply, wrote no flash, and the touchscreen showed no errors **[V]**. The app was back as `BLACK_F407VE CDC` within 4 s.
4. **SWD, last:**
   - Program the 512 KB dump (`stm32_flash_20261110_a.bin`), or only the damaged region: sectors 0–1 bootloader, 2–3 settings, 4–5 app. Read it back.
   - Programming is erase plus write, so it stays a separate decision and should be sector-scoped on the same ST-Link.
   - **Leave the option bytes alone.** RDP is already level 0; writing them is not required.
5. **ST ROM DFU (BOOT0)** is a fallback only. This bootloader does not provide DFU, and the BOOT0 pin is still untraced **[?]**.

## Needs a hardware check

- **[?]** An I²C EEPROM (24Cxx-class) is on PB10/PB11, and what address `0x20..0x2F` holds. It should not be a valid pending record on a printer that boots the app. The bootloader has no command that dumps that record; a check needs a probe on the bus.
- **[?]** USART2 PD5/PD6 is the CH340 link to the A33. The protocol match makes this very likely **[I]**. The USB-C session does not measure that wire.
- **[?]** What PD0 (driven high) and PC1/PC2/PC6/PC7 and PA6/PA7 (driven low) switch.
- **[?]** The 1 s listen window after a cold power-on, timed on the hardware. The software-reset entry is already **[V]**.

## Files

- `REPORT.md` — this note.
- `disasm/*.s` — Capstone listings of the cited functions, literals filled in.
- `disasm/bootloader_full_linear.s` — linear sweep of `0x08000188`–`0x08006933`. Data shows up as junk instructions; read it next to the decompile.
- `disasm/bootloader_ghidra_decompile.c` — full decompile (268 functions).
- `bl_protocol_model_output.txt` — offline protocol run. Regenerate with `python3 tools/stm32/bl_protocol_model.py`.
- `settings_decode.txt` — sectors 2–3 decode.
- `ram_init_0x20000000.bin` — decompressed `.data`.
- `ghidra/DecompAll.java` — headless decompile script.
- `bl_0x08000000_32k.bin`, `settings_0x08008000_32k.bin` — those ranges of the flash dump.
