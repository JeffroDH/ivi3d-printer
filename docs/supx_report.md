# firmware.supx decode (IVI3D motion controller, Marlin V1.3.2-alpha)

## Container format (solved)
- File header (18 B): u32 0x00028C40 (=166976, file len-8), u16 0x0002 (format ver), u16 0xDC2A (whole-image checksum, likely CRC16), u16 0x03A1, u32 0x08010000 (load addr), u32 0x000277C4 (image len ≈161.7 KB).
- Then 652 records of 256 B: `u16 crc | u16 magic 0x40A2 | u32 flash addr | 248 B data`, addresses contiguous from 0x08010000 to 0x080377A0.
- Trailer: one record type 0x0BA2 with "ASCII" + padding, then `a9a9 a302 0aba 0000 de3a` (end marker/checksums).
- **No encryption, no compression.** Data is plaintext Thumb-2; the per-record CRC algorithm not yet identified (not needed to extract).
- Raw image: `supx_raw.bin` (161,696 B), base **0x08010000**. Bootloader therefore occupies 0x08000000–0x0800FFFF (64 KB) — not included.

## Vector table
SP=0x20020000 (128 KB SRAM top), Reset=0x08016E2D, default handler 0x08016E7D. Load in Ghidra: ARM:LE:32:Cortex, base 0x08010000.

## Build / provenance
- Built with PlatformIO, framework-arduinoststm32 3.10700.191028 (STM32duino), on Windows user "absin". Marlin 2.0.x STM32 HAL tree (`Marlin\src\HAL\STM32\HAL.cpp`), config header "Last Updated 2020-12-29".
- Version string "Marlin V1.3.2-alpha" is the vendor's version; codebase is Marlin 2.0.x (GPL). Vendor source not public; a stock Marlin 2.x could be built for STM32F407VET6 delta, but vendor extras (tool-head bus, smart drivers, status machine) would be lost.

## Features found (strings)
- Delta kinematics (M665/M666, home_delta), FIX_MOUNTED_PROBE, M48, UBL/bilinear mesh (M420/M421), linear advance (M900), filament runout + M600/M603, THERMAL_PROTECTION / runaway, MAXTEMP/MINTEMP, plausibility checks (bed 40-…), M112, M999, SOFTWARE_POWER, chamber temp.
- **Closed-loop smart stepper drivers:** DriveX/Y/Z/E0 with fault reports "Overload, locked rotor, phase stagger, High extruder pressure, Overvoltage, Undervoltage" and a driver table "Version HDCP HDCE Sub Mode(Open/Close/Servo/None) Dir RS". So the closed-loop sensing lives in the drivers, queried by this firmware over a bus.
- **Tool-head detection:** "info:Head 3DP,0.15–0.4mm", "Head Laser", "Head CNC", "error:No Print Head", "Tool Head Firmware/Hardware Version", "serial number check crc error" — heads have their own MCU with ID/serial and report nozzle size.
- CNC: "CNC BLCD Speed" (BLDC spindle). Laser: "Current Power".
- Sensors self-test: XMotor/YMotor/ZMotor, limits, Fans, Door (auto door check on/off), TempHumi, ToolHead, Print/Bed heat, Extruder, Filament.
- Job state machine: start work / pause / resume / stop / finish with error codes (driven by the UI host).
- UUID cede2a2f-41a2-4748-9b12-c55c62f367ff in M115.

## Reflash / replacement notes
- App at 0x08010000 behind 64 KB bootloader; UI pushes .supx over serial (M997 → bootloader, record CRC'd). Bootloader can't be read from .supx; needs SWD (check RDP level with ST-Link; if RDP0 full dump possible).
- A stock Marlin/Klipper board swap would need replacements for the smart-driver bus and tool-head bus.

## Limitations
- String/structure analysis only; Ghidra decompilation of M-code dispatch (M2001/M2410/M2411, AA 55 framing), pin map, and bus type (CAN/RS485/UART) not yet done. Record CRC16 polynomial not confirmed.
