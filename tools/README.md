# Tools

| Path | What it is |
|---|---|
| [ivi_touch_nav/](ivi_touch_nav/README.md) | v0.2.0 touchscreen navigator. Runs on the computer, injects taps over SSH. Tests: `python3 -m unittest discover -s tools/ivi_touch_nav/tests -v` from the repo root, or from that directory |
| [stm32/supx_stream.py](stm32/supx_stream.py) | Offline: split `firmware.supx` into the bootloader frames the A33 sends, and check every CRC. Sends nothing |
| [stm32/thumbdis.py](stm32/thumbdis.py) | Offline Thumb disassembly of a raw image. Needs the `capstone` module |
| [a33/](a33/README.md) | `fb2png.py` (raw framebuffer to PNG) and `ivitap.sh` / `ivitap.c` (BusyBox and C tap helpers) |
| [a33_rescue/](a33_rescue/README.md) | A33 FEL and microSD rescue kit. FEL plus a RAM boot writes nothing. Emulation-tested only; the hardware list is still open. The 64 MiB card image is not committed |
| [command_map/](command_map/README.md) | Regenerators for [docs/data/stm32_app_commands.csv](../docs/data/stm32_app_commands.csv) |

Session procedure for the navigator: [docs/home_session/RUNBOOK.md](../docs/home_session/RUNBOOK.md).

`docs/supx_pack.py` still packs a raw STM32 image into a `.supx` file. It lives next to the format notes on purpose.
