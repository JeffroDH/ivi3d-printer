import pexpect, sys, time
OUT='/workspace/a33_rescue_20261110/out'
DTB='/workspace/a33_build/linux-out/arch/arm/boot/dts/allwinner/sun8i-h3-orangepi-pc.dtb'
cmd=(f"qemu-system-arm -M orangepi-pc -m 1024 -nographic -no-reboot "
     f"-kernel {OUT}/zImage -initrd {OUT}/initramfs.cpio.gz -dtb {DTB} "
     f"-drive file=/workspace/a33_build/test/sd.img,format=raw,if=sd "
     f"-append 'console=ttyS0,115200 regulator_ignore_unused clk_ignore_unused rdinit=/sbin/init loglevel=4 ivi.boot=qemu'")
log=open('/workspace/a33_build/test/qemu_session.log','w')
c=pexpect.spawn('/bin/bash',['-c',cmd],encoding='utf-8',timeout=240,codec_errors='replace')
c.logfile_read=log
c.expect('Please press Enter to activate this console')
c.sendline('')
PR='ivi-rescue# '
c.expect_exact(PR)
def run(s, answers=None, t=600):
    c.sendline(s)
    for pat,ans in (answers or []):
        c.expect_exact(pat, timeout=t); c.sendline(ans)
    c.expect_exact(PR, timeout=t)
    return c.before
def rc():
    return run('echo RC=$?').split('RC=')[-1].strip().split()[0]
results=[]
def check(name, cond):
    results.append((name, bool(cond))); print(('PASS ' if cond else 'FAIL ')+name, flush=True)

out=run('ivi-status'); check('init: SD detected+mounted', 'mmcblk0' in out)
run('mount -o remount,size=400m /tmp; cp /mnt/sd/bk/mmcblk0.img /tmp/emmc.img && losetup -P /dev/loop0 /tmp/emmc.img && sleep 1 && ls /dev/loop0p*')
run('export IVI_TEST_EMMC=loop0 IVI_TEST_SD=mmcblk0 IVI_TEST_KNOWN=/mnt/sd/test-known.txt')
run('. /usr/lib/ivi/common.sh; ivi_find_devices; ivi_lock_emmc')
out=run('blockdev --getro /dev/loop0; blockdev --getro /dev/loop0p7'); check('lock: whole+p7 ro', out.count('1')>=2)
run('dd if=/dev/zero of=/dev/loop0p7 bs=1k count=1'); check('ro blocks writes to p7', rc()!='0')
run('dd if=/dev/zero of=/dev/loop0 bs=1k count=1'); check('ro blocks writes to whole disk', rc()!='0')
out=run('ivi-verify'); check('verify: user area MATCH', 'MATCH backup (eMMC' in out)
out=run('ivi-image-check /mnt/sd/bk/mmcblk0.img'); check('image-check md5 match', 'MATCH known' in out); check('image-check layout identical','layout: identical' in out); check('image-check p7 needs recovery','NEEDS RECOVERY' in out)
# p7 straight from raw image must be refused
out=run('ivi-restore-part p7 --from-image /mnt/sd/bk/mmcblk0.img'); check('refuse p7 raw (journal)', 'unreplayed journal' in out)
# corrupt p6 on the fake eMMC, wrong confirmation, then right confirmation
run('blockdev --setrw /dev/loop0; blockdev --setrw /dev/loop0p6; dd if=/dev/zero of=/dev/loop0p6 bs=1M count=1 conv=fsync; . /usr/lib/ivi/common.sh; ivi_find_devices; ivi_lock_emmc')
out=run('ivi-restore-part p6 --from-image /mnt/sd/bk/mmcblk0.img', [('> ','wrong phrase')]); check('wrong phrase aborts', 'Aborted' in out)
out=run('blockdev --getro /dev/loop0p6'); check('still ro after abort', out.strip().endswith('1'))
c.sendline('ivi-restore-part p6 --from-image /mnt/sd/bk/mmcblk0.img')
c.expect(r'type exactly:\s+(WRITE p6 [0-9a-f]{8})'); phrase=c.match.group(1); c.expect_exact('> '); c.sendline(phrase); c.expect_exact(PR, timeout=600); out=c.before
check('p6 restore VERIFIED', 'VERIFIED' in out)
out=run('blockdev --getro /dev/loop0p6; blockdev --getro /dev/loop0'); check('relocked after p6 restore', out.split().count('1')>=2)
# prep p7 then restore it
out=run('ivi-prep-p7 /mnt/sd/bk/mmcblk0.img /mnt/sd/work'); check('prep-p7 ok', 'prepped p7:' in out)
run('mkdir -p /mnt/sd/work; ls /mnt/sd/work')
c.sendline('ivi-restore-part p7 $(ls /mnt/sd/work/p7_prepped_*.img)')
c.expect(r'type exactly:\s+(WRITE p7 [0-9a-f]{8})'); phrase=c.match.group(1); c.expect_exact('> '); c.sendline(phrase); c.expect_exact(PR, timeout=600); out=c.before
check('p7 restore VERIFIED', 'VERIFIED' in out)
out=run('dumpe2fs -h /dev/loop0p7 2>/dev/null | grep features'); check('restored p7 journal clean', 'needs_recovery' not in out)
# full restore after corrupting the whole fake eMMC
run('blockdev --setrw /dev/loop0; dd if=/dev/urandom of=/dev/loop0 bs=1M count=8 conv=fsync; blockdev --setro /dev/loop0')
c.sendline('ivi-restore-full /mnt/sd/bk/mmcblk0.img')
c.expect(r'type exactly:\s+(NO CURRENT BACKUP)'); c.expect_exact('> '); c.sendline('NO CURRENT BACKUP')
c.expect(r'type exactly:\s+(RESTORE FULL EMMC [0-9a-f]{8})'); phrase=c.match.group(1); c.expect_exact('> '); c.sendline(phrase); c.expect_exact(PR, timeout=600); out=c.before
check('full restore VERIFIED', 'VERIFIED: eMMC user area' in out)
out=run('ivi-verify'); check('verify after full restore MATCH', 'MATCH backup (eMMC' in out)
# fsck p7 (journal replay on the restored raw p7)
c.sendline('ivi-fsck-p7'); c.expect_exact('type exactly:   FSCK p7'); c.expect_exact('> '); c.sendline('FSCK p7'); c.expect_exact(PR, timeout=600); out=c.before
check('fsck-p7 ran', 'e2fsck exit code' in out)
out=run('dumpe2fs -h /dev/loop0p7 2>/dev/null | grep features'); check('p7 clean after fsck', 'needs_recovery' not in out)
# backup to SD
out=run('ivi-backup', [('[y/N] ','y')]); check('backup verified', 'Backup complete and verified' in out)
out=run('cat /mnt/sd/ivi-backup-1/images.md5; ls /mnt/sd/ivi-backup-1'); check('backup files', 'mmcblk0.img' in out)
# non-interactive confirmation must be refused
out=run('echo "RESTORE FULL EMMC x" | ivi-restore-full /mnt/sd/bk/mmcblk0.img'); check('non-tty refused', 'no interactive terminal' in out)
out=run('ivi-restore-part p5 /tmp/x'); check('p5 refused', 'only p6 or p7' in out)
run('tail -5 /mnt/sd/ivi-rescue-logs/session.log')
run('sync; umount /mnt/sd')
c.sendline('poweroff -f'); time.sleep(2); c.terminate(force=True)
print('SUMMARY', sum(r for _,r in results), '/', len(results))
