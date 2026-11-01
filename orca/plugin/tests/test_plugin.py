"""Tests the plugin against a stub 'orca' module and a fake bridge HTTP server (no Orca, no printer)."""
import enum, http.server, importlib.util, json, os, sys, tempfile, threading, types, unittest, py_compile

HERE = os.path.dirname(os.path.abspath(__file__)); PLUGIN = os.path.join(os.path.dirname(HERE), "ivi3d_bridge_plugin.py")

def make_orca():
    orca = types.ModuleType("orca")
    class Result:
        def __init__(s, status, message=""): s.status, s.message = status, message
    class ER:
        success = staticmethod(lambda message="", data="": Result("Success", message))
        skipped = staticmethod(lambda message="": Result("Skipped", message))
        failure = staticmethod(lambda status, message, data="": Result(status, message))
    orca.ExecutionResult = ER
    orca.PluginResult = types.SimpleNamespace(RecoverableError="RecoverableError", FatalError="FatalError")
    class Base:
        _cfg = "{}"
        def get_config(self): return self._cfg
        def post_message(self, d): self.sent.append(d)
        def __init__(self): self.sent = []
    Step = enum.Enum("Step", "posSlice psGCodePostProcess")
    orca.slicing = types.SimpleNamespace(SlicingPipelineCapabilityBase=Base, Step=Step)
    orca.pages = types.SimpleNamespace(PagesPluginCapabilityBase=Base)
    orca.base = object
    orca.registered, orca.perms = [], {}
    orca.plugin = lambda cls: (cls().register_capabilities(), cls)[1]
    orca.register_capability = orca.registered.append
    orca.request_permissions = lambda **kw: orca.perms.update(kw)
    return orca

orca = make_orca(); sys.modules["orca"] = orca
spec = importlib.util.spec_from_file_location("plug", PLUGIN); P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE))); import ivi_fdm_header as REF

class Fake(http.server.BaseHTTPRequestHandler):
    state = "Printing"; calls = []
    def log_message(self, *a): pass
    def _j(self, code, o):
        b = json.dumps(o).encode(); self.send_response(code); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.headers.get("X-Api-Key") != "K": return self._j(403, {"error": "Invalid API key"})
        if self.path == "/api/job": return self._j(200, {"state": Fake.state, "job": {"file": {"name": "cube.gcode"}}, "progress": {"completion": 42.0}})
        if self.path == "/api/printer": return self._j(200, {"temperature": {"tool0": {"actual": 210.0, "target": 210.0}}})
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}"); Fake.calls.append((self.path, body))
        if self.path == "/api/ivi/clear": return self._j(200, {"message": "sent M2411 S3; printer reports IDLE"})
        if body.get("command") == "cancel" and Fake.state == "Operational": return self._j(409, {"error": "no active job"})
        return self._j(200, {"state": "Paused" if body.get("action") == "pause" else "Printing"})

class PluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Fake); threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.srv.server_port}"
    @classmethod
    def tearDownClass(cls): cls.srv.shutdown()
    def page(self, key="K", url=None):
        p = P.BridgePage(); p._cfg = json.dumps({"bridge_url": url or self.url, "api_key": key}); return p

    def test_compiles_and_registers(self):
        py_compile.compile(PLUGIN, doraise=True)
        self.assertEqual([c.__name__ for c in orca.registered], ["IviHeader", "BridgePage"])
        self.assertTrue(all("127.0.0.1" in u for u in orca.perms["network_http"]))
        self.assertEqual(orca.perms["network_socket"], ["('127.0.0.1', 5000)"])
        src = open(PLUGIN).read(); self.assertTrue(src.startswith("# /// script")); self.assertIn("[tool.orcaslicer.plugin]", src)
        self.assertEqual(src.count("@orca.plugin"), 1)

    def test_header_matches_reference_and_toggle(self):
        g = "; filament_type = PLA\nG1 X-1 Y2 Z0.3 E1\nG1 X3 Y-4 E2\n; estimated printing time (normal mode) = 2m 5s\n"
        f = tempfile.NamedTemporaryFile("w", suffix=".gcode", delete=False); f.write(g); f.close()
        ctx = types.SimpleNamespace(step=orca.slicing.Step.psGCodePostProcess, gcode_path=f.name)
        h = P.IviHeader(); self.assertEqual(h.execute(ctx).status, "Success")
        out = open(f.name).read()
        strip = lambda t: "\n".join(l for l in t.split("\n") if not l.startswith(";Mon") and not re.match(r";\w{3} \w{3} \d", l))
        import re
        self.assertEqual(strip(out), strip(REF.build(g)))
        h.execute(ctx); self.assertEqual(open(f.name).read(), out)       # idempotent
        g2 = tempfile.NamedTemporaryFile("w", suffix=".gcode", delete=False); g2.write(g); g2.close()
        h._cfg = '{"enabled": false}'
        self.assertEqual(h.execute(types.SimpleNamespace(step=ctx.step, gcode_path=g2.name)).message, "IVI header disabled in settings")
        self.assertEqual(open(g2.name).read(), g)
        self.assertEqual(h.execute(types.SimpleNamespace(step=orca.slicing.Step.posSlice, gcode_path="")).status, "Success")

    def test_status_and_alerts(self):
        Fake.state = "Printing"; p = self.page(); p.on_message({"type": "poll"}); d = p.sent[-1]
        self.assertTrue(d["online"]); self.assertEqual(d["progress"], 42.0); self.assertEqual(d["temps"]["tool0"]["actual"], 210.0)
        Fake.state = "Paused: Drive X locked rotor (motor stalled)"; p.on_message({"type": "poll"}); self.assertIn("stalled", p.sent[-1]["alert"])
        Fake.state = "Error: printer halted (kill) - power-cycle"; p.on_message({"type": "poll"}); self.assertIn("Power-cycle", p.sent[-1]["alert"])
        Fake.state = "Error: printer refused to start (status 5: PAUSE_FINISH (paused))"; p.on_message({"type": "poll"})
        self.assertIn("Clear stuck job", p.sent[-1]["alert"])

    def test_bad_key_and_offline(self):
        p = self.page(key="bad"); p.on_message({"type": "poll"}); self.assertIn("API key", p.sent[-1]["error"])
        p = self.page(url="http://127.0.0.1:1"); p.on_message({"type": "poll"}); d = p.sent[-1]
        self.assertFalse(d["online"]); self.assertIn("not running", d["error"])

    def test_commands(self):
        Fake.state = "Printing"; p = self.page()
        for a in ("pause", "resume", "cancel", "clear"): p.on_message({"type": "command", "action": a})
        self.assertEqual([c[0] for c in Fake.calls[-4:]], ["/api/job"] * 3 + ["/api/ivi/clear"])
        self.assertEqual(Fake.calls[-4][1], {"command": "pause", "action": "pause"})
        self.assertIn("IDLE", p.sent[-1]["message"])
        Fake.state = "Operational"; p.on_message({"type": "command", "action": "cancel"})
        self.assertFalse(p.sent[-1]["ok"]); self.assertIn("409", p.sent[-1]["message"])
        p.on_message({"type": "command", "action": "explode"}); self.assertFalse(p.sent[-1]["ok"])

    def test_ui(self):
        p = self.page(); ui = p.get_ui(); self.assertIn("orca.postMessage", ui); self.assertIn("3000", ui); self.assertNotIn("__POLL_MS__", ui)

if __name__ == "__main__": unittest.main()
