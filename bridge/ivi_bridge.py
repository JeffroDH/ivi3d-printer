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
import argparse, email.parser, email.policy, glob, json, os, re, shutil, sys, threading, time
import urllib.error, urllib.parse, urllib.request, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = "0.1.0"
DEFAULT_CONFIG = {
    "mode": "wifi",                     # "wifi" or "serial"
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
    "line_timeout_s": 600,              # max wait for 'ok' (long heats send 'busy' meanwhile)
}

def log(*a):
    print(time.strftime("%H:%M:%S"), *a, file=sys.stderr, flush=True)

def load_config(path=None):
    cfg = dict(DEFAULT_CONFIG)
    path = path or os.environ.get("IVI_BRIDGE_CONFIG") or os.path.expanduser("~/.config/ivi-bridge/config.json")
    if path and os.path.exists(path):
        with open(path) as f:
            cfg.update(json.load(f))
    if os.environ.get("IVI_PRINTER_TOKEN"):
        cfg["printer_token"] = os.environ["IVI_PRINTER_TOKEN"]
    cfg["spool_dir"] = os.path.expanduser(cfg["spool_dir"])
    return cfg

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

def open_serial(cfg):
    import serial  # pyserial; imported lazily so tests run without it
    port = cfg["serial_port"]
    if any(c in port for c in "*?["):
        hits = sorted(glob.glob(port))
        if not hits:
            raise RuntimeError(f"no serial port matches {port} (is USB-C plugged in?)")
        port = hits[0]
    try:
        return serial.Serial(port, cfg["baud"], timeout=1, exclusive=True)
    except Exception as e:
        raise RuntimeError(f"cannot open {port}: {e}. Disconnect IVI 3licer (only one program may own the port).")

class SerialJob:
    """Streams one job. State: Operational -> Starting -> Printing <-> Paused -> Operational/Cancelled/Error."""
    def __init__(self, ser, lines, name="job", firmware_version="", line_timeout=600, clock=time.monotonic):
        self.ser, self.lines, self.name = ser, lines, name
        self.fw = firmware_version
        self.line_timeout, self.clock = line_timeout, clock
        self.sent = 0; self.state = "Starting"; self.error = None
        self.started = None
        self._pause = threading.Event(); self._cancel = threading.Event()
        self._pending = []   # out-of-band commands (pause/resume) sent between lines

    def _write(self, cmd):
        self.ser.write((cmd + "\n").encode())

    def _readline(self):
        return self.ser.readline().decode(errors="replace").strip()

    def _wait(self, predicate, timeout):
        end = self.clock() + timeout
        while self.clock() < end:
            if self._cancel.is_set() and self.state != "Starting":
                return False
            line = self._readline()
            if not line:
                continue
            if line.lower().startswith(("error", "!!")):
                raise RuntimeError(f"printer error: {line}")
            if predicate(line):
                return True
            # 'echo:busy: processing', temps etc. just keep the wait alive
            if "busy" in line:
                end = self.clock() + timeout
        raise TimeoutError("timed out waiting for printer")

    def detect_firmware(self, wait=3):
        if self.fw:
            return self.fw
        end = self.clock() + wait
        while self.clock() < end:
            line = self._readline()
            if "firmware" in line.lower() and parse_version(line):
                self.fw = line; break
        return self.fw

    def run(self):
        try:
            self.detect_firmware()
            self._write("M2411 S2")
            if needs_m1001(self.fw):
                self._write("M1001 L")
            self._wait(lambda l: "pc start work" in l.lower() or "trigger work: ok" in l.lower(), 30)
            self.state, self.started = "Printing", self.clock()
            log(f"job {self.name}: started, {len(self.lines)} lines")
            for cmd in self.lines:
                while self._pause.is_set() and not self._cancel.is_set():
                    time.sleep(0.2)
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
        # No dedicated stop code is verified; turn heaters off and stop sending.
        for c in ("M104 S0", "M140 S0", "M107"):
            self._write(c)

    def pause(self):
        if self.state == "Printing":
            self._pause.set(); self._write("M2410"); self.state = "Paused"

    def resume(self):
        if self.state == "Paused":
            self._write("M2411 S1"); self._pause.clear(); self.state = "Printing"

    def cancel(self):
        self._cancel.set(); self._pause.clear()

    @property
    def progress(self):
        return 100.0 * self.sent / len(self.lines) if self.lines else 0.0

