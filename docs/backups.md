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
| No boot at all | FEL plus a host tool that exposes the eMMC, or a microSD boot0 that only jumps to FEL. Stock boot0+U-Boot on a card is not that rescue: `work_mode=0` does not burn, and a failed card boot is not a tested path. OTG gadget was disabled in the live capture (`enable=0`), and the micro-USB wiring is **[U]** |
| Motion application damaged, bootloader intact, UI intact | Settings → Update Firmware with a stock package whose `firmware.supx` MD5 matches `config2.ini`. This rewrites `0x08010000` onward only. It does not restore the bootloader or the settings sectors. Entry depends on the bootloader answering `M997`, which needs a working app or a bootloader that waits on its own. The second case is **[U]**. See [stm32.md](stm32.md#update-protocol) |

`saveenv`, partition restores, FEL writes, and SD/eMMC image writes need an explicit decision before anyone runs them.

## STM32

`firmware.supx` is the application only. Sectors 0–1 (bootloader) and 2–3 (settings) are not in any file in this repo. A 512 KiB SWD read is the backup that would capture them. It is allowed only at readout-protection level 0, and only as its own authorized test: no reset, no halt, no erase, no program, no option-byte writes, and never clear readout protection (that mass-erases the chip). Compare the three regions separately. Settings sectors change on every M500.

ROM DFU on the USB-C port (BOOT0 high) would also see the whole flash at level 0. BOOT0 has not been found. Clearing level-1 protection is still a mass erase.

## GD32

Two SWD reads of the 16 KiB flash matched. The image is not published here; the SHA-256 and the listing are in [gd32.md](gd32.md). Option bytes were not read. The listing is not a restore procedure.

## Related

[a33.md](a33.md) · [stm32.md](stm32.md) · [gd32.md](gd32.md) · [tools.md](tools.md)
