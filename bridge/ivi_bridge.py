#!/usr/bin/env python3
"""IVI3D bridge: lets Orca Slicer / Anycubic Slicer Next send jobs to the IVI3D printer.

Emulates a small subset of the OctoPrint REST API so a slicer's "Print host: OctoPrint"
can upload to it, and forwards jobs to the printer over:
  * Wi-Fi  (kore API :8080) - upload only; start the job on the touch screen
           (start_print etc. are 404 on firmware V1.3.2-alpha).
  * USB serial (115200)     - M2411 S2 starts a PC job, then G-code is streamed per 'ok'.

Commands:  serve | send FILE | postprocess FILE | watch DIR      (see --help)
License: CC BY-NC-SA 4.0 (same as the repo).
"""
import argparse, email.parser, fcntl, html, secrets, select, subprocess, termios, email.policy, glob, json, os, re, shutil, sys, threading, time
import urllib.error, urllib.parse, urllib.request, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = "0.1.0"
DEFAULT_CONFIG = {
    "mode": "auto",                     # uploads: "auto"/"wifi" = Wi-Fi upload (default); "serial" = USB streaming
    "serial_monitor": True,             # use the USB port (if free) for live status + temp/speed controls
    "monitor_interval_s": 3,            # M105/M2007 poll period of the monitor
    "notify": True,                     # macOS notifications via osascript
    "caffeinate": True,                 # keep the Mac awake during USB jobs
    "printer_host": "192.168.50.85",
    "printer_port": 8080,
    "printer_token": "",                # kore API token (keep out of git)
    "serial_port": "/dev/tty.usbmodem*",  # glob allowed
    "baud": 115200,
    "firmware_version": "",             # override; otherwise read from the serial banner
    "listen_host": "127.0.0.1",
    "listen_port": 5000,
    "api_key": "",                      # key the slicer must send as X-Api-Key ("" = no check)
    "spool_dir": "~/Library/Application Support/ivi-bridge/jobs",
    "retries": 3,
    "line_timeout_s": 600,
    "report_interval_s": 4,             # M2155 S<n>: printer pushes temps/position/status every n s
    "home_before_job": True,            # laser/CNC: G53, G28, ..., G54 before M2411 S2 (IVI 3licer behaviour)
    "laser_focus_z": None,              # machine Z (mm) to drop to before a laser job; required if homing
    "auto_clear_stale_job": True,       # on "Can't start work in current status: 5" send M2411 S3 and retry once              # max wait for 'ok' (long heats send 'busy' meanwhile)
}

def log(*a):
    print(time.strftime("%H:%M:%S"), *a, file=sys.stderr, flush=True)

def config_path(path=None):
    return path or os.environ.get("IVI_BRIDGE_CONFIG") or os.path.expanduser("~/.config/ivi-bridge/config.json")

def load_config(path=None):
    cfg = dict(DEFAULT_CONFIG)
    path = config_path(path)
    if path and os.path.exists(path):
        with open(path) as f:
            cfg.update(json.load(f))
    if os.environ.get("IVI_PRINTER_TOKEN"):
        cfg["printer_token"] = os.environ["IVI_PRINTER_TOKEN"]
    cfg["spool_dir"] = os.path.expanduser(cfg["spool_dir"])
    return cfg

def init_config(path=None, token="e0cf19a3-e0a4-4740-825f-bdffb49e58b8"):
    """Write a config with defaults if none exists (installer). Returns (path, cfg). The token
    default is the stock IVI 3licer token documented in docs/slicer_report.md."""
    path = config_path(path)
    if not os.path.exists(path):
        cfg = {k: DEFAULT_CONFIG[k] for k in ("mode", "printer_host", "printer_port", "serial_port",
                                             "baud", "listen_host", "listen_port", "notify", "caffeinate")}
        cfg.update(printer_token=token, api_key=secrets.token_hex(16))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f: json.dump(cfg, f, indent=2)
    return path, load_config(path)

def notify(cfg, msg, title="IVI Bridge"):
    log("notify:", msg)
    if cfg.get("notify") and sys.platform == "darwin":
        q = lambda t: t.replace("\\", "\\\\").replace('"', '\\"')
        try: subprocess.Popen(["osascript", "-e", f'display notification "{q(msg)}" with title "{q(title)}"'])
        except OSError: pass

def find_usb_port(pattern):
    if not any(c in pattern for c in "*?["):
        return pattern if os.path.exists(pattern) else None
    hits = sorted(glob.glob(pattern)); return hits[0] if hits else None

def resolve_mode(cfg):
    m = cfg.get("mode", "auto")
    if m == "auto":
        return "serial" if find_usb_port(cfg["serial_port"]) else "wifi"
    return m

def upload_mode(cfg):
    """Where an uploaded file goes. Only an explicit mode "serial" streams over USB; "auto" and "wifi"
    upload to the printer's storage over Wi-Fi (USB is then used for status/controls only)."""
    return "serial" if cfg.get("mode") == "serial" else "wifi"

# ---------------------------------------------------------------- Wi-Fi ----
def encode_multipart(fields, files):
    """fields: {name: str}; files: {name: (filename, bytes)} -> (body, content_type)"""
    b = uuid.uuid4().hex
    out = []
    for k, v in fields.items():
        out += [f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()]
    for k, (fn, data) in files.items():
        out += [f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{fn}\"\r\n"
                f"Content-Type: application/octet-stream\r\n\r\n".encode(), data, b"\r\n"]
    out.append(f"--{b}--\r\n".encode())
    return b"".join(out), f"multipart/form-data; boundary={b}"

