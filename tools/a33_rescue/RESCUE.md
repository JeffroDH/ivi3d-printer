# IVI3D A33 touchscreen board: rescue runbook

Kit built 2026-11-10 (America/Chicago). **Nothing in this kit has been run on the IVI board.**
Every step that touches the board is a separate decision. Do them one at a time, and stop
at the first thing that doesn't match what this page says to expect.

## Risk levels

| Level | Meaning |
|---|---|
| **R0** | Read only. Nothing is written anywhere on the board. |
| **R1** | Writes **board RAM only** (FEL loading), or exports the eMMC **write-protected** over USB. Power-cycling undoes it. |
| **W1** | Writes **the microSD card or a file on the Mac**. The eMMC is not written. |
| **W2** | Lets the **stock system boot normally** from eMMC. That is the same as an ordinary power-on: the stock ramdisk runs `e2fsck -y` on p7, autorun clears `/userapp/tmp`, and it can `mkfs.vfat` p1 if p1 won't mount. It's listed because it is the fallback whenever the BootROM does not take a card. |
| **W3** | **Writes one eMMC partition** (p6 or p7) or repairs p7. Typed confirmation; the source MD5 is checked first. |
| **W4** | **Writes the whole eMMC user area**, bootloaders included. Typed confirmation; the image MD5 is checked first. A power cut part-way leaves the board unbootable from eMMC until it is written again over FEL or from a card. |

## Safest-first order of paths

1. **FEL + RAM boot, no card (R1).** BootROM USB mode; everything is loaded into DRAM over USB. Nothing reads from or writes to storage until you run a rescue command. This needs a way into FEL (see "Entering FEL") and needs the micro-USB port to be the A33 OTG port. Both are **unverified**.
2. **FEL + U-Boot UMS (R1).** The same FEL load, but U-Boot only exports the eMMC to the Mac as a **write-protected** disk, so you can image it with `dd`.
3. **FEL-entry microSD (W1 to make the card, then R1, or W2 on fallback).** The card holds only the 8 KiB `fel-sdboot.sunxi`. If the BootROM takes the card, the board drops into FEL and you continue with path 1. If it doesn't, the board boots normally (W2).
4. **Rescue microSD (W1 to make the card, then R1, or W2 on fallback).** Mainline U-Boot, kernel and initramfs boot from the card. There is no USB cable and no FEL entry needed, and it has room for backups. The fallback is the same as path 3.
5. **Writes (W3, W4)**, from inside the rescue system, only after a fresh backup and the read-only checks.

The A33 manual (User Manual r1.1, §3.2, Fig. 3.2-1) gives the BootROM order as **FEL pin low → USB FEL; otherwise SDC0 (microSD, PF pins) → NAND → SDC2 (eMMC, PC pins) → SPI0 → USB FEL**. A medium that fails moves on to the next. The stock `script.bin` maps SDC0 to PF0–PF5 (card detect PB4) and the eMMC to SDC2 (PC5–PC16). That is the basis for "the microSD is tried before the eMMC". **It has never been observed on this board**, so the card paths still carry the W2 fallback.

## What you need

