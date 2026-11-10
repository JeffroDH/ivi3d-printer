# System architecture and ports

The IVI 3D Printer is a delta (rod 357.50 mm, radius 160.31 mm, height 233.22 mm) with three processors on one carrier, `A33_407MB_200916`. Photos and the pad map are in [mainboard.md](mainboard.md).

| Processor | Role | How you reach it |
|---|---|---|
| **STM32F407VET6** | Marlin-derived motion firmware, "V1.3.2-alpha" | USB-C CDC serial, 115200 8N1. SWD on the central 5-pin header **[O]** |
| **Allwinner A33** (Sinlinx-style module) | Linux 3.4.39, Qt 5.9.6 touchscreen UI, kore HTTP | Wi-Fi TCP 8080 and UDP 20050. Debug console on `DEBUGUART` / the front 3-pin, **ttyS2 at 115200 8N1** **[V]** |
| **GD32E230F4** | Soft power button and rail sequencer. No serial link **[V]** | Lower SWD 5-pin is the likely target **[I]**; chip-pin continuity is **[U]** |

## How the two main CPUs are wired

```
Wi-Fi  ── AP6236 ── A33 ── EHCI ── GL850G hub ── CH340C ── USART2 (PD5/PD6) ── STM32
                              │                                              │
                         ttyS2 console                               USB OTG FS CDC
                         PB0/PB1 [V]                                 PA11/PA12 [V]
                              │                                              │
                    DEBUGUART pads / front 3-pin                      USB-C to the PC
```

- The A33 sees the motion controller as **`/dev/ttyUSB0`** (CH340, `1a86:7523`, hub port 2). Only `IVI-Main-Controller` holds that port while the UI is running **[V]**.
- The PC's USB-C port enumerates the STM32's own CDC interface (`0483:5740`, product `BLACK_F407VE CDC in FS Mode`), not Linux **[V]**.
- G-code on both ports is plain lines. The A33 sends no line numbers and no checksums. The PC port uses Marlin line numbers and checksums **[V]**.
- Toolheads sit on **CAN2** at 500 kbit/s, controller TX id `0x12`. Hotend heat, the head fans, the probe, the laser, and the spindle are on the head, not on mainboard MOSFETs **[V]**. See [stm32.md](stm32.md).

The front bottom-left 5-pin next to the CH340C is a separate connector. Which of the CH340's USB or UART pins it carries is **[U]**.

## What is listening

| Path | Opens | Does |
|---|---|---|
| TCP **8080** (kore, on wlan0) | Yes **[V]** | `connect`, `disconnect`, `status` (static `IDLE`), `setSystemTime`, `upload`, `sliceUpload`. No print start |
| UDP **20050** | Yes **[V]** | Answers ASCII `discover` only |
| TCP **22** | No, on stock boot **[V]** | `sshd` is on disk and not started. See [a33.md](a33.md) |
| USB-C CDC | Yes | Full G-code, including job control (`M2411`) |
| `DEBUGUART` / front 3-pin | Yes, on this unit **[V]** | Root shell on ttyS2, no login |

A LAN scan that shows port 22 closed is consistent with sshd never being started. It does not mean the binary is absent.

## How a job starts

The STM32 does not print from an SD card. The A33 **streams the file** line by line over `ttyUSB0`.

Touchscreen Start does, in order **[V]**:

1. `G53`, `G28`, and `G54` when the head is laser or CNC (homing, before any job-state command).
2. `M2001 S1` (restarts the USB CDC port and force-stops a job already running).
3. `M2411 S2` (enter the working state). This is accepted only from the idle state.
4. The file itself, paced by `CMD buffer:` on the screen port and by `ok`.

End of file appends `M2411 S3` (and `M5` for laser/CNC). Pause is `M2410`. Resume is `M2411 S1`.

A PC job on the USB-C port uses the same `M2411` codes on that port. The screen locks itself when it sees `Working Status: WORKING_PC`. Tapping Start or "Disconnect PC" during that job sends `M2001 S1` and stops it. Details: [stm32.md](stm32.md), [wifi_touch.md](wifi_touch.md).

## Fans, in one line

`M106 S0` with no `P` turns **both head fans on**. Use `M107` or `M106 P0 S0` on an FDM head. The auto heatsink-fan rule is on from boot, and with a laser head it forces P1 on every second. Full behaviour is in [stm32.md](stm32.md#fans).

## Hard limits

The STM32 on this board is irreplaceable.

- Over SWD: no reset, no halt, no erase, no program, and no option-byte writes.
- Never clear readout protection. Unprotecting mass-erases the chip.
- Every hardware test is individually authorized. The same SWD limits apply to the GD32 until a separate decision says otherwise.
- Do not write `ttyUSB0` while the Qt app is running.
- Do not commit eMMC images, rootfs dumps, serial numbers, MAC addresses, SSIDs, or password hashes.

## Where to go next

[stm32.md](stm32.md) · [a33.md](a33.md) · [gd32.md](gd32.md) · [wifi_touch.md](wifi_touch.md) · [backups.md](backups.md) · [mainboard.md](mainboard.md) · [tools.md](tools.md)
