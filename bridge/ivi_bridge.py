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
import argparse, bisect, email.parser, fnmatch, html, secrets, select, subprocess, email.policy, glob, json, os, re, shutil, sys, threading, time
import urllib.error, urllib.parse, urllib.request, uuid, base64, collections
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
try:
    import fcntl, termios          # macOS / Linux: raw serial without pyserial
except ImportError:                # Windows: pyserial (installed by install.ps1)
    fcntl = termios = None

def _data_dir():
    """Per-OS folder for jobs, history and timelapse frames."""
    if sys.platform == "darwin": return "~/Library/Application Support/ivi-bridge"
    if sys.platform == "win32":
        return os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local"), "IVI3D Bridge", "data")
    return os.path.join(os.environ.get("XDG_DATA_HOME") or "~/.local/share", "ivi-bridge")

def _cfg_dir():
    if sys.platform == "win32":
        return os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local"), "IVI3D Bridge")
    return "~/.config/ivi-bridge"

def default_serial_pattern(platform=None):
    """Where the IVI3D's USB-C CDC port shows up: macOS /dev/tty.usbmodem*, Linux /dev/ttyACM* (or ttyUSB*
    for USB-UART adapters), Windows COMn (listed via pyserial / the registry). Comma-separated globs allowed."""
    platform = platform or sys.platform
    if platform == "darwin": return "/dev/tty.usbmodem*"
    if platform == "win32": return "COM*"
    return "/dev/ttyACM*,/dev/ttyUSB*"

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
    "strip_commands": [],  # filtering off by default (stall tests cleared M204/M205/M73/G21); set to ["M204","M205","M73","G21"] to re-enable
    "nozzle_diameter": 0.3,             # used in ';header_type: 3dp,<d>mm' if the G-code doesn't say
    "jog_extrude_temp": 235,            # Extrude/Retract on a cold nozzle (<170 °C target or below target) heat to this first
    "notify": True,                     # macOS notifications via osascript
    "caffeinate": True,                 # keep the Mac awake during USB jobs
    "printer_host": "192.168.50.85",
    "printer_port": 8080,
    "printer_token": "",                # kore API token (keep out of git)
    "serial_port": default_serial_pattern(),  # glob(s), comma-separated; macOS tty.usbmodem*, Linux ttyACM*/ttyUSB*, Windows COM*
    "line_numbers": True,               # USB stream: Marlin 'N<n> <cmd>*<checksum>' lines, M110 N0 reset, Resend handling
    "baud": 115200,
    "firmware_version": "",             # override; otherwise read from the serial banner
    "listen_host": "127.0.0.1",
    "listen_port": 5001,
    "api_key": "",                      # key the slicer must send as X-Api-Key ("" = no check)
    "spool_dir": os.path.join(_data_dir(), "jobs"),
    "retries": 3,
    "line_timeout_s": 600,
    "poll_feedrate": True,              # USB stream: send bare M220 every feedrate_poll_s and scale time left by 100/FR
    "feedrate_poll_s": 45,
    "report_interval_s": 4,             # M2155 S<n>: printer pushes temps/position/status every n s
    "home_before_job": True,            # laser/CNC: G53, G28, ..., G54 before M2411 S2 (IVI 3licer behaviour)
    "laser_focus_z": None,              # machine Z (mm) to drop to before a laser job; required if homing
    "auto_clear_stale_job": True,       # on "Can't start work in current status: 5" send M2411 S3 and retry once              # max wait for 'ok' (long heats send 'busy' meanwhile)
    # --- Fluidd/Mainsail-style extras (all optional) ---
    "ntfy_url": "",                     # phone push: e.g. "https://ntfy.sh/my-secret-topic" ("" = off)
    "webcam_stream_url": "",            # MJPEG stream of an IP camera, shown as-is on the Device page
    "webcam_snapshot_url": "",          # JPEG snapshot URL (IP camera); used for the snapshot view + timelapse
    "webcam_usb_device": "",            # local USB camera via ffmpeg/avfoundation, e.g. "0" ("" = off)
    "timelapse": False,                 # snapshot per layer during USB (Upload and Print) jobs
    "timelapse_dir": os.path.join(_data_dir(), "timelapse"),
    "timelapse_fps": 15,
    "history_file": os.path.join(_data_dir(), "history.json"),
    "macros_file": os.path.join(_cfg_dir(), "macros.json"),
    "backup_dir": os.path.join(_cfg_dir(), "backups"),
    "temp_history_s": 1800,             # temperature graph window
}

def log(*a):
    print(time.strftime("%H:%M:%S"), *a, file=sys.stderr, flush=True)

def config_path(path=None):
    return path or os.environ.get("IVI_BRIDGE_CONFIG") or os.path.expanduser(os.path.join(_cfg_dir(), "config.json"))

def load_config(path=None):
    cfg = dict(DEFAULT_CONFIG)
    path = config_path(path)
    if path and os.path.exists(path):
        with open(path) as f:
            cfg.update(json.load(f))
    if os.environ.get("IVI_PRINTER_TOKEN"):
        cfg["printer_token"] = os.environ["IVI_PRINTER_TOKEN"]
    for k in ("spool_dir", "timelapse_dir", "history_file", "macros_file", "backup_dir"):
        cfg[k] = os.path.expanduser(cfg[k])
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
    url = (cfg.get("ntfy_url") or "").strip()
    if url.startswith(("https://", "http://")):
        def push():
            try:
                req = urllib.request.Request(url, data=msg.encode(), headers={"Title": title})
                urllib.request.urlopen(req, timeout=10).close()
            except Exception as e: log("ntfy failed:", e)
        threading.Thread(target=push, daemon=True).start()

def list_serial_ports():
    """Serial ports the OS reports (Windows: pyserial, else HKLM\\HARDWARE\\DEVICEMAP\\SERIALCOMM)."""
    try:
        from serial.tools import list_ports
        return sorted(p.device for p in list_ports.comports())
    except Exception: pass
    if sys.platform == "win32":
        try:
            import winreg
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM"); out, i = [], 0
            while True:
                try: out.append(winreg.EnumValue(k, i)[1]); i += 1
                except OSError: break
            return sorted(out)
        except OSError: return []
    return []

def find_usb_port(pattern, exists=os.path.exists, globber=glob.glob, ports=None, platform=None):
    """First port matching pattern: a path/COM name, a glob, or several comma-separated ('auto' = OS default)."""
    platform = platform or sys.platform
    pattern = (pattern or "auto").strip()
    if pattern.lower() == "auto": pattern = default_serial_pattern(platform)
    for pat in [p.strip() for p in pattern.split(",") if p.strip()]:
        if re.fullmatch(r"(?i)com[\d*?\[\]-]+", pat) or (platform == "win32" and not any(c in pat for c in "/\\:")):
            avail = list_serial_ports() if ports is None else ports
            hits = sorted((p for p in avail if fnmatch.fnmatch(p.upper(), pat.upper())),
                          key=lambda p: (len(p), p))      # COM3 before COM10
            if hits: return hits[0]
            continue
        if not any(c in pat for c in "*?["):
            if exists(pat): return pat
            continue
        hits = sorted(globber(pat))
        if hits: return hits[0]
    return None

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

DEFAULT_STRIP = ()  # no stripping by default; stall tests cleared these:
LEGACY_STRIP = ("M204", "M205", "M73", "G21")  # the old list, for re-enabling

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

class PySerialPort:
    """Windows (or anywhere termios is missing): pyserial with the same write/readline/close API."""
    def __init__(self, port, baud=115200, timeout=1.0):
        try: import serial
        except ImportError: raise RuntimeError("pyserial is needed on this OS (pip install pyserial)")
        kw = {"exclusive": True} if os.name != "nt" else {}
        self.s = serial.Serial(port, baud, timeout=timeout, write_timeout=timeout, **kw)
        self.s.reset_input_buffer(); self.s.reset_output_buffer()
    def write(self, data): self.s.write(data)
    def readline(self): return self.s.readline()
    def close(self):
        if self.s is not None: self.s.close(); self.s = None

def open_serial(cfg):
    port = find_usb_port(cfg["serial_port"])
    if not port:
        raise RuntimeError(f"no serial port matches {cfg['serial_port']} (is USB-C plugged in?)")
    try:
        return (TermiosSerial if termios else PySerialPort)(port, cfg["baud"])
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

_M73_ANY_RE = re.compile(r"^M73\b(?=.*\bR(\d+(?:\.\d+)?))?(?=.*\bP(\d+(?:\.\d+)?))?", re.I)
_FR_RE = re.compile(r"\bFR:\s*(\d+(?:\.\d+)?)\s*%", re.I)

def parse_m73(cmd):
    """'M73 P12 R34' -> (12.0, 34.0) (percent, minutes left); missing fields None; not M73 -> None."""
    m = _M73_ANY_RE.match(cmd.split(";", 1)[0].strip())
    if not m: return None
    r, p = m.groups()
    return (float(p) if p is not None else None, float(r) if r is not None else None)

