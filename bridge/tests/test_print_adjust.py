"""0.1.19 parity with the on-printer bridge: allow-list, motion lock, Status / Adjust data, fan record,
upload pre-scan, and the M503 mesh readout. Fake ports only; nothing touches real hardware."""
import json, os, sys, tempfile, threading, unittest, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import ivi_bridge as B
from test_bridge import FakeSerial, FakePrinter, MonitorSerial, start

M503 = ["echo:  M665 L357.50 R160.39 H233.23 S200 X0.24 Y-0.09 Z-0.15", "echo:  M851 Z-14.29", "echo:  M420 S1 Z0.00"] + \
       ["echo:  G29 W I%d J%d Z%.5f" % (i, j, (i - 3) * 0.01 + j * 0.001) for j in range(7) for i in range(7)]

class SettingsSerial(MonitorSerial):
    def write(self, b):
        for cmd in b.decode().split("\n"):
            if cmd.strip() == "M503": self.written.append("M503"); self.out += M503 + ["ok"]; return
        MonitorSerial.write(self, b)

class CommandTests(unittest.TestCase):
    def test_m290_steps(self):
        for ok in ("M290 Z0.01", "M290 Z-0.02", "M290 Z+0.05", "m290 z-0.05"): B.check_command(ok)
        for bad in ("M290 Z0.1", "M290 Z0.03", "M290", "M290 X0.01", "M290 Z0.01 Z0.01"):
            with self.assertRaises(ValueError): B.check_command(bad)
        self.assertEqual(B.parse_m290("M290 Z-0.02"), -2)
    def test_fans_and_limits(self):
        for ok in ("M106 P1 S128", "M107 P0", "M106", "M220", "M104 S0 ; off", "M221 S10"):
            B.check_command(ok)
        self.assertEqual(B.check_command("M104 S0 ; off"), "M104 S0")
        for bad in ("M106 P2 S10", "M106 S256", "M3 S200", "M4 S101", "G29", "M500", "M502", "M997", "M221 S201", "M140 S121", "M2001 S1"):
            with self.assertRaises(ValueError): B.check_command(bad)
    def test_print_safe(self):
        for c in ("M104 S200", "M290 Z0.01", "M107", "M114", "M105"): self.assertTrue(B.print_safe(c))
        for c in ("G28", "G1 X1", "G91", "M83", "M503", "M119"): self.assertFalse(B.print_safe(c))

class TrackTests(unittest.TestCase):
    def test_layers_speed_fan(self):
        t = B.PrintTrack()
        for l in ["G28", "G90", "M82", "G92 E0", "G1 Z0.2 F600", "G1 X1 Y1 E1", "G1 X2 E2", "G1 Z0.6", "G1 X3",
                  "G1 Z0.4", "G1 X4 E3", B.checksum_line(9, "M220 S90"), "N10 M221 S95*0", "M106 P1 S128", "M290 Z+0.02", "M290 Z-0.01"]:
            t.track(l)
        self.assertEqual(t.layer, 2); self.assertAlmostEqual(t.lz, 0.4); self.assertEqual((t.speed, t.flow), (90, 95))
        self.assertEqual(t.fans, [None, 128]); self.assertEqual(t.fan_json(), {"fan": 50, "fans": [None, 50]})
        self.assertEqual(t.babystep_h, 1)
        t.track("M107"); self.assertEqual(t.fan_json()["fan"], 0)
        t.reset(); self.assertEqual((t.layer, t.babystep_h), (0, 0))
    def test_relative_extrusion(self):
        t = B.PrintTrack()
        for l in ("M83", "G1 Z0.2", "G1 X1 E0.5", "G1 X2 E0.5", "G1 Z0.4", "G1 X3 E-1", "G1 X4 E0.3"): t.track(l)
        self.assertEqual(t.layer, 2)

class PrescanTests(unittest.TestCase):
    def scan(self, text):
        f = tempfile.NamedTemporaryFile("w", suffix=".gcode", delete=False); f.write(text); f.close()
        try: return B.prescan_gcode(f.name)
        finally: os.unlink(f.name)
    def test_prescan(self):
        self.assertIsNone(self.scan("G28\n;M2411 S3 in a comment\nM3 S50\nG1 X1\n"))
        for bad in ("M2411 S3\n", "M997\n", "G28\nM3 S200\n", "M110 N0\n", "M2001 S1\n", "N5 M2410*12\n"):
            with self.assertRaises(ValueError): self.scan(bad)
    def test_settings_parse(self):
        st = {}
        for l in M503: B.parse_settings_line(l, st)
        self.assertEqual(len(st["grid"]), 7); self.assertAlmostEqual(st["grid"][2][6], 0.032)
        self.assertTrue(st["enabled"]); self.assertEqual(st["H"], 233.23); self.assertEqual(st["probe_z"], -14.29)

