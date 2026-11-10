# IVI3D A33 rescue kit: what was built, versions, how to rebuild

Built offline on Debian 13 (trixie, x86_64), 2026-11-10 (America/Chicago).
No board was touched. The backup image itself was not used (a synthetic
64 MiB stand-in with the same partition types was used for tests).

## Built (binaries in `out/`, checksums in `out/SHA256SUMS`)

| Artifact | What | Built from |
|---|---|---|
| `u-boot-sunxi-with-spl.bin` | Mainline SPL + U-Boot for A33 (FEL or microSD at 8 KiB) | U-Boot **v2026.10** (commit 5508406582f6), `Sinlinx_SinA33_defconfig` + `configs/u-boot-ivi3d-rescue.fragment` + `patches/u-boot-0001-ums-force-read-only.patch` |
| `u-boot-sunxi-with-spl.padded.bin` | Same, padded to a 1 KiB multiple for macOS raw-disk `dd` | |
| `zImage` | Linux **6.18.62** (longterm) | `sunxi_defconfig` + `configs/linux-ivi3d-rescue.fragment` |
| `sun8i-a33-ivi3d-rescue.dtb` | Rescue DT | `dts/sun8i-a33-ivi3d-rescue.dts` (includes mainline `sun8i-a33-sinlinx-sina33.dts`) |
| `initramfs.cpio.gz`, `uInitrd` | RAM-only rescue userspace | BusyBox **1.37.0** static, e2fsprogs **1.47.3** static (`e2fsck`, `dumpe2fs`), `initramfs/rootfs/` scripts |
| `ivi-rescue.scr`, `fel-boot.scr`, `fel-ums.scr` | U-Boot scripts | `bootscripts/*.cmd` |
| `fel-sdboot.sunxi` | 8 KiB eGON image that jumps to BootROM FEL | sunxi-tools commit 34dfa20f8284 (`bin/fel-sdboot.sunxi`, upstream prebuilt; disassembled and checked: `mrc p15 SCTLR; tst V; bx 0xffff0020`) |
| `ivi-rescue-sd-64M.img` | Bootable 64 MiB card image (boot test only). **Not in the git tree** (64 MiB). Hash stays in `out/SHA256SUMS`. Rebuild with the command below | `sdcard/make-sdcard-image.sh` |

`out/ivi-rescue-sd-64M.img` is omitted from the repo. Its sha256 in `out/SHA256SUMS` is `d776ff3b661bc3c64c0e007b9fd74af76d0c2a2e850bf382dcaa628c0881f8fe`. After the other `out/` files are present:

```
sdcard/make-sdcard-image.sh out out/ivi-rescue-sd-64M.img
```

`sha256sum -c out/SHA256SUMS` then reports that file missing until the rebuild. The image is a rescue microSD. It is not an eMMC dump. No eMMC image is in this kit.

## Scripted only (not built or not run here)

- **sunxi-fel for macOS arm64.** It was not built: the box has no macOS SDK or toolchain, and Homebrew has no sunxi-tools formula (formulae.brew.sh/formula/sunxi-tools returned 404 on 2026-11-10). `fel/build-sunxi-fel-macos.sh` builds the same pinned commit natively with Homebrew `libusb dtc pkg-config`. The identical commit was built and run on Linux x86_64 here (`sunxi-fel v1.4.2-221-g34dfa20`, A33 = soc_id 0x1667 in `soc_info.c`).
- **All `fel/*.sh` and the `make-*-macos.sh` scripts** are syntax-checked only. They are untested on macOS, and none has run against a board.

## Toolchain

arm-linux-gnueabihf-gcc (Debian 14.2.0-19) 14.2.0 · GNU ld (GNU Binutils for Debian) 2.44 · glibc (armhf cross) 2.41 · Version: DTC 1.7.2 · mkimage 2025.01 (u-boot-tools) · QEMU 10.0.13 (tests).
Debian packages came from mirrors.kernel.org/debian, because the default deb.debian.org http mirror returned HTTP 500 from the box.

## Source integrity

| Source | URL | SHA-256 |
|---|---|---|
| linux-6.18.62.tar.xz | https://cdn.kernel.org/pub/linux/kernel/v6.x/ | 490a7aedf1b355c565d3a6c05333ccccb5da82064eca46b590448a7099d7d651 |
| busybox-1.37.0.tar.bz2 | https://busybox.net/downloads/ | 3311dff32e746499f4df0d5df04d7eb396382d7e108bb9250e7b519b837043a4 |
| e2fsprogs-1.47.3.tar.xz | https://cdn.kernel.org/pub/linux/kernel/people/tytso/e2fsprogs/v1.47.3/ | 857e6ef800feaa2bb4578fbc810214be5d3c88b072ea53c5384733a965737329 |
| U-Boot v2026.10 | https://source.denx.de/u-boot/u-boot.git (tag) | commit 5508406582f6f7120dce0c4b3059819a41788db2 |
| sunxi-tools | https://github.com/linux-sunxi/sunxi-tools | commit 34dfa20f8284273085666436e4cac09af19646c8 |

