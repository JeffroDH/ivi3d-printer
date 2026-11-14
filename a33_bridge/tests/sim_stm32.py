"""Fake IVI3D motion controller (STM32, Marlin V1.3.2-alpha + IVI job words) on a pty.

Default reply strings are the ones confirmed on hardware (V1.3.2-alpha):
  M2411 S2 -> 'SC start work', 'trigger work: ok'      M2410    -> 'SC trigger pause', 'trigger pause: ok', 'Finish pause'
  M2411 S1 -> 'SC trigger resume', 'trigger resume: ok', then later 'Resume complete'
  M2411 S3 -> 'SC trigger stop', 'trigger stop: ok', 'Finish stop'
  M2411 S4 -> 'SC trigger finish', 'trigger finish: ok', 'Finish stop'
plus the M2007 block, M2155 auto reports, Marlin N/checksum + Resend.
Options:
  plain_ok_nook  also send a plain 'ok' after every job word (the hardware does after pause/resume)
  legacy         the older modelled strings (no 'Finish pause' / 'Resume complete' / 'Finish stop'), for compat tests
  strict_resume  hardware behaviour: numbered lines that arrive between M2411 S1 and 'Resume complete' are silently
                 dropped (no ok); resume_delay sets the gap. drop_keeps_n: the dropped line's N still counts as received
  noise          'CMD buffer: N' after every reply and periodic 'Homed: YES' pushes; M2007/M114 answer plain 'ok'
  drop_lines     {N,...}: swallow that numbered line once (no reply);  slow_lines {N: s}: delay its ok (planner full)
  head           reply to M2051 (e.g. 'info:Head 3DP,0.3mm')
"""
import os, pty, re, threading, time, tty

