# Research archive

Line-level evidence behind the topic docs. The summaries are [../stm32.md](../stm32.md), [../a33.md](../a33.md), and [../gd32.md](../gd32.md).

| Path | Contents |
|---|---|
| [stm32/README.md](stm32/README.md) | Annotated disassembly of the update path and of the fan, CAN, serial, and watchdog functions |
| [stm32/bootloader/REPORT.md](stm32/bootloader/REPORT.md) | Bootloader from the 2026-11-10 SWD dump: boot decision, update protocol, settings, recovery |
| [stm32/supx_stream_output.txt](stm32/supx_stream_output.txt) | CRC check of the stock `.supx`, from [tools/stm32/supx_stream.py](../../tools/stm32/supx_stream.py) |
| [gd32/README.md](gd32/README.md) | GD32E230 listing, functions, peripherals, pseudocode. The 16 KiB image itself is not in the repo |
| [a33_uart_boot_20261107.log](a33_uart_boot_20261107.log) | Redacted ttyS2 capture: boot0 through the UI, plus the read-only shell session used to map processes and USB |

The STM32 flash, system ROM, OTP, and option bytes from 2026-11-10 are in [firmware/stm32_dump/](../../firmware/stm32_dump/README.md). eMMC images, rootfs dumps, and the GD32 image are not in the repo. Password hashes, SSIDs, and the printer serial stay out.
