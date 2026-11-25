"""boot.sh + persist helper under the printer's own busybox (qemu-arm).

Covers: rcS start-before-app (no start if tty missing; no app launch is the
supervisor's job), USB no-bridge, disable files, bootfail, default RAM jobs
dir, p1 log seed + job migrate once 'mounted' (never mounting p1 ourselves),
and the health-reset of bootfail. Timeouts are kept short."""
import os, shutil, subprocess, tempfile, time, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("A33_ROOT", "/tmp/a33root")
BB = ROOT + "/bin/busybox"
BOOT = os.path.join(HERE, "..", "scripts", "boot.sh")
RAM = os.path.join(HERE, "..", "scripts", "ivibridge-ram.sh")

class Boot(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="iviboot-")
        bb = os.path.join(self.d, "bbin"); os.mkdir(bb)
        for a in subprocess.run(["qemu-arm", "-L", ROOT, BB, "--list"], capture_output=True, text=True).stdout.split():
            if "/" in a: continue
            p = os.path.join(bb, a)
            open(p, "w").write('#!/bin/dash\nexec qemu-arm -L %s %s %s "$@"\n' % (ROOT, BB, a)); os.chmod(p, 0o755)
        # record mount/umount and refuse to ever mount p1 rw
        self.mountlog = os.path.join(self.d, "mount.log")
        self.usb_payload = os.path.join(self.d, "usb_payload"); os.mkdir(self.usb_payload)
        mnt = os.path.join(bb, "mount")
        open(mnt, "w").write(r'''#!/bin/dash
echo "$@" >> %s
ro=0
for a in "$@"; do [ "$a" = "ro" ] || [ "$a" = "-o" ] && continue; case "$a" in ro,*|*,ro|ro) ro=1;; esac; done
# last arg is the mount point, second-last the source
eval mp=\${$#}
# copy payload into the mount point when testing the USB probe
if [ -f %s/no-bridge ]; then cp %s/no-bridge "$mp"/no-bridge; fi
# detect a read-write mount of the p1 device or of WifiFile
case " $* " in
  *" /dev/mmcblk0p1 "*|*" WifiFile "*)
    case " $* " in *" rw "*|*" -o rw "*|*"rw,"*) echo P1_RW >> %s; exit 1;; esac
    ;;
esac
exit 0
''' % (self.mountlog, self.usb_payload, self.usb_payload, self.mountlog))
        os.chmod(mnt, 0o755)
        um = os.path.join(bb, "umount")
        open(um, "w").write('#!/bin/dash\necho umount "$@" >> %s\nexit 0\n' % self.mountlog); os.chmod(um, 0o755)
        self.home = os.path.join(self.d, "ivihome"); os.mkdir(self.home)
        self.p1 = os.path.join(self.d, "p1"); os.makedirs(self.p1)
        self.run = os.path.join(self.d, "run"); os.mkdir(self.run)
        self.jobs = os.path.join(self.d, "ivi_jobs"); os.mkdir(self.jobs)
        self.mnts = os.path.join(self.d, "mounts"); open(self.mnts, "w").write("rootfs / rootfs rw 0 0\n")
        self.link = os.path.join(self.d, "ttyUSB0"); open(self.link, "w").write("node 188:0\n")
        self.calls = os.path.join(self.d, "ram.calls")
        # stub supervisor: records start/stop, pretends success, does not talk to hardware
        self.stub = os.path.join(self.d, "stub-ram.sh")
        open(self.stub, "w").write(r'''#!/bin/sh
echo "$*" >> "$IVIB_CALLS"
if [ "$1" = "start" ]; then
    mkdir -p "$IVIB_DIR"
    echo "stub-start" >> "$IVIB_DIR/ram.log"
    echo $$ > "$IVIB_DIR/ivibridge.pid"
    echo $$ > "$IVIB_DIR/watchdog.pid"
    # pretend the daemon took the link
    if [ -n "$IVIB_LINK" ] && [ -e "$IVIB_LINK" ] && [ ! -L "$IVIB_LINK" ]; then
        rm -f "$IVIB_LINK"; ln -s /dev/null "$IVIB_LINK"
    fi
    exit 0
fi
if [ "$1" = "stop" ]; then echo stub-stop; exit 0; fi
exit 0
''')
        os.chmod(self.stub, 0o755)
        shutil.copy(os.path.join(HERE, "..", "scripts", "boot.sh"), os.path.join(self.home, "boot.sh"))
        os.chmod(os.path.join(self.home, "boot.sh"), 0o755)
        self.bb = bb
        self.base_env = dict(
            PATH=bb + ":/usr/bin:/bin",
            IVIB_HOME=self.home, IVIB_DIR=self.run, IVIB_P1=self.p1,
            IVIB_MOUNTS=self.mnts, IVIB_LINK=self.link, IVIB_BOOTFAIL=os.path.join(self.home, "bootfail"),
            IVIB_SELF=self.stub, IVIB_CALLS=self.calls, IVIB_TEST="1",
            IVIB_UPDIR=self.jobs, IVIB_TTY_TIMEOUT="1", IVIB_HEALTH_WAIT="1",
            IVIB_P1_WAIT="0", IVIB_MIGRATE_ROUNDS="0",
            IVIB_USBCHK=os.path.join(self.d, "usbchk"),
            IVIB_USB_TRY=os.path.join(self.d, "fakeusbdev"),
        )

    def tearDown(self):
        subprocess.run(["pkill", "-f", self.d], capture_output=True)
        shutil.rmtree(self.d, ignore_errors=True)

    def sh(self, script, *a, env=None, timeout=20):
        e = dict(self.base_env)
        if env: e.update(env)
        r = subprocess.run(["qemu-arm", "-L", ROOT, BB, "sh", script] + list(a),
                           env=e, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout + r.stderr

    def started(self):
        return os.path.exists(self.calls) and "start" in open(self.calls).read().split()

    def test_tty_timeout_leaves_stock(self):
        os.remove(self.link)
        t0 = time.time()
        rc, out = self.sh(os.path.join(self.home, "boot.sh"))
        self.assertLess(time.time() - t0, 5)
        self.assertEqual(rc, 0, out)
        self.assertIn("timeout", out + open(os.path.join(self.run, "boot.log")).read())
        self.assertFalse(self.started())
        self.assertFalse(os.path.exists(os.path.join(self.home, "bootfail")))

    def test_disable_file_skips_start(self):
        open(os.path.join(self.home, "disable"), "w").close()
        rc, out = self.sh(os.path.join(self.home, "boot.sh"))
        self.assertEqual(rc, 0, out)
        self.assertIn("disabled", out + open(os.path.join(self.run, "boot.log")).read())
        self.assertFalse(self.started())

    def test_p1_disable_when_mounted(self):
        open(self.mnts, "w").write("rootfs / rootfs rw 0 0\n/dev/mmcblk0p1 %s vfat rw 0 0\n" % self.p1)
        open(os.path.join(self.p1, "ivibridge.disable"), "w").close()
        rc, out = self.sh(os.path.join(self.home, "boot.sh"))
        self.assertEqual(rc, 0, out)
        self.assertIn("ivibridge.disable", out + open(os.path.join(self.run, "boot.log")).read())
        self.assertFalse(self.started())
        # must not have tried to mount p1
        if os.path.exists(self.mountlog):
            self.assertNotIn("mmcblk0p1", open(self.mountlog).read())
            self.assertNotIn("P1_RW", open(self.mountlog).read())

    def test_usb_no_bridge_already_mounted(self):
        usb = os.path.join(self.d, "usb"); os.mkdir(usb)
        open(os.path.join(usb, "no-bridge"), "w").close()
        open(self.mnts, "w").write("rootfs / rootfs rw 0 0\n/dev/sda1 %s vfat rw 0 0\n" % usb)
        rc, out = self.sh(os.path.join(self.home, "boot.sh"))
        self.assertEqual(rc, 0, out)
        self.assertIn("no-bridge", out + open(os.path.join(self.run, "boot.log")).read())
        self.assertFalse(self.started())

    def test_usb_no_bridge_probed_when_unmounted(self):
        open(os.path.join(self.usb_payload, "no-bridge"), "w").close()
        # IVIB_TEST=1 lets the probe run even though fakeusbdev is not a block device
        rc, out = self.sh(os.path.join(self.home, "boot.sh"))
        self.assertEqual(rc, 0, out)
        self.assertIn("no-bridge", out + open(os.path.join(self.run, "boot.log")).read())
        self.assertFalse(self.started())
        self.assertTrue(os.path.exists(self.mountlog))
        ml = open(self.mountlog).read()
        self.assertIn("ro", ml)
        self.assertIn("umount", ml)
        self.assertNotIn("P1_RW", ml)

    def test_bootfail_skips_after_two_failures(self):
        open(os.path.join(self.home, "bootfail"), "w").write("2\n")
        rc, out = self.sh(os.path.join(self.home, "boot.sh"))
        self.assertEqual(rc, 0, out)
        self.assertIn("disabled after 2 failed boots", out + open(os.path.join(self.run, "boot.log")).read())
        self.assertFalse(self.started())
        self.assertEqual(open(os.path.join(self.home, "bootfail")).read().strip(), "2")

    def test_bootfail_increments_on_start(self):
        rc, out = self.sh(os.path.join(self.home, "boot.sh"))
        self.assertEqual(rc, 0, out)
        self.assertTrue(self.started())
        self.assertEqual(open(os.path.join(self.home, "bootfail")).read().strip(), "1")
        # default upload dir is RAM, not p1
        # (boot.sh exports IVIB_UPDIR=/tmp/ivi_jobs unless overridden; we overrode for the test)
        log = open(os.path.join(self.run, "boot.log")).read()
        self.assertIn("starting supervisor", log)

    def test_default_updir_is_ram(self):
        env = dict(self.base_env); env.pop("IVIB_UPDIR", None)
        rc, out = self.sh(os.path.join(self.home, "boot.sh"), env=env)
        self.assertEqual(rc, 0, out)
        # the stub does not record the env; inspect boot.sh's exported default by wrapping
        # boot.sh writes nothing about updir, so re-read the script contract via a one-shot
        r = subprocess.run(["qemu-arm", "-L", ROOT, BB, "sh", "-c",
                            'unset IVIB_UPDIR; . %s >/dev/null 2>&1; echo ${IVIB_UPDIR:-unset}' % "/dev/null"],
                           capture_output=True, text=True)
        # direct check of the script text (the default assignment)
        src = open(BOOT).read()
        self.assertIn("IVIB_UPDIR=${IVIB_UPDIR:-/tmp/ivi_jobs}", src)
        self.assertNotIn("WifiFile/ivibridge_jobs", src)

    def test_persist_seeds_logs_and_migrates_idle_jobs(self):
        # p1 already "mounted"; run the real persist helper (not the stub)
        open(self.mnts, "w").write("rootfs / rootfs rw 0 0\n/dev/mmcblk0p1 %s vfat rw 0 0\n" % self.p1)
        open(os.path.join(self.run, "boot.log"), "w").write("early boot line\n")
        open(os.path.join(self.run, "ram.log"), "w").write("early ram line\n")
        open(os.path.join(self.run, "ivibridge.log"), "w").write("early daemon line\n")
        idle = os.path.join(self.jobs, "idle.gcode"); open(idle, "w").write("G90\nM82\n")
        live = os.path.join(self.jobs, "live.gcode"); open(live, "w").write("G1 X1\n")
        open(os.path.join(self.run, "current_job"), "w").write(live)
        # fake a healthy daemon so health reset fires after 1s
        open(os.path.join(self.run, "ivibridge.pid"), "w").write(str(os.getpid()))
        open(os.path.join(self.run, "watchdog.pid"), "w").write(str(os.getpid()))
        os.remove(self.link); os.symlink("/dev/null", self.link)
        open(os.path.join(self.home, "bootfail"), "w").write("1\n")
        env = dict(self.base_env, IVIB_SELF=RAM, IVIB_P1_WAIT="5", IVIB_MIGRATE_ROUNDS="1", IVIB_HEALTH_WAIT="1")
        t0 = time.time()
        rc, out = self.sh(RAM, "persist", env=env, timeout=15)
        self.assertLess(time.time() - t0, 12)
        self.assertEqual(rc, 0, out)
        self.assertTrue(os.path.exists(os.path.join(self.run, "p1.ready")))
        self.assertEqual(open(os.path.join(self.run, "p1.ready")).read().strip(), self.p1)
        self.assertTrue(os.path.isdir(os.path.join(self.p1, "ivibridge_logs")))
        self.assertFalse(os.path.isdir(os.path.join(self.p1, "ivibridge_jobs")))
        self.assertIn("early boot line", open(os.path.join(self.p1, "ivibridge_logs", "boot.log")).read())
        self.assertIn("early ram line", open(os.path.join(self.p1, "ivibridge_logs", "ram.log")).read())
        self.assertIn("early daemon line", open(os.path.join(self.p1, "ivibridge_logs", "ivibridge.log")).read())
        self.assertTrue(os.path.exists(os.path.join(self.p1, "idle.gcode")))
        self.assertFalse(os.path.exists(idle))
        # live job must stay in RAM until it ends
        self.assertTrue(os.path.exists(live))
        self.assertFalse(os.path.exists(os.path.join(self.p1, "live.gcode")))
        # health reset
        deadline = time.time() + 4
        while time.time() < deadline and open(os.path.join(self.home, "bootfail")).read().strip() != "0":
            time.sleep(0.1)
        self.assertEqual(open(os.path.join(self.home, "bootfail")).read().strip(), "0")
        if os.path.exists(self.mountlog):
            self.assertNotIn("P1_RW", open(self.mountlog).read())
            self.assertNotIn("mmcblk0p1", open(self.mountlog).read())

    def test_persist_late_p1_disable_stops(self):
        open(self.mnts, "w").write("rootfs / rootfs rw 0 0\n/dev/mmcblk0p1 %s vfat rw 0 0\n" % self.p1)
        open(os.path.join(self.p1, "ivibridge.disable"), "w").close()
        env = dict(self.base_env, IVIB_SELF=self.stub, IVIB_P1_WAIT="5", IVIB_MIGRATE_ROUNDS="0", IVIB_HEALTH_WAIT="1")
        # persist is in ram.sh; use the real script but stub stop via IVIB_SELF
        # The real persist calls `sh "$SELF" stop`. Point SELF at the stub.
        rc, out = self.sh(RAM, "persist", env=env, timeout=10)
        self.assertEqual(rc, 0, out)
        self.assertTrue(os.path.exists(self.calls) and "stop" in open(self.calls).read())
        self.assertFalse(os.path.exists(os.path.join(self.run, "p1.ready")))

if __name__ == "__main__":
    unittest.main(verbosity=2)
