import json, os, sys, tempfile, threading, time, unittest, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import ivi_bridge as B

class FakeSerial:
    """Answers like the IVI3D Marlin: banner, 'PC start work', 'ok' per line, busy while heating."""
    def __init__(self, banner="echo:Firmware V1.3.2-alpha"):
        self.working = "IDLE"; self.paused5 = False
        self.out = [banner]; self.written = []; self.closed = False; self.lock = threading.Lock()
    def write(self, b):
        cmd = b.decode().strip()
        with self.lock:
            self.written.append(cmd)
            if cmd == "M2411 S2":
                self.out += ["Can't start work in current status: 5", "start work failed, err= 200"] if self.paused5 else ["PC start work", "trigger work: ok"]
            elif cmd == "M1001 L": self.out += ["ok"]
            elif cmd.startswith("M109"): self.out += ["echo:busy: processing", "echo:busy: processing", "ok"]
            elif cmd == "M2007": self.out += ["Working Status: " + self.working, "ok"]
            elif cmd == "M2411 S3": self.out += ["PC trigger stop", "trigger stop: ok", "ok"]; self.working = "IDLE"; self.paused5 = False
            elif cmd == "M2410": self.out += ["PC trigger pause", "trigger pause: ok"]
            elif cmd == "M2411 S1": self.out += ["PC trigger resume", "trigger resume: ok"]
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

class FirmwareEventTests(unittest.TestCase):
    def test_locked_rotor_pauses(self):
        s = FakeSerial(); orig = s.write
        def w(b):
            orig(b)
            if b.decode().strip() == "G1 X-49.75 Y-9.38": s.out.insert(0, "warning:DriveX locked rotor")
        s.write = w; notes = []
        j = B.SerialJob(s, ["G1 X-49.75 Y-9.38", "G1 X0 Y0"], line_timeout=2, notify=notes.append)
        t = threading.Thread(target=j.run); t.start()
        for _ in range(300):
            if j.state == "Paused": break
            time.sleep(0.01)
        self.assertEqual(j.state, "Paused"); self.assertIn("M2410", s.written); self.assertIn("locked rotor", notes[0])
        j.cancel(); t.join(5); self.assertEqual(j.state, "Cancelled"); self.assertIn("M2411 S3", s.written)
    def test_kill(self):
        s = FakeSerial(); orig = s.write
        s.write = lambda b: (orig(b), s.out.insert(0, "Printer halted. kill() called!") if b.decode().startswith("G0") else None)
        j = B.SerialJob(s, ["G0 Z10"], line_timeout=2); j.run()
        self.assertEqual(j.state, "Error"); self.assertIn("power-cycle", j.error)
    def test_status5_autoclear(self):
        s = FakeSerial(); s.paused5 = True
        j = B.SerialJob(s, ["G28"], line_timeout=2); j.run()
        self.assertEqual(j.state, "Operational"); self.assertEqual(s.written.count("M2411 S2"), 2); self.assertIn("M2411 S3", s.written)
    def test_status5_no_autoclear(self):
        s = FakeSerial(); s.paused5 = True
        j = B.SerialJob(s, ["G28"], line_timeout=2, auto_clear=False); j.run()
        self.assertEqual(j.state, "Error"); self.assertIn("status 5", j.error)
    def test_stale_pc_job_stopped_on_connect(self):
        s = FakeSerial(); s.working = "WORKING_PC"
        j = B.SerialJob(s, ["G28"], line_timeout=2); j.run()
        self.assertEqual(s.written[4], "M2411 S3"); self.assertEqual(j.state, "Operational")
    def test_screen_job_refused(self):
        s = FakeSerial(); s.working = "WORKING_SCREEN"
        j = B.SerialJob(s, ["G28"], line_timeout=2); j.run()
        self.assertEqual(j.state, "Error"); self.assertNotIn("M2411 S2", s.written)
    def test_screen_pause_and_resume(self):
        s = FakeSerial(); j = B.SerialJob(s, ["G1 X%d" % i for i in range(100000)], line_timeout=2)
        t = threading.Thread(target=j.run); t.start()
        while j.state != "Printing": time.sleep(0.01)
        s.out.append("SC trigger pause")
        for _ in range(300):
            if j.state == "Paused": break
            time.sleep(0.01)
        self.assertEqual(j.state, "Paused"); self.assertIn("touch screen", j.reason)
        s.out.append("trigger resume: ok")
        for _ in range(300):
            if j.state == "Printing": break
            time.sleep(0.01)
        self.assertEqual(j.state, "Printing"); j.cancel(); t.join(5)

class PreludeTests(unittest.TestCase):
    def test_fdm_none(self): self.assertEqual(B.job_prelude({}, "3dp", ["G28"]), [])
    def test_cnc(self): self.assertEqual(B.job_prelude({}, "cnc", ["G0 Z10.00 F400"]), ["G53", "G28", "G54"])
    def test_laser_needs_focus(self):
        with self.assertRaises(RuntimeError): B.job_prelude({}, "laser", ["G1 X-49.75 Y-9.38"])
        self.assertEqual(B.job_prelude({"laser_focus_z": 120}, "laser", ["G1 X1 Y1"]), ["G53", "G28", "G0 Z120.00 F1500", "G54"])
        self.assertEqual(B.job_prelude({}, "laser", ["G0 Z50", "G1 X1 Y1"]), ["G53", "G28", "G54"])
        self.assertEqual(B.job_prelude({"home_before_job": False}, "laser", ["G1 X1 Y1"]), ["G53", "G54"])
    def test_header_type(self):
        self.assertEqual(B.header_type(";Header Start\n;header_type: laser\n"), "laser"); self.assertEqual(B.header_type("G28"), "3dp")