# ------------------------------------------------- OctoPrint emulation ----
class Bridge:
    def __init__(self, cfg, wifi_factory=None, serial_factory=None):
        self.cfg = cfg
        self.wifi_factory = wifi_factory or (lambda: WifiPrinter(cfg["printer_host"], cfg["printer_port"],
                                                                 cfg["printer_token"], cfg["retries"]))
        self.serial_factory = serial_factory or (lambda: open_serial(cfg))
        self.job = None; self.thread = None; self.last_file = None
        self.lock = threading.Lock()

    def busy(self):
        return self.job is not None and self.job.state in ("Starting", "Printing", "Paused")

    def submit(self, path, name, start=True, mode=None):
        mode = mode or self.cfg["mode"]
        self.last_file = name
        if mode == "wifi":
            self.wifi_factory().upload(path, name)
            return f"Uploaded {name} to the printer over Wi-Fi. Start it on the touch screen."
        if not start:
            return f"Stored {name} in the spool folder (serial mode; print=false)."
        with self.lock:
            if self.busy():
                raise RuntimeError("a job is already running")
            with open(path, errors="replace") as f:
                lines = clean_gcode(f.read())
            ser = self.serial_factory()
            self.job = SerialJob(ser, lines, name, self.cfg.get("firmware_version", ""),
                                 self.cfg.get("line_timeout_s", 600))
            def runner(job=self.job):
                try:
                    job.run()
                finally:
                    try: ser.close()
                    except Exception: pass
            self.thread = threading.Thread(target=runner, daemon=True); self.thread.start()
        return f"Printing {name} over USB serial."

    def job_info(self):
        j = self.job
        state = j.state if j else "Operational"
        if j and j.error: state = f"Error: {j.error}"
        elapsed = (time.monotonic() - j.started) if j and j.started else None
        return {"job": {"file": {"name": j.name if j else self.last_file, "origin": "local"}},
                "progress": {"completion": j.progress if j else None, "printTime": elapsed,
                             "printTimeLeft": None, "filepos": j.sent if j else None},
                "state": state}

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
            if key and self.headers.get("X-Api-Key") != key and \
               self.headers.get("Authorization", "") != f"Bearer {key}":
                self._json(403, {"error": "Invalid API key"}); return False
            return True
        def do_GET(self):
            if not self._auth(): return
            p = self.path.split("?")[0]
            if p == "/api/version":
                return self._json(200, {"api": "0.1", "server": "1.9.0", "text": f"OctoPrint (ivi-bridge {VERSION})"})
            if p == "/api/server":
                return self._json(200, {"version": "1.9.0", "safemode": None})
            if p == "/api/job":
                return self._json(200, bridge.job_info())
            if p == "/api/printer":
                st = bridge.job_info()["state"]
                return self._json(200, {"state": {"text": st, "flags": {"operational": True,
                                   "printing": st == "Printing", "paused": st == "Paused", "ready": not bridge.busy()}}})
            if p.startswith("/api/files"):
                return self._json(200, {"files": [], "free": 0})
            self._json(404, {"error": "not found"})
        def do_POST(self):
            if not self._auth(): return
            p = self.path.split("?")[0]
            n = int(self.headers.get("Content-Length", 0)); body = self.rfile.read(n)
            if p in ("/api/files/local", "/api/files/sdcard"):
                return self._upload(body)
            if p == "/api/job":
                try: cmd = json.loads(body or b"{}")
                except ValueError: return self._json(400, {"error": "bad json"})
                j = bridge.job
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

def serve(cfg, bridge=None):
    bridge = bridge or Bridge(cfg)
    srv = ThreadingHTTPServer((cfg["listen_host"], cfg["listen_port"]), make_handler(bridge))
    log(f"ivi-bridge {VERSION} on http://{cfg['listen_host']}:{cfg['listen_port']} mode={cfg['mode']}")
    if cfg["mode"] == "serial":
        log("serial mode: disconnect IVI 3licer first - only one program can own the USB port")
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
        if cfg["mode"] != "wifi":
            raise RuntimeError("bridge service not running; serial mode needs `ivi_bridge.py serve`")
        return Bridge(cfg).submit(path, name)

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config"); ap.add_argument("--mode", choices=["wifi", "serial"])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("serve", help="run the OctoPrint-compatible service")
    s = sub.add_parser("send", help="send a G-code file now"); s.add_argument("file")
    pp = sub.add_parser("postprocess", help="slicer post-processing hook (file path is last arg)")
    pp.add_argument("file")
    w = sub.add_parser("watch", help="send every new .gcode file that appears in DIR (for Anycubic Next exports)")
    w.add_argument("dir"); w.add_argument("--interval", type=float, default=3)
    a = ap.parse_args(argv)
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