class WifiPrinter:
    """Upload-only client for the kore HTTP API."""
    def __init__(self, host, port, token, retries=3, timeout=30, sleep=time.sleep):
        if not token:
            raise ValueError("printer_token is not set (config file or IVI_PRINTER_TOKEN)")
        self.base = f"http://{host}:{port}/api/v1"
        self.token, self.retries, self.timeout, self.sleep = token, retries, timeout, sleep

    def _post(self, ep, fields, files=None):
        if files:
            body, ctype = encode_multipart(fields, files)
        else:
            body, ctype = urllib.parse.urlencode(fields).encode(), "application/x-www-form-urlencoded"
        req = urllib.request.Request(f"{self.base}/{ep}", data=body, headers={"Content-Type": ctype})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.status, r.read().decode(errors="replace")

    def _retry(self, ep, fields, files=None):
        last = None
        for i in range(self.retries):
            try:
                return self._post(ep, fields, files)
            except urllib.error.HTTPError as e:   # printer answered: don't hammer it
                raise RuntimeError(f"{ep}: HTTP {e.code} {e.read().decode(errors='replace')[:200]}")
            except (urllib.error.URLError, OSError) as e:
                last = e; log(f"{ep} failed ({e}); retry {i + 1}/{self.retries}")
                self.sleep(2 * (i + 1))
        raise RuntimeError(f"{ep}: printer unreachable: {last}")

    def upload(self, path, name=None):
        name = name or os.path.basename(path)
        with open(path, "rb") as f:
            data = f.read()
        self._retry("connect", {"token": self.token})
        try:
            st, txt = self._retry("upload", {"token": self.token}, {"file": (name, data)})
            if st not in (200, 201):
                raise RuntimeError(f"upload: HTTP {st} {txt[:200]}")
            log(f"uploaded {name} ({len(data)} B): {txt.strip()[:100]}")
            return txt
        finally:
            try:
                self._post("disconnect", {"token": self.token})
            except Exception as e:
                log(f"disconnect failed (ignored): {e}")

# --------------------------------------------------------------- serial ----
def clean_gcode(text):
    """Strip comments/blank lines; returns list of commands."""
    out = []
    for line in text.splitlines():
        line = line.split(";", 1)[0].strip()
        if line:
            out.append(line)
    return out

def parse_version(s):
    m = re.search(r"V?(\d+)\.(\d+)\.(\d+)", s or "")
    return tuple(int(x) for x in m.groups()) if m else None

def needs_m1001(version):
    v = parse_version(version)
    return bool(v and v >= (2, 4, 0))

class TermiosSerial:
    """Minimal raw 8N1 serial port (no pyserial). Exclusive via flock + TIOCEXCL."""
    def __init__(self, port, baud=115200, timeout=1.0):
        self.fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if hasattr(termios, "TIOCEXCL"): fcntl.ioctl(self.fd, termios.TIOCEXCL)
            a = termios.tcgetattr(self.fd)
            speed = getattr(termios, f"B{baud}")
            a[0] = 0; a[1] = 0                                    # iflag, oflag raw
            a[2] = termios.CS8 | termios.CREAD | termios.CLOCAL   # 8N1, no flow control
            a[3] = 0; a[4] = a[5] = speed
            termios.tcsetattr(self.fd, termios.TCSANOW, a)
            termios.tcflush(self.fd, termios.TCIOFLUSH)
        except Exception:
            os.close(self.fd); raise
        self.timeout, self.buf = timeout, b""
    def write(self, data):
        view = memoryview(data)
        while view:
            select.select([], [self.fd], [], self.timeout)
            try: n = os.write(self.fd, view); view = view[n:]
            except BlockingIOError: pass
    def readline(self):
        end = time.monotonic() + self.timeout
        while b"\n" not in self.buf:
            left = end - time.monotonic()
            if left <= 0: break
            r, _, _ = select.select([self.fd], [], [], left)
            if r:
                try: chunk = os.read(self.fd, 4096)
                except BlockingIOError: continue
                if not chunk: raise OSError("serial port closed (USB unplugged?)")
                self.buf += chunk
        if b"\n" in self.buf:
            line, self.buf = self.buf.split(b"\n", 1); return line + b"\n"
        return b""
    def close(self):
        if self.fd is not None: os.close(self.fd); self.fd = None

def open_serial(cfg):
    port = find_usb_port(cfg["serial_port"])
    if not port:
        raise RuntimeError(f"no serial port matches {cfg['serial_port']} (is USB-C plugged in?)")
    try:
        return TermiosSerial(port, cfg["baud"])
    except Exception as e:
        raise RuntimeError(f"cannot open {port}: {e}. Disconnect IVI 3licer (only one program may own the port).")

TEMP_RE = re.compile(r"\b([TB]\d?):\s*(-?[\d.]+)\s*/\s*(-?[\d.]+)")
def parse_status(line, status):
    """Update status dict from unsolicited reports like ' T:215.0 /215.0 B:50.1 /50.0' or
    'Working Status: IDLE'. Returns True if the line was a status report."""
    hit = False
    for k, cur, tgt in TEMP_RE.findall(line):
        name = {"T": "tool0", "B": "bed"}.get(k, "tool" + k[1:] if k[0] == "T" else k)
        status.setdefault("temps", {})[name] = {"actual": float(cur), "target": float(tgt)}; hit = True
    m = re.search(r"(?:job|work|sys)?\s*status\s*[:=]\s*(\d+)\b", line, re.I)
    if m: status["systat"] = int(m.group(1)); hit = True
    m = re.search(r"(?:progress|percent)\s*[:=]\s*([\d.]+)", line, re.I)
    if m: status["progress"] = float(m.group(1)); hit = True
    m = re.search(r"Working Status:\s*(\S+)", line, re.I)
    if m: status["working"] = m.group(1); hit = True
    return hit

