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
                        mode="wifi", notify=False, serial_monitor=False)
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
    def test_duplicated_key_header(self):
        self.assertEqual(self.req("/api/version", key="KEY, KEY")[0], 200)
        self.assertEqual(self.req("/api/version", key="bad, KEY")[0], 200)
        for k in ("bad, worse", "", "KEYKEY", "KEY;KEY"):
            with self.assertRaises(urllib.error.HTTPError) as e: self.req("/api/version", key=k)
            self.assertEqual(e.exception.code, 403)
    def test_wifi_upload(self):
        st, js = self.upload("G28\n")
        self.assertEqual(st, 201); self.assertIn("touch screen", js["message"])
        self.assertEqual([c[0] for c in FakePrinter.calls], ["connect", "upload", "disconnect"])
        self.assertNotIn("start_print", [c[0] for c in FakePrinter.calls])
    def test_wifi_upload_gets_ivi_header(self):
        self.upload("; HEADER_BLOCK_START\n; generated by OrcaSlicer\nM73 P0 R5\nG1 X1 E1\n; filament_type = PETG\n")
        body = FakePrinter.calls[1][1]
        self.assertIn(b";Header Start", body); self.assertIn(b";estimated_time(s): 300", body); self.assertIn(b";material_type: PETG", body)
        self.assertIn(b";header_type: 3dp,0.3mm", body)
        FakePrinter.calls = []; self.cfg["ivi_header"] = False; self.upload("G28\n")
        self.assertNotIn(b";Header Start", FakePrinter.calls[1][1])
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

class MonitorSerial:
    """Fake USB port for the status monitor: answers M105/M2007, records everything."""
    def __init__(self, systat=1):
        self.written = []; self.out = []; self.closed = False; self.systat = systat; self.t = 0.0
    def write(self, b):
        for cmd in b.decode().split("\n"):
            cmd = cmd.strip()
            if not cmd: continue
            self.written.append(cmd)
            if cmd == "M105": self.out.append("ok T:%.1f /%.1f B:50.0 /60.0" % (21.0 + self.t, self.t))
            elif cmd == "M2007": self.out += ["Working Status: " + ("WORKING_SCREEN" if self.systat in (2, 5) else "IDLE"),
                                              "job status: %d" % self.systat, "ok"]
            elif cmd == "M114": self.out += ["X:0.00 Y:0.00 Z:237.51 E:0.00 Count A:0 B:0 C:0", "ok"]
            elif cmd.startswith("M104 S"): self.t = float(cmd[6:]); self.out.append("ok")
            else: self.out.append("ok")
    def readline(self):
        return (self.out.pop(0) + "\n").encode() if self.out else b""
    def close(self): self.closed = True

class MonitorTests(unittest.TestCase):
    def mon(self, factory):
        return B.SerialMonitor(dict(B.DEFAULT_CONFIG), factory)
    def test_status_and_commands(self):
        s = MonitorSerial(); m = self.mon(lambda: s)
        self.assertTrue(m.poll_once()); self.assertIn("M2155 S4", s.written)
        self.assertEqual(m.status["temps"]["bed"], {"actual": 50.0, "target": 60.0}); self.assertEqual(m.status["systat"], 1)
        self.assertEqual(m.send("m104  s200"), "M104 S200"); m.poll_once()
        self.assertEqual(m.status["temps"]["tool0"]["target"], 200.0)
    def test_absent_or_busy_port(self):
        def busy(): raise RuntimeError("cannot open /dev/x: [Errno 16] Resource busy. Disconnect IVI 3licer")
        m = self.mon(busy); self.assertFalse(m.poll_once()); self.assertIn("busy", m.error)
        with self.assertRaises(RuntimeError): m.send("M104 S0")
    def test_usb_lost(self):
        s = MonitorSerial(); m = self.mon(lambda: s); m.poll_once()
        def boom(b): raise OSError("serial port closed")
        s.write = boom; self.assertFalse(m.poll_once()); self.assertFalse(m.connected); self.assertIn("USB lost", m.error)
    def test_command_whitelist(self):
        for bad in ("G29", "M104 S400", "G1 X200", "G1 E-500", "G1 X1 X2", "G1 F0", "G1 F9000", "G0 X1", "M106 S300", "M220 S5", "M140 S200", "M104 S200\nG28", "M2411 S2"):
            with self.assertRaises(ValueError): B.check_command(bad)
        self.assertEqual(B.check_command("M221 S95"), "M221 S95")
    def test_upload_mode(self):
        self.assertEqual(B.upload_mode({"mode": "auto"}), "wifi"); self.assertEqual(B.upload_mode({"mode": "wifi"}), "wifi")
        self.assertEqual(B.upload_mode({"mode": "serial"}), "serial")

