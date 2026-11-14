"""install.sh / uninstall.sh under the printer's own busybox (qemu-arm) on a scratch root (IVIB_ROOT).
Hooks /etc/init.d/rcS (not autorun.sh). The existing ivissh line must be left untouched.
Checks: one tagged line added, sh -n, idempotent, uninstall matches rcS.before_bridge."""
import hashlib, os, shutil, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.environ.get("A33_ROOT", "/tmp/a33root"); BB = ROOT + "/bin/busybox"
STOCK = os.environ.get("STOCK_RCS", os.path.join(HERE, "stock_rcS"))
SSH_LINE = "/bin/sh /userapp/ivissh/boot.sh </dev/null >/dev/null 2>&1 &\n"
HOOK = "/bin/sh /userapp/ivibridge/boot.sh </dev/null >/dev/null 2>&1 &  # ivibridge-hook"

class Install(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="iviinst-"); bb = os.path.join(self.d, "bbin"); os.mkdir(bb)
        for a in subprocess.run(["qemu-arm", "-L", ROOT, BB, "--list"], capture_output=True, text=True).stdout.split():
            p = os.path.join(bb, a); open(p, "w").write('#!/bin/dash\nexec qemu-arm -L %s %s %s "$@"\n' % (ROOT, BB, a)); os.chmod(p, 0o755)
        self.r = os.path.join(self.d, "root"); os.makedirs(self.r + "/etc/init.d"); os.makedirs(self.r + "/userapp/script")
        self.a = self.r + "/etc/init.d/rcS"
        # stock image rcS plus the SSH-at-boot line already on the printer
        open(self.a, "w").write(open(STOCK).read().rstrip("\n") + "\n" + SSH_LINE)
        os.chmod(self.a, 0o755)
        self.orig = open(self.a, "rb").read()
        self.src = os.path.join(self.d, "pkg"); os.mkdir(self.src)
        for f in ("ivibridge-ram.sh", "boot.sh", "uninstall.sh", "install.sh"): shutil.copy(os.path.join(HERE, "..", "scripts", f), self.src)
        shutil.copy(os.path.join(HERE, "..", "bin", "ivibridge-armv7-static"), os.path.join(self.src, "ivibridge"))
        h = hashlib.sha256(open(os.path.join(self.src, "ivibridge"), "rb").read()).hexdigest()
        open(os.path.join(self.src, "SHA256SUMS"), "w").write("%s  ivibridge\n" % h)
        self.env = dict(PATH=bb + ":/usr/bin:/bin", IVIB_ROOT=self.r)
    def tearDown(self): shutil.rmtree(self.d, ignore_errors=True)
    def sh(self, script, *a):
        r = subprocess.run(["qemu-arm", "-L", ROOT, BB, "sh", script] + list(a), env=self.env, capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout + r.stderr

    def test_install_idempotent_uninstall_exact(self):
        rc, out = self.sh(os.path.join(self.src, "install.sh"), self.src); self.assertEqual(rc, 0, out)
        new = open(self.a, "rb").read()
        self.assertTrue(new.startswith(self.orig), "rcS prefix (including the ivissh line) must be preserved")
        added = new[len(self.orig):].decode()
        self.assertEqual(added.count("\n"), 1)
        self.assertIn("# ivibridge-hook", added)
        self.assertIn("/bin/sh /userapp/ivibridge/boot.sh </dev/null >/dev/null 2>&1 &", added)
        self.assertNotIn("$RTE", added)
        self.assertIn(SSH_LINE.encode(), new)
        h = self.r + "/userapp/ivibridge"
        self.assertEqual(sorted(os.listdir(h)), ["apikey", "boot.sh", "ivibridge", "ivibridge-ram.sh", "rcS.before_bridge", "uninstall.sh"])
        self.assertEqual(oct(os.stat(h + "/apikey").st_mode & 0o777), "0o600")
        self.assertEqual(open(h + "/rcS.before_bridge", "rb").read(), self.orig)
        # autorun.sh must not have been created or edited
        self.assertFalse(os.path.exists(self.r + "/userapp/script/autorun.sh"))
        rc, out = self.sh(os.path.join(self.src, "install.sh"), self.src); self.assertIn("already installed", out)
        self.assertEqual(open(self.a, "rb").read(), new)
        r = subprocess.run(["qemu-arm", "-L", ROOT, BB, "sh", "-n", self.a], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        rc, out = self.sh(h + "/uninstall.sh"); self.assertEqual(rc, 0, out)
        self.assertIn("matches backup", out)
        self.assertEqual(open(self.a, "rb").read(), self.orig)
        self.assertEqual(oct(os.stat(self.a).st_mode & 0o777), "0o755")
        self.assertIn(SSH_LINE.encode(), open(self.a, "rb").read())
        self.assertFalse(os.path.exists(h))

    def test_checksum_mismatch_refused(self):
        open(os.path.join(self.src, "SHA256SUMS"), "w").write("%s  ivibridge\n" % ("0" * 64))
        rc, out = self.sh(os.path.join(self.src, "install.sh"), self.src); self.assertNotEqual(rc, 0); self.assertIn("checksum", out)
        self.assertEqual(open(self.a, "rb").read(), self.orig)
        self.assertFalse(os.path.exists(self.r + "/userapp/ivibridge"))
        self.assertIn(SSH_LINE.encode(), open(self.a, "rb").read())

if __name__ == "__main__":
    unittest.main(verbosity=2)
