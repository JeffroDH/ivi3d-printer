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
import argparse, bisect, email.parser, fcntl, html, secrets, select, subprocess, termios, email.policy, glob, json, os, re, shutil, sys, threading, time
import urllib.error, urllib.parse, urllib.request, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = "0.1.0"
DEFAULT_CONFIG = {
    "mode": "auto",                     # "auto" (default): Upload = Wi-Fi to printer storage, Upload and Print = USB stream;
                                        # "wifi": both go over Wi-Fi; "serial": both stream over USB
    "serial_monitor": True,             # use the USB port (if free) for live status + temp/speed controls
    "monitor_interval_s": 3,            # M105/M114/M2007 poll period of the monitor
    "filament_load": "extrude",         # Load/Unload: "extrude" (heat, then E moves) or "m701" (M701/M702 - IGNORED by fw V1.3.2-alpha)
    "filament_load_mm": 100,            # load/unload length (<=150)
    "filament_retry_mm": 20,            # "No, extrude more" length after a load
    "filaments": [["PLA", 210], ["PETG", 240], ["ABS", 250], ["TPU", 225], ["PCTG", 250]],  # picker [name, nozzle °C]
    "filament_tolerance_c": 3,          # start moving once the nozzle is within this of target
    "filament_heat_timeout_s": 900,
    "filament_poll_s": 1,
    "ivi_header": True,                 # prepend IVI 3licer's ';Header Start' block (time/material on the touch screen)
    "strip_commands": ["M204", "M205", "M73", "G21"],  # dropped on upload (firmware stalled on Orca's M204/M205/M73/G21)
    "nozzle_diameter": 0.3,             # used in ';header_type: 3dp,<d>mm' if the G-code doesn't say
    "jog_extrude_temp": 235,            # Extrude/Retract on a cold nozzle (<170 °C target or below target) heat to this first
    "notify": True,                     # macOS notifications via osascript
    "caffeinate": True,                 # keep the Mac awake during USB jobs
    "printer_host": "192.168.50.85",
    "printer_port": 8080,
    "printer_token": "",                # kore API token (keep out of git)
    "serial_port": "/dev/tty.usbmodem*",  # glob allowed (IVI3D: /dev/tty.usbmodemREDACTED)
    "line_numbers": True,               # USB stream: Marlin 'N<n> <cmd>*<checksum>' lines, M110 N0 reset, Resend handling
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

def route_upload(cfg, start):
    """Where one upload goes: 'usb' (stream now, live monitoring) or 'wifi' (store on the printer)."""
    m = cfg.get("mode", "auto")
    if m == "serial": return "usb"
    if m == "wifi": return "wifi"
    return "usb" if start else "wifi"

def checksum_line(n, cmd):
    """Marlin line-numbered command with XOR checksum: 'N<n> <cmd>*<cs>'."""
    body = f"N{n} {cmd}"; cs = 0
    for ch in body.encode(): cs ^= ch
    return f"{body}*{cs}"

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

# ------------------------------------------------------ IVI file header ----
# IVI 3licer (server/index.js) prepends this block; the touch screen reads it for time / material info.
_GEN_RE = re.compile(r"^;\s*generated", re.I)
_TIME_RE = re.compile(r"^;\s*estimated printing time \(normal mode\)\s*=\s*(.+)$")
_M73_RE = re.compile(r"^M73\s+P0\s+R(\d+)", re.I)
_SET_RE = re.compile(r"^;\s*(filament_type|nozzle_temperature|hot_plate_temp|bed_temperature|sparse_infill_speed|"
                     r"max_z_height|nozzle_diameter|filament used \[mm\]|filament used \[g\]|total filament used \[g\])\s*[=:]\s*(.*)$")
_AX_RE = re.compile(r"([XYZEF])(-?\d*\.?\d+)")

def parse_duration(s):
    """'5h 58m 3s' / '1d 2h 3m' -> seconds (int) or None."""
    tot, hit = 0.0, False
    for v, u in re.findall(r"(\d+(?:\.\d+)?)\s*([dhms])", s):
        tot += float(v) * {"d": 86400, "h": 3600, "m": 60, "s": 1}[u]; hit = True
    return int(round(tot)) if hit else None

def _first(v):
    return v.split(",")[0].split(";")[0].strip()

def _num(v):
    try: f = float(_first(v))
    except ValueError: return None
    return int(f) if f == int(f) else f

def _fmt(v): return "%g" % v if isinstance(v, float) else str(v)

DEFAULT_STRIP = ("M204", "M205", "M73", "G21")

def strip_regex(codes):
    """Matches command lines whose first word is one of codes (e.g. 'M204 P500 ; accel', not M2040)."""
    codes = [c.strip().upper() for c in codes if c.strip()]
    if not codes: return None
    return re.compile(r"^\s*(?:%s)(?![0-9.])" % "|".join(re.escape(c) for c in codes), re.I)

def scan_gcode(f, strip=None):
    """One streaming pass over a text file object -> stats dict. strip: regex from strip_regex(); those lines
    are not counted (they are dropped from the output) but M73 is still read for the time estimate."""
    st = {"lines": 0, "stripped": 0, "valid": 0, "head": [], "head_done": False, "time": None, "m73": None, "set": {},
          "min": [None] * 3, "max": [None] * 3}
    pos = [0.0, 0.0, 0.0]; e = 0.0; rel = False; rel_e = False
    mn, mx = st["min"], st["max"]
    for raw in f:
        if strip and strip.match(raw):
            st["stripped"] += 1
            if st["m73"] is None:
                m = _M73_RE.match(raw.strip())
                if m: st["m73"] = int(m.group(1)) * 60
            continue
        st["lines"] += 1
        line = raw.strip()
        if not st["head_done"]:
            if line.startswith(";") and not _GEN_RE.match(line) and len(st["head"]) < 100:
                st["head"].append(raw.rstrip("\r\n")); continue
            st["head_done"] = True
            if not _GEN_RE.match(line): st["head"] = []        # no ';Generated' marker: keep the file as is
        if not line: continue
        if line[0] == ";":
            m = _TIME_RE.match(line)
            if m: st["time"] = parse_duration(m.group(1)); continue
            m = _SET_RE.match(line)
            if m and m.group(1) not in st["set"]: st["set"][m.group(1)] = m.group(2).strip()
            continue
        st["valid"] += 1
        c = line.split(";", 1)[0].upper()
        if c[:3] in ("G0 ", "G1 ") or c in ("G0", "G1") or c.startswith(("G0X", "G0Y", "G0Z", "G1X", "G1Y", "G1Z", "G1E")):
            new = list(pos); ext = False
            for k, v in _AX_RE.findall(c[2:]):
                v = float(v)
                if k == "E":
                    ext = v > 0 if rel_e else v > e
                    e = e + v if rel_e else v
                elif k != "F":
                    i = "XYZ".index(k); new[i] = pos[i] + v if rel else v
            if ext:
                for p in (pos, new):
                    for i in range(3):
                        if mn[i] is None or p[i] < mn[i]: mn[i] = p[i]
                        if mx[i] is None or p[i] > mx[i]: mx[i] = p[i]
            pos = new
        elif c.startswith("G91"): rel = rel_e = True
        elif c.startswith("G90"): rel = rel_e = False
        elif c.startswith("M83"): rel_e = True
        elif c.startswith("M82"): rel_e = False
        elif c.startswith("G92"):
            for k, v in _AX_RE.findall(c[3:]):
                if k == "E": e = float(v)
                elif k in "XYZ": pos["XYZ".index(k)] = float(v)
        elif st["m73"] is None:
            m = _M73_RE.match(c)
            if m: st["m73"] = int(m.group(1)) * 60
    return st

def build_ivi_header(st, nozzle=0.4, date=None):
    s = st["set"]
    t = st["time"] if st["time"] is not None else (st["m73"] or 0)
    nz = _num(s["nozzle_diameter"]) if s.get("nozzle_diameter") else nozzle
    bed = s.get("hot_plate_temp") or s.get("bed_temperature") or "0"
    spd = _num(s.get("sparse_infill_speed", "0")) or 0
    mn = [v if v is not None else 0.0 for v in st["min"]]; mx = [v if v is not None else 0.0 for v in st["max"]]
    if st["max"][2] is None and s.get("max_z_height"): mx[2] = float(_num(s["max_z_height"]) or 0)
    out = [";Header Start", ""] + st["head"] + ["", ";header_type: 3dp,%smm" % _fmt(nz),
           ";file_total_lines: %d" % (st["lines"] + 20), ";file_valid_lines: %d" % st["valid"],
           ";estimated_time(s): %d" % t]
    if s.get("filament used [mm]"):     # unverified extras (IVI 3licer logs these, unknown if the screen reads them)
        out.append(";filament_used(m): %.2f" % (sum(float(x) for x in s["filament used [mm]"].split(",") if x.strip()) / 1000))
    g = s.get("filament used [g]") or s.get("total filament used [g]")
    if g: out.append(";filament_weight(g): %.2f" % sum(float(x) for x in g.split(",") if x.strip()))
    out += [";material_type: %s" % (_first(s.get("filament_type", "PLA")) or "PLA"),
            ";nozzle_temperature(°C): %s" % _fmt(_num(s.get("nozzle_temperature", "0")) or 0),
            ";build_plate_temperature(°C): %s" % _fmt(_num(bed) or 0),
            ";work_speed(mm/minute): %s" % _fmt(spd * 60)]
    for k, arr in (("max", mx), ("min", mn)):
        out += [";%s_%s(mm): %.2f" % (k, a, arr[i]) for i, a in enumerate("xyz")]
    out += ["", ";Header End", "", ";G-code for 3dp engraving", ";Generated by IVI 3licer",
            ";" + (date or time.strftime("%Y-%m-%d %H:%M:%S")), "", ""]
    return "\n".join(out)

def has_ivi_header(path):
    with open(path, "rb") as f: return b";Header Start" in f.read(4096)

def prepare_gcode(src, dst=None, nozzle=0.4, date=None, header=True, strip=DEFAULT_STRIP):
    """Stream src -> dst (None = in place): drop command lines whose first word is in strip and, if header and
    the file has no ';Header Start', prepend the IVI header (original comment lines before ';Generated' move
    into it; line counts describe the output). Returns {"header": bool, "removed": int}."""
    rx = strip_regex(strip or ())
    add = header and not has_ivi_header(src)
    if not add and not rx:
        if dst and dst != src: shutil.copyfile(src, dst)
        return {"header": False, "removed": 0}
    st = {"head": [], "stripped": 0}
    if add:
        with open(src, encoding="utf-8", errors="surrogateescape", newline="") as f:
            st = scan_gcode(f, rx)
    tmp = (dst or src) + ".ivitmp"; removed = 0
    with open(src, encoding="utf-8", errors="surrogateescape", newline="") as fi, \
         open(tmp, "w", encoding="utf-8", errors="surrogateescape", newline="") as fo:
        if add:
            fo.write(build_ivi_header(st, nozzle, date))
            n = len(st["head"])
            while n:                                  # head lines moved into the header (stripped ones dropped)
                raw = next(fi)
                if rx and rx.match(raw): removed += 1; continue
                n -= 1
        if rx:
            buf = []
            for raw in fi:
                if rx.match(raw): removed += 1; continue
                buf.append(raw)
                if len(buf) >= 4096: fo.writelines(buf); buf = []
            fo.writelines(buf)
        else:
            shutil.copyfileobj(fi, fo, 1 << 20)
    os.replace(tmp, dst or src)
    return {"header": add, "removed": removed}

def add_ivi_header(src, dst=None, nozzle=0.4, date=None, strip=()):
    """Header only (no stripping unless strip is given). Returns False if src already has ';Header Start'."""
    return prepare_gcode(src, dst, nozzle, date, True, strip)["header"]

# --------------------------------------------------------------- serial ----
_ZRX = re.compile(r"[Zz](-?[\d.]+)")
_ERX = re.compile(r"[Ee](-?[\d.]+)")
def layer_starts(lines):
    """0-based indices where a new layer starts: first extruding G0/G1 at a new Z (absolute XYZ assumed,
    G91 blocks skipped). Same rule as the Device page's toolpath parser."""
    out, z, lz, rel = [], 0.0, None, False
    for i, l in enumerate(lines):
        w = l.split(None, 1); c = w[0].upper() if w else ""
        if c == "G91": rel = True; continue
        if c == "G90": rel = False; continue
        if c not in ("G0", "G1") or rel: continue
        m = _ZRX.search(l)
        if m:
            try: z = float(m.group(1))
            except ValueError: pass
        e = _ERX.search(l)
        if e and c == "G1" and lz != z:
            try: ev = float(e.group(1))
            except ValueError: continue
            if ev > 0: out.append(i); lz = z
    return out

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
    m = re.match(r"X:\s*(-?[\d.]+)\s+Y:\s*(-?[\d.]+)\s+Z:\s*(-?[\d.]+)", line)
    if m: status["position"] = dict(zip("xyz", (float(v) for v in m.groups()))); hit = True
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
                 prelude=(), report_interval=4, auto_clear=True, notify=None, line_numbers=False):
        self.ser, self.lines, self.name = ser, lines, name
        self.line_numbers = line_numbers; self._resend = None
        self.fw = firmware_version
        self.line_timeout, self.clock = line_timeout, clock
        self.prelude, self.report_interval, self.auto_clear = list(prelude), report_interval, auto_clear
        self.notify = notify or (lambda m: None)
        self.sent = 0; self.state = "Starting"; self.error = None; self.reason = None
        self.started = None; self.status = {}
        self._pause = threading.Event(); self._cancel = threading.Event()
        self._flags = set(); self._layers = None

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
        m = re.match(r"(?:resend|rs)[:\s]\s*N?(\d+)", low)
        if m: self._resend = int(m.group(1))

    def _wait(self, predicate, timeout):
        end = self.clock() + timeout
        while self.clock() < end:
            if self._cancel.is_set() and self.state not in ("Starting", "Stopping"):
                return False
            line = self._readline()
            if not line:
                continue
            if low_err(line):
                l2 = line.lower()
                if not (self.line_numbers and any(k in l2 for k in ("checksum", "line number", "last line", "no line"))):
                    raise RuntimeError(f"printer error: {line}")
                continue                     # Marlin follows with 'Resend: N' + ok
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
            if self.line_numbers:
                self._write("M110 N0")
                self._wait(lambda l: l == "ok" or l.startswith("ok "), self.line_timeout)
            i = 0; resends = 0
            while i < len(self.lines):
                while self._pause.is_set() and not self._cancel.is_set():
                    self._readline()          # keep watching for resume / kill while paused
                if self._cancel.is_set():
                    break
                cmd = self.lines[i]
                self._resend = None
                self._write(checksum_line(i + 1, cmd) if self.line_numbers else cmd)
                if self._wait(lambda l: l == "ok" or l.startswith("ok "), self.line_timeout) is False:
                    break
                if self._resend is not None and self.line_numbers:
                    resends += 1
                    if resends > 50: raise RuntimeError("too many resend requests (line noise?)")
                    i = max(0, self._resend - 1); self.sent = i; continue
                i += 1; self.sent = i
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

    def info(self):
        el = (self.clock() - self.started) if self.started else None
        left = el * (len(self.lines) - self.sent) / self.sent if el and self.sent else None
        if self._layers is None: self._layers = layer_starts(self.lines)
        layer = bisect.bisect_right(self._layers, self.sent - 1) if self.sent else 0
        return {"source": "usb stream", "sent": self.sent, "total": len(self.lines), "elapsed": el, "left": left,
                "line": self.sent, "layer": layer, "layers": len(self._layers), "gcode": "/api/ivi/job/gcode"}

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
ALLOWED_CMD = re.compile(r"^(M104 S\d{1,3}|M140 S\d{1,3}|M220 S\d{1,3}|M221 S\d{1,3}|M105|M2007|M2410|M2411 S[13]"
                         r"|M106( S\d{1,3})?|M107|M114|M701|M702|M82|M83|G90|G91|G28( X)?( Y)?( Z)?"
                         r"|G1( [XYZEF]-?\d{1,4}(\.\d{1,3})?)+)$")