class StatusTests(unittest.TestCase):
    def test_parse(self):
        st = {}
        self.assertTrue(B.parse_status("ok T:20.5 /0.0 B:21.0 /0.0 @:0 B@:0", st))
        self.assertEqual(st["temps"]["bed"], {"actual": 21.0, "target": 0.0})
        self.assertTrue(B.parse_status("Working Status: IDLE", st)); self.assertEqual(st["working"], "IDLE")
        self.assertFalse(B.parse_status("ok", st))
    def test_init_config(self):
        p = os.path.join(tempfile.mkdtemp(), "c", "config.json")
        _, c1 = B.init_config(p); _, c2 = B.init_config(p)
        self.assertEqual(len(c1["api_key"]), 32); self.assertEqual(c1["api_key"], c2["api_key"])
        self.assertEqual(oct(os.stat(p).st_mode & 0o777), "0o600"); self.assertEqual(c1["mode"], "auto")

class TermiosSerialTests(unittest.TestCase):
    def test_pty_roundtrip(self):
        import pty
        m, sl = pty.openpty(); name = os.ttyname(sl)
        s = B.TermiosSerial(name, 115200, timeout=0.5)
        s.write(b"M105\n"); self.assertEqual(os.read(m, 100).strip(), b"M105")
        os.write(m, b"ok T:20 /0\npartial"); self.assertEqual(s.readline(), b"ok T:20 /0\n")
        self.assertEqual(s.readline(), b"")  # incomplete line -> timeout
        with self.assertRaises(OSError): B.TermiosSerial(name)  # exclusive lock
        s.close(); os.close(m); os.close(sl)

class SerialJobTests(unittest.TestCase):
    def test_stream(self):
        s = FakeSerial(); j = B.SerialJob(s, ["G28", "M109 S215", "G1 X1"], line_timeout=2); j.run()
        self.assertEqual(j.state, "Operational"); self.assertEqual(j.sent, 3)
        self.assertEqual(s.written, ["M2005", "M2007", "M105", "M2155 S4"] + ["M2411 S2", "G28", "M109 S215", "G1 X1"])  # no M1001 on 1.3.2
        self.assertEqual(j.progress, 100.0)
    def test_m1001_new_fw(self):
        s = FakeSerial("Firmware V2.4.1"); j = B.SerialJob(s, ["G28"], line_timeout=2); j.run()
        self.assertEqual(s.written[4:6], ["M1001 L", "M2411 S2"])
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
                        printer_token="tok123", api_key="KEY", spool_dir=self.tmp, listen_port=0,
                        mode="wifi", notify=False)
        self.awake = []
        self.ser = FakeSerial()
        self.bridge = B.Bridge(self.cfg, serial_factory=lambda: self.ser, awake_factory=self._awake)
        self.srv = B.serve(self.cfg, self.bridge); threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.srv.server_port}"
    def _awake(self):
        class A:
            terminated = False
            def terminate(s): s.terminated = True
        a = A(); self.awake.append(a); return a
    def tearDown(self): self.srv.shutdown(); self.printer.shutdown()
    def test_clear_endpoint(self):
        self.ser.working = "WORKING_PC"
        st, js = self.req("/api/ivi/clear", b"{}")
        self.assertIn("M2411 S3", self.ser.written); self.assertIn("IDLE", js["message"])
    def test_status_page_no_key_needed(self):
        with urllib.request.urlopen(self.url + "/", timeout=5) as r: page = r.read().decode()
        self.assertIn("IVI Bridge", page); self.assertIn('"KEY"', page)
    def test_auto_mode_picks_usb_when_present(self):
        self.cfg["mode"] = "auto"; port = os.path.join(self.tmp, "tty.usbmodemX"); open(port, "w").close()
        self.cfg["serial_port"] = os.path.join(self.tmp, "tty.usbmodem*")
        self.assertEqual(B.resolve_mode(self.cfg), "serial")
        self.cfg["serial_port"] = os.path.join(self.tmp, "nothing*"); self.assertEqual(B.resolve_mode(self.cfg), "wifi")
    def test_temps_and_caffeinate(self):
        self.cfg["mode"] = "serial"
        orig = self.ser.write
        def w(b):
            orig(b)
            if b.decode().startswith("M109"): self.ser.out.insert(0, " T:214.8 /215.0 B:50.1 /50.0 @:0")
        self.ser.write = w
        self.upload("G28\nM109 S215\n"); self.bridge.thread.join(5)
        t = self.req("/api/printer")[1]["temperature"]
        self.assertEqual(t["tool0"], {"actual": 214.8, "target": 215.0}); self.assertEqual(t["bed"]["actual"], 50.1)
        self.assertEqual(len(self.awake), 1); self.assertTrue(self.awake[0].terminated)
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
        self.assertEqual(self.ser.written, ["M2005", "M2007", "M105", "M2155 S4"] + ["M2411 S2", "G28", "M109 S215", "G1 X1"]); self.assertTrue(self.ser.closed)
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