class MonitorApiTests(OctoPrintApiTests):
    """Bridge with the USB monitor on (fake port) and default mode auto -> uploads go over Wi-Fi."""
    def setUp(self):
        FakePrinter.calls = []; self.printer = start(FakePrinter); self.tmp = tempfile.mkdtemp()
        self.cfg = dict(B.DEFAULT_CONFIG, printer_host="127.0.0.1", printer_port=self.printer.server_port,
                        printer_token="tok123", api_key="KEY", spool_dir=self.tmp, listen_port=0, notify=False)
        self.ms = MonitorSerial(); self.ser = FakeSerial(); self.awake = []
        self.bridge = B.Bridge(self.cfg, serial_factory=lambda: self.ms, awake_factory=self._awake)
        self.srv = B.serve(self.cfg, self.bridge, start_monitor=False)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.srv.server_port}"; self.bridge.monitor.poll_once()
    # inherited tests that need a FakeSerial job port are covered by OctoPrintApiTests
    test_clear_endpoint = test_temps_and_caffeinate = test_serial_print_and_job = test_serial_pause_cancel_via_api = None
    def post(self, path, obj):
        r = urllib.request.Request(self.url + path, data=json.dumps(obj).encode(), headers={"X-Api-Key": "KEY", "Content-Type": "application/json"})
        with urllib.request.urlopen(r, timeout=5) as resp: return resp.status
    def test_auto_print_true_uploads_over_wifi_only(self):
        st, js = self.upload("G28\n", start=True)
        self.assertEqual(st, 201); self.assertIn("touch screen", js["message"])
        self.assertEqual([c[0] for c in FakePrinter.calls], ["connect", "upload", "disconnect"])
        self.assertNotIn("M2411 S2", self.ms.written)
    def test_live_status(self):
        p = self.req("/api/printer")[1]
        self.assertTrue(p["ivi"]["usb"]); self.assertEqual(p["temperature"]["bed"]["target"], 60.0)
        self.assertEqual(self.req("/api/job")[1]["state"], "Operational")
        self.ms.systat = 5; self.bridge.monitor.poll_once()
        j = self.req("/api/job")[1]; self.assertEqual(j["state"], "Paused"); self.assertEqual(j["ivi"]["systat"], 5)
        self.assertTrue(self.req("/api/printer")[1]["state"]["flags"]["paused"])
    def test_octoprint_control_endpoints(self):
        self.assertEqual(self.post("/api/printer/tool", {"command": "target", "targets": {"tool0": 205}}), 204)
        self.post("/api/printer/bed", {"command": "target", "target": 55})
        self.post("/api/printer/command", {"commands": ["M220 S90", "M221 S105"]})
        self.post("/api/printer/printhead", {"command": "feedrate", "factor": 110})
        self.post("/api/printer/tool", {"command": "flowrate", "factor": 98})
        for g in ("M104 S205", "M140 S55", "M220 S90", "M221 S105", "M220 S110", "M221 S98"): self.assertIn(g, self.ms.written)
        with self.assertRaises(urllib.error.HTTPError) as e: self.post("/api/printer/command", {"command": "M502"})
        self.assertEqual(e.exception.code, 400)
    def test_pause_resume_screen_job_over_usb(self):
        self.ms.systat = 2; self.bridge.monitor.poll_once()
        self.post("/api/job", {"command": "pause", "action": "pause"}); self.assertIn("M2410", self.ms.written)
        self.ms.systat = 5; self.bridge.monitor.poll_once()
        self.post("/api/job", {"command": "pause", "action": "toggle"}); self.assertIn("M2411 S1", self.ms.written)
        self.post("/api/job", {"command": "cancel"}); self.assertIn("M2411 S3", self.ms.written)
    def test_no_usb_controls_fail_gracefully(self):
        self.bridge.monitor.release()
        with self.assertRaises(urllib.error.HTTPError) as e: self.post("/api/printer/bed", {"command": "target", "target": 50})
        self.assertEqual(e.exception.code, 409); self.assertFalse(self.req("/api/printer")[1]["ivi"]["usb"])
    def test_allowlist_new_codes(self):
        for c in ("G28", "G90", "G91", "M114", "M701", "M702", "M83", "M82", "G1 X-10 F1500", "G1 Z0.05 F200",
                  "G1 E-100 F1000", "M106 S255", "M107"): self.assertEqual(B.check_command(c), c)
    def test_position_and_jog(self):
        self.assertEqual(self.req("/api/printer")[1]["position"], {"x": 0.0, "y": 0.0, "z": 237.51})
        self.post("/api/printer/command", {"commands": ["G91", "G1 Z-10 F1500", "G90"]})
        i = self.ms.written.index("G91"); self.assertEqual(self.ms.written[i:i + 3], ["G91", "G1 Z-10 F1500", "G90"])
        with self.assertRaises(urllib.error.HTTPError) as e: self.post("/api/printer/command", {"commands": ["G1 Z-500"]})
        self.assertEqual(e.exception.code, 400)
    def test_page_matches_touchscreen_spec(self):
        with urllib.request.urlopen(self.url + "/", timeout=5) as r: page = r.read().decode()
        for s in (">Control<", "Load Filament", "Unload Filament", ">210°C<", ">240°C<", ">270°C<", ">60°C<", ">80°C<", ">100°C<",
                  ">Fan ", "Cooldown", "Extrude", "Retract", ">1000<", ">0.05<", ">1500<", ">3000<", "Home", "Y+", "X/Y",
                  "Z+", "Z-", "'G91'", "'G90'", "/api/ivi/filament", "M107", "Pause", "Resume", "Cancel"):
            self.assertIn(s, page)
    def test_page_has_panels(self):
        with urllib.request.urlopen(self.url + "/", timeout=5) as r: page = r.read().decode()
        for s in ("Toolhead", "Filament", "M220 S", "M221 S", "min-width:1100px"): self.assertIn(s, page)