- **The USB-TTL adapter on the debug UART pads** (PB0/PB1, the same pads as the stock `ttyS2` console): 3.3 V, VCC left open, RX/TX crossed, GND common, 115200 8N1. The rescue U-Boot and Linux use the same pads (mainline calls the port `uart0` on PB0/PB1, so it shows up as `ttyS0`). Open the terminal before power-on.
- **For FEL paths:** a micro-USB data cable to the Mac, and `sunxi-fel` (`fel/build-sunxi-fel-macos.sh`).
- **For card paths:** a spare microSD card. Use 8–32 GB if you want to keep a backup on it (the eMMC image is about 3.96 GB, which fits FAT32's 4 GiB file limit).
- **The checksums:** the `out/` files and `out/SHA256SUMS`. Every script re-checks these before loading anything.

Reference values for the 2026-11-07 backup (also in `/etc/ivi/known-good.txt` inside the rescue system):

| File | Bytes | MD5 |
|---|---|---|
| `mmcblk0.img` (user area) | 3,959,422,976 | `400889383907f6a864e65bbea4e27c57` |
| `mmcblk0boot0.img` | 2,097,152 | `50446d3316c714e8203433f714253ef8` |
| `mmcblk0boot1.img` | 2,097,152 | `b2d1236c286a3c0704224fe4105eca49` |

---

## Part 1: steps that only read (R0/R1), plus making cards (W1)

### 1.1 Build sunxi-fel on the Mac (W1 on the Mac only, board not involved)
```
cd tools/a33_rescue/fel && ./build-sunxi-fel-macos.sh
export SUNXI_FEL=$PWD/sunxi-tools/sunxi-fel
```

### 1.2 Enter FEL (board action, R0 by itself)
See "Entering FEL" below. In FEL the board shows nothing on the screen or the UART and waits on USB.
- **Mac check:** `system_profiler SPUSBDataType | grep -A4 -i "1f3a"`. The device should be vendor 0x1f3a, product 0xefe8.

### 1.3 Identify the SoC (R0)
```
fel/fel-identify.sh
```
- **Expect:** `AWUSBFEX soc=00001667(A33) ...`.
- `sunxi-fel version` asks the BootROM for its ID and changes nothing.
- Do **not** publish the output of `sunxi-fel sid`. It is the chip's unique ID.

### 1.4 RAM-boot the rescue system over FEL (R1)
```
fel/fel-ramboot.sh
```
- **Expect on the UART, in order:**
  - `U-Boot SPL 2026.10-ivi3d-rescue`, then DRAM size `512 MiB`.
  - `U-Boot 2026.10-ivi3d-rescue`, then `(FEL boot) sourcing script from RAM`.
  - Kernel messages, then the `IVI3D A33 RESCUE` banner with `eMMC : /dev/mmcblk1 -> READ-ONLY`.
- Press Enter to get the `ivi-rescue#` prompt.
- **If SPL hangs after the DRAM line** (wrong DRAM settings), nothing has been written. Power off.

### 1.5 Look around (R0)
```
ivi-status
```
- Shows the device sizes, the read-only flags (expect `ro=1` everywhere on the eMMC) and the partition starts and sizes.
- It also shows **EXT_CSD PARTITION_CONFIG**, which says whether the eMMC boots from boot0, boot1 or the user area. Write that value down: it was never recorded.

### 1.6 Compare the eMMC with the backup (R0)
```
ivi-verify --parts
```
- boot0 and boot1 should **MATCH**.
- The user area will normally **DIFFER**, because the stock system writes p1 and p7 on every boot. The per-partition MD5s show which partitions changed.

### 1.7 Image the eMMC to the Mac instead (R1, writes a file on the Mac)
```
fel/fel-ums.sh                       # board: U-Boot exports eMMC write-protected
diskutil list                        # find the ~3.96 GB external disk, e.g. disk6
fel/image-emmc-macos.sh disk6        # refuses any disk that isn't exactly 3,959,422,976 bytes
```
- macOS may auto-mount p1 and p2 read-only. The script unmounts them before reading.
- Press Ctrl-C on the UART to stop UMS, then power off.

### 1.8 Make a rescue microSD (W1, card only)
On the Mac: `fel/make-sdcard-macos.sh diskN`.
- **Guards:** whole disk only, external or removable only, ≤64 GB, and you type the disk id to confirm.
- **What it writes:**
  - MBR with p1 FAT32 from 4 MiB.
  - U-Boot at 8 KiB.
  - The kernel, DTB, initramfs, `ivi-rescue.scr` and this file.
- On Linux instead, rebuild `out/ivi-rescue-sd-64M.img` from BUILD.md (it is not in the git tree) and write it with `dd`. It is only 64 MiB, which is enough to boot but not for backups.

### 1.9 Boot the rescue microSD (R1 if the card is taken, W2 if not)
- Insert the card, open the UART, then power on.
- **Expect:**
  - `U-Boot SPL 2026.10-ivi3d-rescue`, then `== IVI3D rescue U-Boot (read-only MMC build) ==`.
  - `IVI3D rescue: loading kernel + initramfs from microSD (mmc 0:1)`.
  - The banner, showing the SD mounted at `/mnt/sd`.
- **If you see `BOOT0 is starting!` instead**, the BootROM skipped the card and this is a normal stock boot (W2). Let it finish, then power off.

### 1.10 Back up the eMMC to the card (W1, card only)
```
ivi-backup
```
- Copies the user area plus boot0 and boot1 to `/mnt/sd/ivi-backup-N/`.
- Re-reads the eMMC and the copies, and refuses to finish unless the MD5s match.
- Writes `images.md5` and `mmcblk0.img.md5`.
- Do this before **any** W3 or W4 step: it is the snapshot of what is on the eMMC *now*.

### 1.11 Check a restore image (R0)
- Copy the image onto the card's `backups/` folder on the Mac (read from the 14TB drive, write to the card).
- Then run:
```
ivi-image-check /mnt/sd/backups/mmcblk0.img --parts
```
- **Checks:**
  - Size, and the MD5 against the known value or the image's `.md5` sidecar.
  - The partition table, start and size, against the eMMC.
  - Whether p7's journal still needs recovery. It does for the 2026-11-07 image.

### 1.12 Prepare p7 (W1, card only)
```
ivi-prep-p7 /mnt/sd/backups/mmcblk0.img
```
- Re-checks the image MD5.
- Copies p7 out of the read-only-attached image onto the card.
- Runs `e2fsck -fy` on **that copy**, which replays the journal.
- Writes `p7_prepped_<md5>.img`, `.md5`, `.e2fsck.log` and `.prepped`.
- The original image is never modified.

### 1.13 Leave
`ivi-off` syncs, unmounts the card and powers off. If the PMIC does not cut power, unplug once the console says the system halted.

---

## Part 2: steps that write the eMMC (W3/W4)

**Before any of these:**
- 1.10 is done with this card in place: a fresh, verified backup.
- 1.11 passed for the source image.
- Power is stable, and nothing else is connected to the printer.

**Every write command:**
- refuses to run with an eMMC partition mounted;
- re-checks the source MD5, against the known value or a sidecar, before asking anything;
- checks that the source size equals the target size;
- asks you to type an exact phrase, so anything else aborts with nothing written;
- turns on writes only for the target;
- sets the eMMC read-only again on exit, including after Ctrl-C;
- reads the target back and compares its MD5.

Logs go to `/mnt/sd/ivi-rescue-logs/session.log`.

### 2.1 Restore the boot image partition p6 (W3)
```
ivi-restore-part p6 --from-image /mnt/sd/backups/mmcblk0.img
#   phrase: WRITE p6 <first 8 hex of the p6 MD5>
```
- With `--from-image`, it also checks that the image's partition table matches the eMMC's.
- A raw file can be used instead, as `ivi-restore-part p6 FILE`. It needs `FILE.md5` next to it.

### 2.2 Restore the rootfs p7 (W3)
```
ivi-restore-part p7 /mnt/sd/backups/p7_prepped_40088938.img
#   phrase: WRITE p7 <first 8 hex>
```
It refuses any p7 source whose journal still needs recovery. That includes `--from-image` on the raw 2026-11-07 image: run 1.12 first.

### 2.3 Repair p7 on the eMMC (W3)
```
ivi-fsck-p7          # prints e2fsck -fn (read-only) first, then phrase: FSCK p7
```

### 2.4 Restore the whole eMMC user area (W4)
```
ivi-restore-full /mnt/sd/backups/mmcblk0.img
#   if no ivi-backup-* on the card: phrase NO CURRENT BACKUP
#   then: RESTORE FULL EMMC <first 8 hex of image MD5>   (40088938 for the 2026-11-07 image)
```
- Writes MBR, boot0 at 8 KiB, U-Boot at sector 38192, env, kernel, rootfs and UDISK.
- Re-reads all 3,959,422,976 bytes to verify.
- **Then run 2.3.** The restored p7 carries the backup's unreplayed journal (the stock ramdisk's `e2fsck -y` would also replay it on first boot).

