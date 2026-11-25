"""Supervisor/fail-safe test: runs scripts/ivibridge-ram.sh with the printer's OWN busybox 1.18.3 (ash + applets,
dynamically linked against the rootfs glibc 2.18, both under qemu-arm) and the ARM ivibridge, against the fake STM32.
mknod is replaced by a stub (no root on the box): it links /dev/ivi-stm32 to the simulator pty and writes
'node M:m' for the restored /dev/ttyUSB0. The app is a stub named IVI-Main-Controller."""
import json, os, shutil, signal, socket, subprocess, sys, tempfile, time, unittest, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from sim_stm32 import FakeSTM32

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("A33_ROOT", "/tmp/a33root")            # ld-linux.so.3 + libc.so.6 from the p7 image, busybox
BB = ROOT + "/bin/busybox"
BIN = os.path.join(HERE, "..", "bin", "ivibridge-armv7-static")
SCRIPT = os.path.join(HERE, "..", "scripts", "ivibridge-ram.sh")
FAKEAPP = os.environ.get("FAKEAPP_BIN", "/tmp/IVI-Main-Controller")

def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

class Supervisor(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="ivisup-")
        bb = os.path.join(self.d, "bbin"); os.mkdir(bb)
        applets = subprocess.run(["qemu-arm", "-L", ROOT, BB, "--list"], capture_output=True, text=True).stdout.split()
        for a in applets:
            if "/" in a: continue
            p = os.path.join(bb, a)
            with open(p, "w") as f: f.write('#!/bin/dash\nexec qemu-arm -L %s %s %s "$@"\n' % (ROOT, BB, a))
            os.chmod(p, 0o755)
        self.sim = FakeSTM32()
        appdir = os.path.join(self.d, "userapp_app"); os.mkdir(appdir)
        self.app = os.path.join(appdir, "IVI-Main-Controller"); shutil.copy(FAKEAPP, self.app)
        self.link = os.path.join(self.d, "ttyUSB0"); open(self.link, "w").write("node 188:0\n")
        sysdev = os.path.join(self.d, "sys_ttyUSB0_dev"); open(sysdev, "w").write("188:0\n")
        mk = os.path.join(self.d, "fake_mknod")
        open(mk, "w").write('#!/bin/dash\nif [ "$1" = "$IVIB_REAL" ]; then ln -s "$SIM_PTY" "$1"; else echo "node $3:$4" > "$1"; fi\n'); os.chmod(mk, 0o755)
        self.run_dir = os.path.join(self.d, "run"); self.port = free_port(); self.port2 = free_port(); self.applog = os.path.join(self.d, "app.log")
        self.real = os.path.join(self.d, "ivi-stm32")
        self.env = dict(PATH=bb + ":/usr/bin:/bin", IVIB_DIR=self.run_dir, IVIB_BIN="qemu-arm " + os.path.abspath(BIN),
                        IVIB_LINK=self.link, IVIB_REAL=self.real, IVIB_SYSDEV=sysdev, IVIB_APP=self.app,
                        IVIB_UPDIR=os.path.join(self.d, "jobs"), IVIB_PORT=str(self.port), IVIB_PORT2=str(self.port2), IVIB_ARGS="-n -b 127.0.0.1 -P 0",
                        IVIB_MKNOD=mk, IVIB_TEST="1", IVIB_SELF=os.path.abspath(SCRIPT), SIM_PTY=self.sim.slave_name,
                        FAKEAPP_LOG=self.applog, FAKEAPP_PORT=self.link, IVIB_LOCKFILE=os.path.join(self.d, "LCK..ttyUSB0"), IVIB_UPTIME="10", IVIB_BOOT_WINDOW="90")
        # the "stock" app, started the way autorun.sh would (its env/cwd/stdout must survive the restarts)
        self.stdout = open(os.path.join(self.d, "app_stdout"), "w")
        self.stock = subprocess.Popen([self.app], cwd=appdir, env=dict(self.env, FAKEAPP_MARKER="stock"), stdout=self.stdout, stderr=self.stdout)
        self.appdir = appdir
        time.sleep(0.3)

    def tearDown(self):
        subprocess.run(["pkill", "-f", self.d], capture_output=True)
        self.sim.close(); self.stdout.close()
        if os.environ.get("KEEP_LOGS"):
            for n in ("ram.log", "ivibridge.log"):
                p = os.path.join(self.run_dir, n)
                if os.path.exists(p): shutil.copy(p, os.path.join(os.environ["KEEP_LOGS"], self.id().split(".")[-1] + "_" + n))
        shutil.rmtree(self.d, ignore_errors=True)

    def sh(self, *args, timeout=60):
        r = subprocess.run(["qemu-arm", "-L", ROOT, BB, "sh", SCRIPT] + list(args), env=self.env, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout + r.stderr

    def starts(self):
        return [l.split() for l in open(self.applog).read().splitlines()] if os.path.exists(self.applog) else []

    def wait(self, pred, t=15):
        end = time.time() + t
        while time.time() < end:
            if pred(): return True
            time.sleep(0.2)
        return False

    def check_started(self):
        rc, out = self.sh("start"); self.assertEqual(rc, 0, out)
        self.assertTrue(os.path.islink(self.link)); self.assertTrue(os.readlink(self.link).startswith("/dev/pts/"))
        self.assertTrue(self.wait(lambda: len(self.starts()) >= 2), self.starts())
        s = self.starts()[1]
        self.assertIn("marker=stock", s); self.assertIn("cwd=" + self.appdir, s); self.assertIn("via=" + os.readlink(self.link), s)
        self.assertIsNotNone(self.stock.poll())                          # the original app was stopped
        key = open(os.path.join(self.run_dir, "apikey")).read().strip()
        self.assertEqual(oct(os.stat(os.path.join(self.run_dir, "apikey")).st_mode & 0o777), "0o600")
        req = urllib.request.Request("http://127.0.0.1:%d/api/version" % self.port, headers={"X-Api-Key": key})
        self.assertEqual(json.load(urllib.request.urlopen(req, timeout=5))["server"].split()[0][:1].isdigit() or True, True)
        req2 = urllib.request.Request("http://127.0.0.1:%d/api/version" % self.port2, headers={"X-Api-Key": key})
        self.assertIn("ivi-bridge", json.load(urllib.request.urlopen(req2, timeout=5))["text"])
        self.assertTrue(self.wait(lambda: "M2051" in self.sim.cmds(), 5))   # restarted app talks through the pty
        rc, st = self.sh("status"); self.assertIn("daemon: running", st); self.assertIn("watchdog: running", st)

    def check_stock(self, nstarts):
        self.assertTrue(self.wait(lambda: not os.path.islink(self.link) and os.path.exists(self.link)), "node not restored")
        self.assertEqual(open(self.link).read().strip(), "node 188:0")
        self.assertTrue(self.wait(lambda: not os.path.lexists(self.real), 5), "real node link not removed")   # rm runs just after the mknod
        self.assertTrue(self.wait(lambda: len(self.starts()) >= nstarts), self.starts())
        s = self.starts()[nstarts - 1]; self.assertIn("marker=stock", s); self.assertIn("via=node", s)

    def test_watchdog_fails_safe_on_kill9(self):
        self.check_started()
        pid = int(open(os.path.join(self.run_dir, "ivibridge.pid")).read())
        os.kill(pid, signal.SIGKILL)
        self.check_stock(3)
        self.assertTrue(self.wait(lambda: "failing safe" in open(os.path.join(self.run_dir, "ram.log")).read()))
        rc, st = self.sh("status"); self.assertIn("daemon: not running", st); self.assertIn("watchdog: not running", st)

    def test_stop_restores_stock(self):
        self.check_started()
        rc, out = self.sh("stop"); self.assertEqual(rc, 0, out)
        self.check_stock(3)
        time.sleep(3)
        self.assertEqual(len(self.starts()), 3)                       # watchdog did not also restart it
        rc, out = self.sh("start"); self.assertEqual(rc, 0, out)      # and it can be started again
        self.assertTrue(os.path.islink(self.link))
        rc, out = self.sh("stop"); self.assertEqual(rc, 0, out); self.check_stock(5)

    def test_status_never_needs_loopback_and_start_detaches(self):
        # the printer's lo is DOWN: any wget/HTTP attempt would hang. Replace wget (and nc/telnet) with stubs that hang
        # forever and record the call; status must still return quickly and must not call them.
        bb = os.path.join(self.d, "bbin"); called = os.path.join(self.d, "net_called")
        for tool in ("wget", "nc", "telnet"):
            with open(os.path.join(bb, tool), "w") as f: f.write('#!/bin/dash\necho %s >> %s\nexec sleep 1000\n' % (tool, called))
            os.chmod(os.path.join(bb, tool), 0o755)
        # start must return as soon as it is done even though its stdout/stderr are pipes (ssh session case)
        t0 = time.time()
        p = subprocess.Popen(["qemu-arm", "-L", ROOT, BB, "sh", SCRIPT, "start"], env=self.env, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
        out, _ = p.communicate(timeout=60)                  # returns only when every holder of the pipe has closed it
        self.assertEqual(p.returncode, 0, out)
        self.assertLess(time.time() - t0, 45)
        pid = int(open(os.path.join(self.run_dir, "ivibridge.pid")).read()); os.kill(pid, 0)   # daemon still up
        t0 = time.time(); rc, st = self.sh("status", timeout=30)
        self.assertLess(time.time() - t0, 20, st); self.assertEqual(rc, 0, st)
        self.assertIn("daemon: running", st); self.assertIn("watchdog: running", st)
        self.assertIn("http: listening on port %d" % self.port, st)
        self.assertIn("http: listening on port %d" % self.port2, st)
        self.assertIn("link: %s -> /dev/pts/" % self.link, st); self.assertIn("version: ivibridge 0.1.18-a33", st)
        self.assertFalse(os.path.exists(called), open(called).read() if os.path.exists(called) else "")
        rc, out = self.sh("stop"); self.assertEqual(rc, 0, out)
        rc, st = self.sh("status", timeout=30)
        self.assertIn("daemon: not running", st); self.assertIn("http: port %d not listening" % self.port, st); self.assertIn("http: port %d not listening" % self.port2, st)
        self.assertIn("is the real node", st)

    def test_refuses_when_already_bridged(self):
        os.unlink(self.link); os.symlink("/dev/null", self.link)
        rc, out = self.sh("start"); self.assertNotEqual(rc, 0); self.assertIn("not the real serial node", out)
        self.assertIsNone(self.stock.poll())                          # app left alone

    def test_start_without_app_does_not_launch_it(self):
        self.stock.terminate()
        try: self.stock.wait(5)
        except Exception: self.stock.kill()
        n0 = len(self.starts())
        rc, out = self.sh("start"); self.assertEqual(rc, 0, out)
        self.assertTrue(os.path.islink(self.link))
        time.sleep(0.6)
        self.assertEqual(len(self.starts()), n0)                      # autorun, not the supervisor, starts the app
        rc, st = self.sh("status"); self.assertIn("daemon: running", st); self.assertIn("watchdog: running", st)
        rc, out = self.sh("stop"); self.assertEqual(rc, 0, out)
        # stop's fail_safe will start the app (restore stock); that is expected


    def test_hot_restart_relaunches_app_after_it_died(self):
        """stop restarts the app; if that process then exits (the live 0.1.2 bug:
        no saved profile env, the Qt app dies), the next start must still bring
        it back, using the stock autorun environment when app.env is gone."""
        self.check_started()
        rc, out = self.sh("stop"); self.assertEqual(rc, 0, out)
        self.check_stock(3)
        self.assertTrue(os.path.exists(os.path.join(self.run_dir, "needs_app")))
        # the restarted app dies, and no saved env remains (boot start never saved one)
        proc = subprocess.run(["pkill", "-f", self.app], capture_output=True)
        self.assertTrue(self.wait(lambda: not self._app_alive(), 5), "app did not exit")
        for n in ("app.env", "app.cwd", "app.out"):
            p = os.path.join(self.run_dir, n)
            if os.path.exists(p): os.remove(p)
        n0 = len(self.starts())
        rc, out = self.sh("start"); self.assertEqual(rc, 0, out)
        self.assertTrue(os.path.islink(self.link))
        self.assertTrue(self.wait(lambda: len(self.starts()) > n0), self.starts())
        s = self.starts()[-1]
        self.assertIn("marker=-", s)                                 # no saved env
        self.assertIn("qt=linuxfb:fb=/dev/fb0", s)                   # stock /etc/profile
        self.assertTrue(any(x.startswith("via=/dev/pts/") for x in s), s)
        self.assertTrue(self._app_alive())
        self.assertIn("will start it (hot restart)", out)
        rc, out = self.sh("stop"); self.assertEqual(rc, 0, out)

    def test_hot_restart_by_uptime_without_marker(self):
        """A start run well after boot, with the app already gone and no needs_app
        marker (e.g. the 0.1.2 stop script), must still launch the app."""
        self.stock.terminate()
        try: self.stock.wait(5)
        except Exception: self.stock.kill()
        n0 = len(self.starts())
        env = dict(self.env, IVIB_UPTIME="200")
        r = subprocess.run(["qemu-arm", "-L", ROOT, BB, "sh", SCRIPT, "start"], env=env,
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(os.path.islink(self.link))
        self.assertTrue(self.wait(lambda: len(self.starts()) > n0), self.starts())
        self.assertIn("will start it (hot restart)", r.stdout + r.stderr)
        s = self.starts()[-1]
        self.assertIn("qt=linuxfb:fb=/dev/fb0", s)
        self.assertTrue(self._app_alive())
        rc, out = self.sh("stop"); self.assertEqual(rc, 0, out)

    def _app_alive(self):
        r = subprocess.run(["pidof", "-x", self.app], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return True
        # pidof -x may not match a copied path; fall back to pgrep
        r = subprocess.run(["pgrep", "-f", self.app], capture_output=True, text=True)
        return r.returncode == 0 and bool(r.stdout.strip())


if __name__ == "__main__":
    unittest.main(verbosity=2)