class FakeSTM32:
    def __init__(self, plain_ok_nook=False, ok_delay=0.002, bad_checksum_at=None, legacy=False, strict_resume=False,
                 resume_delay=0.1, drop_keeps_n=False, noise=False, drop_lines=None, slow_lines=None, head="info:Head 3DP,0.4mm"):
        self.master, self.slave = pty.openpty()
        tty.setraw(self.slave)
        self.slave_name = os.ttyname(self.slave)
        self.plain_ok_nook = plain_ok_nook; self.ok_delay = ok_delay
        self.bad_at = set(bad_checksum_at or ())
        self.legacy = legacy; self.strict_resume = strict_resume; self.resume_delay = resume_delay
        self.drop_keeps_n = drop_keeps_n; self.noise = noise; self.head = head
        self.drop_lines = set(drop_lines or ()); self.slow_lines = dict(slow_lines or {})
        self.resuming = False; self.resume_complete_t = None
        self.executed = []          # N of every numbered line actually executed
        self.dropped = []           # (t, N) lines swallowed without reply
        self.timers = []
        self.received = []          # (t, raw line)
        self.emitted = []           # every line written
        self.violations = []
        self.lock = threading.Lock()
        self.ws = "IDLE"; self.systat = 1; self.t = 21.0; self.tt = 0.0; self.b = 22.0; self.bt = 0.0
        self.report_s = 0; self.next_report = 0; self.last_n = 0
        self.stop = False
        threading.Thread(target=self._rx, daemon=True).start()
        threading.Thread(target=self._reports, daemon=True).start()

    def out(self, *lines):
        with self.lock:
            for l in lines:
                self.emitted.append(l)
                os.write(self.master, (l + "\r\n").encode())

    def cmds(self):
        return [r for _, r in self.received]

    def _reports(self):
        last_homed = 0
        while not self.stop:
            time.sleep(0.05)
            if self.noise and time.time() - last_homed > 0.5:
                last_homed = time.time(); self.out("Homed: YES")
            if self.report_s and time.time() >= self.next_report:
                self.next_report = time.time() + self.report_s
                self.out(" T:%.1f /%.1f B:%.1f /%.1f @:0 B@:0" % (self.t, self.tt, self.b, self.bt),
                         "X:0.00 Y:0.00 Z:237.51 E:0.00 Count A:0 B:0 C:0",
                         "Working Status: " + self.ws, "job status: %d" % self.systat)

    def _rx(self):
        buf = b""
        while not self.stop:
            try: d = os.read(self.master, 4096)
            except OSError: return
            buf += d
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                raw = line.decode(errors="replace").strip()
                if raw:
                    self.received.append((time.time(), raw)); self._handle(raw)

    def _handle(self, raw):
        m = re.match(r"^N(\d+) (.*)\*(\d+)$", raw)
        cmd = raw
        if m:
            n, body = int(m.group(1)), m.group(2)
            cs = 0
            for ch in ("N%d %s" % (n, body)).encode(): cs ^= ch
            if n in self.bad_at:
                self.bad_at.discard(n); cs = -1
            if cs != int(m.group(3)) or (body.strip().upper() != "M110 N0" and n != self.last_n + 1):
                self.out("Error:checksum mismatch, Last Line: %d" % self.last_n, "Resend: %d" % (self.last_n + 1), "ok"); self._noise(); return
            if self.resuming and self.strict_resume:
                self.dropped.append((time.time(), n))
                if self.drop_keeps_n: self.last_n = n
                return
            if n in self.drop_lines:
                self.drop_lines.discard(n); self.dropped.append((time.time(), n))
                if self.drop_keeps_n: self.last_n = n
                return
            self.last_n = n; cmd = body
            self.executed.append(n)
            if n in self.slow_lines: time.sleep(self.slow_lines.pop(n))
        c = " ".join(cmd.upper().split())
        mm = re.match(r"^M0?[34]\b.*\bS([\d.]+)", c)
        if mm and float(mm.group(1)) > 100: self.violations.append(c)
        time.sleep(self.ok_delay)
        nook_ok = ["ok"] if self.plain_ok_nook else []
        L = self.legacy
        if c.startswith("M110"): self.last_n = 0; self.out("ok")
        elif c == "M105": self.out("ok T:%.1f /%.1f B:%.1f /%.1f @:0 B@:0" % (self.t, self.tt, self.b, self.bt))
        elif c in ("M2007", "M114") and self.noise: self.out("ok")
        elif c == "M114": self.out("X:1.00 Y:2.00 Z:3.00 E:0.00 Count A:0 B:0 C:0", "ok")
        elif c == "M2007": self.out("X:0.00 Y:0.00 Z:237.51 E:0.00 Count A:0 B:0 C:0", "Working Status: " + self.ws, "job status: %d" % self.systat, "ok")
        elif c.startswith("M2155 S"): self.report_s = int(c[7:]); self.next_report = time.time() + self.report_s; self.out("ok")
        elif c == "M2051": self.out(self.head, "ok")
        elif re.match(r"^G0?4\b", c):
            ms = 0.0
            mp = re.search(r"\bP([\d.]+)", c); ms += float(mp.group(1)) if mp else 0
            ms_ = re.search(r"\bS([\d.]+)", c); ms += float(ms_.group(1)) * 1000 if ms_ else 0
            self.later(ms / 1000.0, "ok")      # dwell runs in the background so job words still get through
        elif c == "M2001 S1":
            if self.systat in (2, 5): self.systat = 1; self.ws = "IDLE"
            self.out("ok")
        elif c == "M2411 S2":
            if self.systat == 1: self.systat = 2; self.ws = "WORKING_SCREEN"; self.out("SC start work", "trigger work: ok", *nook_ok)
            else: self.out("Can't start work in current status: %d" % self.systat, "start work failed, err= 200", *nook_ok)
        elif c == "M2410":
            if self.systat == 2: self.systat = 5
            if L: self.out("SC trigger pause", "trigger pause: ok", *nook_ok)
            else: self.out("SC trigger pause", "trigger pause: ok", "Finish pause", *nook_ok)
        elif c == "M2411 S1":
            if self.systat == 5: self.systat = 2
            self.out("SC trigger resume", "trigger resume: ok", *nook_ok)
            if not L:
                self.resuming = True
                if self.noise: self.out("CMD buffer: 6")
                def done():
                    self.resuming = False; self.resume_complete_t = time.time(); self.out("Resume complete")
                self.later(self.resume_delay, done)
                return
        elif c == "M2411 S3":
            self.systat = 1; self.ws = "IDLE"
            if L: self.out("SC trigger stop", "trigger stop: ok", "ok")
            else: self.out("SC trigger stop", "trigger stop: ok", "Finish stop", *nook_ok)
        elif c == "M2411 S4":
            self.systat = 1; self.ws = "IDLE"
            if L: self.out("trigger finish: ok", "ok")
            else: self.out("SC trigger finish", "trigger finish: ok", "Finish stop", *nook_ok)
        elif c.startswith("M104 S"): self.tt = float(c[6:]); self.out("ok")
        elif c.startswith("M140 S"): self.bt = float(c[6:]); self.out("ok")
        elif c.startswith("M109") or c.startswith("G28"):
            self.out("echo:busy: processing"); time.sleep(0.3); self.out("echo:busy: processing", "ok")
        else: self.out("ok")
        self._noise()

    def _noise(self):
        if self.noise: self.out("CMD buffer: 6")

    def later(self, sec, what):
        def fire():
            if self.stop: return
            try:
                if callable(what): what()
                else: self.out(what)
            except OSError: pass
        t = threading.Timer(sec, fire); t.daemon = True; self.timers.append(t); t.start()

    def close(self):
        self.stop = True
        for t in self.timers: t.cancel()
        for fd in (self.master, self.slave):
            try: os.close(fd)
            except OSError: pass


class FakeApp:
    """Stands in for IVI-Main-Controller: opens the link path, sends one line, waits for its 'ok'."""
    def __init__(self, path):
        self.fd = os.open(path, os.O_RDWR | os.O_NOCTTY)
        tty.setraw(self.fd)
        self.lines = []; self.oks = 0; self.stop = False; self.cv = threading.Condition()
        threading.Thread(target=self._rx, daemon=True).start()

    def _rx(self):
        buf = b""
        while not self.stop:
            try: d = os.read(self.fd, 4096)
            except OSError: return
            if not d: return
            buf += d
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                l = line.decode(errors="replace").strip()
                with self.cv:
                    self.lines.append(l)
                    if l == "ok" or l.startswith("ok "): self.oks += 1
                    self.cv.notify_all()

    def send(self, cmd, wait=True, timeout=5.0):
        with self.cv: before = self.oks
        os.write(self.fd, (cmd + "\n").encode())
        if not wait: return True
        end = time.time() + timeout
        with self.cv:
            while self.oks <= before:
                left = end - time.time()
                if left <= 0: return False
                self.cv.wait(left)
        return True

    def wait_line(self, pred, timeout=5.0):
        end = time.time() + timeout
        with self.cv:
            while not any(pred(l) for l in self.lines):
                left = end - time.time()
                if left <= 0: return False
                self.cv.wait(left)
        return True

    def close(self):
        self.stop = True
        try: os.close(self.fd)
        except OSError: pass