### Not provided, on purpose
- **Writing the eMMC hardware boot areas (boot0/boot1):** they are verify-only here. boot1 is all zero in the backup, and which boot area the BootROM uses is still unknown; 1.5 records it.
- **Writing EXT_CSD** (boot partition enable, bus width): no command here.
- **U-Boot writes:** the rescue U-Boot is built without MMC write support, environment saving, fastboot, DFU or EFI.

---

## Entering FEL (all **unverified on this board**)

| Method | How | What runs | Status |
|---|---|---|---|
| **FEL / UBOOT_SEL pin low at power-on** | A33 manual §3.2.1: "the UBOOT_SEL pin pulled up by internal 50K resistor … can be set to low level" to boot USB directly. On many A33 boards it is a button marked FEL, UBOOT or RECOVERY, or a test pad. Hold it to GND while applying power, then release. | BootROM only | **[U]** The location on the IVI board is not known. Look for an unpopulated button or a pad labelled FEL/UBOOT/BOOT near the A33 or the SinA33 module. Do not short random pads. |
| **FEL-entry microSD** | `fel/make-fel-sdcard-macos.sh diskN`, insert, power on. | BootROM, then the 6-instruction `fel-sdboot` (jump to the BootROM FEL entry 0xffff0020) | **[U]** It depends on the BootROM trying the microSD slot (manual says yes; not observed here). If it isn't taken, you get a normal stock boot (W2). |
| **Stock U-Boot `fel_key`** | `script.bin` `[fel_key] fel_key_min=2 fel_key_max=7`. The stock U-Boot reads an LRADC key at boot and has "## jump to efex". | **Stock** boot0 + U-Boot from eMMC | **Not recommended.** It runs the vendor bootloader and its efex/flash code. The key wiring is unknown. |
| **Fall-through** | The BootROM reaches FEL when no medium boots. | none | Not usable: the eMMC always boots. |

