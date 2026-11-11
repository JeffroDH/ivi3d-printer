# STM32 SWD dump, 2026-11-10

Read-only capture of the motion controller over the board's SWD pads, with an ST-Link V2 clone. OpenOCD used a `mem_ap` target only: no reset, no halt, and no `cortex_m` examine (that examine writes DHCSR, DEMCR and the FPB). The command pattern is [tools/stm32/openocd_readonly.cfg](../../tools/stm32/openocd_readonly.cfg).

Two independent reads of the 512 KB flash had the same MD5. One copy is stored here. `md5sum -c MD5SUMS` checks the four files.

| File | What |
|---|---|
| `stm32_flash_20261110_a.bin` | Flash at `0x08000000`, 512 KB. Bootloader, settings, and the V1.3.2 application |
| `stm32_sysmem_20261110.bin` | ST system ROM at `0x1FFF0000`, 30 KB. The bootloader does not call it |
| `stm32_otp_20261110.bin` | OTP at `0x1FFF7800`, 528 bytes, all `0xFF` (blank, lock bytes included) |
| `stm32_optbytes_20261110.bin` | Option bytes at `0x1FFFC000`, 16 bytes |

`FLASH_OPTCR` at the time of the read was `0x0FFFAAED`: RDP level 0 (`0xAA`), no sector write protection (`nWRP = 0xFFF`). DBGMCU_IDCODE `0x10076413` (STM32F405/407/415/417 family), CPUID `0x410FC241`, DPIDR `0x2BA01477`.

The application bytes match `firmware/Firmware/firmware.supx`. Sectors 2–3 are this unit's Marlin settings as of that night; a later M500 changes sector 3. There is no serial number or unit ID in the image. The chip UID at `0x1FFF7A10` was not part of these reads.

What the bootloader does with this image: [docs/stm32.md](../../docs/stm32.md) and [docs/research/stm32/bootloader/REPORT.md](../../docs/research/stm32/bootloader/REPORT.md).
