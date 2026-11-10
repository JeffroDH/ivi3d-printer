"""SSH transport (Mac -> A33) and the Device API built on it.

Safe invocation (from the sshd-readiness findings, ivi_a33_sshd_readiness.md):
  * ALWAYS pass a remote command. sshd then runs `/bin/sh -c '<cmd>'` (root's shell is BusyBox ash):
    a non-login, non-interactive shell, so /etc/profile (setup_module.sh, extra kore watchdogs,
    autorun.sh) is NOT run and $ENV is not read. There is no /etc/sshrc or ~/.ssh/rc on the image.
  * NEVER open a session without a command: that is a login shell (`-sh`) which runs /etc/profile; with
    -T (no pty) autorun.sh would bounce wlan0 and start a second IVI-Main-Controller.
  * -T (no pty) keeps stdout binary-clean for framebuffer grabs.
  * One multiplexed connection (ControlMaster=auto + ControlPersist) => one TCP/key exchange, then each
    step is one exec channel (tap + settle + grab are combined into a single command).
"""
import gzip, subprocess
from .fb import Frame


def _read(path):
    with open(path, "rb") as fh:
        return fh.read()

HELPER = "/tmp/ivitap2"

GRAB_SH = ("S=$(cat /sys/class/graphics/fb0/stride); P=$(cat /sys/class/graphics/fb0/pan); "
           "B=$(cat /sys/class/graphics/fb0/bits_per_pixel); V=$(cat /sys/class/graphics/fb0/virtual_size); "
           "echo \"FBINFO $S $P $B $V\"; dd if=/dev/fb0 bs=$S skip=${P#*,} count=480 2>/dev/null | gzip -1")


class TransportError(RuntimeError):
    pass


class SSHTransport:
    def __init__(self, host, key="~/.ssh/ivi_ecdsa", user="root", known_hosts="~/.ssh/ivi_known_hosts",
                 control_path="~/.ssh/ivi-cm-%C", persist=600, timeout=30, extra_opts=()):
        self.host, self.user, self.timeout = host, user, timeout
        self.base = ["ssh", "-i", key, "-T",
                     "-o", "BatchMode=yes", "-o", "UserKnownHostsFile=" + known_hosts, "-o", "StrictHostKeyChecking=accept-new",
                     "-o", "HostKeyAlgorithms=ecdsa-sha2-nistp256", "-o", "ConnectTimeout=8",
                     "-o", "ControlMaster=auto", "-o", "ControlPath=" + control_path,
                     "-o", "ControlPersist=%d" % persist, "-o", "ServerAliveInterval=15", *extra_opts]

    def run(self, cmd, stdin=None, timeout=None):
        if not cmd or not cmd.strip():
            raise TransportError("refusing an empty remote command (would start a login shell -> /etc/profile)")
        # sshd gives exec sessions a minimal env; pin PATH explicitly (BusyBox applets live in these dirs)
        argv = self.base + ["%s@%s" % (self.user, self.host), "--", "PATH=/bin:/sbin:/usr/bin:/usr/sbin; " + cmd]
        try:
            p = subprocess.run(argv, input=stdin, capture_output=True, timeout=timeout or self.timeout)
        except subprocess.TimeoutExpired:
            raise TransportError("ssh timed out: %s" % cmd[:60])
        if p.returncode == 255:
            raise TransportError("ssh failed: %s" % p.stderr.decode(errors="replace").strip()[:300])
        return p.returncode, p.stdout, p.stderr

    def close(self):
        subprocess.run(self.base + ["-O", "exit", "%s@%s" % (self.user, self.host)], capture_output=True)


def parse_grab(out):
    nl = out.index(b"\n")
    hdr = out[:nl].decode().split()
    if hdr[0] != "FBINFO":
        raise TransportError("bad grab header %r" % out[:60])
    stride, pan, bpp = int(hdr[1]), hdr[2], int(hdr[3])
    xoff, yoff = (int(v) for v in pan.split(","))
    if bpp != 32 or xoff != 0:
        raise TransportError("unsupported framebuffer: bpp=%d pan=%s (expected 32 bpp, xoffset 0)" % (bpp, pan))
    data = gzip.decompress(out[nl + 1:])
    return Frame(data, 800, 480, stride), {"stride": stride, "pan": pan, "bpp": bpp,
                                           "virtual_size": hdr[4] if len(hdr) > 4 else "?"}


