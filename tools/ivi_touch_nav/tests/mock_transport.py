"""Mock SSH transport: interprets exactly the remote commands ivi_touch sends and drives the Sim."""
import gzip, hashlib, os, re, shlex
from ivi_touch import transport as T
from ivi_touch.fb import Frame


def _read(path):
    with open(path, "rb") as fh:
        return fh.read()

HELPER_LOCAL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "device", "ivitap2_armel")


class MockTransport:
    def __init__(self, sim, helper_installed=True, on_grab=None):
        self.sim = sim
        self.cmds = []
        self.helper_installed = helper_installed
        self.on_grab = on_grab          # hook(sim, n) called after grab n is captured (UI changes later)
        self.grabs = 0

    def _grab_bytes(self):
        f = self.sim.render()
        if self.on_grab:                 # runs AFTER the frame is captured: simulates a repaint right after
            self.on_grab(self.sim, self.grabs)
        self.grabs += 1
        return b"FBINFO 3200 0,0 32 800,960\n" + gzip.compress(f.data, 1)

    def run(self, cmd, stdin=None, timeout=None):
        assert cmd and cmd.strip(), "empty remote command would start a login shell"
        self.cmds.append(cmd)
        if cmd == T.GRAB_SH:
            return 0, self._grab_bytes(), b""
        if cmd.startswith(T.HELPER + " "):
            head, rest = cmd.split("; echo \"TAPRC=$?\" >&2; ", 1)
            usleep, grab = rest.split("; ", 1)
            assert grab == T.GRAB_SH and usleep.startswith("usleep ")
            argv = shlex.split(head)[1:]
            guard = drag = None
            pos = []
            i = 0
            while i < len(argv):
                if argv[i] == "-G":
                    guard = argv[i + 1]; i += 2
                elif argv[i] == "-S":
                    drag = argv[i + 1]; i += 2
                else:
                    pos.append(int(argv[i])); i += 1
            x, y = pos
            assert 0 <= x < 800 and 0 <= y < 480
            rc = 0
            if guard is None:
                rc = 2
            else:
                gx, gy, gw, gh, gh_hash = guard.split(",")
                cur = Frame(self.sim.render().data).region_hash(int(gx), int(gy), int(gw), int(gh))
                if "%08x" % cur != gh_hash:
                    rc = 4
            if rc == 0:
                if drag:
                    x2, y2, ms = (int(v) for v in drag.split(","))
                    self.sim.drag(x, y, y2)
                else:
                    self.sim.tap(x, y)
            err = (b"GUARD_MISMATCH\n" if rc == 4 else b"") + b"TAPRC=%d\n" % rc
            return 0, self._grab_bytes(), err
        if cmd.startswith("cd /userdata/WifiFile"):
            out = "".join("T\t%d\t%s\n" % (t, n) for n, (t, _) in self.sim.files.items())
            out += "".join("L\t%s\n" % n for n, _ in sorted(self.sim.files.items(), key=lambda kv: -kv[1][0]))
            return 0, out.encode(), b""
        if cmd.startswith("P=$(pidof IVI-Main-Controller)"):
            return 0, ("\n".join(self.sim.open_files()) + "\n").encode(), b""
        if cmd.startswith("[ -x " + T.HELPER):
            if not self.helper_installed:
                return 0, b"MISSING\n", b""
            return 0, (hashlib.md5(_read(HELPER_LOCAL)).hexdigest() + "  /tmp/ivitap2\n").encode(), b""
        m = re.match(r"touch /userdata/WifiFile/'(.*)'$", cmd)
        if m:
            name = m.group(1).replace("'\\''", "'")
            t, ivi = self.sim.files[name]
            self.sim.files[name] = (max(v[0] for v in self.sim.files.values()) + 1, ivi)
            return 0, b"", b""
        raise AssertionError("unexpected remote command: %r" % cmd)