# Job state enum of the motion firmware (byte +0x1e of the job object, firmware V1.3.2-alpha).
# Names 0-8 come from IVI 3licer's server (SYSTAT_*); 9/10 from the firmware stop path.
SYSTAT = {0: "INIT", 1: "IDLE", 2: "WORK", 3: "PAUSE_TRIG", 4: "PAUSE_STOPPED", 5: "PAUSE_FINISH (paused)",
          6: "RESUME_TRIG", 7: "RESUME_MOVING", 8: "RESUME_WAITING", 9: "STOPPING", 10: "STOPPING (from pause)"}

def header_type(text):
    m = re.search(r"^;header_type:\s*(\w+)", text[:4000], re.M)
    return m.group(1).lower() if m else "3dp"

def z_before_xy(lines):
    for c in lines:
        u = c.upper()
        if re.match(r"G[01]\b", u):
            if " Z" in u or u.startswith(("G0Z", "G1Z")): return True
            if " X" in u or " Y" in u: return False
    return False

class PrinterHalted(RuntimeError): pass

class SerialJob:
    """Streams one job. States: Starting -> Printing <-> Paused -> Operational | Cancelled | Error."""
    def __init__(self, ser, lines, name="job", firmware_version="", line_timeout=600, clock=time.monotonic,
                 prelude=(), report_interval=4, auto_clear=True, notify=None):
        self.ser, self.lines, self.name = ser, lines, name
        self.fw = firmware_version
        self.line_timeout, self.clock = line_timeout, clock
        self.prelude, self.report_interval, self.auto_clear = list(prelude), report_interval, auto_clear
        self.notify = notify or (lambda m: None)
        self.sent = 0; self.state = "Starting"; self.error = None; self.reason = None
        self.started = None; self.status = {}
        self._pause = threading.Event(); self._cancel = threading.Event()
        self._flags = set()

    def _write(self, cmd):
        self.ser.write((cmd + "\n").encode())

    def _readline(self):
        line = self.ser.readline().decode(errors="replace").strip()
        if line:
            parse_status(line, self.status)
            self._event(line)
        return line

    def _event(self, line):
        """Asynchronous printer messages (decoded from firmware + IVI 3licer's parser)."""
        low = line.lower()
        if "kill() called" in low or "printer halted" in low:
            raise PrinterHalted(f"printer halted (kill) - power-cycle or reset it before the next job ({line})")
        if "locked rotor" in low:
            m = re.search(r"Drive(\w+)", line)
            self.reason = (f"Drive {m.group(1) if m else '?'} locked rotor (motor stalled). On a delta this usually "
                           "means the head was asked to move sideways at the very top after homing - lower Z first.")
            if self.state == "Printing":
                self._pause.set(); self._write("M2410")   # what IVI 3licer does (shouldPause)
                self.state = "Paused"
            self.notify(f"{self.name}: {self.reason}")
        m = re.match(r"(PC|SC)\s+trigger pause\b", line)
        if m and self.state == "Printing":
            self._pause.set(); self.state = "Paused"
            self.reason = self.reason or ("paused from the touch screen" if m.group(1) == "SC" else "paused")
            self.notify(f"{self.name}: {self.reason}")
        if "trigger resume: ok" in low and self.state == "Paused":
            self._pause.clear(); self.state = "Printing"; self.reason = None
        for key in ("trigger stop: ok", "finish stop", "trigger work: ok", "pc start work"):
            if key in low: self._flags.add(key)
        m = re.search(r"Can't start work in current status:\s*(\d+)", line)
        if m: self._flags.add(("cant_start", int(m.group(1))))
        if "start work failed" in low: self._flags.add("start_failed")

    def _wait(self, predicate, timeout):
        end = self.clock() + timeout
        while self.clock() < end:
            if self._cancel.is_set() and self.state not in ("Starting", "Stopping"):
                return False
            line = self._readline()
            if not line:
                continue
            if low_err(line):
                raise RuntimeError(f"printer error: {line}")
            if predicate(line):
                return True
            if "busy" in line:          # 'echo:busy: processing' during heating/homing
                end = self.clock() + timeout
        raise TimeoutError("timed out waiting for printer")

    def _drain(self, seconds):
        end = self.clock() + seconds
        while self.clock() < end:
            self._readline()

    def handshake(self):
        """Same queries IVI 3licer sends on connect: M2005 (versions), M2007 (position/origin/Working Status),
        M105, M2155 S<n> (auto status report every n s, max 60)."""
        for c in ("M2005", "M2007", "M105", f"M2155 S{int(self.report_interval)}"):
            self._write(c)
        end = self.clock() + 2
        while self.clock() < end and "working" not in self.status:
            line = self._readline()
            if not self.fw and "firmware" in line.lower() and parse_version(line):
                self.fw = line
        self._drain(0.2)
        ws = self.status.get("working", "")
        if ws == "WORKING_SCREEN":
            raise RuntimeError("the printer is running a touch-screen job; finish or stop it there first")
        if ws == "WORKING_PC":      # stale PC job: IVI 3licer sends M2411 S3 on connect
            self._stop_stale()

    def _stop_stale(self):
        self._flags.discard("trigger stop: ok"); self._flags.discard("finish stop")
        self._write("M2411 S3")
        try: self._wait(lambda l: "trigger stop: ok" in l.lower() or "finish stop" in l.lower(), 10)
        except TimeoutError: pass
        self._drain(1)

    def detect_firmware(self, wait=3):     # kept for callers; handshake() normally sets self.fw
        return self.fw

    def _start(self):
        for attempt in (1, 2):
            self._flags = {f for f in self._flags if not (isinstance(f, tuple) or f in ("start_failed",))}
            if needs_m1001(self.fw):
                self._write("M1001 L")
            self._write("M2411 S2")
            end = self.clock() + 30
            while self.clock() < end:
                self._readline()
                if "trigger work: ok" in self._flags or "pc start work" in self._flags:
                    return
                bad = [f for f in self._flags if isinstance(f, tuple)]
                if bad or "start_failed" in self._flags:
                    st = bad[0][1] if bad else None
                    if st == 5 and self.auto_clear and attempt == 1:
                        log("printer still holds a paused job (status 5); sending M2411 S3 to clear it")
                        self._stop_stale(); break
                    raise RuntimeError(f"printer refused to start (status {st}: {SYSTAT.get(st, '?')}). "
                                       "A previous job is still paused/active - press Clear on the status page "
                                       "or stop it on the touch screen.")
            else:
                raise TimeoutError("printer did not acknowledge M2411 S2")

    def run(self):
        try:
            self.handshake()
            for c in self.prelude:           # laser/CNC: G53, G28, [G0 Z focus], G54 (IVI 3licer behaviour)
                self._write(c)
                self._wait(lambda l: l == "ok" or l.startswith("ok "), self.line_timeout)
            self._start()
            self.state, self.started = "Printing", self.clock()
            log(f"job {self.name}: started, {len(self.lines)} lines")
            for cmd in self.lines:
                while self._pause.is_set() and not self._cancel.is_set():
                    self._readline()          # keep watching for resume / kill while paused
                if self._cancel.is_set():
                    break
                self._write(cmd)
                if self._wait(lambda l: l == "ok" or l.startswith("ok "), self.line_timeout) is False:
                    break
                self.sent += 1
            if self._cancel.is_set():
                self._stop_printer(); self.state = "Cancelled"
            else:
                self.state = "Operational"
            log(f"job {self.name}: {self.state} ({self.sent}/{len(self.lines)})")
        except Exception as e:
            self.error, self.state = str(e), "Error"
            log(f"job {self.name}: ERROR {e}")

    def _stop_printer(self):
        # M2411 S3 = "trigger stop" in the firmware job state machine (also what IVI 3licer's Stop sends)
        self.state = "Stopping"
        self._write("M2411 S3")
        try: self._wait(lambda l: "trigger stop: ok" in l.lower() or "finish stop" in l.lower()
                        or "can't trigger stop" in l.lower(), 10)
        except (TimeoutError, RuntimeError): pass
        for c in ("M5", "M104 S0", "M140 S0", "M107"):
            self._write(c)

    def pause(self):
        if self.state == "Printing":
            self._pause.set(); self._write("M2410"); self.state = "Paused"; self.reason = "paused from the bridge"

    def resume(self):
        if self.state == "Paused":
            self._write("M2411 S1"); self._pause.clear(); self.state = "Printing"; self.reason = None

    def cancel(self):
        self._cancel.set(); self._pause.clear()

    @property
    def progress(self):
        return 100.0 * self.sent / len(self.lines) if self.lines else 0.0

