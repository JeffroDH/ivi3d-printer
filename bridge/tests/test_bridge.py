import json, os, sys, tempfile, threading, time, unittest, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import ivi_bridge as B

class FakeSerial:
    """Answers like the IVI3D Marlin: banner, 'PC start work', 'ok' per line, busy while heating."""
    def __init__(self, banner="echo:Firmware V1.3.2-alpha"):
        self.out = [banner]; self.written = []; self.closed = False; self.lock = threading.Lock()
    def write(self, b):
        cmd = b.decode().strip()
        with self.lock:
            self.written.append(cmd)
            if cmd == "M2411 S2": self.out += ["PC start work", "trigger work: ok"]
            elif cmd == "M1001 L": self.out += ["ok"]
            elif cmd.startswith("M109"): self.out += ["echo:busy: processing", "echo:busy: processing", "ok"]
            elif cmd in ("M2410", "M2411 S1"): pass
            else: self.out.append("ok")
    def readline(self):
        with self.lock:
            if self.out: return (self.out.pop(0) + "\n").encode()
        time.sleep(0.001); return b""
    def close(self): self.closed = True

class GcodeTests(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(B.clean_gcode("; hi\nG28 ; home\n\n  M104 S215\n"), ["G28", "M104 S215"])
    def test_m1001(self):
        self.assertFalse(B.needs_m1001("Firmware V1.3.2-alpha"))
        self.assertTrue(B.needs_m1001("V2.4.0")); self.assertFalse(B.needs_m1001(""))

class SerialJobTests(unittest.TestCase):
    def test_stream(self):
        s = FakeSerial(); j = B.SerialJob(s, ["G28", "M109 S215", "G1 X1"], line_timeout=2); j.run()
        self.assertEqual(j.state, "Operational"); self.assertEqual(j.sent, 3)
        self.assertEqual(s.written, ["M2411 S2", "G28", "M109 S215", "G1 X1"])  # no M1001 on 1.3.2
        self.assertEqual(j.progress, 100.0)
    def test_m1001_new_fw(self):
        s = FakeSerial("Firmware V2.4.1"); j = B.SerialJob(s, ["G28"], line_timeout=2); j.run()
        self.assertEqual(s.written[:2], ["M2411 S2", "M1001 L"])
    def test_pause_resume_cancel(self):
        s = FakeSerial(); j = B.SerialJob(s, ["G1 X%d" % i for i in range(100000)], line_timeout=2)
        t = threading.Thread(target=j.run); t.start()
        while j.state != "Printing": time.sleep(0.01)
        j.pause(); self.assertEqual(j.state, "Paused"); n = j.sent; time.sleep(0.3)
        self.assertLessEqual(j.sent - n, 1)
        j.resume(); time.sleep(0.05); j.cancel(); t.join(5)
        self.assertEqual(j.state, "Cancelled"); self.assertIn("M2410", s.written); self.assertIn("M2411 S1", s.written)
        self.assertIn("M104 S0", s.written)
    def test_error(self):
        s = FakeSerial(); s.write = lambda b: s.out.append("Error:Printer halted")
        j = B.SerialJob(s, ["G28"], line_timeout=1); j.run(); self.assertEqual(j.state, "Error")

class FakePrinter(BaseHTTPRequestHandler):
    calls = []; fail_first_upload = False
    def log_message(self, *a): pass
    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        ep = self.path.rsplit("/", 1)[-1]; FakePrinter.calls.append((ep, body))
        if ep in ("start_print", "prepare_print"): self.send_response(404); self.end_headers(); return
        if ep == "connect" and b"tok123" not in body: self.send_response(403); self.end_headers(); return
        code = 201 if ep == "upload" else 200
        self.send_response(code); self.end_headers(); self.wfile.write(b'{"msg":"Upload successfully"}' if code == 201 else b"{}")

def start(handler):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start(); return srv

class WifiTests(unittest.TestCase):
    def setUp(self):
        FakePrinter.calls = []; self.srv = start(FakePrinter)
        self.f = tempfile.NamedTemporaryFile("w", suffix=".gcode", delete=False); self.f.write("G28\n"); self.f.close()
    def tearDown(self): self.srv.shutdown()
    def test_upload_sequence(self):
        w = B.WifiPrinter("127.0.0.1", self.srv.server_port, "tok123", sleep=lambda s: None)
        w.upload(self.f.name, "a.gcode")
        self.assertEqual([c[0] for c in FakePrinter.calls], ["connect", "upload", "disconnect"])
        self.assertIn(b'filename="a.gcode"', FakePrinter.calls[1][1]); self.assertIn(b"tok123", FakePrinter.calls[1][1])
    def test_bad_token_no_retry_and_disconnects(self):
        w = B.WifiPrinter("127.0.0.1", self.srv.server_port, "wrong", sleep=lambda s: None)
        with self.assertRaises(RuntimeError): w.upload(self.f.name)
        self.assertEqual([c[0] for c in FakePrinter.calls], ["connect"])
    def test_unreachable_retries(self):
        w = B.WifiPrinter("127.0.0.1", 1, "tok123", retries=2, sleep=lambda s: None)
        with self.assertRaises(RuntimeError): w.upload(self.f.name)
    def test_empty_token(self):
        with self.assertRaises(ValueError): B.WifiPrinter("h", 1, "")

class OctoPrintApiTests(unittest.TestCase):
    def setUp(self):
        FakePrinter.calls = []; self.printer = start(FakePrinter); self.tmp = tempfile.mkdtemp()
        self.cfg = dict(B.DEFAULT_CONFIG, printer_host="127.0.0.1", printer_port=self.printer.server_port,
                        printer_token="tok123", api_key="KEY", spool_dir=self.tmp, listen_port=0)
        self.ser = FakeSerial()
        self.bridge = B.Bridge(self.cfg, serial_factory=lambda: self.ser)
        self.srv = B.serve(self.cfg, self.bridge); threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.srv.server_port}"
    def tearDown(self): self.srv.shutdown(); self.printer.shutdown()
    def req(self, path, data=None, ctype="application/json", key="KEY"):
        r = urllib.request.Request(self.url + path, data=data, headers={"X-Api-Key": key, "Content-Type": ctype})
        with urllib.request.urlopen(r, timeout=5) as resp: return resp.status, json.loads(resp.read())
    def upload(self, text, start=True):
        body, ct = B.encode_multipart({"print": "true" if start else "false", "path": ""}, {"file": ("cube.gcode", text.encode())})
        return self.req("/api/files/local", body, ct)
    def test_version_and_key(self):
        self.assertIn("OctoPrint", self.req("/api/version")[1]["text"])
        with self.assertRaises(urllib.error.HTTPError) as e: self.req("/api/version", key="bad")
        self.assertEqual(e.exception.code, 403)
    def test_wifi_upload(self):
        st, js = self.upload("G28\n")
        self.assertEqual(st, 201); self.assertIn("touch screen", js["message"])
        self.assertEqual([c[0] for c in FakePrinter.calls], ["connect", "upload", "disconnect"])
        self.assertNotIn("start_print", [c[0] for c in FakePrinter.calls])
    def test_serial_print_and_job(self):
        self.cfg["mode"] = "serial"
        st, js = self.upload("; c\nG28\nM109 S215\nG1 X1\n"); self.assertEqual(st, 201)
        self.bridge.thread.join(5)
        job = self.req("/api/job")[1]
        self.assertEqual(job["state"], "Operational"); self.assertEqual(job["progress"]["completion"], 100.0)
        self.assertEqual(self.ser.written, ["M2411 S2", "G28", "M109 S215", "G1 X1"]); self.assertTrue(self.ser.closed)
    def test_serial_pause_cancel_via_api(self):
        self.cfg["mode"] = "serial"
        self.upload("\n".join("G1 X%d" % i for i in range(100000)))
        while self.bridge.job.state != "Printing": time.sleep(0.01)
        self.assertEqual(self.req("/api/job", json.dumps({"command": "pause", "action": "pause"}).encode())[1]["state"], "Paused")
        self.assertEqual(self.req("/api/job", json.dumps({"command": "pause", "action": "resume"}).encode())[1]["state"], "Printing")
        with self.assertRaises(urllib.error.HTTPError) as e: self.upload("G28\n")
        self.assertEqual(e.exception.code, 409)
        self.req("/api/job", json.dumps({"command": "cancel"}).encode()); self.bridge.thread.join(5)
        self.assertEqual(self.bridge.job.state, "Cancelled")

if __name__ == "__main__": unittest.main()
