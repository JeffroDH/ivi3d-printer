"""Wi-Fi upload names: the printer's kore upload route (printer_http_api.so file_upload) rejects any name whose
second '.'-separated piece isn't exactly gcode/cnc/nc with HTTP 412 'File type error'."""
import json, os, sys, tempfile, threading, unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ivi_bridge as B


def kore_accepts(name):
    """Model of file_upload(): kore_split_string(name, ".", parts, 3) keeps the first two NON-EMPTY pieces
    (strsep, empty pieces skipped); parts[1] must strcmp-equal gcode/cnc/nc. No second piece -> NULL
    strcmp (treated as reject here). Plus the 128-byte strcpy buffer."""
    pieces = [p for p in name.split(".") if p]
    return len(name.encode()) < 128 and len(pieces) >= 2 and pieces[1] in ("gcode", "cnc", "nc")


class KoreModelTests(unittest.TestCase):
    def test_model_matches_documented_cases(self):
        for n in ("cube.gcode", "a.nc", "b.cnc", "cube..gcode"): self.assertTrue(kore_accepts(n), n)
        for n in ("benchy_0.2mm.gcode", "Cube_0.2mm_PLA.gcode", "x.GCODE", "x.g", "noext", "a.gcodex"):
            self.assertFalse(kore_accepts(n), n)


class SafeNameTests(unittest.TestCase):
    CASES = {
        "Cube_0.2mm_PLA.gcode": "Cube_0-2mm_PLA.gcode",
        "benchy_0.2mm.gcode": "benchy_0-2mm.gcode",
        "cube.gcode": "cube.gcode",
        "x.GCODE": "x.gcode",
        "x.g": "x.gcode",
        "part.gco": "part.gcode",
        "My Part (v2).gcode": "My-Part-v2.gcode",
        "a..b.gcode": "a-b.gcode",
        ".hidden.gcode": "hidden.gcode",
        "noext": "noext.gcode",
        "laser job 0.5mm.nc": "laser-job-0-5mm.nc",
        "carve.CNC": "carve.cnc",
        "weird.3mf": "weird-3mf.gcode",
        "../../etc/x.gcode": "x.gcode",
        "C:\\jobs\\b.c.gcode": "b-c.gcode",
        "Ünïcode.gcode": "Unicode.gcode",
        "..gcode": "print.gcode",
        "a.b.c.d.nc": "a-b-c-d.nc",
        'q"uote;x.gcode': "q-uote-x.gcode",
    }
    def test_cases(self):
        for src, want in self.CASES.items():
            got = B.wifi_safe_name(src)
            self.assertEqual(got, want, src)
            self.assertTrue(B.wifi_name_ok(got), got)
            self.assertTrue(kore_accepts(got), got)
            self.assertEqual(got.count("."), 1, got)
    def test_extension_kept(self):
        for ext in ("gcode", "nc", "cnc"):
            self.assertTrue(B.wifi_safe_name(f"a.b.{ext}").endswith("." + ext))
    def test_length_limit_with_suffix(self):
        n = B.wifi_safe_name("x" * 300 + ".1.gcode", "-12")
        self.assertLessEqual(len(n.encode()), B.WIFI_NAME_MAX); self.assertTrue(n.endswith("-12.gcode")); self.assertTrue(kore_accepts(n))
    def test_ok_rejects_what_kore_rejects(self):
        for n in ("Cube_0.2mm_PLA.gcode", "x.GCODE", "x.g", "a b.gcode", "../x.gcode", "", "x" * 120 + ".gcode"):
            self.assertFalse(B.wifi_name_ok(n), n)


class NameMapTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.path = os.path.join(self.d, "sub", "wifi_names.json")
        self.m = B.WifiNameMap(self.path)
    def test_valid_name_unchanged_and_stable(self):
        self.assertEqual(self.m.assign("cube.gcode"), "cube.gcode"); self.assertEqual(self.m.assign("cube.gcode"), "cube.gcode")
    def test_same_original_reuses_name(self):
        a = self.m.assign("Cube_0.2mm.gcode"); b = self.m.assign("Cube_0.2mm.gcode")
        self.assertEqual(a, "Cube_0-2mm.gcode"); self.assertEqual(a, b)
    def test_collision_gets_suffix(self):
        self.assertEqual(self.m.assign("a.b.gcode"), "a-b.gcode")
        self.assertEqual(self.m.assign("a b.gcode"), "a-b-2.gcode")
        self.assertEqual(self.m.assign("a-b.gcode"), "a-b-3.gcode")   # valid, but taken by another original
        self.assertEqual(self.m.assign("a b.gcode"), "a-b-2.gcode")   # stable on re-send
    def test_persisted_and_logged(self):
        self.m.assign("Cube_0.2mm_PLA.gcode")
        with open(self.path) as f: self.assertEqual(json.load(f), {"Cube_0-2mm_PLA.gcode": "Cube_0.2mm_PLA.gcode"})
        self.assertEqual(B.WifiNameMap(self.path).assign("x y.gcode"), "x-y.gcode")
        logged = []; orig = B.log; B.log = lambda *a: logged.append(" ".join(map(str, a)))
        try: B.WifiNameMap(self.path).assign("p.q.gcode")
        finally: B.log = orig
        self.assertTrue(any("'p.q.gcode' -> 'p-q.gcode'" in l for l in logged), logged)
    def test_unwritable_map_falls_back_to_memory(self):
        f = os.path.join(self.d, "file"); open(f, "w").close()
        m = B.WifiNameMap(os.path.join(f, "x.json"))          # parent is a file: cannot save
        self.assertEqual(m.assign("a.b.gcode"), "a-b.gcode"); self.assertEqual(m.assign("a b.gcode"), "a-b-2.gcode")