class Device:
    """High-level A33 operations; every method is one SSH round trip."""

    def __init__(self, transport, dry_run=False, settle_ms=800, helper=HELPER):
        self.t, self.dry_run, self.settle_ms, self.helper = transport, dry_run, settle_ms, helper
        self.fbinfo = None

    def grab(self):
        rc, out, err = self.t.run(GRAB_SH)
        frame, self.fbinfo = parse_grab(out)
        return frame

    def tap(self, x, y, guard, settle_ms=None, drag_to=None):
        """Guarded tap (or slow drag) then settle and grab, all in ONE round trip.
        guard = (gx, gy, gw, gh, hash). Returns (status, frame) where status is 'OK', 'GUARD', 'DRY' or 'ERR:..'."""
        gx, gy, gw, gh, gh_hash = guard
        if self.dry_run:
            return "DRY", None
        opt = "-G %d,%d,%d,%d,%08x" % (gx, gy, gw, gh, gh_hash)
        if drag_to:
            opt += " -S %d,%d,%d" % drag_to
        cmd = "%s %s %d %d; echo \"TAPRC=$?\" >&2; usleep %d; %s" % (
            self.helper, opt, x, y, (settle_ms or self.settle_ms) * 1000, GRAB_SH)
        rc, out, err = self.t.run(cmd)
        tag = [l for l in err.decode(errors="replace").splitlines() if l.startswith("TAPRC=")]
        trc = int(tag[-1][6:]) if tag else -1
        frame, self.fbinfo = parse_grab(out)
        if trc == 0:
            return "OK", frame
        if trc == 4:
            return "GUARD", frame
        return "ERR:%d %s" % (trc, err.decode(errors="replace").strip()[-200:]), frame

    def list_wifi(self):
        """[(mtime, name)] for /userdata/WifiFile. Uses BusyBox `date -r FILE +%s` (present in the 1.18.3 help
        text [O]);
        falls back to `ls -1t` order (newest first) if date -r is unavailable."""
        cmd = ("cd /userdata/WifiFile 2>/dev/null || exit 3; for f in *; do [ -f \"$f\" ] && [ -r \"$f\" ] && "
               "printf 'T\\t%s\\t%s\\n' \"$(date -r \"$f\" +%s 2>/dev/null)\" \"$f\"; done; "
               "ls -1t 2>/dev/null | while read -r f; do printf 'L\\t%s\\n' \"$f\"; done; true")
        rc, out, err = self.t.run(cmd)
        if rc == 3:
            raise TransportError("/userdata/WifiFile not mounted")
        timed, order = [], []
        for line in out.decode("utf-8", "replace").splitlines():
            parts = line.split("\t")
            if parts[0] == "T" and len(parts) >= 3:
                timed.append((parts[1], "\t".join(parts[2:])))
            elif parts[0] == "L" and len(parts) >= 2:
                order.append("\t".join(parts[1:]))
        if timed and all(t.isdigit() for t, _ in timed):
            return [(int(t), n) for t, n in timed]
        names = {n for _, n in timed}
        return [(len(order) - i, n) for i, n in enumerate(order) if not names or n in names]

    def printing_probe(self):
        """One entry per open file descriptor of IVI-Main-Controller that points at a print file (any
        directory; extensions .g/.gcode/.nc/.cnc, case-insensitive). Duplicates are meaningful - see
        nav.classify_probe(): from the app disassembly (Offline check B) the app holds
          * 1 fd from the moment a file is selected (Work::startWorkFile opens Work+0x30 and never closes
            it; it is only closed by the next selection's QFile::setFileName or app exit), and
          * a 2nd fd on the same file while streaming (GlobalFuntions+0xa0, opened by cachegcodeFromFile,
            closed at EOF of the cache read, stopPrinting or PrintgcodefileFinish)."""
        cmd = ("P=$(pidof IVI-Main-Controller); [ -n \"$P\" ] || { echo NOAPP; exit 0; }; "
               "ls -l /proc/$P/fd 2>/dev/null | sed -n 's/.*-> //p' | "
               "grep -i -E '\\.(g|gcode|nc|cnc)$' ; true")
        rc, out, err = self.t.run(cmd)
        s = out.decode("utf-8", "replace").split("\n")
        if s and s[0] == "NOAPP":
            raise TransportError("IVI-Main-Controller is not running")
        return [l for l in s if l.strip()]

    def helper_status(self):
        rc, out, err = self.t.run("[ -x %s ] && md5sum %s || echo MISSING" % (self.helper, self.helper))
        return out.decode().split()[0] if out else "MISSING"

    def install_helper(self, local_path):
        data = _read(local_path)
        rc, out, err = self.t.run("cat > %s.new && chmod 755 %s.new && mv %s.new %s && md5sum %s" % (
            (self.helper,) * 5), stdin=data)
        return out.decode().split()[0] if out else None