class HeatingSerial(MonitorSerial):
    """Nozzle warms 60 °C per M105 toward the M104 target."""
    def __init__(self):
        super().__init__(); self.actual = 25.0; self.hold = False
    def write(self, b):
        for cmd in b.decode().split("\n"):
            cmd = cmd.strip()
            if cmd == "M105":
                self.written.append(cmd)
                if not self.hold: self.actual = min(self.t, self.actual + 60) if self.t > self.actual else self.actual
                self.out.append("ok T:%.1f /%.1f B:25.0 /0.0" % (self.actual, self.t))
            elif cmd: MonitorSerial.write(self, (cmd + "\n").encode())

class FilamentTests(unittest.TestCase):
    def setUp(self):
        self.cfg = dict(B.DEFAULT_CONFIG, notify=False, filament_poll_s=0.01)
        self.hs = HeatingSerial(); self.b = B.Bridge(self.cfg, serial_factory=lambda: self.hs); self.b.monitor.poll_once()
    def wait(self, *states):
        for _ in range(500):
            if self.b.filament.state in states: return
            time.sleep(0.01)
        self.fail(self.b.filament.info())
    def moves(self):
        return [c for c in self.hs.written if c[:2] in ("M8", "G1")]
    def test_default_extrude(self): self.assertEqual(B.DEFAULT_CONFIG["filament_load"], "extrude")
    def test_unload(self):
        self.b.start_filament("unload", 240); self.wait("done")
        self.assertIn("M104 S240", self.hs.written); self.assertNotIn("M109", " ".join(self.hs.written))
        self.assertEqual(self.moves(), ["M83", "G1 E10 F300", "G1 E-100 F1500", "M82"]); self.assertEqual(self.hs.written[-1], "M104 S0")
        i = self.hs.written.index("M83"); self.assertGreaterEqual(self.hs.actual, 237)
        self.assertGreater(self.hs.written[:i].count("M105"), 3)   # polled while heating
    def test_load_custom_length(self):
        self.cfg["filament_load_mm"] = 80; self.cfg["filament_retry_mm"] = 15
        self.b.start_filament("load", 215); self.wait("confirm")
        self.assertEqual(self.moves(), ["M83", "G1 E80 F300", "M82"])
        self.assertNotIn("M104 S0", self.hs.written)          # hot while asking
        self.b.filament.answer(False); self.assertEqual(self.b.filament.state, "confirm")
        self.b.filament.answer(False)
        self.assertEqual(self.moves()[3:], ["M83", "G1 E15 F300", "M82"] * 2)
        self.b.filament.answer(True); self.assertEqual(self.b.filament.state, "done")
        self.assertEqual(self.hs.written[-1], "M104 S0")       # off only after "Yes, done"
        with self.assertRaises(RuntimeError): self.b.filament.answer(True)
    def test_cancel_while_heating(self):
        self.hs.hold = True; self.b.start_filament("load", 250); time.sleep(0.05)
        self.assertEqual(self.b.filament.state, "heating"); self.b.filament.cancel(); self.wait("cancelled")
        self.assertEqual(self.moves(), []); self.assertIn("M104 S0", self.hs.written)
    def test_timeout_and_bad_input(self):
        self.hs.hold = True; self.cfg["filament_heat_timeout_s"] = 0.05
        self.b.start_filament("load", 250); self.wait("error"); self.assertIn("did not reach", self.b.filament.error)
        for a, t in (("eat", 200), ("load", 400), ("load", 20)):
            with self.assertRaises(ValueError): self.b.start_filament(a, t)
    def test_no_usb_error(self):
        b = B.Bridge(self.cfg, serial_factory=lambda: (_ for _ in ()).throw(RuntimeError("no port")))
        b.start_filament("load", 210)
        for _ in range(200):
            if b.filament.state == "error": break
            time.sleep(0.01)
        self.assertEqual(b.filament.state, "error")
    def test_m701_option(self):
        self.cfg["filament_load"] = "m701"; self.b.start_filament("unload", 210); self.wait("done")
        self.assertIn("M702", self.hs.written)