The tarball hashes are pinned in `build/build-all.sh`. All three match the upstream published checksum files (kernel.org `sha256sums.asc` for Linux and e2fsprogs, busybox.net `.sha256`), checked 2026-11-10. The PGP signatures on those files were not verified.

## Rebuild

```
W=/path/to/workdir ./build/build-all.sh      # about 3 min on 8 cores from a warm tree
```
The package list is at the top of `build/build-all.sh`. The script fails if any safety audit below fails.

## Safety properties enforced at build time

**U-Boot** (`configs/u-boot-ivi3d-rescue.config.full`):
- `MMC_WRITE` and `SPL_MMC_WRITE` are off, and `mmc_write.o` is not built. `nm` shows no `mmc_bwrite`, `mmc_berase`, `env_save`, `fastboot_init` or `efi_set_variable_int`.
- `SUPPORT_EMMC_BOOT` is off, so there is no `mmc partconf` or `bootbus`.
- `ENV_IS_NOWHERE`, with no `saveenv`, `eraseenv` or `gpt` commands.
- There is no fastboot, DFU, EFI loader, network, LCD (video) or USB host (EHCI/OHCI), and `PREBOOT` is empty. U-Boot never powers the GL850G hub, CH340 or STM32 side.
- The UMS LUN is forced read-only by the patch (`initially_ro = 1`).
- `bootcmd` is fixed: the FEL script in RAM, otherwise `ivi-rescue.scr` on `mmc 0:1`, otherwise the prompt. It never scans the eMMC. The full default environment is in `build/u-boot-default-env.txt`. The distro-boot variables are still defined, but nothing runs them.
- DRAM 408 MHz, ZQ 15291 (0x3bbb), ODT on. AXP223 at the stock `[power_sply]` values. `bootdelay=3`.

**SPL boot device:** the sunxi SPL boots only from the device the BootROM reports (`sunxi_get_boot_device`). There is no board fallback list, so SPL from SD never reads U-Boot from the eMMC.

**Kernel:**
- No USB serial, USB host (EHCI/OHCI), DRM, sound, Wi-Fi or networking.
- The DT disables the display, audio and USB host, keeps the SoC at the bootloader clock (no 1.1/1.2 GHz OPPs), and aliases the SD to `mmcblk0` and the eMMC to `mmcblk1`.
- `regulator_ignore_unused clk_ignore_unused` leave the PMIC rails as the bootloader set them.

**Userspace:**
- `/etc/rescue-init.sh` sets the eMMC and every partition read-only (`BLKROSET`) before the prompt. It mounts only the microSD.
- Nothing fscks or mounts the eMMC automatically.

## Off-target test (QEMU)

QEMU `orangepi-pc` emulates an Allwinner H3, a sun8i Cortex-A7 sibling. There is no A33 model in QEMU. The test booted **the same `zImage` and `initramfs.cpio.gz`** with the mainline H3 DTB and a 512 MiB emulated microSD. A loop device stood in for the eMMC, using the test-only `IVI_TEST_EMMC`/`IVI_TEST_KNOWN` variables, which are never set on the board. Driver: `tests/qemu_test.py`. **24/24 checks passed:**
- **Detection and locking:** SD detected and mounted; the read-only lock blocks writes to the whole disk and to p7.
- **Read-only checks:** `ivi-verify` MATCH; `ivi-image-check` MD5, layout and needs_recovery detection.
- **Refusals:**
  - p7 from the raw image (journal not replayed);
  - a wrong confirmation phrase (still read-only afterwards);
  - a non-tty confirmation;
  - p5.
- **Writes and verification:**
  - p6 restore and read-back VERIFIED, then relocked;
  - `ivi-prep-p7`, then the p7 restore VERIFIED with a clean journal;
  - after deliberate corruption, `ivi-restore-full` VERIFIED and `ivi-verify` MATCH;
  - `ivi-fsck-p7` cleared needs_recovery;
  - `ivi-backup` verified.

**Not covered by the test:**
- the A33 SPL, DRAM, PMIC or eMMC driver;
- U-Boot itself (it is A33-specific);
- FEL;
- the USB gadget (`ivi-ums-ro`, U-Boot `ums`);
- EXT_CSD reading.

The session log is `tests/qemu_session.log`. The final run used the shipped `zImage` and `initramfs.cpio.gz` (sha256 3147fb45…). The stand-in eMMC layout is `tests/layout.sfdisk`.
