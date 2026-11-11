# Backups and restore

No disk image belongs in this repo. The notes below say what was checked and which restore routes exist. None of the write routes is authorized.

## A33 eMMC (checked 2026-11-09)

A live `dd` of the running system, taken 2026-11-07 to the microSD card, is stored off-repo on the owner's drive. It is a full user-area image (3959422976 bytes) plus the two 2 MiB hardware boot areas. Zip CRC, the image manifest, and the boot-area checksums taken on the device all matched.

Partition table and mounts agree with [a33.md](a33.md#boot-chain): p1 FAT32 Wi-Fi files, p2 FAT16 logos, p5 environment, p6 kernel, p7 ext4 rootfs (512 MiB). `fsck_msdos -n` was clean on p1 and p2. `e2fsck -fn` on p7 needed a journal replay, which is expected for a copy taken while the filesystem was mounted read-write; after replay the only message was cosmetic padding on the inode bitmap.

Limits of this backup:

- It was taken **live**, with the UI running. The rootfs is not a quiescent snapshot, and it has never been restored onto a board.
- p1 may have been mid-write. autorun will format p1 if it fails to mount.
- The eMMC EXT_CSD boot-partition enable was not recorded, so which boot area the BROM actually uses is **[U]**.
- The image contains credential material (password hash, Wi-Fi config). That is why it stays off-repo.

A redacted console log from the backup session and from earlier read-only UART sessions is [research/a33_uart_boot_20261107.log](research/a33_uart_boot_20261107.log).

## Restore routes (none authorized)

| Situation | Route |
|---|---|
| UI binary damaged, Linux still boots | ttyS2 shell. Copy a known-good `firmware` onto `/userapp/app/IVI-Main-Controller` from a stick. Do not run the USB update package if the goal is only to replace that one file: the package copies `script/` and `printer_http_api/` before its checks |
| Rootfs will not mount, console still reaches U-Boot or a rescue ramdisk | Restore individual partitions from the off-repo image. Do not `dd` p7 while it is the running root. Run `e2fsck` so the journal replays before relying on the copy |
| No boot at all | [tools/a33_rescue/](../tools/a33_rescue/README.md). Safest is FEL plus a RAM boot, which writes nothing (risk **R1**). Read-only UMS and a rescue microSD are the next paths. A card the BootROM ignores falls through to a normal stock boot (**W2**). Partition restores and a full user-area write are **W3** / **W4** and stay unauthorized. Stock `work_mode=0` on a card does not burn. OTG gadget was disabled in the live capture (`enable=0`), and the micro-USB wiring is **[U]** |
| Motion application damaged, bootloader intact | Gentlest routes, in order, are in [stm32.md](stm32.md#recovery). A same-version USB-stick package rewrites sectors 4–5 only and also works when an interrupted update has left the bootloader waiting. USB-C entry from a computer is confirmed (2026-11-10); the update stream itself has not been sent. `A4` starts the app and writes no flash. SWD is last |

`saveenv`, partition restores, FEL writes, and SD/eMMC image writes need an explicit decision before anyone runs them.

## A33 rescue kit

[tools/a33_rescue/](../tools/a33_rescue/README.md) is the FEL and microSD kit for the routes above. The safest path is FEL plus a RAM boot: the BootROM loads the rescue system into DRAM, and the eMMC is not written. Risk labels run from **R0** (read only) to **W4** (whole user-area write). QEMU checked the userspace scripts, 24 of 24, on a stand-in disk. SPL, DRAM, FEL, the USB gadget, and EXT_CSD reads have not been run on this board. The hardware verification list in [RESCUE.md](../tools/a33_rescue/RESCUE.md) is still open.

Built binaries that fit are in `tools/a33_rescue/out/`, with checksums in `SHA256SUMS`. The 64 MiB rescue card image is left out of the repo. Its sha256 stays in that file. Rebuild it from [BUILD.md](../tools/a33_rescue/BUILD.md). No eMMC image is in the repo.

## STM32

RDP on this unit is **level 0** (`FLASH_OPTCR` `0x0FFFAAED`), with no sector write protection. OTP is blank. The 2026-11-10 read-only SWD image is [firmware/stm32_dump/](../firmware/stm32_dump/README.md): 512 KB flash (two reads, one MD5), system ROM, OTP, and option bytes. `firmware.supx` is only the application, and those bytes match the dump from `0x08010000`. Sectors 0–1 are the bootloader. Sectors 2–3 are Marlin `V81` settings (sector 3 live, sector 2 an older copy, no serial number). A later M500 rewrites sector 3, so compare regions separately.

Recovery, gentlest first. The mechanisms are in [stm32.md](stm32.md#recovery).

1. **A33 package.** Settings → Update Firmware with a stock package whose `firmware.supx` MD5 matches `config2.ini`. Rewrites sectors 4–5 only. An interrupted update leaves an EEPROM "pending" record, and the bootloader then stays up for a re-send. Settings and the bootloader are not restored, and they are not erased by this path.
2. **USB-C from a computer.** Confirmed reachable on 2026-11-10 **[V]**: `M997\n` to the running app (`/dev/cu.usbmodem*`, product `BLACK_F407VE CDC in FS Mode`) re-enumerated the bootloader as `STM32 Virtual ComPort` in about 0.9 s, and a second `M997\n` returned `C4 05 B0 19 A2`. The A1/A2/A3 stream has not been sent. Stop `ivi_bridge.py` first; it holds the USB port while it runs. Start it again afterwards. `tools/stm32/bootloader_probe.py` does the entry check and the return, and does not send a write frame.
3. **`A4 02 AA AA AA AA 9F BD`** starts the app and writes no flash **[V]** on that USB-C session (no reply, app back within 4 s, touchscreen clean). Use this when the board is sitting in the bootloader.
4. **SWD**, last. Program the dump, or one region, and read it back. Programming erases. Do not write option bytes. The read pattern is [tools/stm32/openocd_readonly.cfg](../tools/stm32/openocd_readonly.cfg): `mem_ap` only, no reset, no halt, no `cortex_m` examine.
5. **ROM DFU** (BOOT0 high) remains a fallback. BOOT0 has not been found **[?]**. Clearing readout protection mass-erases the chip; this unit is already level 0, so that step does not belong in a restore.

## GD32

Two SWD reads of the 16 KiB flash matched. The image is not published here; the SHA-256 and the listing are in [gd32.md](gd32.md). Option bytes were not read. The listing is not a restore procedure.

## Related

[a33.md](a33.md) · [stm32.md](stm32.md) · [gd32.md](gd32.md) · [tools.md](tools.md) · [../tools/a33_rescue/README.md](../tools/a33_rescue/README.md)
