# STM32 disassembly excerpts

These are the functions cited from [stm32.md](../../stm32.md). They were produced offline from `firmware.supx` and from the A33 UI ELF. Nothing here was run on a board.

| Directory | What |
|---|---|
| [update/disasm/](update/disasm/) | A33 `Work` update path (`startUpgradeFirmware`, `jumpToBootloader`, `jumpToApp`, the reply parser) and the STM32 `M997` reset, flash driver, and option-byte register scan |
| [open_items/disasm/](open_items/disasm/) | `M106`/`M107`, CAN TX/RX, head-type `M2051`, serial `begin`, `CMD buffer` (screen port only), IWDG, fan pins |

The reproducible frame dump is [supx_stream_output.txt](supx_stream_output.txt). Regenerate it with:

```
python3 tools/stm32/supx_stream.py firmware/Firmware/firmware.supx
```
