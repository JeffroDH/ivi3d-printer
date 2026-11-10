# IVI3D A33 rescue kit

Offline build. Not yet run on the board. The userspace was checked under QEMU only, and the hardware verification list in RESCUE.md is still open.

The safest path is FEL plus a RAM boot: nothing is written to the eMMC. Steps are labelled R0 through W4.

- **RESCUE.md**: the runbook. Risk levels, safest-first paths, read steps vs write steps, how to enter FEL, and the hardware verification list.
- **BUILD.md**: what was built vs only scripted, exact versions and sources, the safety audits and the QEMU test results.
- **out/**: binaries that fit in the repo, plus SHA256SUMS. `ivi-rescue-sd-64M.img` is omitted (64 MiB). Its hash stays in SHA256SUMS. Rebuild it from BUILD.md.
- **fel/**: the macOS sunxi-fel build, identify, RAM boot, read-only UMS, eMMC imaging, and card makers.
- **initramfs/rootfs/**: rescue userspace scripts (`ivi-*`).
- **configs/, patches/, dts/, bootscripts/**: U-Boot and Linux configuration, the U-Boot read-only UMS patch, the rescue DT and U-Boot scripts.
- **build/build-all.sh**: a reproducible build. **sdcard/**: the Linux card-image builder. **tests/**: the QEMU harness and log.

The kit contains no secrets and no backup image data. `known-good.txt` holds only sizes and MD5s.