LIMITS = {"M104": 300, "M140": 120, "M220": 300, "M221": 200, "M106": 255}
G1_LIMITS = {"X": 150.0, "Y": 150.0, "Z": 300.0, "E": 150.0, "F": 6000.0}   # |value| caps (mm, mm/min)

def check_command(cmd):
    c = " ".join(cmd.strip().upper().split())
    if not ALLOWED_CMD.match(c):
        raise ValueError(f"command not allowed: {cmd!r}")
    if c.startswith("G1 "):
        seen = set()
        for w in c.split()[1:]:
            k, v = w[0], float(w[1:])
            if k in seen: raise ValueError(f"duplicate {k} in {c}")
            seen.add(k)
            if abs(v) > G1_LIMITS[k]: raise ValueError(f"{k}{v:g} exceeds limit {G1_LIMITS[k]:g}")
            if k == "F" and v <= 0: raise ValueError("feed rate must be > 0")
        return c
    code, _, arg = c.partition(" S")
    if code in LIMITS and arg and int(arg) > LIMITS[code]:
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
                self.ser.write(b"M105\n"); self.ser.write(b"M114\n"); self.ser.write(b"M2007\n")
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

class FilamentChange:
    """Touch-screen style load/unload: M104 S<t>, poll temps (no blocking M109, so the monitor keeps
    running) until within tolerance, then M83 + E moves + M82. States: heating, moving, done, cancelled, error."""
    def __init__(self, bridge, action, temp, clock=time.monotonic, distance=None, feed=None, heat=True, prev=0):
        self.b, self.action, self.temp, self.clock = bridge, action, temp, clock
        self.distance, self.feed, self.heat, self.prev = distance, feed, heat, prev
        self.state, self.error, self.actual, self.note = ("heating" if heat else "moving"), None, None, None
        self._cancel = threading.Event(); self.thread = None

    def info(self):
        return {"action": self.action, "target": self.temp, "actual": self.actual, "state": self.state,
                "error": self.error, "note": self.note}

    @property
    def jog(self): return self.action in ("extrude", "retract")

    def _restore(self):
        """Cancel: jog extrude puts the nozzle back to its previous target; load/unload turn it off."""
        if not self.jog: return self._off()
        try: self.b.send_command("M104 S%d" % int(round(self.prev)))
        except Exception as e: log("filament: restore failed:", e)

    def _off(self):
        try: self.b.send_command("M104 S0")          # like the touch screen: nozzle off at the end
        except Exception as e: log("filament: nozzle off failed:", e)

    def cancel(self):
        self._cancel.set()
        if self.state == "confirm": self.state = "cancelled"; self._off()

    def answer(self, ok):
        """Load prompt 'Filament coming out of the nozzle?': yes -> done; no -> extrude filament_retry_mm, ask again.
        The nozzle stays at temperature."""
        if self.state != "confirm": raise RuntimeError("not waiting for a load confirmation")
        if ok: self._off(); self.state = "done"; return
        self.state = "moving"
        try:
            for c in ("M83", "G1 E%g F300" % float(self.b.cfg.get("filament_retry_mm", 20)), "M82"):
                self.b.send_command(c)
            self.state = "confirm"
        except Exception as e:
            self.state, self.error = "error", str(e)

    def moves(self):
        n = float(self.b.cfg.get("filament_load_mm", 100))
        if self.jog:
            return ["M83", "G1 E%g F%g" % (self.distance if self.action == "extrude" else -self.distance, self.feed), "M82"]
        if self.action == "unload":
            return ["M83", "G1 E10 F300", "G1 E-%g F1500" % n, "M82"]  # then M104 S0
        return ["M83", "G1 E%g F300" % n, "M82"]

    def start(self):
        self.thread = threading.Thread(target=self.run, daemon=True); self.thread.start()

    def run(self):
        cfg, mon = self.b.cfg, self.b.monitor
        try:
            if self.b.cfg.get("filament_load") == "m701" and not self.jog:
                self.state = "moving"; self.b.send_command("M104 S%d" % self.temp)
                self.b.send_command("M701" if self.action == "load" else "M702"); self.state = "done"; return
            if self.heat: self.b.send_command("M104 S%d" % self.temp)
            tol = float(cfg.get("filament_tolerance_c", 3)); end = self.clock() + float(cfg.get("filament_heat_timeout_s", 900))
            while self.heat:
                if self._cancel.is_set():
                    self._restore(); self.state = "cancelled"; return
                if mon and not (mon.thread and mon.thread.is_alive()): mon.poll_once()   # no monitor thread (tests/CLI)
                t = self.b.live_status().get("temps", {}).get("tool0")
                if t: self.actual = t["actual"]
                if self.actual is not None and abs(self.actual - self.temp) <= tol: break
                if self.clock() > end: raise TimeoutError("nozzle did not reach %d °C in time" % self.temp)
                if mon and not mon.connected: raise RuntimeError("USB disconnected while heating")
                self._cancel.wait(float(cfg.get("filament_poll_s", 1)))
            self.state = "moving"
            for c in self.moves():
                if self._cancel.is_set(): self._restore(); self.state = "cancelled"; return
                self.b.send_command(c)
            if self.jog:
                self.note = "Nozzle left at %d°C – Cooldown to turn off" % self.temp; self.state = "done"
            elif self.action == "load": self.state = "confirm"
            else: self._off(); self.state = "done"
        except Exception as e:
            self.state, self.error = "error", str(e); log("filament:", e)

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
        self.filament = None
        self.storage_print = None      # name of a Wi-Fi-uploaded job; USB stays closed until the user re-enables it

    def usb_locked(self): return self.storage_print is not None

    def lock_usb(self, name):
        """After 'Upload': the job will run from printer storage. Opening USB mid-print stalls it, so let go."""
        self.storage_print = name
        if self.monitor: self.monitor.release()

    def unlock_usb(self):
        self.storage_print = None
        if self.monitor: self.monitor.resume()

    def send_command(self, cmd):
        """Temp/speed/flow etc. over USB: through the streaming job if one runs, else the monitor."""
        c = check_command(cmd)
        if self.busy() and isinstance(self.job, SerialJob):
            self.job._write(c); return c
        if self.usb_locked(): raise RuntimeError("USB controls are off while the printer prints from its own storage")
        if not self.monitor: raise RuntimeError("serial_monitor is off")
        return self.monitor.send(c)

    def start_filament(self, action, temp):
        if action not in ("load", "unload"): raise ValueError("action must be load or unload")
        temp = int(round(float(temp)))
        if not 150 <= temp <= 300: raise ValueError("temperature must be 150-300 °C")
        if self.busy(): raise RuntimeError("a USB job is running")
        f = self.filament
        if f and f.state in ("heating", "moving", "confirm"): raise RuntimeError("a filament change is already running")
        self.filament = FilamentChange(self, action, temp); self.filament.start(); return self.filament.info()

    def start_jog_extrude(self, action, distance, feed):
        """Extrude/Retract button: heat to jog_extrude_temp first unless the nozzle is already hot
        (target >= 170 °C and within tolerance of it); the nozzle is left hot afterwards."""
        if action not in ("extrude", "retract"): raise ValueError("action must be extrude or retract")
        distance, feed = float(distance), float(feed)
        if not 0 < distance <= G1_LIMITS["E"]: raise ValueError("distance must be 0-%g mm" % G1_LIMITS["E"])
        if not 0 < feed <= G1_LIMITS["F"]: raise ValueError("feed must be 0-%g mm/min" % G1_LIMITS["F"])
        if self.busy(): raise RuntimeError("a USB job is running")
        f = self.filament
        if f and f.state in ("heating", "moving", "confirm"): raise RuntimeError("a filament change is already running")
        mon = self.monitor
        if mon and not (mon.thread and mon.thread.is_alive()): mon.poll_once()
        t = self.live_status().get("temps", {}).get("tool0") or {}
        tgt, act = float(t.get("target", 0)), t.get("actual")
        tol = float(self.cfg.get("filament_tolerance_c", 3))
        hot = tgt >= 170 and act is not None and act >= tgt - tol
        temp = int(round(tgt)) if hot else int(self.cfg.get("jog_extrude_temp", 235))
        self.filament = FilamentChange(self, action, temp, distance=distance, feed=feed, heat=not hot, prev=tgt)
        self.filament.actual = act; self.filament.start(); return self.filament.info()

    def live_status(self):
        if self.busy(): return self.job.status
        return self.monitor.status if self.monitor and self.monitor.connected else {}

    def _caffeinate(self):
        if self.cfg.get("caffeinate") and sys.platform == "darwin":
            try: return subprocess.Popen(["caffeinate", "-s", "-i", "-m", "-w", str(os.getpid())])
            except OSError: pass
        return None

    def busy(self):
        return self.job is not None and self.job.state in ("Starting", "Printing", "Paused", "Stopping")

    def clear_printer(self):
        """Clear a stale/paused PC job on the printer (M2411 S3), e.g. after 'Can't start work in current status: 5'."""
        with self.lock:
            if self.busy(): raise RuntimeError("a job is running; use Cancel")
            if self.usb_locked(): raise RuntimeError("USB controls are off while the printer prints from its own storage")
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
        if mode in ("serial", "usb"): route = "usb" if start else "spool"
        elif mode == "wifi": route = "wifi"
        else: route = route_upload(self.cfg, start)
        if route == "usb" and self.cfg.get("mode") == "serial" and not start: route = "spool"
        self.last_file = name
        if route == "wifi":
            if self.busy(): raise RuntimeError("a USB job is already running")
            try: self.wifi_factory().upload(path, name)
            except Exception as e:
                notify(self.cfg, f"Wi-Fi upload of {name} failed: {e}"); raise
            self.lock_usb(name)
            m = (f"Uploaded {name} to the printer over Wi-Fi. Start it on the touch screen. "
                 "USB controls are off until you press 'Printer idle, re-enable USB' on the Device page.")
            notify(self.cfg, m); return m
        if route == "spool":
            return f"Stored {name} in the spool folder (serial mode; print=false)."
        with self.lock:
            if self.busy():
                raise RuntimeError("a job is already running")
            self.storage_print = None      # user chose a USB print: the printer is not running a stored job
            with open(path, errors="replace") as f:
                raw = f.read()
            rx = strip_regex(self.cfg.get("strip_commands", DEFAULT_STRIP))
            lines, kind = clean_gcode(raw), header_type(raw)
            if rx: lines = [l for l in lines if not rx.match(l)]
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
                                 notify=lambda m: notify(self.cfg, m),
                                 line_numbers=self.cfg.get("line_numbers", True))
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
        if self.usb_locked() and not self.busy():
            return {"job": {"file": {"name": self.storage_print, "origin": "printer"}},
                    "progress": {"completion": None, "printTime": None, "printTimeLeft": None, "filepos": None},
                    "state": "Printing from printer storage (USB off)",
                    "ivi": {"source": "printer storage", "usb_locked": True}}
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
        d = j.info() if j and hasattr(j, "info") else {}
        return {"job": {"file": {"name": j.name if j else self.last_file, "origin": "local"}},
                "progress": {"completion": j.progress if j else None, "printTime": elapsed,
                             "printTimeLeft": d.get("left"), "filepos": j.sent if j else None},
                "state": state, "ivi": dict(d, usb_locked=False) if j else {"usb_locked": False}}

PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>IVI Bridge - Control</title>
<style>
:root{--b:#1a5cf0;--lb:#dbe8fb;--sel:#a9c8f5;--t:#1a3d8f}
*{box-sizing:border-box}body{font:15px -apple-system,Helvetica,sans-serif;margin:0;background:#fff;color:#223}
.top{background:var(--lb);color:#123;text-align:center;font-size:22px;padding:.55em;border-bottom:1px solid #b8cdee;position:relative}
.top a{position:absolute;right:.8em;top:.45em;font-size:14px;color:var(--t);text-decoration:none}
.info{display:flex;flex-wrap:wrap;gap:.4em 1.4em;padding:.5em 1em;font-size:13px;color:#456;background:#f4f8fe}
.info b{color:#123}.bar{height:6px;background:#e3ebf7}.bar>div{height:100%;background:var(--b);width:0}
.panels{padding:1em;max-width:1500px;margin:0 auto}.panel{display:none}.panel.on{display:block}
button{font:inherit;cursor:pointer;border:0}button:disabled{opacity:.4;cursor:default}
.big{background:var(--b);color:#fff;border-radius:999px;padding:.6em 1em;font-size:17px;width:100%}
.lite{background:var(--lb);color:var(--t);border-radius:999px;padding:.6em 1em;font-size:17px;width:100%}
.btn{background:var(--b);color:#fff;border-radius:999px;padding:.55em 1.2em;font-size:16px;min-width:8em}
.opts{display:flex;background:#eef4fd;border-radius:6px;overflow:hidden}.opts button{flex:1;background:none;color:#334;padding:.6em .3em;font-size:16px}
.opts button.sel{background:var(--sel);color:#012;font-weight:600}.opts button.pm{background:#c9dbf6;color:var(--t);font-size:18px}
.lbl{font-size:12px;color:#567}.val{font-size:17px;font-weight:600;color:#123}
.fgrid{display:grid;grid-template-columns:7.5em 1fr 10em;gap:.7em 1em;align-items:center}
.two{display:grid;grid-template-columns:1fr 1fr;gap:1.2em;margin-bottom:1em}
.side{display:flex;flex-direction:column;gap:.7em;grid-row:span 4}
.fan{display:flex;align-items:center;justify-content:space-between;color:var(--t)}
.tog{width:3.4em;height:1.8em;border-radius:999px;background:#c9d3e2;position:relative}.tog:after{content:"";position:absolute;top:.2em;left:.2em;width:1.4em;height:1.4em;border-radius:50%;background:#fff;transition:.15s}
.tog.on{background:var(--b)}.tog.on:after{left:1.8em}
.tgrid{display:grid;grid-template-columns:1fr 1fr;gap:1em 1.5em;align-items:start}
.pos{border:1px solid #c9d7ee;border-radius:6px;padding:.7em 1em;display:flex;justify-content:space-between;color:#345}
.pad{display:grid;grid-template-columns:repeat(3,4.2em) 1.2em 4.2em;grid-template-rows:repeat(3,3.4em);gap:.35em;justify-content:center}
.pad button{background:var(--lb);color:var(--t);border-radius:6px;font-size:16px}
.compact{display:flex;flex-wrap:wrap;gap:.6em;align-items:center;margin-top:1.2em;padding-top:.9em;border-top:1px solid #e0e8f5;font-size:14px}
.compact input{width:4.2em;font:inherit;padding:.3em;border:1px solid #bcd;border-radius:6px}
.compact button{background:var(--lb);color:var(--t);border-radius:999px;padding:.4em .9em}
h3{margin:.2em 0 .8em;color:var(--t);font-weight:600}
.tabs{display:flex;position:sticky;bottom:0;background:#fff;border-top:1px solid #c9d7ee}
.tabs button{flex:1;background:#fff;color:var(--b);font-size:20px;padding:.6em}.tabs button.on{background:var(--sel)}
.note{font-size:12px;color:#789;padding:0 1em 1em}
.dlg{position:fixed;inset:0;background:rgba(20,40,80,.35);align-items:center;justify-content:center;z-index:9}
.box{background:#fff;border-radius:12px;width:min(560px,92vw);box-shadow:0 10px 40px rgba(0,0,40,.3)}
.fgrid2{display:grid;grid-template-columns:repeat(3,1fr);gap:.6em}.fbtn{background:var(--lb);color:var(--t);border-radius:10px;padding:.8em;display:flex;flex-direction:column;align-items:center;font-size:17px}
.fbtn span{font-size:14px;color:#456}.fbtn:hover{background:var(--sel)}
.hs{text-align:center;font-size:22px;color:var(--t);margin-bottom:.8em}.hs.done{color:#1a8a3a}.hs.error{color:#c22}
.hbar{height:14px;background:#e3ebf7;border-radius:7px;overflow:hidden;margin-bottom:.6em}.hbar>div{height:100%;background:var(--b);width:0;transition:width .5s}
.ban{display:none;margin:.8em 1em 0;padding:.8em 1em;border-radius:10px;background:#fff4d6;border:1px solid #e8b84a;color:#5a3d00;align-items:center;gap:1em}
.ban b{color:#3d2900}.ban button{background:#e8b84a;color:#2a1c00;border-radius:999px;padding:.5em 1em;white-space:nowrap}
.job{display:none;margin:.8em 1em 0;padding:.8em 1em;border-radius:10px;background:#eaf2ff;border:1px solid #b8cdee}
.job .hbar{margin:.5em 0}.job .row{display:flex;flex-wrap:wrap;gap:.4em 1.4em;font-size:13px;color:#456}.job button{background:var(--lb);color:var(--t);border-radius:999px;padding:.4em .9em}
@media (min-width:1100px){.tabs{display:none}.panels{display:grid;grid-template-columns:1fr 1fr;gap:2em}
.panel{display:block;border:1px solid #d3e0f3;border-radius:10px;padding:1em}}
</style>
<div class=top>Control<a href=# onclick="tick();return false">&#8635;</a></div>
<div class=info><span>Uploads: <b>__MODE__</b></span><span>USB: <b id=usb>…</b></span><span>State: <b id=st>…</b></span><span>File: <b id=fn></b></span><span id=pc></span></div>
<div class=bar><div id=pb></div></div>
<div class=ban id=ban><div style="flex:1"><b>USB controls are off &mdash; the printer is printing <span id=banf></span> from its own storage.</b><br>
You used <i>Upload</i>, so the job runs from the touch screen. Opening USB during a stored-file print stalls it, so the bridge
keeps the port closed. Pause or cancel on the touch screen. When the printer is idle, turn USB back on.</div>
<button title="Only press this when the printer is idle (job finished or cancelled on the touch screen)" onclick="usbOn()">Printer idle, re-enable USB</button></div>
<div class=job id=jobp><b>USB print: <span id=jn></span></b> <span id=js2 style="color:#456"></span>
<div class=hbar><div id=jb></div></div>
<div class=row><span>Progress <b id=jpc>–</b></span><span>Lines <b id=jl>–</b></span><span>Elapsed <b id=je>–</b></span><span>Left ≈ <b id=jt>–</b></span></div>
<div class=row style="margin-top:.5em"><button title="M2410" onclick="cmd('pause','pause')">Pause</button><button title="M2411 S1" onclick="cmd('pause','resume')">Resume</button><button title="Stop the stream and the printer job (M2411 S3)" onclick="if(confirm('Cancel print?'))cmd('cancel')">Cancel</button>
<span style="font-size:12px;color:#789">Streamed from this Mac over USB with live monitoring &ndash; keep the Mac awake and the cable connected until it finishes.</span></div></div>
<div class=job id=tpp style="display:none"><b>Live toolpath</b> <span id=tpc style="color:#456;font-size:13px"></span>
<div id=tpn style="font-size:13px;color:#789;margin:.3em 0"></div>
<div id=tpw style="display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap"><canvas id=tpv width=560 height=560 style="width:min(560px,100%);background:#15171c;border-radius:8px"></canvas>
<div><div style="font-size:12px;color:#456">Z height</div><canvas id=tpz width=150 height=470 style="background:#15171c;border-radius:8px"></canvas>
<div style="font-size:12px;color:#456">top view &middot; bright = printed this layer, faint = still to print, dim = earlier layers, orange = nozzle</div></div></div></div>
<div class=panels>
<div class=panel id=p_tool><h3>Toolhead</h3>
<div class=tgrid>
 <div><div class=pos><span id=px>X: –</span><span id=py>Y: –</span><span id=pz>Z: –</span></div>
  <p class=lbl>Jog Speed(mm/min)</p><div class=opts data-g=tspd><button>200</button><button>500</button><button class=sel>1500</button><button>3000</button></div>
  <p class=lbl>Jog Distance (mm)</p><div class=opts data-g=tdst><button>0.05</button><button>1</button><button class=sel>10</button><button>50</button></div></div>
 <div><button class="lite u" onclick="g(['G28'])">Home</button>
  <div class=pad style="margin-top:1em">
   <span></span><button class=u onclick="jog('Y',1)">Y+</button><span></span><span></span><button class=u onclick="jog('Z',1)">Z+</button>
   <button class=u onclick="jog('X',-1)">X-</button><button class=u title="Move to X0 Y0" onclick="g(['G90','G1 X0 Y0 F'+sel('tspd')])">X/Y</button><button class=u onclick="jog('X',1)">X+</button><span></span><button class=u title="Home (G28)" onclick="g(['G28'])">Z</button>
   <span></span><button class=u onclick="jog('Y',-1)">Y-</button><span></span><span></span><button class=u onclick="jog('Z',-1)">Z-</button></div></div>
</div>
<div class=compact>Speed <input id=sp type=number min=10 max=300 value=100>% <button class=u onclick="g(['M220 S'+sp.value])">Set</button>
 Flow <input id=fl type=number min=10 max=200 value=100>% <button class=u onclick="g(['M221 S'+fl.value])">Set</button>
 <button onclick="cmd('pause','pause')">Pause</button><button onclick="cmd('pause','resume')">Resume</button>
 <button onclick="if(confirm('Cancel print?'))cmd('cancel')">Cancel</button>
 <button title="M2411 S3: clear a stuck/paused PC job" onclick="if(confirm('Clear a stuck job on the printer (M2411 S3)?'))fetch('/api/ivi/clear',{method:'POST',headers:H}).then(r=>r.json()).then(j=>say(j.message||j.error))">Clear stuck job</button></div>
</div>
<div class=panel id=p_fil><h3>Filament</h3>
<div class=two><button class="big u" onclick="pick('load')">Load Filament</button><button class="big u" onclick="pick('unload')">Unload Filament</button></div>
<div class=fgrid>
 <div><div class=lbl>Nozzle</div><div class=val id=nzv>–</div></div>
 <div class=opts data-g=nz data-c=M104><button>210°C</button><button>240°C</button><button>270°C</button><button class=pm data-d=-5>-</button><button class=pm data-d=5>+</button></div>
 <div class=side><div class=fan>Fan <button class="tog u" id=fan onclick="fanT()"></button></div>
  <button class="btn u" onclick="g(['M104 S0','M140 S0'])">Cooldown</button>
  <button class="btn u" onclick="ext(1)">Extrude</button><button class="btn u" onclick="ext(-1)">Retract</button></div>
 <div><div class=lbl>Bed</div><div class=val id=bdv>–</div></div>
 <div class=opts data-g=bd data-c=M140><button>60°C</button><button>80°C</button><button>100°C</button><button class=pm data-d=-5>-</button><button class=pm data-d=5>+</button></div>
 <div class=lbl>Jog Speed<br>(mm/min)</div><div class=opts data-g=fspd><button class=sel>100</button><button>200</button><button>500</button><button>1000</button></div>
 <div class=lbl>Jog Distance<br>(mm)</div><div class=opts data-g=fdst><button class=sel>10</button><button>20</button><button>50</button><button>100</button></div>
</div></div>
</div>
<p class=note id=msg>Controls need USB. <b>Upload and Print</b> streams the job over USB (live status, Mac must stay awake and connected); <b>Upload</b> stores it on the printer for the touch screen and turns USB controls off during that print. Speed % (M220) and flow % (M221) are not yet verified on this firmware.</p>
<div class=tabs><button id=t_tool class=on onclick="tab('tool')">Toolhead</button><button id=t_fil onclick="tab('fil')">Filament</button></div>
<div id=dlg class=dlg style="display:none"><div class=box><div class=top style="border-radius:12px 12px 0 0">
<span id=mt>Filament</span></div><div style="padding:1.2em">
<div id=v_pick><p class=lbl>Which filament is loaded?</p><div id=fp class=fgrid2></div>
<div style="display:flex;gap:.6em;align-items:center;margin-top:1em">Custom <input id=fcu type=number min=150 max=300 value=220 style="width:5em;font:inherit;padding:.4em;border:1px solid #bcd;border-radius:6px"> °C
<button class=btn onclick="run(+fcu.value)">Start</button><span style="flex:1"></span><button class=lite style="width:auto" onclick="fclose()">Close</button></div></div>
<div id=v_heat style="display:none"><div id=hs class=hs>Heating…</div><div class=hbar><div id=hb></div></div><div id=ht class=val style="text-align:center">–</div><div id=hn class=lbl style="text-align:center;margin-top:.4em"></div>
<div style="display:flex;justify-content:center;gap:.8em;margin-top:1.2em"><button id=fy class=btn style="display:none" onclick="fans('yes')">Yes, done</button><button id=fm class=btn style="display:none" onclick="fans('more')">No, extrude more</button><button id=fc class=btn onclick="fcancel()">Cancel</button><button id=fk class=btn style="display:none" onclick="fclose()">OK</button></div></div>
</div></div></div>
<script>const K=__KEY__,FIL=__FIL__,H={'X-Api-Key':K,'Content-Type':'application/json'};let T={},fanOn=false;
async function usbOn(){if(!confirm('Is the printer idle (stored print finished or cancelled)? Opening USB during a stored print stalls it.'))return;
 await fetch('/api/ivi/usb',{method:'POST',headers:H,body:JSON.stringify({action:'enable'})});say('USB controls re-enabled');tick()}
function hms(s){if(s==null)return'–';s=Math.round(s);return Math.floor(s/3600)+'h '+String(Math.floor(s%3600/60)).padStart(2,'0')+'m'}
function tab(t){for(const n of['tool','fil']){document.getElementById('t_'+n).classList.toggle('on',n==t);document.getElementById('p_'+n).classList.toggle('on',n==t)}}
tab('tool');
function say(m){msg.textContent=m}
function sel(gr){const b=document.querySelector('[data-g='+gr+'] .sel');return b?b.textContent:''}
document.querySelectorAll('.opts').forEach(o=>o.querySelectorAll('button').forEach(b=>b.onclick=()=>{
 const c=o.dataset.c;
 if(b.dataset.d){const cur=(T[o.dataset.g]||0)+(+b.dataset.d);return g([c+' S'+Math.max(0,cur)])}
 o.querySelectorAll('button').forEach(x=>x.classList.toggle('sel',x==b));if(c)g([c+' S'+parseInt(b.textContent)])}));
async function g(cs){const r=await fetch('/api/printer/command',{method:'POST',headers:H,body:JSON.stringify({commands:cs})});
 say(r.ok?'Sent '+cs.join(' · '):'Failed: '+((await r.json().catch(()=>({}))).error||r.status));setTimeout(tick,300)}
function jog(a,s){g(['G91','G1 '+a+(s*sel('tdst'))+' F'+sel('tspd'),'G90'])}
async function ext(s){FA=s>0?'extrude':'retract';
 const r=await fetch('/api/ivi/filament',{method:'POST',headers:H,body:JSON.stringify({action:FA,distance:+sel('fdst'),feed:+sel('fspd')})});
 const j=await r.json();if(!r.ok){say('Failed: '+j.error);return}
 if(j.state=='heating'){mt.textContent=s>0?'Extrude':'Retract';fv('heat');dlg.style.display='flex';show(j);clearInterval(FT);FT=setInterval(fpoll,1000)}
 else{say((s>0?'Extruding ':'Retracting ')+sel('fdst')+' mm (nozzle already hot)');setTimeout(async()=>{const k=await (await fetch('/api/ivi/filament',{headers:H})).json();if(k.note)say(k.note);else if(k.error)say('Error: '+k.error)},800)}}
let FA=null,FT=null;
function pick(a){FA=a;mt.textContent=(a=='load'?'Load':'Unload')+' Filament';fp.innerHTML='';
 FIL.forEach(([n,t])=>{const b=document.createElement('button');b.className='fbtn';b.innerHTML='<b>'+n+'</b><span>'+t+'°C</span>';b.onclick=()=>run(t);fp.appendChild(b)});
 fv('pick');dlg.style.display='flex'}
function fv(v){for(const k of['pick','heat'])document.getElementById('v_'+k).style.display=k==v?'block':'none'}
async function run(t){const r=await fetch('/api/ivi/filament',{method:'POST',headers:H,body:JSON.stringify({action:FA,temp:t})});
 const j=await r.json();if(!r.ok){say('Failed: '+j.error);return}fv('heat');show(j);clearInterval(FT);FT=setInterval(fpoll,1000)}
async function fpoll(){show(await (await fetch('/api/ivi/filament',{headers:H})).json())}
function show(j){const a=j.actual,t=j.target,pct=a==null?0:Math.max(0,Math.min(100,100*a/t));
 hb.style.width=pct+'%';ht.textContent=(a==null?'–':Math.round(a))+'°C / '+t+'°C';
 hs.textContent={heating:'Heating…',moving:({load:'Loading…',unload:'Unloading…',extrude:'Extruding…',retract:'Retracting…'}[j.action]),confirm:'Filament coming out of the nozzle?',done:'Done',cancelled:'Cancelled',error:'Error: '+j.error}[j.state]||j.state;
 hs.className='hs '+j.state;const fin=['done','cancelled','error'].includes(j.state);const cf=j.state=='confirm';fy.style.display=fm.style.display=cf?'':'none';fc.style.display=fin?'none':'';fk.style.display=fin?'':'none';hn.textContent=j.note||'';if(fin)clearInterval(FT)}
async function fans(a){const r=await fetch('/api/ivi/filament',{method:'POST',headers:H,body:JSON.stringify({action:a})});show(await r.json())}
async function fcancel(){await fetch('/api/ivi/filament',{method:'POST',headers:H,body:JSON.stringify({action:'cancel'})});fpoll()}
function fclose(){dlg.style.display='none';clearInterval(FT)}
function fanT(){fanOn=!fanOn;fan.classList.toggle('on',fanOn);g([fanOn?'M106 S255':'M107'])}
async function cmd(c,a){const r=await fetch('/api/job',{method:'POST',headers:H,body:JSON.stringify({command:c,action:a})});say(r.ok?c+' sent':'Failed: '+((await r.json()).error||r.status));tick()}
async function tick(){try{const j=await (await fetch('/api/job',{headers:H})).json(),p=await (await fetch('/api/printer',{headers:H})).json();
 const lk=p.ivi&&p.ivi.usb_locked;ban.style.display=lk?'flex':'none';banf.textContent=(p.ivi&&p.ivi.storage_file)||'';
 const ji=j.ivi||{},us=ji.source=='usb stream'&&!/^(Operational|Cancelled)/.test(j.state);jobp.style.display=us?'block':'none';
 if(us){jn.textContent=j.job.file.name;js2.textContent=j.state;const c2=j.progress.completion||0;jb.style.width=c2+'%';jpc.textContent=c2.toFixed(1)+'%';jl.textContent=ji.sent+' / '+ji.total;je.textContent=hms(ji.elapsed);jt.textContent=hms(ji.left)}
 const u=p.ivi&&p.ivi.usb&&!lk;usb.textContent=lk?'off (printing from printer storage)':u?(us?'streaming job':'connected'):'not connected'+(p.ivi&&p.ivi.usb_error?' ('+p.ivi.usb_error+')':'');
 document.querySelectorAll('.u,.opts[data-c] button').forEach(b=>b.disabled=!u);
 st.textContent=j.state;fn.textContent=j.job.file.name||'–';const c=j.progress.completion;pb.style.width=(c||0)+'%';pc.textContent=c==null?'':c.toFixed(1)+'%';
 const t=p.temperature||{},f=v=>v?Math.round(v.actual)+'°C/'+Math.round(v.target)+'°C':'–';nzv.textContent=f(t.tool0);bdv.textContent=f(t.bed);
 T.nz=t.tool0?t.tool0.target:0;T.bd=t.bed?t.bed.target:0;
 for(const[g2,v]of[['nz',T.nz],['bd',T.bd]])document.querySelectorAll('[data-g='+g2+'] button:not(.pm)').forEach(b=>b.classList.toggle('sel',parseInt(b.textContent)==v));
 try{tpTick(j,lk)}catch(e){}
 const q=p.position;px.textContent='X: '+(q?q.x.toFixed(2):'–');py.textContent='Y: '+(q?q.y.toFixed(2):'–');pz.textContent='Z: '+(q?q.z.toFixed(2):'–')
}catch(e){st.textContent='bridge offline';document.querySelectorAll('.u').forEach(b=>b.disabled=true)}}
let TP={key:null,M:null,lay:null,n:0,busy:false,drawn:-1};
async function tpLoad(key){TP={key,M:null,lay:null,n:0,busy:true,drawn:-1};tpn.textContent='Loading toolpath…';
 try{const r=await fetch('/api/ivi/job/gcode',{headers:H});if(!r.ok)throw new Error(r.status);let txt=await r.text();
 const mv=[],lay=[];let x=0,y=0,z=0,e=0,lz=null,rel=false,i=0,a=0;
 while(a<=txt.length){let b=txt.indexOf('\\n',a);if(b<0)b=txt.length;const s=txt.slice(a,b);a=b+1;i++;
  const k=s.trim().split(/\\s+/),c=(k[0]||'').toUpperCase();if(c=='G91'){rel=true;continue}if(c=='G90'){rel=false;continue}
  if(c=='G92'){for(const q of k.slice(1))if(q[0]=='E'||q[0]=='e')e=+q.slice(1)||0;continue}
  if((c!='G0'&&c!='G1')||rel)continue;let nx=x,ny=y,nz=z,ex=0,hasE=false;
  for(const q of k.slice(1)){const v=+q.slice(1),L=q[0].toUpperCase();if(isNaN(v))continue;if(L=='X')nx=v;else if(L=='Y')ny=v;else if(L=='Z')nz=v;else if(L=='E'){hasE=true;ex=v-e;e=v}}
  const ext=c=='G1'&&hasE&&ex>0;if(ext&&lz!==nz){lay.push(mv.length/4);lz=nz}
  mv.push(nx,ny,ext?1:0,i);x=nx;y=ny;z=nz}
 txt=null;TP.M=new Float32Array(mv);TP.lay=lay;TP.n=TP.M.length/4;tpn.textContent=''}
 catch(err){tpn.textContent='Toolpath not available ('+err.message+')'}TP.busy=false}
function tpIdx(line){const M=TP.M;let lo=0,hi=TP.n-1,r=-1;while(lo<=hi){const m=(lo+hi)>>1;if(M[m*4+3]<=line){r=m;lo=m+1}else hi=m-1}return r}
function tpDraw(line){const M=TP.M,n=TP.n,lay=TP.lay;if(!M||!n)return;const cur=Math.max(0,tpIdx(line));
 let li=0;while(li<lay.length&&lay[li]<=cur)li++;const ls=li?lay[li-1]:0,le=li<lay.length?lay[li]:n;
 const g=tpv.getContext('2d'),S=2.55,C=280,P=(a,b)=>[C+a*S,C-b*S];g.clearRect(0,0,560,560);
 g.lineWidth=1.2;g.strokeStyle='#59606d';g.setLineDash([6,5]);g.beginPath();g.arc(C,C,105*S,0,7);g.stroke();g.setLineDash([]);g.strokeStyle='#8a93a3';g.beginPath();g.arc(C,C,100*S,0,7);g.stroke();
 function seg(a,b,col,w){g.strokeStyle=col;g.lineWidth=w;g.beginPath();for(let i=Math.max(1,a+1);i<b;i++){if(!M[i*4+2])continue;const[p,q]=P(M[i*4-4],M[i*4-3]),[r,t]=P(M[i*4],M[i*4+1]);g.moveTo(p,q);g.lineTo(r,t)}g.stroke()}
 seg(0,ls,'rgba(120,140,170,.25)',1);seg(cur,le,'rgba(63,182,255,.18)',1.2);seg(ls,cur+1,'#3fd2ff',1.6);
 const[nx,ny]=P(M[cur*4],M[cur*4+1]);g.fillStyle='#ff9f2e';g.beginPath();g.arc(nx,ny,6,0,7);g.fill();g.strokeStyle='#fff';g.lineWidth=2;g.stroke();
 const h=tpz.getContext('2d'),N=Math.max(1,lay.length),bh=420/N;h.clearRect(0,0,150,470);
 for(let i=0;i<lay.length;i++){const yy=450-(i/N)*420;h.fillStyle=i<li-1?'#3fd2ff':i==li-1?'#ff9f2e':'#39404c';h.fillRect(20,yy-bh+(bh>4?2:0),110,Math.max(1,bh-(bh>4?3:0)))}
 h.fillStyle='#8a93a3';h.font='11px sans-serif';h.fillText('top',2,24);h.fillText('bed',2,465);
 tpc.textContent='· Layer '+li+' / '+lay.length+', line '+line.toLocaleString()}
function tpTick(j,lk){const ji=j.ivi||{},us=ji.source=='usb stream'&&!/^(Operational|Cancelled)/.test(j.state);
 if(lk){tpp.style.display='block';tpw.style.display='none';tpc.textContent='';tpn.textContent='Not available for Upload (Wi-Fi) prints: the printer runs the file from its own storage, so the bridge has no line position. Use Upload and Print for a live toolpath.';TP.key=null;TP.M=null;return}
 if(!us){tpp.style.display='none';TP.key=null;TP.M=null;return}
 tpp.style.display='block';tpw.style.display='flex';const key=j.job.file.name+'|'+ji.total;
 if(TP.key!==key&&!TP.busy)tpLoad(key).then(()=>tpDraw(ji.line||0));else if(TP.M&&TP.drawn!==ji.line){tpDraw(ji.line||0);TP.drawn=ji.line}}
tick();setInterval(tick,2000)</script>"""

def status_page(cfg):
    m = {"serial": "all over USB", "wifi": "all over Wi-Fi"}.get(cfg.get("mode"),
         "Upload = Wi-Fi to printer storage · Upload and Print = USB stream")
    fil = [[str(n), int(t)] for n, t in cfg.get("filaments") or DEFAULT_CONFIG["filaments"]]
    return PAGE.replace("__MODE__", html.escape(m)).replace("__FIL__", json.dumps(fil).replace("<", "\\u003c")).replace(
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
            if p == "/api/ivi/filament":
                return self._json(200, bridge.filament.info() if bridge.filament else {"state": "idle"})
            if p == "/api/ivi/job/gcode":
                j = bridge.job
                if not j or not getattr(j, "lines", None):
                    return self._json(404, {"error": "no USB job"})
                b = ("\n".join(j.lines) + "\n").encode()
                self.send_response(200); self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("X-Job-Name", re.sub(r"[^\w.\- ]", "_", j.name or ""))
                self.send_header("Content-Length", str(len(b))); self.end_headers(); return self.wfile.write(b)
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
                                   "temperature": temps, "position": bridge.live_status().get("position"),
                                   "ivi": {"usb": bool(bridge.busy() or (mon and mon.connected)),
                                           "usb_error": mon.error if mon else "serial_monitor off",
                                           "usb_locked": bridge.usb_locked(), "storage_file": bridge.storage_print}})
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
            if p == "/api/ivi/filament":
                try: cmd = json.loads(body or b"{}")
                except ValueError: return self._json(400, {"error": "bad json"})
                if cmd.get("action") in ("yes", "more"):
                    if not bridge.filament: return self._json(409, {"error": "no filament change"})
                    try: bridge.filament.answer(cmd["action"] == "yes")
                    except Exception as e: return self._json(409, {"error": str(e)})
                    return self._json(200, bridge.filament.info())
                if cmd.get("action") == "cancel":
                    if bridge.filament: bridge.filament.cancel()
                    return self._json(200, bridge.filament.info() if bridge.filament else {"state": "idle"})
                try:
                    if cmd.get("action") in ("extrude", "retract"):
                        return self._json(200, bridge.start_jog_extrude(cmd["action"], cmd.get("distance", 0), cmd.get("feed", 0)))
                    return self._json(200, bridge.start_filament(cmd.get("action"), cmd.get("temp", 0)))
                except (ValueError, TypeError) as e: return self._json(400, {"error": str(e)})
                except Exception as e: return self._json(409, {"error": str(e)})
            if p == "/api/ivi/usb":
                try: cmd = json.loads(body or b"{}")
                except ValueError: return self._json(400, {"error": "bad json"})
                if cmd.get("action") == "enable": bridge.unlock_usb()
                elif cmd.get("action") == "disable": bridge.lock_usb(bridge.last_file or "manual")
                else: return self._json(400, {"error": "action must be enable or disable"})
                return self._json(200, {"usb_locked": bridge.usb_locked()})
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
                if (not j or not bridge.busy()) and bridge.usb_locked():
                    return self._json(409, {"error": "USB controls are off while the printer prints from its own storage; "
                                                     "pause/cancel on the touch screen"})
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
            try:
                r = prepare_gcode(path, nozzle=float(cfg.get("nozzle_diameter", 0.3)), header=cfg.get("ivi_header", True),
                                  strip=cfg.get("strip_commands", DEFAULT_STRIP))
                if r["header"]: log(f"added IVI header to {fname}")
                if r["removed"]: log(f"removed {r['removed']} line(s) ({', '.join(cfg.get('strip_commands', DEFAULT_STRIP))}) from {fname}")
            except Exception as e: log(f"G-code preparation skipped for {fname}: {e}")
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
