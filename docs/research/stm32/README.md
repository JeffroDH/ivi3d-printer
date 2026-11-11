# STM32 disassembly excerpts

These are the functions cited from [stm32.md](../../stm32.md). The application and A33 listings were produced offline from `firmware.supx` and the UI ELF. The bootloader listings are from the 2026-11-10 flash dump.

| Directory | What |
|---|---|
| [bootloader/](bootloader/REPORT.md) | Bootloader at `0x08000000`: boot decision, update handlers, settings decode, decompile and Capstone listings |
| [update/disasm/](update/disasm/) | A33 `Work` update path (`startUpgradeFirmware`, `jumpToBootloader`, `jumpToApp`, the reply parser) and the STM32 `M997` reset, flash driver, and option-byte register scan |
| [open_items/disasm/](open_items/disasm/) | `M106`/`M107`, CAN TX/RX, head-type `M2051`, serial `begin`, `CMD buffer` (screen port only), IWDG, fan pins |

The frame dump is [supx_stream_output.txt](supx_stream_output.txt). The bootloader model output is [bootloader/bl_protocol_model_output.txt](bootloader/bl_protocol_model_output.txt). Regenerate with:

```
python3 tools/stm32/supx_stream.py firmware/Firmware/firmware.supx
python3 tools/stm32/bl_protocol_model.py
```