class JogExtrudeTests(FilamentTests):
    test_default_extrude = test_unload = test_load_custom_length = test_cancel_while_heating = None
    test_timeout_and_bad_input = test_no_usb_error = test_m701_option = None
    def test_cold_heats_to_235_then_moves_and_stays_hot(self):
        self.b.start_jog_extrude("retract", 10, 200); self.wait("done")
        self.assertIn("M104 S235", self.hs.written); self.assertGreaterEqual(self.hs.actual, 232)
        self.assertEqual(self.moves(), ["M83", "G1 E-10 F200", "M82"]); self.assertNotIn("M104 S0", self.hs.written)
        self.assertIn("235°C", self.b.filament.info()["note"])
    def test_hot_moves_immediately(self):
        self.hs.write(b"M104 S240\n"); self.hs.actual = 239.0; self.b.monitor.poll_once(); n = len([c for c in self.hs.written if c.startswith("M104")])
        info = self.b.start_jog_extrude("extrude", 20, 100); self.assertIn(info["state"], ("moving", "done")); self.wait("done")
        self.assertEqual(len([c for c in self.hs.written if c.startswith("M104")]), n)   # no new M104
        self.assertEqual(self.moves(), ["M83", "G1 E20 F100", "M82"])
    def test_low_target_counts_as_cold(self):
        self.hs.write(b"M104 S150\n"); self.hs.actual = 150.0; self.b.monitor.poll_once()
        self.b.start_jog_extrude("extrude", 10, 100); self.wait("done"); self.assertIn("M104 S235", self.hs.written)
    def test_cancel_restores_previous_target(self):
        self.hs.write(b"M104 S150\n"); self.hs.actual = 30.0; self.hs.hold = True; self.b.monitor.poll_once()
        self.b.start_jog_extrude("extrude", 10, 100); time.sleep(0.05); self.b.filament.cancel(); self.wait("cancelled")
        self.assertEqual(self.hs.written[-1], "M104 S150"); self.assertEqual(self.moves(), [])
    def test_custom_temp_and_limits(self):
        self.cfg["jog_extrude_temp"] = 220; self.b.start_jog_extrude("extrude", 5, 100); self.wait("done")
        self.assertIn("M104 S220", self.hs.written)
        for a, d, f in (("spin", 1, 1), ("extrude", 0, 100), ("extrude", 500, 100), ("extrude", 10, 9000)):
            with self.assertRaises(ValueError): self.b.start_jog_extrude(a, d, f)