def parse_feedrate(line):
    """Marlin M220 reply 'FR:100%' (also inside 'echo:FR:120%') -> 120.0, else None."""
    m = _FR_RE.search(line)
    return float(m.group(1)) if m else None

def estimate_left(m73_left_s, m73_age_s, feedrate, seg_left):
    """Time left (s), source. M73 R baseline minus time since that M73, scaled by 100/FR;
    falls back to the segment estimate (lines-per-second) when the file has no M73 R."""
    fr = feedrate if feedrate and feedrate > 0 else 100.0
    if m73_left_s is not None:
        return max(0.0, m73_left_s - (m73_age_s or 0.0)) * 100.0 / fr, "slicer M73" + ("" if fr == 100.0 else " @%g%%" % fr)
    if seg_left is not None:
        return seg_left, "line rate"
    return None, None

class SerialJob:
    """Streams one job. States: Starting -> Printing <-> Paused -> Operational | Cancelled | Error."""
    def __init__(self, ser, lines, name="job", firmware_version="", line_timeout=600, clock=time.monotonic,
                 prelude=(), report_interval=4, auto_clear=True, notify=None, line_numbers=False,
                 poll_feedrate=False, feedrate_poll_s=45):
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
        self.on_line = None; self.on_layer = None      # console log / timelapse hooks
        self.poll_feedrate, self.feedrate_poll_s = poll_feedrate, feedrate_poll_s
        self.feedrate = None; self._m73 = None; self._last_fr_poll = None   # _m73 = (seconds left, clock)
        self._boff = None; self._sent_t = None   # byte-offset prefix (lazy), clock of the last ack

    def _write(self, cmd):
        self.ser.write((cmd + "\n").encode())

    def _readline(self):
        line = self.ser.readline().decode(errors="replace").strip()
        if line:
            fr = parse_feedrate(line)
            if fr is not None: self.feedrate = fr
            st = parse_status(line, self.status)
            if self.on_line and not st and not (line == "ok" or line.startswith("ok ") or "busy" in line):
                try: self.on_line(line)
                except Exception: pass
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
            lset = set(layer_starts(self.lines)) if self.on_layer else (); fired = set()
            while i < len(self.lines):
                while self._pause.is_set() and not self._cancel.is_set():
                    self._readline()          # keep watching for resume / kill while paused
                if self._cancel.is_set():
                    break
                cmd = self.lines[i]
                if i in lset and i not in fired:
                    fired.add(i)
                    try: self.on_layer(len(fired))
                    except Exception as e: log("layer hook:", e)
                self._resend = None
                self._write(checksum_line(i + 1, cmd) if self.line_numbers else cmd)
                if self._wait(lambda l: l == "ok" or l.startswith("ok "), self.line_timeout) is False:
                    break
                if self._resend is not None and self.line_numbers:
                    resends += 1
                    if resends > 50: raise RuntimeError("too many resend requests (line noise?)")
                    i = max(0, self._resend - 1); self.sent = i; self._sent_t = self.clock(); continue
                pm = parse_m73(cmd) if cmd[:3].upper() == "M73" else None
                if pm and pm[1] is not None: self._m73 = (pm[1] * 60.0, self.clock())
                i += 1; self.sent = i; self._sent_t = self.clock()
                self._maybe_poll_feedrate()
            if self._cancel.is_set():
                self._stop_printer(); self.state = "Cancelled"
            else:
                self.state = "Operational"
            log(f"job {self.name}: {self.state} ({self.sent}/{len(self.lines)})")
        except Exception as e:
            self.error, self.state = str(e), "Error"
            log(f"job {self.name}: ERROR {e}")

    def _maybe_poll_feedrate(self):
        """Bare M220 between stream lines every feedrate_poll_s; a missing reply is tolerated (short wait)."""
        if not self.poll_feedrate: return
        now = self.clock()
        if self._last_fr_poll is None: self._last_fr_poll = now; return
        if now - self._last_fr_poll < self.feedrate_poll_s: return
        self._last_fr_poll = now
        self._write("M220")
        try: self._wait(lambda l: l == "ok" or l.startswith("ok "), 3)
        except (TimeoutError, RuntimeError): pass

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
        seg = el * (len(self.lines) - self.sent) / self.sent if el and self.sent else None
        m73 = self._m73
        left, src = estimate_left(m73[0] if m73 else None, (self.clock() - m73[1]) if m73 else None, self.feedrate, seg)
        if self._layers is None: self._layers = layer_starts(self.lines)
        layer = bisect.bisect_right(self._layers, self.sent - 1) if self.sent else 0
        return {"source": "usb stream", "sent": self.sent, "total": len(self.lines), "elapsed": el, "left": left,
                "left_source": src, "feedrate": self.feedrate,
                "line": self.sent, "byte": self.byte_pos(), "layer": layer, "layers": len(self._layers),
                "gcode": "/api/ivi/job/gcode", "pos": "/api/ivi/job/pos"}

    def byte_pos(self, line=None):
        """Byte offset in the /api/ivi/job/gcode text of the start of 0-based line `line` (default: the
        next unsent line), i.e. the bytes fully acknowledged by the printer."""
        if self._boff is None:
            off, acc = [0], 0
            for l in self.lines: acc += len(l.encode()) + 1; off.append(acc)
            self._boff = off
        n = self.sent if line is None else line
        return self._boff[max(0, min(n, len(self._boff) - 1))]

    def pos(self):
        """Lightweight live position for the toolpath animation (no printer traffic: what the stream knows)."""
        age = (self.clock() - self._sent_t) if self._sent_t is not None else None
        return {"active": True, "name": self.name, "state": self.state, "line": self.sent, "total": len(self.lines),
                "byte": self.byte_pos(), "feedrate": self.feedrate, "age": age}

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
ALLOWED_CMD = re.compile(r"^(M503|M115|M119|M104 S\d{1,3}|M140 S\d{1,3}|M220 S\d{1,3}|M221 S\d{1,3}|M105|M2007|M2410|M2411 S[13]"
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
        self.thread = None; self.last_cmd = None; self.on_line = None

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
                    elif self.on_line and line != "ok" and not line.startswith("ok "): self.on_line(line)
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

    def query(self, cmd, seconds=3.0, until_ok=True):
        """Send one allowed command and collect its reply lines (e.g. M503) until 'ok' or timeout."""
        c = check_command(cmd); out = []
        with self.lock:
            if not self.ser: raise RuntimeError(f"USB not connected: {self.error or 'no port'}")
            self.ser.write((c + "\n").encode()); self.last_cmd = c
            end = self.clock() + seconds
            while self.clock() < end:
                line = self.ser.readline().decode(errors="replace").strip()
                if not line: continue
                if parse_status(line, self.status) and not line.startswith(("echo:", "M")): continue
                if until_ok and (line == "ok" or line.startswith("ok ")):
                    if out: break
                    continue
                out.append(line)
        log("monitor: query", c, f"-> {len(out)} line(s)"); return out

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

# ------------------------------------------- Fluidd/Mainsail-style extras ---
_THUMB_RE = re.compile(r"^;\s*thumbnail(?:_(PNG|JPG|QOI))?\s+begin\s+(\d+)x(\d+)", re.I)
_FIL_MM_RE = re.compile(r"^;\s*(?:total\s+)?filament used \[mm\]\s*=\s*([\d.]+)", re.I)
_FIL_G_RE = re.compile(r"^;\s*(?:total\s+)?filament used \[g\]\s*=\s*([\d.]+)", re.I)
_EST_RE = re.compile(r"^;\s*(?:estimated printing time \(normal mode\)|model printing time)\s*=\s*(.+)$", re.I)
_IVI_EST_RE = re.compile(r"^;\s*estimated_time\(s\):\s*(\d+)", re.I)

def _head_tail(path, head=2 << 20, tail=128 << 10):
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        a = f.read(head)
        if size <= head: return a.decode(errors="replace"), ""
        f.seek(max(head, size - tail)); return a.decode(errors="replace"), f.read().decode(errors="replace")

def gcode_thumbnail(path):
    """Largest Orca/Prusa embedded thumbnail ('; thumbnail begin WxH LEN' base64 block) -> (mime, bytes) or None."""
    head, _ = _head_tail(path)
    best, cur, buf = None, None, []
    for line in head.splitlines():
        m = _THUMB_RE.match(line.strip())
        if m: cur = ((m.group(1) or "PNG").upper(), int(m.group(2)) * int(m.group(3))); buf = []; continue
        if cur:
            t = line.strip()
            if re.match(r"^;\s*thumbnail(?:_\w+)?\s+end", t, re.I):
                if cur[0] != "QOI" and (not best or cur[1] > best[1]): best = (cur[0], cur[1], "".join(buf))
                cur = None
            else: buf.append(t.lstrip(";").strip())
    if not best: return None
    try: data = base64.b64decode(best[2])
    except Exception: return None
    return ("image/jpeg" if best[0] == "JPG" else "image/png"), data

def gcode_stats(path):
    """Slicer estimate (s) and filament used from Orca's comments (top config block or end of file)."""
    head, tail = _head_tail(path)
    st = {"time_s": None, "filament_mm": None, "filament_g": None, "thumbnail": False}
    for line in (head + "\n" + tail).splitlines():
        l = line.strip()
        if not l.startswith(";"): continue
        if _THUMB_RE.match(l): st["thumbnail"] = True
        m = _EST_RE.match(l)
        if m and st["time_s"] is None: st["time_s"] = parse_duration(m.group(1))
        m = _IVI_EST_RE.match(l)
        if m and st["time_s"] is None: st["time_s"] = int(m.group(1))
        m = _FIL_MM_RE.match(l)
        if m and st["filament_mm"] is None: st["filament_mm"] = float(m.group(1))
        m = _FIL_G_RE.match(l)
        if m and st["filament_g"] is None: st["filament_g"] = float(m.group(1))
    return st

def safe_job_path(cfg, name):
    """Spool file by bare name only (no paths), must exist and be G-code."""
    name = str(name or "")
    if not name or name != os.path.basename(name) or name.startswith(".") or not name.lower().endswith((".gcode", ".gco", ".g")):
        raise ValueError("bad file name")
    p = os.path.join(cfg["spool_dir"], name)
    if not os.path.isfile(p): raise FileNotFoundError(name)
    return p

def list_jobs(cfg):
    d = cfg["spool_dir"]; out = []
    if not os.path.isdir(d): return out
    for n in os.listdir(d):
        p = os.path.join(d, n)
        if n.startswith(".") or not n.lower().endswith((".gcode", ".gco", ".g")) or not os.path.isfile(p): continue
        try: st = gcode_stats(p)
        except OSError: continue
        out.append(dict(st, name=n, size=os.path.getsize(p), mtime=os.path.getmtime(p)))
    return sorted(out, key=lambda f: -f["mtime"])

class History:
    """Print history in a small JSON file (newest last, capped)."""
    def __init__(self, path, cap=500):
        self.path, self.cap, self.lock = path, cap, threading.Lock()
    def load(self):
        try:
            with open(self.path) as f: return json.load(f)
        except (OSError, ValueError): return []
    def add(self, rec):
        with self.lock:
            h = self.load(); h.append(rec); h = h[-self.cap:]
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            tmp = self.path + ".tmp"
            with open(tmp, "w") as f: json.dump(h, f, indent=1)
            os.replace(tmp, self.path)
    def clear(self):
        with self.lock:
            try: os.remove(self.path)
            except OSError: pass
    def summary(self):
        h = self.load(); done = [r for r in h if r.get("state") == "Finished"]
        return {"jobs": h[::-1], "totals": {"count": len(h), "finished": len(done),
                "print_time_s": round(sum(r.get("duration_s") or 0 for r in h)),
                "filament_g": round(sum(r.get("filament_g") or 0 for r in done), 2),
                "filament_mm": round(sum(r.get("filament_mm") or 0 for r in done), 1)}}

DEFAULT_MACROS = [
    {"name": "Preheat PLA", "commands": ["M104 S210", "M140 S60"]},
    {"name": "Preheat PETG", "commands": ["M104 S240", "M140 S80"]},
    {"name": "Cooldown", "commands": ["M104 S0", "M140 S0", "M107"]},
    {"name": "Park (home)", "commands": ["G28"]},
    {"name": "Load filament", "commands": ["@load"]},
    {"name": "Unload filament", "commands": ["@unload"]},
    {"name": "Settings backup (M503)", "commands": ["@backup"]},
]
# Commands that are safe to send while a USB stream runs (reports + the live tuning the page already offers).
STREAM_SAFE = re.compile(r"^(M105|M2007|M114|M115|M104 S\d+|M140 S\d+|M106( S\d+)?|M107|M220 S\d+|M221 S\d+)$")

def check_macro_line(c):
    c = " ".join(str(c).strip().split())
    if c.startswith("@"):
        w = c.split()
        if w[0] in ("@load", "@unload") and len(w) <= 2: return c
        if c == "@backup": return c
        raise ValueError(f"unknown macro directive {c!r} (use @load [name|°C], @unload [name|°C], @backup)")
    return check_command(c)

def validate_macros(ms):
    if not isinstance(ms, list) or len(ms) > 50: raise ValueError("macros must be a list (max 50)")
    out = []
    for m in ms:
        name = str((m or {}).get("name", "")).strip()[:40]
        cmds = (m or {}).get("commands")
        if isinstance(cmds, str): cmds = [x for x in re.split(r"[\n;]+", cmds) if x.strip()]
        if not name or not cmds or len(cmds) > 40: raise ValueError(f"macro {name or '?'}: needs a name and 1-40 commands")
        out.append({"name": name, "commands": [check_macro_line(c) for c in cmds]})
    if len({m["name"] for m in out}) != len(out): raise ValueError("macro names must be unique")
    return out

def find_ffmpeg():
    return shutil.which("ffmpeg") or next((p for p in ("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg")
                                           if os.path.exists(p)), None)

class Webcam:
    def __init__(self, cfg, fetch=None, run=None):
        self.cfg = cfg; self.fetch = fetch or self._fetch; self.run = run or subprocess.run
    def info(self):
        c = self.cfg; usb = bool(str(c.get("webcam_usb_device", "")).strip())
        snap = bool(c.get("webcam_snapshot_url")) or (usb and bool(find_ffmpeg()))
        return {"enabled": bool(c.get("webcam_stream_url") or snap), "stream": bool(c.get("webcam_stream_url")),
                "snapshot": snap, "source": "ip" if c.get("webcam_snapshot_url") or c.get("webcam_stream_url") else ("usb" if usb else None),
                "usb_without_ffmpeg": usb and not find_ffmpeg(), "timelapse": bool(c.get("timelapse")),
                "ffmpeg": bool(find_ffmpeg())}
    def _fetch(self, url):
        with urllib.request.urlopen(url, timeout=10) as r: return r.read(8 << 20)
    def snapshot(self):
        """JPEG bytes from the snapshot URL, else one frame from the USB camera via ffmpeg."""
        url = self.cfg.get("webcam_snapshot_url")
        if url: return self.fetch(url)
        dev = str(self.cfg.get("webcam_usb_device", "")).strip(); ff = find_ffmpeg()
        if dev and ff:
            fmt = {"darwin": "avfoundation", "win32": "dshow"}.get(sys.platform, "v4l2")
            r = self.run([ff, "-loglevel", "error", "-f", fmt, "-framerate", "30", "-i", dev, "-frames:v", "1",
                          "-f", "image2", "-vcodec", "mjpeg", "-"], capture_output=True, timeout=15)
            if r.returncode == 0 and r.stdout: return r.stdout
            raise RuntimeError("ffmpeg could not read the USB camera: " + (r.stderr or b"").decode(errors="replace")[-200:])
        raise RuntimeError("no webcam configured")

class Timelapse:
    """One snapshot per layer change of a USB job; assembled to MP4 with ffmpeg at the end (frames kept otherwise)."""
    def __init__(self, cfg, cam, name, run=None):
        self.cfg, self.cam, self.run = cfg, cam, run or subprocess.run
        stem = re.sub(r"[^\w.\-]+", "_", os.path.splitext(name)[0])[:60] or "job"
        self.dir = os.path.join(cfg["timelapse_dir"], time.strftime("%Y%m%d-%H%M%S") + "-" + stem)
        self.frames = 0; self.busy = False; self.video = None; self.error = None
    def layer(self, n):
        if self.busy: return                       # previous snapshot still running: skip this layer
        self.busy = True
        threading.Thread(target=self._grab, daemon=True).start()
    def _grab(self):
        try:
            img = self.cam.snapshot(); os.makedirs(self.dir, exist_ok=True)
            with open(os.path.join(self.dir, "frame_%05d.jpg" % (self.frames + 1)), "wb") as f: f.write(img)
            self.frames += 1
        except Exception as e: self.error = str(e)
        finally: self.busy = False
    def finish(self):
        for _ in range(100):
            if not self.busy: break
            time.sleep(0.1)
        ff = find_ffmpeg()
        if not self.frames: return None
        if not ff: self.error = "ffmpeg not found; frames kept in " + self.dir; return None
        out = self.dir + ".mp4"
        try:
            r = self.run([ff, "-loglevel", "error", "-y", "-framerate", str(int(self.cfg.get("timelapse_fps", 15))),
                          "-i", os.path.join(self.dir, "frame_%05d.jpg"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                          "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", out], capture_output=True, timeout=600)
            if r.returncode == 0 and os.path.exists(out): self.video = out; shutil.rmtree(self.dir, ignore_errors=True)
            else: self.error = "ffmpeg failed: " + (r.stderr or b"").decode(errors="replace")[-200:]
        except Exception as e: self.error = str(e)
        return self.video

def list_timelapses(cfg):
    d = cfg["timelapse_dir"]
    if not os.path.isdir(d): return []
    out = [{"name": n, "size": os.path.getsize(os.path.join(d, n)), "mtime": os.path.getmtime(os.path.join(d, n))}
           for n in os.listdir(d) if n.endswith(".mp4")]
    return sorted(out, key=lambda f: -f["mtime"])

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
        self.console = collections.deque(maxlen=400); self.console_seq = 0; self.clock = time.time
        if self.monitor: self.monitor.on_line = lambda l: self.log_console("<", l)
        self.history = History(cfg.get("history_file") or os.path.join(cfg["spool_dir"], "..", "history.json"))
        self.webcam = Webcam(cfg); self.timelapse = None; self.last_timelapse = None
        self.temps = collections.deque(maxlen=max(10, int(cfg.get("temp_history_s", 1800)) // 2))
        self.queue = []

    # ---- console / safety layer ----
    def log_console(self, d, text):
        self.console_seq += 1
        self.console.append({"seq": self.console_seq, "t": time.time(), "dir": d, "text": str(text)[:500]})

    def guard(self, cmds):
        """Safety layer for console + macros: validate everything first; nothing while the printer prints
        from its own storage; only STREAM_SAFE commands while a USB job streams."""
        cs = [check_macro_line(c) for c in cmds]
        if self.usb_locked(): raise RuntimeError("USB controls are off while the printer prints from its own storage")
        if self.busy():
            bad = [c for c in cs if not STREAM_SAFE.match(c)]
            if bad: raise RuntimeError(f"not allowed while a USB job is streaming: {', '.join(bad)} "
                                       "(only temperature/fan/speed/flow and status reports)")
        return cs

    def console_send(self, cmd):
        c, = self.guard([cmd])
        if c.startswith("@"): raise ValueError("@ directives are for macros")
        self.log_console(">", c)
        if not self.busy() and self.monitor and c in ("M503", "M115", "M119", "M114", "M105", "M2007"):
            for l in self.monitor.query(c, 3.0): self.log_console("<", l)
            return c
        return self.send_command(c)

    # ---- macros ----
    def macros(self):
        try:
            with open(self.cfg["macros_file"]) as f: return validate_macros(json.load(f))
        except (OSError, ValueError, KeyError): return [dict(m) for m in DEFAULT_MACROS]

    def save_macros(self, ms):
        ms = validate_macros(ms); path = self.cfg["macros_file"]
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path + ".tmp", "w") as f: json.dump(ms, f, indent=2)
        os.replace(path + ".tmp", path); return ms

    def _fil_temp(self, arg):
        if arg is None: raise ValueError("choose a filament (the page opens the picker)")
        for n, t in self.cfg.get("filaments") or DEFAULT_CONFIG["filaments"]:
            if str(n).lower() == arg.lower(): return int(t)
        return int(float(arg))

    def run_macro(self, name):
        m = next((m for m in self.macros() if m["name"] == name), None)
        if not m: raise KeyError(f"no macro {name!r}")
        cs = self.guard(m["commands"]); out = []
        for c in cs:
            if c.startswith("@load") or c.startswith("@unload"):
                w = c.split(); self.start_filament(w[0][1:], self._fil_temp(w[1] if len(w) > 1 else None))
                out.append(c)
            elif c == "@backup": out.append("backup: " + os.path.basename(self.backup_settings()))
            else: self.log_console(">", c); out.append(self.send_command(c))
        return out

    def backup_settings(self):
        """M503 -> ~/.config/ivi-bridge/backups/m503-<time>.txt (0600). Idle + USB monitor only."""
        if self.busy(): raise RuntimeError("a USB job is running")
        if self.usb_locked(): raise RuntimeError("USB controls are off while the printer prints from its own storage")
        if not self.monitor: raise RuntimeError("serial_monitor is off")
        self.log_console(">", "M503"); lines = self.monitor.query("M503", 5.0)
        for l in lines: self.log_console("<", l)
        if not lines: raise RuntimeError("printer sent no M503 reply")
        d = self.cfg["backup_dir"]; os.makedirs(d, mode=0o700, exist_ok=True)
        path = os.path.join(d, time.strftime("m503-%Y%m%d-%H%M%S.txt"))
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f: f.write("; IVI3D settings backup (M503) %s\n" % time.strftime("%Y-%m-%d %H:%M:%S") + "\n".join(lines) + "\n")
        return path

    def list_backups(self):
        d = self.cfg["backup_dir"]
        return sorted((n for n in os.listdir(d) if n.endswith(".txt")), reverse=True) if os.path.isdir(d) else []

    # ---- temperature graph ----
    def sample_temps(self):
        t = (self.live_status() or {}).get("temps") or {}
        if not t: return None
        r = {"t": round(time.time(), 1)}
        for k in ("tool0", "bed"):
            if k in t: r[k] = [t[k]["actual"], t[k]["target"]]
        self.temps.append(r); return r

    def _temp_loop(self):
        while True:
            try: self.sample_temps()
            except Exception: pass
            time.sleep(2)

    # ---- files / queue ----
    def print_file(self, name):
        path = safe_job_path(self.cfg, name)
        if self.usb_locked(): raise RuntimeError("USB controls are off while the printer prints from its own storage")
        if self.busy(): raise RuntimeError("a job is already running")
        return self.submit(path, name, start=True, mode="usb")

    def delete_file(self, name):
        path = safe_job_path(self.cfg, name)
        if self.busy() and self.job and self.job.name == name: raise RuntimeError("file is printing")
        os.remove(path); self.queue = [q for q in self.queue if q != name]

    def start_next(self):
        if not self.queue: raise RuntimeError("queue is empty")
        msg = self.print_file(self.queue[0]); self.queue.pop(0); return msg

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
            try:
                st = gcode_stats(path)
                self.history.add({"name": name, "started": time.time(), "ended": None, "duration_s": None,
                                  "state": "Sent to printer (Wi-Fi)", "via": "wifi", "estimate_s": st.get("time_s"),
                                  "filament_mm": st.get("filament_mm"), "filament_g": st.get("filament_g")})
            except Exception as e: log("history:", e)
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
                                 poll_feedrate=self.cfg.get("poll_feedrate", True),
                                 feedrate_poll_s=self.cfg.get("feedrate_poll_s", 45),
                                 line_numbers=self.cfg.get("line_numbers", True))
            self.job.on_line = lambda l: self.log_console("<", l)
            self.timelapse = None
            if self.cfg.get("timelapse") and self.webcam.info()["snapshot"]:
                self.timelapse = Timelapse(self.cfg, self.webcam, name); self.job.on_layer = self.timelapse.layer
            try: stats = gcode_stats(path)
            except OSError: stats = {}
            t0 = time.time()
            awake = self.awake_factory()
            def runner(job=self.job, tl=self.timelapse):
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
                    rec = {"name": job.name, "started": t0, "ended": time.time(), "duration_s": round(time.time() - t0),
                           "state": {"Operational": "Finished"}.get(job.state, job.state), "error": job.error,
                           "via": "usb", "lines": job.sent, "total_lines": len(job.lines),
                           "estimate_s": stats.get("time_s"), "filament_mm": stats.get("filament_mm"),
                           "filament_g": stats.get("filament_g")}
                    if tl:
                        v = tl.finish(); rec["timelapse"] = os.path.basename(v) if v else None
                        self.last_timelapse = {"frames": tl.frames, "video": rec["timelapse"], "error": tl.error}
                    try: self.history.add(rec)
                    except Exception as e: log("history:", e)
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
.flist{display:flex;flex-direction:column;gap:.5em;max-height:420px;overflow:auto}.fi{display:flex;gap:.7em;align-items:center;border:1px solid #e0e8f5;border-radius:8px;padding:.4em}
.fi img,.fi .nt{width:72px;height:72px;object-fit:contain;background:#f4f8fe;border-radius:6px;flex:none}.fi .nt{display:flex;align-items:center;justify-content:center;font-size:11px;color:#89a}
.fi b{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.fa{display:flex;gap:.4em;margin-top:.3em}.fa button,.mb{background:var(--lb);color:var(--t);border-radius:999px;padding:.35em .9em;font-size:13px}
.mlist{display:flex;flex-wrap:wrap;gap:.5em}.mb{font-size:15px;padding:.5em 1em}
.ht{width:100%;border-collapse:collapse;font-size:12px;margin:.4em 0}.ht th{text-align:left;color:#567;font-weight:600;border-bottom:1px solid #d3e0f3}.ht td{padding:.25em .3em;border-bottom:1px solid #eef3fa}.ht .ok{color:#1a8a3a}.ht .bad{color:#c22}
.con{height:260px;overflow:auto;background:#15171c;color:#cfd6e2;font:12px Menlo,monospace;border-radius:8px;padding:.5em}.con .cs{color:#7fc8ff}.con .ce{color:#ff8a7a}
.wtabs{display:none;gap:.5em;margin:.8em 1em 0;max-width:1500px}.wtabs button{background:var(--lb);color:var(--t);border-radius:999px;padding:.5em 1.4em;font-size:16px}.wtabs button.on{background:var(--b);color:#fff}
@media (max-width:560px){.tabs button{font-size:15px;padding:.6em .15em}#tpzw{display:none}}
@media (min-width:1100px){.tabs{display:none}.panels{display:grid;grid-template-columns:1fr 1fr;gap:2em}
.panel{display:block;border:1px solid #d3e0f3;border-radius:10px;padding:1em}
.panels{grid-template-areas:"tool fil" "con files" "cam files";align-items:start}
#p_tool{grid-area:tool}#p_fil{grid-area:fil}#p_con{grid-area:con}#p_cam{grid-area:cam}#p_files{grid-area:files}
.wtabs{display:flex}#p_tp{display:none}body.wtp .panels>.panel{display:none}body.wtp #p_tp{display:block;grid-column:1/-1}}
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
<div class=wtabs><button id=w_main class=on onclick="wtab(0)">Controls</button><button id=w_tp onclick="wtab(1)">Toolpath</button></div>
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
<div class=panel id=p_cam><h3>Webcam</h3>
<div id=camoff class=lbl>No camera configured. Set <code>webcam_stream_url</code>, <code>webcam_snapshot_url</code> or <code>webcam_usb_device</code> in the bridge config (see README).</div>
<img id=camimg alt="webcam" style="display:none;width:100%;max-height:420px;object-fit:contain;background:#15171c;border-radius:8px">
<div class=lbl id=caminfo style="margin-top:.4em"></div>
<div id=tlv class=lbl style="margin-top:.4em"></div>
<h3 style="margin-top:1em">Temperatures <span class=lbl id=tgl></span></h3>
<canvas id=tg width=640 height=220 style="width:100%;background:#fbfdff;border:1px solid #d3e0f3;border-radius:8px"></canvas>
<div class=lbl><span style="color:#e2531f">&#9644; nozzle</span> &nbsp; <span style="color:#1a5cf0">&#9644; bed</span> &nbsp; dashed = target</div>
</div>
<div class=panel id=p_files><h3>Files <span class=lbl>uploaded jobs on this Mac</span></h3>
<div id=flist class=flist></div>
<h3 style="margin-top:1em">Queue</h3><div id=qlist class=lbl>Empty.</div>
<div class=compact style="margin-top:.4em;border:0;padding:0"><button class=u onclick="qact('start_next')">Start next</button><button onclick="qact('clear')">Clear queue</button><span class=lbl>Queued jobs never start on their own: remove the finished part first, then press Start next.</span></div>
<h3 style="margin-top:1em">History</h3><div id=hstat class=lbl></div>
<table class=ht id=htab></table>
<div class=compact style="border:0;padding:0"><button onclick="if(confirm('Clear print history?'))hact()">Clear history</button></div>
</div>
<div class=panel id=p_con><h3>Macros</h3>
<div id=mlist class=mlist></div>
<details style="margin-top:.6em"><summary class=lbl>Edit macros</summary>
<p class=lbl>One macro per line: <code>Name | command; command</code>. Commands must pass the bridge's safety list. Special: <code>@load</code> / <code>@unload</code> (filament picker, or <code>@load PLA</code>), <code>@backup</code> (M503 to a file).</p>
<textarea id=med rows=8 style="width:100%;font:13px Menlo,monospace;border:1px solid #bcd;border-radius:6px;padding:.4em"></textarea>
<div class=compact style="border:0;padding:0"><button onclick="msave()">Save macros</button><button onclick="if(confirm('Restore the default macros?'))mreset()">Restore defaults</button></div></details>
<h3 style="margin-top:1em">Console</h3>
<div id=con class=con></div>
<div style="display:flex;gap:.5em;margin-top:.5em"><input id=cin placeholder="G-code, e.g. M105" style="flex:1;font:14px Menlo,monospace;padding:.45em;border:1px solid #bcd;border-radius:6px" onkeydown="if(event.key=='Enter')csend()"><button id=cbtn class=btn style="min-width:5em" onclick="csend()">Send</button></div>
<div class=lbl id=cnote style="margin-top:.3em">Only commands on the bridge's safety list are sent. During a USB print only temperature, fan, speed, flow and status commands are allowed; during an Upload (Wi-Fi) print the console is off.</div>
</div>
<div class=panel id=p_tp><h3>Live toolpath <span id=tpc style="color:#456;font-size:13px;font-weight:400"></span></h3><div id=tpp>
<div id=tpn style="font-size:13px;color:#789;margin:.3em 0"></div>
<div id=tpw style="display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap"><canvas id=tpv width=560 height=560 style="width:min(560px,100%);background:#15171c;border-radius:8px"></canvas>
<div id=tpzw><div style="font-size:12px;color:#456">Z height</div><canvas id=tpz width=150 height=470 style="background:#15171c;border-radius:8px"></canvas>
<div style="font-size:12px;color:#456">top view &middot; bright = printed this layer, faint = still to print, dim = earlier layers, orange = nozzle</div></div></div></div></div>
</div>
<p class=note id=msg>Controls need USB. <b>Upload and Print</b> streams the job over USB (live status, Mac must stay awake and connected); <b>Upload</b> stores it on the printer for the touch screen and turns USB controls off during that print. Speed % (M220) and flow % (M221) are not yet verified on this firmware.</p>
<div class=tabs><button id=t_tool class=on onclick="tab('tool')">Toolhead</button><button id=t_fil onclick="tab('fil')">Filament</button><button id=t_cam onclick="tab('cam')">Camera</button><button id=t_files onclick="tab('files')">Files</button><button id=t_con onclick="tab('con')">Console</button><button id=t_tp onclick="tab('tp')">Toolpath</button></div>
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
function tab(t){for(const n of['tool','fil','cam','files','con','tp']){document.getElementById('t_'+n).classList.toggle('on',n==t);document.getElementById('p_'+n).classList.toggle('on',n==t)}}
tab('tool');
function wtab(v){document.body.classList.toggle('wtp',!!v);w_main.classList.toggle('on',!v);w_tp.classList.toggle('on',!!v)}
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
 if(us){jn.textContent=j.job.file.name;js2.textContent=j.state;const c2=j.progress.completion||0;jb.style.width=c2+'%';jpc.textContent=c2.toFixed(1)+'%';jl.textContent=ji.sent+' / '+ji.total;je.textContent=hms(ji.elapsed);jt.textContent=hms(ji.left)+(ji.left_source?' ('+ji.left_source+')':'')}
 const u=p.ivi&&p.ivi.usb&&!lk;usb.textContent=lk?'off (printing from printer storage)':u?(us?'streaming job':'connected'):'not connected'+(p.ivi&&p.ivi.usb_error?' ('+p.ivi.usb_error+')':'');
 document.querySelectorAll('.u,.opts[data-c] button').forEach(b=>b.disabled=!u);
 st.textContent=j.state;fn.textContent=j.job.file.name||'–';const c=j.progress.completion;pb.style.width=(c||0)+'%';pc.textContent=c==null?'':c.toFixed(1)+'%';
 const t=p.temperature||{},f=v=>v?Math.round(v.actual)+'°C/'+Math.round(v.target)+'°C':'–';nzv.textContent=f(t.tool0);bdv.textContent=f(t.bed);
 T.nz=t.tool0?t.tool0.target:0;T.bd=t.bed?t.bed.target:0;
 for(const[g2,v]of[['nz',T.nz],['bd',T.bd]])document.querySelectorAll('[data-g='+g2+'] button:not(.pm)').forEach(b=>b.classList.toggle('sel',parseInt(b.textContent)==v));
 try{tpTick(j,lk)}catch(e){}
 const q=p.position;px.textContent='X: '+(q?q.x.toFixed(2):'–');py.textContent='Y: '+(q?q.y.toFixed(2):'–');pz.textContent='Z: '+(q?q.z.toFixed(2):'–')
}catch(e){st.textContent='bridge offline';document.querySelectorAll('.u').forEach(b=>b.disabled=true)}}
let TP={key:null,M:null,lay:null,n:0,busy:false,line:0,fr:100,ai:0,af:1,last:0,bgk:null,bg:null,run:false};
async function tpLoad(key){TP={key,M:null,lay:null,n:0,busy:true,line:0,fr:100,ai:0,af:1,last:0,bgk:null,bg:null,run:false};tpn.textContent='Loading toolpath…';
 try{const r=await fetch('/api/ivi/job/gcode',{headers:H});if(!r.ok)throw new Error(r.status);let txt=await r.text();
 const mv=[],lay=[],lzs=[];let x=0,y=0,z=0,e=0,f=1800,lz=null,rel=false,i=0,a=0;
 while(a<=txt.length){let b=txt.indexOf('\\n',a);if(b<0)b=txt.length;const s=txt.slice(a,b);a=b+1;i++;
  const k=s.trim().split(/\\s+/),c=(k[0]||'').toUpperCase();if(c=='G91'){rel=true;continue}if(c=='G90'){rel=false;continue}
  if(c=='G92'){for(const q of k.slice(1))if(q[0]=='E'||q[0]=='e')e=+q.slice(1)||0;continue}
  if((c!='G0'&&c!='G1')||rel)continue;let nx=x,ny=y,nz=z,ex=0,hasE=false;
  for(const q of k.slice(1)){const v=+q.slice(1),L=q[0].toUpperCase();if(isNaN(v))continue;if(L=='X')nx=v;else if(L=='Y')ny=v;else if(L=='Z')nz=v;else if(L=='F'&&v>0)f=v;else if(L=='E'){hasE=true;ex=v-e;e=v}}
  const ext=c=='G1'&&hasE&&ex>0;if(ext&&lz!==nz){lay.push(mv.length/5);lzs.push(nz);lz=nz}
  mv.push(nx,ny,ext?1:0,i,f);x=nx;y=ny;z=nz}
 txt=null;TP.M=new Float32Array(mv);TP.lay=lay;TP.lz=lzs;TP.n=TP.M.length/5;tpn.textContent=''}
 catch(err){tpn.textContent='Toolpath not available ('+err.message+')'}TP.busy=false}
// last move whose 1-based G-code line is <= line (lines before `line` are acknowledged by the printer)
function tpIdx(line){const M=TP.M;let lo=0,hi=TP.n-1,r=-1;while(lo<=hi){const m=(lo+hi)>>1;if(M[m*5+3]<=line){r=m;lo=m+1}else hi=m-1}return r}
function tpLayer(i){const lay=TP.lay;let lo=0,hi=lay.length;while(lo<hi){const m=(lo+hi)>>1;if(lay[m]<=i)lo=m+1;else hi=m}return lo}
const tpS=2.55,tpC=280,tpP=(a,b)=>[tpC+a*tpS,tpC-b*tpS];
function tpSeg(g,a,b,col,w){const M=TP.M;g.strokeStyle=col;g.lineWidth=w;g.beginPath();for(let i=Math.max(1,a+1);i<b;i++){if(!M[i*5+2])continue;const[p,q]=tpP(M[i*5-5],M[i*5-4]),[r,t]=tpP(M[i*5],M[i*5+1]);g.moveTo(p,q);g.lineTo(r,t)}g.stroke()}
// static background per layer: bed, earlier layers, faint rest of this layer (cached; redrawn only on layer change)
function tpBg(li){if(TP.bgk===li&&TP.bg)return TP.bg;const n=TP.n,lay=TP.lay,ls=li?lay[li-1]:0,le=li<lay.length?lay[li]:n;
 const c=TP.bg||document.createElement('canvas');c.width=c.height=560;const g=c.getContext('2d');g.clearRect(0,0,560,560);
 g.lineWidth=1.2;g.strokeStyle='#59606d';g.setLineDash([6,5]);g.beginPath();g.arc(tpC,tpC,105*tpS,0,7);g.stroke();g.setLineDash([]);g.strokeStyle='#8a93a3';g.beginPath();g.arc(tpC,tpC,100*tpS,0,7);g.stroke();
 tpSeg(g,0,ls,'rgba(120,140,170,.25)',1);tpSeg(g,ls,le,'rgba(63,182,255,.18)',1.2);TP.bg=c;TP.bgk=li;return c}
// draw printed moves up to move ai, with move ai drawn to fraction af (0..1); nozzle at that point
function tpDraw(ai,af){const M=TP.M,n=TP.n,lay=TP.lay;if(!M||!n)return;ai=Math.max(0,Math.min(n-1,ai));
 const li=tpLayer(ai),ls=li?lay[li-1]:0,g=tpv.getContext('2d');g.clearRect(0,0,560,560);g.drawImage(tpBg(li),0,0);
 tpSeg(g,ls,ai,'#3fd2ff',1.6);let x=M[ai*5],y=M[ai*5+1];
 if(ai>0&&af<1){const x0=M[ai*5-5],y0=M[ai*5-4];x=x0+(x-x0)*af;y=y0+(y-y0)*af}
 if(ai>0&&M[ai*5+2]){const[p,q]=tpP(M[ai*5-5],M[ai*5-4]),[r,t]=tpP(x,y);g.strokeStyle='#3fd2ff';g.lineWidth=1.6;g.beginPath();g.moveTo(p,q);g.lineTo(r,t);g.stroke()}
 const[nx,ny]=tpP(x,y);g.fillStyle='#ff9f2e';g.beginPath();g.arc(nx,ny,6,0,7);g.fill();g.strokeStyle='#fff';g.lineWidth=2;g.stroke();
 if(TP.zli!==li){TP.zli=li;const h=tpz.getContext('2d'),N=Math.max(1,lay.length),bh=420/N;h.clearRect(0,0,150,470);
  for(let i=0;i<lay.length;i++){const yy=450-(i/N)*420;h.fillStyle=i<li-1?'#3fd2ff':i==li-1?'#ff9f2e':'#39404c';h.fillRect(20,yy-bh+(bh>4?2:0),110,Math.max(1,bh-(bh>4?3:0)))}
  h.fillStyle='#8a93a3';h.font='11px sans-serif';h.fillText('top',2,24);h.fillText('bed',2,465)}
 tpc.textContent='· Layer '+li+' / '+lay.length+' · Z '+(li&&TP.lz?TP.lz[li-1].toFixed(2):'0.00')+' mm, line '+TP.line.toLocaleString()}
// one animation step of dt seconds: advance along the path at the move's feedrate (x speed %), never past
// the last acknowledged move; far behind (or the job went backwards) -> catch up faster / snap
function tpStep(dt){const M=TP.M;if(!M||!TP.n)return;const tgt=Math.max(0,tpIdx(TP.line));
 if(TP.ai>tgt||tgt-TP.ai>400||tpLayer(tgt)!=tpLayer(TP.ai)&&tgt-TP.ai>40){TP.ai=tgt;TP.af=1;return}
 let bud=dt*(1+(tgt-TP.ai)/12);
 while(bud>0){if(TP.af>=1){if(TP.ai>=tgt){TP.af=1;return}TP.ai++;TP.af=0}
  const i=TP.ai,L=i?Math.hypot(M[i*5]-M[i*5-5],M[i*5+1]-M[i*5-4]):0,v=Math.max(1,M[i*5+4]*TP.fr/100/60);
  if(L<=1e-6){TP.af=1;continue}const need=(1-TP.af)*L/v;if(need<=bud){bud-=need;TP.af=1}else{TP.af+=bud*v/L;bud=0}}}
function tpFrame(t){if(!TP.run)return;const dt=TP.last?Math.min(.25,(t-TP.last)/1000):0;TP.last=t;
 if(!document.hidden&&TP.M){tpStep(dt);tpDraw(TP.ai,TP.af)}requestAnimationFrame(tpFrame)}
function tpStart(){if(TP.run)return;TP.run=true;TP.last=0;requestAnimationFrame(tpFrame)}
// fast, lightweight position poll (bridge-only, no printer traffic) while a USB print is shown
async function tpPoll(){if(!TP.M||!TP.run||document.hidden)return;try{const d=await J('/api/ivi/job/pos');
 if(!d.active)return;TP.line=d.line||0;if(d.feedrate)TP.fr=d.feedrate}catch(e){}}
function tpTick(j,lk){const ji=j.ivi||{},us=ji.source=='usb stream'&&!/^(Operational|Cancelled)/.test(j.state);
 if(lk||!us){tpw.style.display='none';tpc.textContent='';tpn.textContent=lk?'Not available for Upload (Wi-Fi) prints: the printer runs the file from its own storage, so the bridge has no line position. Use Upload and Print for a live toolpath.':'No USB print running. The toolpath appears here during an Upload and Print job.';TP.key=null;TP.M=null;TP.run=false;return}
 tpn.textContent='';tpw.style.display='flex';const key=j.job.file.name+'|'+ji.total;TP.line=ji.line||0;if(ji.feedrate)TP.fr=ji.feedrate;
 if(TP.key!==key&&!TP.busy)tpLoad(key).then(()=>{TP.line=ji.line||0;TP.ai=Math.max(0,tpIdx(TP.line));TP.af=1;tpStart()});else if(TP.M)tpStart()}
setInterval(tpPoll,350);
const NL=String.fromCharCode(10);let CS=0,CAM=null,MAC=[];
function esc(t){return String(t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
async function J(u,o){const r=await fetch(u,o?{method:'POST',headers:H,body:JSON.stringify(o)}:{headers:H});const j=await r.json().catch(()=>({}));if(!r.ok)throw new Error(j.error||r.status);return j}
async function camInit(){try{CAM=await J('/api/ivi/webcam')}catch(e){return}
 if(!CAM.enabled){camoff.style.display='block';camimg.style.display='none';caminfo.textContent=CAM.usb_without_ffmpeg?'USB camera set, but ffmpeg was not found (brew install ffmpeg).':'';return}
 camoff.style.display='none';camimg.style.display='block';if(CAM.stream)camimg.src=CAM.stream_url;else camSnap();
 caminfo.textContent=(CAM.stream?'Live stream':'Snapshot every 3 s')+' · timelapse '+(CAM.timelapse?(CAM.snapshot?'on (one frame per layer, USB prints)':'needs a snapshot URL or USB camera'):'off')+(CAM.timelapse&&!CAM.ffmpeg?' · no ffmpeg: frames are kept, no video':'')}
function camSnap(){if(CAM&&CAM.enabled&&!CAM.stream)camimg.src='/api/ivi/webcam/snapshot?apikey='+encodeURIComponent(K)+'&t='+Date.now()}
async function tlLoad(){try{const v=(await J('/api/ivi/timelapse')).videos;tlv.innerHTML=v.length?'Timelapses: '+v.slice(0,5).map(x=>'<a target=_blank href="/api/ivi/timelapse/file?name='+encodeURIComponent(x.name)+'&apikey='+encodeURIComponent(K)+'">'+esc(x.name)+'</a>').join(' · '):''}catch(e){}}
async function tgDraw(){let d;try{d=await J('/api/ivi/temps')}catch(e){return}const S=d.samples,c=tg.getContext('2d'),W=640,Hh=220,L=36;c.clearRect(0,0,W,Hh);
 const mx=Math.max(60,...S.flatMap(s=>[s.tool0?Math.max(s.tool0[0],s.tool0[1]):0,s.bed?Math.max(s.bed[0],s.bed[1]):0]))*1.1,now=Date.now()/1000,win=Math.min(d.window_s,Math.max(120,S.length?now-S[0].t:0));
 c.font='11px sans-serif';c.fillStyle='#789';c.strokeStyle='#e3ebf7';c.lineWidth=1;
 for(let v=0;v<=mx;v+=50){const y=Hh-14-(Hh-24)*v/mx;c.beginPath();c.moveTo(L,y);c.lineTo(W,y);c.stroke();c.fillText(v+'°',4,y+4)}
 c.fillText('-'+Math.round(win/60)+' min',L,Hh-2);c.fillText('now',W-24,Hh-2);
 const X=t=>L+(W-L)*(1-(now-t)/win),Y=v=>Hh-14-(Hh-24)*v/mx;
 for(const[k,col]of[['tool0','#e2531f'],['bed','#1a5cf0']])for(const i of[1,0]){c.strokeStyle=col;c.lineWidth=i?1:2;c.setLineDash(i?[5,4]:[]);c.beginPath();let f=1;for(const s of S){if(!s[k])continue;const x=X(s.t),y=Y(s[k][i]);f?c.moveTo(x,y):c.lineTo(x,y);f=0}c.stroke()}
 c.setLineDash([]);const l=S[S.length-1];tgl.textContent=l?('nozzle '+(l.tool0?Math.round(l.tool0[0])+'/'+Math.round(l.tool0[1]):'–')+'°C · bed '+(l.bed?Math.round(l.bed[0])+'/'+Math.round(l.bed[1]):'–')+'°C'):'(no data yet — needs USB)'}
function fmtG(f){return f.filament_g!=null?f.filament_g.toFixed(1)+' g':f.filament_mm!=null?(f.filament_mm/1000).toFixed(2)+' m':'–'}
async function filesLoad(){let d;try{d=await J('/api/ivi/files')}catch(e){return}
 flist.innerHTML=d.files.length?d.files.map(f=>'<div class=fi>'+(f.thumbnail?'<img src="/api/ivi/files/thumb?name='+encodeURIComponent(f.name)+'&apikey='+encodeURIComponent(K)+'">':'<div class=nt>no preview</div>')+'<div style="flex:1;min-width:0"><b>'+esc(f.name)+'</b><div class=lbl>'+hms(f.time_s)+' · '+fmtG(f)+' · '+(f.size/1048576).toFixed(1)+' MB · '+new Date(f.mtime*1000).toLocaleString()+'</div>'
  +'<div class=fa><button class=u data-a=print data-n="'+esc(f.name)+'">Print (USB)</button><button class=u data-a=queue data-n="'+esc(f.name)+'">Queue</button><button data-a=delete data-n="'+esc(f.name)+'">Delete</button></div></div></div>').join(''):'<div class=lbl>No uploaded jobs yet.</div>';
 flist.querySelectorAll('button').forEach(b=>b.onclick=()=>fact(b.dataset.a,b.dataset.n));
 qlist.innerHTML=d.queue.length?d.queue.map((n,i)=>(i+1)+'. '+esc(n)+' <a href=# data-n="'+esc(n)+'">remove</a>').join('<br>'):'Empty.';
 qlist.querySelectorAll('a').forEach(a=>a.onclick=e=>{e.preventDefault();fact('unqueue',a.dataset.n)});uLock()}
async function fact(a,n){if(a=='delete'&&!confirm('Delete '+n+' from this Mac?'))return;if(a=='print'&&!confirm('Print '+n+' now over USB? Make sure the bed is clear.'))return;
 try{const j=await J('/api/ivi/files',{action:a,name:n});say(j.message||(a+': '+n))}catch(e){say('Failed: '+e.message)}filesLoad();tick()}
async function qact(a){if(a=='start_next'&&!confirm('Start the next queued job over USB? Make sure the bed is clear.'))return;try{const j=await J('/api/ivi/queue',{action:a});say(j.message||'Queue cleared')}catch(e){say('Failed: '+e.message)}filesLoad()}
async function histLoad(){let d;try{d=await J('/api/ivi/history')}catch(e){return}const t=d.totals;
 hstat.textContent=t.count+' jobs · '+t.finished+' finished · '+hms(t.print_time_s)+' printing · '+t.filament_g+' g filament';
 htab.innerHTML='<tr><th>Job</th><th>Result</th><th>Time</th><th>Est.</th><th>Filament</th><th>When</th></tr>'+d.jobs.slice(0,30).map(r=>'<tr><td>'+esc(r.name)+'</td><td class="'+(r.state=='Finished'?'ok':r.via=='wifi'?'':'bad')+'">'+esc(r.state)+'</td><td>'+hms(r.duration_s)+'</td><td>'+hms(r.estimate_s)+'</td><td>'+fmtG(r)+'</td><td>'+new Date(r.started*1000).toLocaleString()+'</td></tr>').join('')}
async function hact(){await J('/api/ivi/history',{action:'clear'}).catch(()=>{});histLoad()}
async function mLoad(){try{MAC=(await J('/api/ivi/macros')).macros}catch(e){return}
 mlist.innerHTML=MAC.map((m,i)=>'<button class="mb u" data-i='+i+' title="'+esc(m.commands.join('; '))+'">'+esc(m.name)+'</button>').join('');
 mlist.querySelectorAll('button').forEach(b=>b.onclick=()=>mrun(MAC[+b.dataset.i]));med.value=MAC.map(m=>m.name+' | '+m.commands.join('; ')).join(NL);uLock()}
async function mrun(m){const c0=m.commands[0];if(m.commands.length==1&&(c0=='@load'||c0=='@unload'))return pick(c0.slice(1));
 try{const j=await J('/api/ivi/macros',{action:'run',name:m.name});say('Ran '+m.name+': '+j.ran.join(' · '))}catch(e){say('Failed: '+e.message)}conPoll();tick()}
async function msave(){const ms=med.value.split(NL).filter(l=>l.trim()).map(l=>{const i=l.indexOf('|');return{name:l.slice(0,i).trim(),commands:l.slice(i+1).split(';').map(s=>s.trim()).filter(s=>s)}});
 try{await J('/api/ivi/macros',{action:'save',macros:ms});say('Macros saved')}catch(e){say('Not saved: '+e.message)}mLoad()}
async function mreset(){await J('/api/ivi/macros',{action:'reset'}).catch(()=>{});mLoad()}
async function conPoll(){let d;try{d=await J('/api/ivi/console?since='+CS)}catch(e){return}
 for(const l of d.lines){const e=document.createElement('div');e.className=l.dir=='>'?'cs':'cr';e.textContent=(l.dir=='>'?'> ':'')+l.text;con.appendChild(e)}
 if(d.lines.length){CS=d.seq;while(con.children.length>400)con.removeChild(con.firstChild);con.scrollTop=con.scrollHeight}
 cin.disabled=cbtn.disabled=!d.enabled;cin.placeholder=d.usb_locked?'Console off: printing from printer storage (Upload)':!d.enabled?'Console needs USB':d.streaming?'USB print running: temp/fan/speed/flow/status only':'G-code, e.g. M105'}
async function csend(){const c=cin.value.trim();if(!c)return;try{await J('/api/ivi/console',{command:c});cin.value=''}catch(e){const x=document.createElement('div');x.className='ce';x.textContent='! '+e.message;con.appendChild(x);con.scrollTop=con.scrollHeight}conPoll()}
function uLock(){const u=!usb.textContent.startsWith('off')&&!usb.textContent.startsWith('not');document.querySelectorAll('#p_files .u,#p_con .u').forEach(b=>b.disabled=!u)}
camInit();tlLoad();tgDraw();filesLoad();histLoad();mLoad();conPoll();
setInterval(()=>{camSnap();tgDraw();conPoll()},3000);setInterval(()=>{filesLoad();histLoad();tlLoad()},15000);
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
            q = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query).get("apikey", [])   # <img>/<video> src
            if key and key not in sent and key not in q and \
               self.headers.get("Authorization", "") != f"Bearer {key}":
                self._json(403, {"error": "Invalid API key"}); return False
            return True
        def _bytes(self, code, data, ctype, extra=()):
            self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Cache-Control", "no-store")
            for k, v in extra: self.send_header(k, v)
            self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
        def _q(self, k, d=None):
            return urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query).get(k, [d])[0]
        def _extras_get(self, p):
            if p == "/api/ivi/console":
                since = int(self._q("since", 0) or 0)
                return self._json(200, {"lines": [l for l in bridge.console if l["seq"] > since], "seq": bridge.console_seq,
                                        "enabled": not bridge.usb_locked() and bool(bridge.busy() or (bridge.monitor and bridge.monitor.connected)),
                                        "streaming": bridge.busy(), "usb_locked": bridge.usb_locked()})
            if p == "/api/ivi/macros": return self._json(200, {"macros": bridge.macros()})
            if p == "/api/ivi/temps":
                return self._json(200, {"samples": list(bridge.temps), "window_s": cfg.get("temp_history_s", 1800)})
            if p == "/api/ivi/files":
                return self._json(200, {"files": list_jobs(cfg), "queue": list(bridge.queue)})
            if p == "/api/ivi/files/thumb":
                try: t = gcode_thumbnail(safe_job_path(cfg, self._q("name")))
                except (ValueError, OSError) as e: return self._json(404, {"error": str(e)})
                if not t: return self._json(404, {"error": "no thumbnail"})
                return self._bytes(200, t[1], t[0])
            if p == "/api/ivi/history": return self._json(200, bridge.history.summary())
            if p == "/api/ivi/webcam":
                return self._json(200, dict(bridge.webcam.info(), stream_url=cfg.get("webcam_stream_url") or None,
                                            last_timelapse=bridge.last_timelapse,
                                            recording=bool(bridge.timelapse and bridge.busy()),
                                            frames=bridge.timelapse.frames if bridge.timelapse else 0))
            if p == "/api/ivi/webcam/snapshot":
                try: img = bridge.webcam.snapshot()
                except Exception as e: return self._json(503, {"error": str(e)})
                return self._bytes(200, img, "image/jpeg")
            if p == "/api/ivi/timelapse": return self._json(200, {"videos": list_timelapses(cfg)})
            if p == "/api/ivi/timelapse/file":
                n = self._q("name") or ""
                fp = os.path.join(cfg["timelapse_dir"], n)
                if n != os.path.basename(n) or not n.endswith(".mp4") or not os.path.isfile(fp):
                    return self._json(404, {"error": "not found"})
                with open(fp, "rb") as f: data = f.read()
                return self._bytes(200, data, "video/mp4", [("Content-Disposition", f'inline; filename="{n}"')])
            if p == "/api/ivi/backups": return self._json(200, {"backups": bridge.list_backups(), "dir": "~/.config/ivi-bridge/backups"})
            return False
        def _extras_post(self, p, body):
            if p not in ("/api/ivi/console", "/api/ivi/macros", "/api/ivi/files", "/api/ivi/queue", "/api/ivi/history"): return False
            try: cmd = json.loads(body or b"{}")
            except ValueError: return self._json(400, {"error": "bad json"})
            a = cmd.get("action")
            try:
                if p == "/api/ivi/console":
                    c = bridge.console_send(str(cmd.get("command", ""))); return self._json(200, {"sent": c, "seq": bridge.console_seq})
                if p == "/api/ivi/macros":
                    if a == "run": return self._json(200, {"ran": bridge.run_macro(str(cmd.get("name", "")))})
                    if a == "save": return self._json(200, {"macros": bridge.save_macros(cmd.get("macros"))})
                    if a == "reset":
                        try: os.remove(cfg["macros_file"])
                        except OSError: pass
                        return self._json(200, {"macros": bridge.macros()})
                    return self._json(400, {"error": "action must be run, save or reset"})
                if p == "/api/ivi/files":
                    n = cmd.get("name")
                    if a == "print": return self._json(200, {"message": bridge.print_file(n)})
                    if a == "delete": bridge.delete_file(n); return self._json(200, {"deleted": n})
                    if a == "queue":
                        safe_job_path(cfg, n); bridge.queue.append(n); return self._json(200, {"queue": bridge.queue})
                    if a == "unqueue":
                        if n in bridge.queue: bridge.queue.remove(n)
                        return self._json(200, {"queue": bridge.queue})
                    return self._json(400, {"error": "action must be print, delete, queue or unqueue"})
                if p == "/api/ivi/queue":
                    if a == "start_next": return self._json(200, {"message": bridge.start_next(), "queue": bridge.queue})
                    if a == "clear": bridge.queue = []; return self._json(200, {"queue": []})
                    return self._json(400, {"error": "action must be start_next or clear"})
                if p == "/api/ivi/history":
                    if a == "clear": bridge.history.clear(); return self._json(200, bridge.history.summary())
                    return self._json(400, {"error": "action must be clear"})
            except FileNotFoundError as e: return self._json(404, {"error": f"no such file: {e}"})
            except (ValueError, TypeError, KeyError) as e: return self._json(400, {"error": str(e).strip('"')})
            except Exception as e: return self._json(409, {"error": str(e)})
        def do_GET(self):
            p = self.path.split("?")[0]
            if p not in ("/", "/index.html") and not self._auth(): return
            if p.startswith("/api/ivi/") and self._extras_get(p) is not False: return
            if p == "/api/ivi/filament":
                return self._json(200, bridge.filament.info() if bridge.filament else {"state": "idle"})
            if p == "/api/ivi/job/pos":
                j = bridge.job
                if not j or not getattr(j, "lines", None) or not hasattr(j, "pos"):
                    return self._json(200, {"active": False})
                return self._json(200, j.pos())
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
            if self._extras_post(p, body) is not False: return
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

def lan_ip(probe="192.168.1.1"):
    """This Mac's LAN address (UDP connect only picks a route; nothing is sent)."""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try: s.connect((probe, 9)); return s.getsockname()[0]
    except OSError: return None
    finally: s.close()

def serve(cfg, bridge=None, start_monitor=True):
    bridge = bridge or Bridge(cfg)
    handler = make_handler(bridge)
    try:
        srv = ThreadingHTTPServer((cfg["listen_host"], cfg["listen_port"]), handler)
    except OSError as e:
        # macOS AirPlay Receiver (ControlCenter) holds *:5000 (hence the 5001 default). Binding 0.0.0.0 on 5000 then fails, but specific
        # addresses still work: serve on 127.0.0.1 (Orca) + the LAN address (OctoApp) instead.
        if e.errno not in (48, 98) or cfg["listen_host"] not in ("0.0.0.0", ""): raise
        srv = ThreadingHTTPServer(("127.0.0.1", cfg["listen_port"]), handler)
        ip = lan_ip(cfg.get("printer_host") or "192.168.1.1")
        log(f"port {cfg['listen_port']} is taken on all addresses (AirPlay Receiver?); serving on 127.0.0.1 and {ip or 'no LAN address'}")
        if ip and not ip.startswith("127."):
            try:
                extra = ThreadingHTTPServer((ip, cfg["listen_port"]), handler)
                threading.Thread(target=extra.serve_forever, daemon=True).start(); srv.extra = extra
            except OSError as e2: log(f"LAN listener on {ip} failed: {e2}")
    log(f"ivi-bridge {VERSION} on http://{cfg['listen_host']}:{cfg['listen_port']} uploads={upload_mode(cfg)}")
    if bridge.monitor:
        log("USB monitor on: status/controls use the USB port when it is free (IVI 3licer must be disconnected)")
        if start_monitor: bridge.monitor.start()
    if start_monitor: threading.Thread(target=bridge._temp_loop, daemon=True).start()
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