The micro-USB to A33 USB0 (OTG) wiring is **[U]**. The stock system had the OTG gadget disabled (`enable=0`), so "no USB device seen" from stock Linux says nothing about FEL. If FEL is entered and the Mac sees no 1f3a:efe8 device, try another cable or port before assuming anything else.

---

## Must be verified on hardware (each its own authorised step; none done)

1. **FEL entry:** the button or pad location, or whether the FEL-entry card is taken.
2. **micro-USB = USB0/OTG:** the Mac sees 1f3a:efe8 in FEL.
3. **`sunxi-fel version` reports A33 (soc 0x1667).**
4. **Mainline SPL DRAM init** works with the stock values used here: DDR3 at 408 MHz, ZQ 0x3bbb (15291), ODT on, DCDC5 1.5 V. **The stock `dram_tpr*` timings are not used by mainline**, and that is the most likely place for a failure (a hang right after the SPL banner, no writes).
5. **PMIC voltages** match the stock `[power_sply]`: DCDC1 3.0 V, DCDC2 1.1 V, DCDC3 1.2 V, DCDC5 1.5 V, ALDO2 2.5 V, ALDO3 3.0 V. ALDO1 is set to 3.0 V, the A33 reference "vcc-io" value; the stock file doesn't list it.
6. **The debug UART shows SPL and U-Boot output** on the same PB0/PB1 pads (mainline uart0 function).
7. **The BootROM tries the microSD before the eMMC on this board,** and the slot is wired to SDC0.
8. **U-Boot device numbering:** `mmc list` should show `mmc@1c0f000` (SD) as 0 and `mmc@1c11000` (eMMC) as 1. `fel-ums.scr` and `ivi-rescue.scr` assume this. A mismatch is read-only either way.
9. **Linux sees the eMMC as `mmcblk1`** with 7,733,248 sectors, and p1/p2/p5/p6/p7 at the backup's offsets. `ivi-image-check` compares them.
10. **`ivi-status` reads EXT_CSD PARTITION_CONFIG.** Record it.
11. **The OTG gadget enumerates in peripheral mode** for `ivi-ums-ro` and U-Boot `ums`. VBUS detection uses the SinA33 DT defaults, not the stock `axp_ctrl`/PH8 ID settings.
12. **`ivi-off` powers off through the AXP223.** If not, unplug.