class FilamentApiTests(MonitorApiTests):
    test_auto_print_true_uploads_over_wifi_only = test_live_status = test_octoprint_control_endpoints = None
    test_pause_resume_screen_job_over_usb = test_no_usb_controls_fail_gracefully = test_allowlist_new_codes = None
    test_position_and_jog = test_page_matches_touchscreen_spec = test_page_has_panels = None
    test_version_and_key = test_duplicated_key_header = test_wifi_upload = test_status_page_no_key_needed = None
    test_auto_mode_picks_usb_when_present = None
    def test_api_flow_and_page(self):
        self.cfg["filament_poll_s"] = 0.01; self.cfg["filaments"] = [["PLA", 215], ["PETG", 240]]
        self.ms.__class__ = HeatingSerial; self.ms.actual = 25.0; self.ms.hold = False
        self.assertEqual(self.req("/api/ivi/filament")[1]["state"], "idle")
        st, j = self.req("/api/ivi/filament", json.dumps({"action": "load", "temp": 215}).encode())
        self.assertEqual(j["target"], 215)
        for _ in range(300):
            if self.req("/api/ivi/filament")[1]["state"] == "confirm": break
            time.sleep(0.01)
        self.assertEqual(self.req("/api/ivi/filament", json.dumps({"action": "more"}).encode())[1]["state"], "confirm")
        self.assertIn("G1 E20 F300", self.ms.written)
        self.assertEqual(self.req("/api/ivi/filament", json.dumps({"action": "yes"}).encode())[1]["state"], "done")
        with self.assertRaises(urllib.error.HTTPError) as e: self.req("/api/ivi/filament", json.dumps({"action": "load", "temp": 999}).encode())
        self.assertEqual(e.exception.code, 400)
        with urllib.request.urlopen(self.url + "/", timeout=5) as r: page = r.read().decode()
        self.assertIn('[["PLA", 215], ["PETG", 240]]', page); self.assertIn("Heating…", page); self.assertIn("Custom", page)
        st, j = self.req("/api/ivi/filament", json.dumps({"action": "retract", "distance": 10, "feed": 200}).encode())
        self.assertEqual(j["state"], "heating")          # "Yes, done" turned the nozzle off
        self.req("/api/ivi/filament", json.dumps({"action": "cancel"}).encode())
        for _ in range(300):
            if self.req("/api/ivi/filament")[1]["state"] == "cancelled": break
            time.sleep(0.01)
        self.assertEqual(self.req("/api/ivi/filament")[1]["state"], "cancelled")
        for t in ("Retracting…", "Filament coming out of the nozzle?", "Yes, done", "No, extrude more"): self.assertIn(t, page)

if __name__ == "__main__": unittest.main()