class ApiTests(unittest.TestCase):
    def setUp(self):
        FakePrinter.calls = []; self.printer = start(FakePrinter); self.tmp = tempfile.mkdtemp()
        self.cfg = dict(B.DEFAULT_CONFIG, printer_host="127.0.0.1", printer_port=self.printer.server_port,
                        printer_token="tok123", api_key="KEY", spool_dir=self.tmp, listen_port=0, notify=False)
        self.ms = SettingsSerial()
        self.bridge = B.Bridge(self.cfg, serial_factory=lambda: self.ms, awake_factory=lambda: None)
        self.srv = B.serve(self.cfg, self.bridge, start_monitor=False)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.srv.server_port}"; self.bridge.monitor.poll_once()
    def tearDown(self): self.srv.shutdown(); self.printer.shutdown()
    def req(self, path, obj=None, raw=None, ctype="application/json"):
        data = raw if raw is not None else (json.dumps(obj).encode() if obj is not None else None)
        r = urllib.request.Request(self.url + path, data=data, headers={"X-Api-Key": "KEY", "Content-Type": ctype})
        with urllib.request.urlopen(r, timeout=5) as resp:
            b = resp.read(); return resp.status, (json.loads(b) if b else None)
    def code(self, path, obj):
        with self.assertRaises(urllib.error.HTTPError) as e: self.req(path, obj)
        return e.exception.code, json.loads(e.exception.read() or b"{}").get("error", "")
    def test_idle(self):
        p = self.req("/api/printer")[1]["ivi"]
        self.assertFalse(p["print"]["active"]); self.assertIsNone(p["print"]["source"]); self.assertEqual(p["version"], "0.1.19")
        self.assertEqual(self.req("/api/ivi/console")[1]["reason"], "")
        self.assertEqual(self.req("/api/printer/command", {"commands": ["G91", "G1 Z1", "G90"]})[0], 204)
        self.assertIn("G1 Z1", self.ms.written)
    def test_touchscreen_job_motion_lock(self):
        self.ms.systat = 2; self.bridge.monitor.poll_once()
        pr = self.req("/api/printer")[1]["ivi"]["print"]
        self.assertTrue(pr["active"]); self.assertEqual(pr["source"], "printer"); self.assertTrue(pr["usb_controls"])
        n = len(self.ms.written)
        c, err = self.code("/api/printer/command", {"commands": ["G91", "G1 Z1", "G90"]})
        self.assertEqual(c, 409); self.assertIn("blocked while a print runs", err); self.assertEqual(len(self.ms.written), n)
        self.assertEqual(self.code("/api/ivi/console", {"command": "G28"})[0], 409)
        self.assertEqual(self.code("/api/ivi/filament", {"action": "load", "temp": 210})[0], 409)
        self.assertEqual(self.code("/api/ivi/filament", {"action": "extrude", "distance": 10, "feed": 100})[0], 409)
        self.assertEqual(self.code("/api/ivi/macros", {"action": "run", "name": "Park (home)"})[0], 409)
        self.assertEqual(self.req("/api/ivi/macros", {"action": "run", "name": "Preheat PLA"})[0], 200)
        for cmds in (["M104 S205"], ["M290 Z-0.02"], ["M220 S90"], ["M106 S255"]):
            self.assertEqual(self.req("/api/printer/command", {"commands": cmds})[0], 204)
        pr = self.req("/api/printer")[1]["ivi"]
        self.assertEqual(pr["print"]["speed"], 90); self.assertEqual(pr["print"]["zoffset_h"], -2); self.assertEqual(pr["fan"], 100)
        self.assertEqual(self.req("/api/fan")[1], {"fan": 100, "fans": [100, 100], "on": True})
        self.assertIn("Touchscreen job", self.req("/api/ivi/console")[1]["reason"])
        self.assertEqual(self.req("/api/job", {"command": "pause", "action": "pause"})[0], 200); self.assertIn("M2410", self.ms.written)
        self.assertEqual(self.code("/api/ivi/cal/refresh", {})[0], 409)
    def test_mesh_refresh_and_cal_flows_point_to_printer(self):
        c = self.req("/api/ivi/cal/refresh", {})[1]
        self.assertEqual(len(c["level"]["grid"]), 7); self.assertTrue(c["level"]["enabled"]); self.assertEqual(c["probe_z"], -14.29)
        self.assertEqual(self.req("/api/printer")[1]["ivi"]["cal"]["level"]["grid"][0][0], -0.03)
        self.assertEqual(self.code("/api/ivi/cal/start", {"action": "level", "bed": 60})[0], 501)
    def test_upload_prescan(self):
        body, ct = B.encode_multipart({"print": "false"}, {"file": ("bad.gcode", b"G28\nM997\n")})
        with self.assertRaises(urllib.error.HTTPError) as e: self.req("/api/files/local", raw=body, ctype=ct)
        self.assertEqual(e.exception.code, 400); self.assertEqual(FakePrinter.calls, [])
    def test_page(self):
        r = urllib.request.urlopen(self.url + "/", timeout=5).read().decode()
        for s in ("id=pstat", "id=padj", "Z offset distance (mm)", "id=calmesh", "id=creason", "t_mesh", "function prTick"):
            self.assertIn(s, r)

class StreamLockTests(unittest.TestCase):
    def test_usb_stream_adjust_goes_between_lines(self):
        cfg = dict(B.DEFAULT_CONFIG, serial_monitor=False, notify=False)
        b = B.Bridge(cfg, serial_factory=FakeSerial, awake_factory=lambda: None)
        ser = FakeSerial(); j = B.SerialJob(ser, ["G1 X1"], "t.gcode"); j.state = "Printing"; j.on_write = b.pt.track
        b.job = j
        self.assertEqual(b.print_info()["source"], "usb")
        with self.assertRaises(B.MotionLocked): b.send_command("G28")
        with self.assertRaises(B.MotionLocked): b.console_send("G1 X5")
        self.assertEqual(b.send_command("M221 S96"), "M221 S96"); self.assertIn("M221 S96", ser.written)
        self.assertEqual(b.print_info()["flow"], 96)
        self.assertIn("Print running", b.console_reason())

if __name__ == "__main__": unittest.main()