def low_err(line):
    return line.lower().startswith(("error", "!!"))

def job_prelude(cfg, kind, lines):
    """Start moves IVI 3licer sends for laser/CNC (auto-home + workspace). Raises if a laser job would start
    with a sideways move at the homed (top) height, which stalls a delta tower ('locked rotor')."""
    if kind not in ("laser", "cnc"):
        return []
    pre = ["G53"]
    if cfg.get("home_before_job", True):
        pre.append("G28")
    fz = cfg.get("laser_focus_z")
    if kind == "laser" and fz not in (None, ""):
        pre.append(f"G0 Z{float(fz):.2f} F1500")      # machine Z, like IVI 3licer's focus-height move
    elif kind == "laser" and cfg.get("home_before_job", True) and not z_before_xy(lines):
        raise RuntimeError("laser job has no Z move and the printer would start at the top after homing, which "
                           "stalls the delta ('locked rotor'). Set laser_focus_z (machine Z in mm) in the config.")
    pre.append("G54")
    return pre

# ---------------------------------------------------------- monitor -------
# Commands the bridge lets the UI / Orca send over USB. M104/M140/M220/M221 are standard Marlin and
# NOT yet verified on firmware V1.3.2-alpha.
ALLOWED_CMD = re.compile(r"^(M104 S\d{1,3}|M140 S\d{1,3}|M220 S\d{1,3}|M221 S\d{1,3}|M105|M2007|M2410|M2411 S[13]|M106( S\d{1,3})?|M107)$")
LIMITS = {"M104": 300, "M140": 120, "M220": 300, "M221": 200}

def check_command(cmd):
    c = " ".join(cmd.strip().upper().split())
    if not ALLOWED_CMD.match(c):
        raise ValueError(f"command not allowed: {cmd!r}")
    code, _, arg = c.partition(" S")
    if code in LIMITS and int(arg) > LIMITS[code]:
        raise ValueError(f"{code} S{arg} exceeds limit {LIMITS[code]}")
    if code in ("M220", "M221") and int(arg) < 10:
        raise ValueError(f"{code} S{arg} below 10%")
    return c