class KorePrinter(BaseHTTPRequestHandler):
    """Fake printer that applies kore's real name check."""
    names = []
    def log_message(self, *a): pass
    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        ep = self.path.rsplit("/", 1)[-1]
        if ep == "upload":
            fn = body.split(b'filename="', 1)[1].split(b'"', 1)[0].decode()
            KorePrinter.names.append(fn)
            if not kore_accepts(fn):
                self.send_response(412); self.end_headers(); self.wfile.write(b"File type error"); return
            self.send_response(201); self.end_headers(); self.wfile.write(b"Upload successfully"); return
        self.send_response(200); self.end_headers(); self.wfile.write(b"{}")


class BridgeUploadTests(unittest.TestCase):
    def setUp(self):
        KorePrinter.names = []
        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), KorePrinter)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.tmp = tempfile.mkdtemp()
        self.cfg = dict(B.DEFAULT_CONFIG, printer_host="127.0.0.1", printer_port=self.srv.server_port, printer_token="tok",
                        spool_dir=self.tmp, mode="wifi", notify=False, serial_monitor=False,
                        history_file=os.path.join(self.tmp, "h.json"), wifi_names_file=os.path.join(self.tmp, "n.json"))
        self.bridge = B.Bridge(self.cfg)
        self.f = os.path.join(self.tmp, "Cube_0.2mm_PLA.gcode")
        with open(self.f, "w") as fh: fh.write("G28\n")
    def tearDown(self): self.srv.shutdown()
    def test_dotted_name_uploads_sanitized(self):
        msg = self.bridge.submit(self.f, "Cube_0.2mm_PLA.gcode", start=False)
        self.assertEqual(KorePrinter.names, ["Cube_0-2mm_PLA.gcode"])
        self.assertIn("as Cube_0-2mm_PLA.gcode", msg)
        self.assertEqual(self.bridge.storage_print, "Cube_0-2mm_PLA.gcode")
        rec = self.bridge.history.load()[-1]
        self.assertEqual((rec["name"], rec["printer_name"]), ("Cube_0.2mm_PLA.gcode", "Cube_0-2mm_PLA.gcode"))
    def test_plain_name_untouched(self):
        msg = self.bridge.submit(self.f, "cube.gcode", start=False)
        self.assertEqual(KorePrinter.names, ["cube.gcode"]); self.assertNotIn(" as ", msg)
        self.assertNotIn("printer_name", self.bridge.history.load()[-1])
    def test_two_originals_do_not_overwrite(self):
        self.bridge.submit(self.f, "a.b.gcode", start=False); self.bridge.storage_print = None
        self.bridge.submit(self.f, "a b.gcode", start=False)
        self.assertEqual(KorePrinter.names, ["a-b.gcode", "a-b-2.gcode"])
    def test_without_fix_kore_would_412(self):
        w = B.WifiPrinter("127.0.0.1", self.srv.server_port, "tok", sleep=lambda s: None)
        with self.assertRaises(ValueError): w.upload(self.f, "Cube_0.2mm_PLA.gcode")   # refused before sending
        self.assertEqual(KorePrinter.names, [])
        st = B.encode_multipart({}, {"file": ("Cube_0.2mm_PLA.gcode", b"G28\n")})
        import urllib.request, urllib.error
        r = urllib.request.Request(f"http://127.0.0.1:{self.srv.server_port}/api/v1/upload", data=st[0], headers={"Content-Type": st[1]})
        with self.assertRaises(urllib.error.HTTPError) as e: urllib.request.urlopen(r, timeout=5)
        self.assertEqual(e.exception.code, 412)


if __name__ == "__main__": unittest.main()