class SerialMonitor:
    """Owns the USB port while no USB job is streaming: polls M105 + M2007 and asks for M2155 auto
    reports, so /api/printer and /api/job show live status. Absent/busy port (e.g. IVI 3licer) -> retries
    quietly; status shows why."""
    def __init__(self, cfg, serial_factory, clock=time.monotonic, sleep=time.sleep):
        self.cfg, self.factory, self.clock, self.sleep = cfg, serial_factory, clock, sleep
        self.ser = None; self.status = {}; self.error = None; self.updated = None
        self.lock = threading.Lock(); self._stop = threading.Event(); self._paused = threading.Event()
        self.thread = None; self.last_cmd = None

    @property
    def connected(self): return self.ser is not None

    def start(self):
        self.thread = threading.Thread(target=self._loop, daemon=True); self.thread.start()

    def stop(self):
        self._stop.set(); self.release()

    def release(self):
        """Give the port up (a USB job is about to start)."""
        self._paused.set()
        with self.lock:
            if self.ser:
                try: self.ser.close()
                except Exception: pass
            self.ser = None

    def resume(self): self._paused.clear()

    def _open(self):
        try:
            ser = self.factory()
        except Exception as e:
            self.error = str(e); return False
        with self.lock:
            self.ser, self.error = ser, None
            for c in ("M2005", f"M2155 S{int(self.cfg.get('report_interval_s', 4))}", "M105", "M2007"):
                ser.write((c + "\n").encode())
        log("monitor: USB port open (status/controls)")
        return True

    def poll_once(self):
        """One cycle: open if needed, send M105/M2007, read what arrived. Returns True if connected."""
        if self._paused.is_set(): return False
        if not self.ser and not self._open(): return False
        try:
            with self.lock:
                self.ser.write(b"M105\n"); self.ser.write(b"M2007\n")
                end = self.clock() + 0.5
                while self.clock() < end:
                    line = self.ser.readline().decode(errors="replace").strip()
                    if not line: continue
                    if parse_status(line, self.status): self.updated = time.time()
        except Exception as e:
            self.error = f"USB lost: {e}"; log("monitor:", self.error)
            with self.lock:
                try: self.ser.close()
                except Exception: pass
                self.ser = None
            return False
        return True

    def _loop(self):
        while not self._stop.is_set():
            try: self.poll_once()
            except Exception as e: self.error = str(e)
            self._stop.wait(self.cfg.get("monitor_interval_s", 3))

    def send(self, cmd):
        c = check_command(cmd)
        with self.lock:
            if not self.ser: raise RuntimeError(f"USB not connected: {self.error or 'no port'}")
            self.ser.write((c + "\n").encode()); self.last_cmd = c
        log("monitor: sent", c); return c

# ------------------------------------------------- OctoPrint emulation ----
class Bridge:
    def __init__(self, cfg, wifi_factory=None, serial_factory=None, awake_factory=None):
        self.cfg = cfg
        self.awake_factory = awake_factory or self._caffeinate
        self.wifi_factory = wifi_factory or (lambda: WifiPrinter(cfg["printer_host"], cfg["printer_port"],
                                                                 cfg["printer_token"], cfg["retries"]))
        self.serial_factory = serial_factory or (lambda: open_serial(cfg))
        self.job = None; self.thread = None; self.last_file = None
        self.lock = threading.Lock()
        self.monitor = SerialMonitor(cfg, self.serial_factory) if cfg.get("serial_monitor", True) else None

    def send_command(self, cmd):
        """Temp/speed/flow etc. over USB: through the streaming job if one runs, else the monitor."""
        c = check_command(cmd)
        if self.busy() and isinstance(self.job, SerialJob):
            self.job._write(c); return c
        if not self.monitor: raise RuntimeError("serial_monitor is off")
        return self.monitor.send(c)

    def live_status(self):
        if self.busy(): return self.job.status
        return self.monitor.status if self.monitor and self.monitor.connected else {}

    def _caffeinate(self):
        if self.cfg.get("caffeinate") and sys.platform == "darwin":
            try: return subprocess.Popen(["caffeinate", "-i", "-w", str(os.getpid())])
            except OSError: pass
        return None

    def busy(self):
        return self.job is not None and self.job.state in ("Starting", "Printing", "Paused", "Stopping")

    def clear_printer(self):
        """Clear a stale/paused PC job on the printer (M2411 S3), e.g. after 'Can't start work in current status: 5'."""
        with self.lock:
            if self.busy(): raise RuntimeError("a job is running; use Cancel")
            if self.monitor: self.monitor.release()
            ser = self.serial_factory()
            try:
                j = SerialJob(ser, [], "clear", report_interval=self.cfg.get("report_interval_s", 4))
                j.handshake()
                if "trigger stop: ok" not in j._flags and "finish stop" not in j._flags: j._stop_stale()
                j.status.pop("working", None); j._write("M2007"); j._drain(1)
                return f"sent M2411 S3; printer reports {j.status.get('working', 'unknown')}"
            finally:
                ser.close()
                if self.monitor: self.monitor.resume()

    def submit(self, path, name, start=True, mode=None):
        mode = mode or upload_mode(self.cfg)
        self.last_file = name
        if mode == "wifi":
            try: self.wifi_factory().upload(path, name)
            except Exception as e:
                notify(self.cfg, f"Wi-Fi upload of {name} failed: {e}"); raise
            m = f"Uploaded {name} to the printer over Wi-Fi. Start it on the touch screen."
            notify(self.cfg, m); return m
        if not start:
            return f"Stored {name} in the spool folder (serial mode; print=false)."
        with self.lock:
            if self.busy():
                raise RuntimeError("a job is already running")
            with open(path, errors="replace") as f:
                raw = f.read()
            lines, kind = clean_gcode(raw), header_type(raw)
            try: pre = job_prelude(self.cfg, kind, lines)
            except Exception as e:
                notify(self.cfg, f"Not starting {name}: {e}"); raise
            if self.monitor: self.monitor.release()
            try: ser = self.serial_factory()
            except Exception as e:
                if self.monitor: self.monitor.resume()
                notify(self.cfg, f"USB print of {name} failed: {e}"); raise
            self.job = SerialJob(ser, lines, name, self.cfg.get("firmware_version", ""),
                                 self.cfg.get("line_timeout_s", 600), prelude=pre,
                                 report_interval=self.cfg.get("report_interval_s", 4),
                                 auto_clear=self.cfg.get("auto_clear_stale_job", True),
                                 notify=lambda m: notify(self.cfg, m))
            awake = self.awake_factory()
            def runner(job=self.job):
                try:
                    job.run()
                finally:
                    try: ser.close()
                    except Exception: pass
                    if self.monitor: self.monitor.resume()
                    if awake:
                        try: awake.terminate()
                        except Exception: pass
                    msg = {"Operational": f"Finished {job.name}", "Cancelled": f"Cancelled {job.name}"}.get(
                        job.state, f"Print {job.name} stopped: {job.error}")
                    notify(self.cfg, msg)
            self.thread = threading.Thread(target=runner, daemon=True); self.thread.start()
        notify(self.cfg, f"Printing {name} over USB")
        return f"Printing {name} over USB serial."

    def job_info(self):
        j = self.job
        if not self.busy() and self.monitor and self.monitor.connected:
            st = self.monitor.status; code = st.get("systat"); ws = st.get("working", "")
            if code is not None or ws:
                state = {2: "Printing", 3: "Pausing", 4: "Paused", 5: "Paused", 9: "Cancelling", 10: "Cancelling"}.get(
                    code, "Printing" if ws.startswith("WORKING") else "Operational")
                return {"job": {"file": {"name": self.last_file, "origin": "local"}},
                        "progress": {"completion": st.get("progress"), "printTime": None, "printTimeLeft": None,
                                     "filepos": None},
                        "state": state, "ivi": {"systat": code, "systat_name": SYSTAT.get(code), "working": ws,
                                                "source": "usb monitor"}}
        state = j.state if j else "Operational"
        if j and j.error: state = f"Error: {j.error}"
        elif j and j.reason and j.state == "Paused": state = f"Paused: {j.reason}"
        elapsed = (time.monotonic() - j.started) if j and j.started else None
        return {"job": {"file": {"name": j.name if j else self.last_file, "origin": "local"}},
                "progress": {"completion": j.progress if j else None, "printTime": elapsed,
                             "printTimeLeft": None, "filepos": j.sent if j else None},
                "state": state}

PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>IVI Bridge</title>
<style>body{font:15px -apple-system,sans-serif;max-width:1400px;margin:1.5em auto;padding:0 1em}button{font-size:15px;margin:.2em .4em .2em 0}
.bar{height:14px;background:#ddd;border-radius:7px}.bar>div{height:100%;background:#3a7;border-radius:7px;width:0}
.tabs{display:flex;gap:.3em;margin:1em 0 0}.tabs button{border:1px solid #bbb;background:#f4f4f4;border-radius:6px 6px 0 0;padding:.4em 1.2em;margin:0}
.tabs button.on{background:#fff;border-bottom-color:#fff;font-weight:600}
.panels{display:block}.panel{border:1px solid #bbb;border-radius:0 8px 8px 8px;padding:1em;display:none}.panel.on{display:block}
.panel h3{margin-top:0}input[type=number]{width:5em;font-size:15px}.row{margin:.6em 0}.note{color:#777;font-size:13px}
@media (min-width:1100px){.tabs{display:none}.panels{display:grid;grid-template-columns:1fr 1fr;gap:1em;margin-top:1em}.panel{display:block;border-radius:8px}}</style>
<h2>IVI Bridge</h2><p>Uploads: <b>__MODE__</b> &nbsp; USB: <b id=usb>…</b></p><p>State: <b id=st>…</b> &nbsp; File: <span id=fn></span></p>
<div class=bar><div id=pb></div></div><p id=pc></p><p id=tp></p>
<div class=tabs><button id=t_tool class=on onclick="tab('tool')">Toolhead</button><button id=t_fil onclick="tab('fil')">Filament</button></div>
<div class=panels>
<div class="panel on" id=p_tool><h3>Toolhead</h3>
<div class=row>Nozzle <input id=nz type=number min=0 max=300 value=215> °C <button onclick="g('M104 S'+nz.value)">Set</button></div>
<div class=row>Bed <input id=bd type=number min=0 max=120 value=60> °C <button onclick="g('M140 S'+bd.value)">Set</button></div>
<div class=row><button onclick="g('M104 S0');g('M140 S0')">Cooldown</button></div>
<div class=row>Speed <input id=sp type=number min=10 max=300 value=100> % <button onclick="g('M220 S'+sp.value)">Set</button></div>
<div class=row><button onclick="cmd('pause','pause')">Pause</button><button onclick="cmd('pause','resume')">Resume</button>
<button onclick="if(confirm('Cancel print?'))cmd('cancel')">Cancel</button>
<button title="Sends M2411 S3 to clear a stuck/paused PC job (e.g. 'current status: 5')" onclick="if(confirm('Clear a stuck job on the printer (M2411 S3)?'))fetch('/api/ivi/clear',{method:'POST',headers:H}).then(r=>r.json()).then(j=>alert(j.message||j.error))">Clear stuck job</button></div></div>
<div class=panel id=p_fil><h3>Filament</h3>
<div class=row>Flow <input id=fl type=number min=10 max=200 value=100> % <button onclick="g('M221 S'+fl.value)">Set</button></div>
<div class=row>Preheat <button onclick="g('M104 S210');g('M140 S60')">PLA 210/60</button><button onclick="g('M104 S240');g('M140 S80')">PETG 240/80</button><button onclick="g('M104 S250');g('M140 S100')">ABS 250/100</button></div>
<div class=row><button onclick="g('M104 S0')">Nozzle off</button></div>
<p class=note>Manual filament swap: the slicer pauses with M2410; swap, then Resume (M2411 S1).</p></div>
</div><p class=note id=msg>Controls use USB (M104/M140/M220/M221; not yet verified on this firmware).</p>
<script>const K=__KEY__,H={'X-Api-Key':K,'Content-Type':'application/json'};
function tab(t){for(const n of['tool','fil']){document.getElementById('t_'+n).classList.toggle('on',n==t);document.getElementById('p_'+n).classList.toggle('on',n==t)}}
async function g(c){const r=await fetch('/api/printer/command',{method:'POST',headers:H,body:JSON.stringify({command:c})});msg.textContent=r.ok?'Sent '+c:'Failed: '+((await r.json()).error||r.status)}
async function cmd(c,a){await fetch('/api/job',{method:'POST',headers:H,body:JSON.stringify({command:c,action:a})});tick()}
async function tick(){try{const j=await (await fetch('/api/job',{headers:H})).json(),p=await (await fetch('/api/printer',{headers:H})).json();
usb.textContent=p.ivi&&p.ivi.usb?'connected':'not connected'+(p.ivi&&p.ivi.usb_error?' ('+p.ivi.usb_error+')':'');
st.textContent=j.state;fn.textContent=j.job.file.name||'';const c=j.progress.completion;pb.style.width=(c||0)+'%';
pc.textContent=c==null?'':c.toFixed(1)+'%';tp.textContent=Object.entries(p.temperature||{}).map(([k,v])=>k+': '+v.actual+' / '+v.target+' °C').join('   ')}catch(e){st.textContent='bridge offline'}}
tick();setInterval(tick,2000)</script>"""

def status_page(cfg):
    m = "USB streaming" if upload_mode(cfg) == "serial" else "Wi-Fi (start on the touch screen)"
    return PAGE.replace("__MODE__", html.escape(m)).replace(
        "__KEY__", json.dumps(cfg.get("api_key", "")).replace("<", "\\u003c"))

def octo_printer_cmds(path, cmd):
    """OctoPrint printer endpoints -> G-code list (validated later by check_command)."""
    c = cmd.get("command")
    if path == "/api/printer/command":
        lst = cmd.get("commands") or ([c] if c else [])
        if not lst: raise ValueError("no command")
        return [str(x) for x in lst]
    if path == "/api/printer/tool":
        if c == "target":
            return [f"M104 S{int(round(float(v)))}" for v in (cmd.get("targets") or {}).values()]
        if c == "flowrate": return [f"M221 S{int(cmd['factor'])}"]
    if path == "/api/printer/bed" and c == "target":
        return [f"M140 S{int(round(float(cmd['target'])))}"]
    if path == "/api/printer/printhead" and c == "feedrate":
        return [f"M220 S{int(cmd['factor'])}"]
    raise ValueError(f"unsupported {path} command {c}")

def make_handler(bridge):
    cfg = bridge.cfg
    class H(BaseHTTPRequestHandler):
        server_version = "ivi-bridge/" + VERSION
        def log_message(self, fmt, *a): log("http", fmt % a)
        def _json(self, code, obj):
            b = json.dumps(obj).encode()
            self.send_response(code); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        def _auth(self):
            key = cfg.get("api_key")
            # Orca's Device-tab webview sends X-Api-Key twice -> merged as "key, key"
            sent = [k.strip() for k in (self.headers.get("X-Api-Key") or "").split(",")]
            if key and key not in sent and \
               self.headers.get("Authorization", "") != f"Bearer {key}":
                self._json(403, {"error": "Invalid API key"}); return False
            return True
        def do_GET(self):
            p = self.path.split("?")[0]
            if p not in ("/", "/index.html") and not self._auth(): return
            if p == "/api/version":
                return self._json(200, {"api": "0.1", "server": "1.9.0", "text": f"OctoPrint (ivi-bridge {VERSION})"})
            if p == "/api/server":
                return self._json(200, {"version": "1.9.0", "safemode": None})
            if p == "/api/job":
                return self._json(200, bridge.job_info())
            if p == "/api/printer":
                st = bridge.job_info()["state"]; mon = bridge.monitor
                temps = bridge.live_status().get("temps", {}) or (bridge.job.status.get("temps", {}) if bridge.job else {})
                return self._json(200, {"state": {"text": st, "flags": {"operational": True,
                                   "printing": st == "Printing", "paused": st.startswith("Paused"),
                                   "ready": not bridge.busy()}},
                                   "temperature": temps,
                                   "ivi": {"usb": bool(bridge.busy() or (mon and mon.connected)),
                                           "usb_error": mon.error if mon else "serial_monitor off"}})
            if p == "/" or p == "/index.html":
                b = status_page(cfg).encode()
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(b))); self.end_headers(); return self.wfile.write(b)
            if p.startswith("/api/files"):
                return self._json(200, {"files": [], "free": 0})
            self._json(404, {"error": "not found"})
        def do_POST(self):
            if not self._auth(): return
            p = self.path.split("?")[0]
            n = int(self.headers.get("Content-Length", 0)); body = self.rfile.read(n)
            if p in ("/api/files/local", "/api/files/sdcard"):
                return self._upload(body)
            if p == "/api/ivi/clear":
                try: return self._json(200, {"message": bridge.clear_printer()})
                except Exception as e: return self._json(409, {"error": str(e)})
            if p.startswith("/api/printer/"):
                try: cmd = json.loads(body or b"{}")
                except ValueError: return self._json(400, {"error": "bad json"})
                try: gcodes = octo_printer_cmds(p, cmd)
                except ValueError as e: return self._json(400, {"error": str(e)})
                try:
                    for g in gcodes: bridge.send_command(g)
                except ValueError as e: return self._json(400, {"error": str(e)})
                except Exception as e: return self._json(409, {"error": str(e)})
                self.send_response(204); self.end_headers(); return
            if p == "/api/job":
                try: cmd = json.loads(body or b"{}")
                except ValueError: return self._json(400, {"error": "bad json"})
                j = bridge.job
                if (not j or not bridge.busy()) and bridge.monitor and bridge.monitor.connected:
                    # Wi-Fi-uploaded job started on the touch screen: control it over USB
                    c, a = cmd.get("command"), cmd.get("action", "toggle")
                    paused = bridge.monitor.status.get("systat") in (3, 4, 5)
                    g = {"pause": {"pause": "M2410", "resume": "M2411 S1"}.get(a, "M2411 S1" if paused else "M2410"),
                         "cancel": "M2411 S3"}.get(c)
                    if not g: return self._json(400, {"error": f"unsupported command {c}"})
                    try: bridge.send_command(g)
                    except Exception as e: return self._json(409, {"error": str(e)})
                    return self._json(200, {"state": bridge.job_info()["state"], "sent": g})
                if not j or not bridge.busy(): return self._json(409, {"error": "no active job"})
                c, a = cmd.get("command"), cmd.get("action", "toggle")
                if c == "pause":
                    if a == "pause" or (a == "toggle" and j.state == "Printing"): j.pause()
                    else: j.resume()
                elif c == "cancel": j.cancel()
                else: return self._json(400, {"error": f"unsupported command {c}"})
                return self._json(200, {"state": j.state})
            self._json(404, {"error": "not found"})
        def _upload(self, body):
            msg = email.parser.BytesParser(policy=email.policy.HTTP).parsebytes(
                b"Content-Type: " + self.headers.get("Content-Type", "").encode() + b"\r\n\r\n" + body)
            fname, data, fields = None, None, {}
            for part in msg.iter_parts():
                name = part.get_param("name", header="content-disposition")
                if part.get_filename():
                    fname, data = os.path.basename(part.get_filename()), part.get_payload(decode=True)
                elif name:
                    fields[name] = part.get_content().strip()
            if not fname:
                return self._json(400, {"error": "no file"})
            os.makedirs(cfg["spool_dir"], exist_ok=True)
            path = os.path.join(cfg["spool_dir"], fname)
            with open(path, "wb") as f: f.write(data)
            start = fields.get("print", "false").lower() == "true"
            try:
                msg_txt = bridge.submit(path, fname, start=start)
            except Exception as e:
                log("submit failed:", e)
                return self._json(409 if "already" in str(e) else 500, {"error": str(e)})
            log(msg_txt)
            self._json(201, {"done": True, "files": {"local": {"name": fname, "origin": "local"}},
                             "effectivePrint": start, "message": msg_txt})
    return H

def serve(cfg, bridge=None, start_monitor=True):
    bridge = bridge or Bridge(cfg)
    srv = ThreadingHTTPServer((cfg["listen_host"], cfg["listen_port"]), make_handler(bridge))
    log(f"ivi-bridge {VERSION} on http://{cfg['listen_host']}:{cfg['listen_port']} uploads={upload_mode(cfg)}")
    if bridge.monitor:
        log("USB monitor on: status/controls use the USB port when it is free (IVI 3licer must be disconnected)")
        if start_monitor: bridge.monitor.start()
    return srv

# ----------------------------------------------------------------- CLI -----
def post_to_bridge(cfg, path, name, start=True):
    body, ctype = encode_multipart({"print": "true" if start else "false"}, {"file": (name, open(path, "rb").read())})
    req = urllib.request.Request(f"http://127.0.0.1:{cfg['listen_port']}/api/files/local", data=body,
                                 headers={"Content-Type": ctype, "X-Api-Key": cfg.get("api_key", "")})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read()).get("message", "ok")

def send_file(cfg, path, name=None):
    """Prefer a running bridge service (needed for serial: the stream outlives this process);
    otherwise upload directly over Wi-Fi."""
    name = name or os.path.basename(path)
    try:
        return post_to_bridge(cfg, path, name)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"bridge refused: HTTP {e.code} {e.read()[:200]!r}")
    except (urllib.error.URLError, OSError):
        if upload_mode(cfg) != "wifi":
            raise RuntimeError("bridge service not running; serial mode needs `ivi_bridge.py serve`")
        return Bridge(cfg).submit(path, name)

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config"); ap.add_argument("--mode", choices=["auto", "wifi", "serial"])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("serve", help="run the OctoPrint-compatible service")
    s = sub.add_parser("send", help="send a G-code file now"); s.add_argument("file")
    pp = sub.add_parser("postprocess", help="slicer post-processing hook (file path is last arg)")
    pp.add_argument("file")
    sub.add_parser("init-config", help="create the config with defaults if missing; print Orca settings as JSON")
    w = sub.add_parser("watch", help="send every new .gcode file that appears in DIR (for Anycubic Next exports)")
    w.add_argument("dir"); w.add_argument("--interval", type=float, default=3)
    a = ap.parse_args(argv)
    if a.cmd == "init-config":
        path, cfg = init_config(a.config)
        print(json.dumps({"config": path, "host": f"127.0.0.1:{cfg['listen_port']}", "api_key": cfg["api_key"],
                          "usb_port": find_usb_port(cfg["serial_port"])}))
        return 0
    cfg = load_config(a.config)
    if a.mode: cfg["mode"] = a.mode
    if a.cmd == "serve":
        serve(cfg).serve_forever()
    elif a.cmd == "send":
        print(send_file(cfg, a.file))
    elif a.cmd == "postprocess":
        # Orca/Next run this on Export/Send with a temp file path; we don't modify the file.
        # If the slicer is already uploading to the bridge (OctoPrint host), do nothing to avoid a double send.
        host = os.environ.get("SLIC3R_PP_HOST", "")
        if host.lower().startswith("octoprint"):
            return 0
        out = os.environ.get("SLIC3R_PP_OUTPUT_NAME") or a.file
        tmp = os.path.join(cfg["spool_dir"], os.path.basename(out)); os.makedirs(cfg["spool_dir"], exist_ok=True)
        shutil.copyfile(a.file, tmp)
        print(send_file(cfg, tmp))
    elif a.cmd == "watch":
        seen = set(glob.glob(os.path.join(a.dir, "*.gcode")))
        log(f"watching {a.dir}")
        while True:
            time.sleep(a.interval)
            for f in sorted(set(glob.glob(os.path.join(a.dir, "*.gcode"))) - seen):
                s1 = os.path.getsize(f); time.sleep(1)
                if os.path.getsize(f) != s1: continue   # still being written; next pass
                seen.add(f)
                try: log(send_file(cfg, f))
                except Exception as e: log(f"send {f} failed: {e}")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as e:
        log("error:", e); sys.exit(1)
