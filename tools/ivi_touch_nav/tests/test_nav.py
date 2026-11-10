"""Offline tests: synthetic framebuffers (sim.py) + mocked SSH transport. Run: python3 -m unittest -v"""
import io, os, shutil, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)

from ivi_touch import layout as L
from ivi_touch.nav import Navigator, NavAbort
from ivi_touch.runlog import RunLog
from ivi_touch.safety import StaticBridgeState
from ivi_touch.screens import Classifier
from ivi_touch.transport import Device, SSHTransport, TransportError
from ivi_touch.fb import Frame
from sim import Sim
from mock_transport import MockTransport

TARGET = "benchy_0.2mm.gcode"


def files_small():
    return {"cube.gcode": (1700000300, True), TARGET: (1700000200, True), "old.gcode": (1700000100, True),
            "notes.txt": (1700000400, True), "laser.nc": (1700000050, False)}


def files_many():
    d = {"part%02d.gcode" % i: (1700001000 - i * 10, True) for i in range(9)}
    d[TARGET] = (1700000925, True)              # sorts to row 8 of 10 (needs scrolling)
    d["zz_same_time.gcode"] = (1700000925, True)  # tie on mtime -> name order
    return d


CALIB = None


def calibrate_dir():
    """Calibrate from the simulator once, with DIFFERENT dynamic content than the scenarios use."""
    global CALIB
    if CALIB:
        return CALIB
    CALIB = tempfile.mkdtemp(prefix="ivi_calib_")
    clf = Classifier(CALIB)
    s = Sim(files={"calib_a.gcode": (5, True), "calib_b.gcode": (4, True), "calib_c.gcode": (3, False)})
    s.loaded = "calib_a.gcode"
    shots = [("home", "home", None), ("files", "files", None), ("wifi_list", "wifi_list", None),
             ("dialog_print", "dialog_print", "wifi_list"), ("dialog_not_ivi", "dialog_not_ivi", "wifi_list"),
             ("dialog_delete_confirm", "dialog_delete_confirm", "wifi_list"),
             ("dialog_plate", "dialog_plate", "status_ready"),
             ("dialog_stop_confirm", "dialog_stop_confirm", "status_printing"),
             ("status_ready", "status_ready", None), ("status_printing", "status_printing", None),
             ("status_paused", "status_paused", None), ("status_stopped", "status_stopped", None),
             ("status_complete", "status_complete", None), ("homing", "homing", None),
             ("page:control", "page:control", None)]
    for label, st, under in shots:
        s.state = st
        if under:
            s.under_dialog = under
        f = s.render()
        clf.save_reference(label, f)
        if label in ("files", "wifi_list") or label.startswith("page:"):
            clf.save_home_icon(f)
    return CALIB


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ivi_run_")

    def tearDown(self):
        if getattr(self, "log", None):
            self.log.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def make(self, sim, dry=False, bridge=StaticBridgeState(False), probe=True, on_grab=None, **kw):
        if getattr(self, "log", None):
            self.log.close()
        self.sim = sim
        self.t = MockTransport(sim, on_grab=on_grab)
        dev = Device(self.t, dry_run=dry)
        self.log = RunLog(self.tmp, self.id().split(".")[-1], save_png=False, echo=None)
        self.nav = Navigator(dev, Classifier(calibrate_dir()), bridge=bridge, log=self.log, printing_probe=probe,
                             sleep=lambda s: None, **kw)
        return self.nav

    def assert_safe(self):
        for x, y, st in self.sim.taps:
            if st == "wifi_list":
                self.assertLessEqual(x, L.MAX_LIST_TAP_X, "list tap beyond Make column")
        self.assertEqual(self.sim.deleted, [], "Delete was tapped")

    def assert_arrived(self, r):
        self.assertEqual(r.label, "status_ready")
        self.assertEqual(self.sim.state, "status_ready")
        self.assertEqual(self.sim.loaded, TARGET)
        self.assertEqual(self.sim.started, 0, "Start must not be tapped without --start")
        self.assert_safe()


class TestClassifier(Base):
    def test_all_states_identified(self):
        clf = Classifier(calibrate_dir())
        s = Sim(files=files_small()); s.loaded = TARGET; s.extra = " ext"
        cases = {"home": None, "files": None, "wifi_list": None, "dialog_print": "wifi_list",
                 "dialog_not_ivi": "wifi_list", "dialog_plate": "status_ready", "status_ready": None,
                 "status_printing": None, "status_paused": None, "status_stopped": None, "status_complete": None,
                 "dialog_stop_confirm": "status_paused", "page:control": None, "homing": None}
        for st, under in cases.items():
            s.state = st
            if under:
                s.under_dialog = under
            ident = clf.identify(s.render())
            self.assertTrue(ident.confident, "%s -> %r" % (st, ident))
            self.assertEqual(ident.label, st, "%s -> %r" % (st, ident))

    def test_unknowns_not_confident(self):
        clf = Classifier(calibrate_dir())
        s = Sim(files=files_small())
        for st, under in (("page:settings", None), ("garbage", None), ("dialog_lowtemp", "status_printing"),
                          ("page:wifi_setup", None)):
            s.state = st
            if under:
                s.under_dialog = under
            ident = clf.identify(s.render())
            self.assertFalse(ident.confident, "%s wrongly identified as %r" % (st, ident))

    def test_blank(self):
        s = Sim(blanked=True)
        self.assertEqual(Classifier(calibrate_dir()).identify(s.render()).label, "blank")

    def test_uncalibrated_never_taps(self):
        sim = Sim("home", files=files_small())
        t = MockTransport(sim)
        nav = Navigator(Device(t), Classifier(None), bridge=StaticBridgeState(False), sleep=lambda s: None)
        with self.assertRaises(NavAbort):
            nav.goto_print(TARGET)
        self.assertEqual(sim.taps, [])

    def test_sort_order(self):
        order = L.list_filter_sort([(t, n) for n, (t, _) in files_many().items()])
        self.assertEqual(order.index(TARGET), 8)          # part00..07 are newer; tie with zz_ -> name order
        self.assertLess(order.index(TARGET), order.index("zz_same_time.gcode"))
        self.assertNotIn("notes.txt", L.list_filter_sort([(1, "notes.txt"), (2, ".x.gcode"), (3, "a.NC")]))


class TestScenarios(Base):
    # ---- the 7 required starting points -----------------------------------------------------------------
    def test_1_from_home(self):
        self.assert_arrived(self.make(Sim("home", files=files_small())).goto_print(TARGET))

    def test_2_from_files(self):
        nav = self.make(Sim("files", files=files_small()))
        self.assert_arrived(nav.goto_print(TARGET))
        self.assertNotIn("home", [st for _, _, st in self.sim.taps], "should continue from Files, not go Home")

    def test_3_from_wifi_list_with_scroll(self):
        sim = Sim("wifi_list", files=files_many())
        nav = self.make(sim)
        self.assert_arrived(nav.goto_print(TARGET))
        self.assertTrue(any(st.endswith(":drag") for _, _, st in sim.taps), "expected a scroll drag")
        self.assertFalse(any(st in ("home", "files") for _, _, st in sim.taps))

    def test_3b_wifi_list_already_scrolled_past(self):
        sim = Sim("wifi_list", files=files_many()); sim.content_y = 10 * 128 - 360
        self.assert_arrived(self.make(sim).goto_print(TARGET))

    def test_4_inside_dialog_wrong_file(self):
        sim = Sim("dialog_print", files=files_small()); sim.loaded = "cube.gcode"; sim.under_dialog = "wifi_list"
        self.assert_arrived(self.make(sim).goto_print(TARGET))
        self.assertEqual(sim.taps[0], (215, 345, "dialog_print"))   # first tap: Cancel (no wake tap on dialogs)

    def test_4b_inside_delete_confirm(self):
        sim = Sim("dialog_delete_confirm", files=files_small()); sim.under_dialog = "wifi_list"
        self.assert_arrived(self.make(sim).goto_print(TARGET))
        self.assertIn((215, 345, "dialog_delete_confirm"), sim.taps)   # Cancel, never Continue
        self.assertNotIn((585, 345, "dialog_delete_confirm"), sim.taps)

    def test_4c_status_page_with_other_file(self):
        sim = Sim("status_ready", files=files_small()); sim.loaded = "cube.gcode"
        self.assert_arrived(self.make(sim).goto_print(TARGET))
        self.assertIn((680, 421, "status_ready"), sim.taps)            # Cancel, then reselect

    def test_5_unknown_page_with_home_button(self):
        sim = Sim("page:settings", files=files_small())
        self.assert_arrived(self.make(sim).goto_print(TARGET))
        self.assertEqual(sim.taps[0][2], "page:settings"); self.assertEqual(sim.taps[0][:2], (740, 29))

    def test_5b_unknown_screen_no_home_aborts_without_tapping(self):
        sim = Sim("garbage", files=files_small())
        with self.assertRaises(NavAbort):
            self.make(sim).goto_print(TARGET)
        self.assertEqual(sim.taps, [])

    def test_5c_unconfirmed_dialog_not_tapped(self):
        sim = Sim("dialog_lowtemp", files=files_small()); sim.under_dialog = "status_printing"
        with self.assertRaises(NavAbort):
            self.make(sim, probe=False).goto_print(TARGET)
        self.assertEqual(sim.taps, [])

    def test_6_blanked_screen(self):
        sim = Sim("files", files=files_small(), blanked=True)
        self.assert_arrived(self.make(sim).goto_print(TARGET))
        self.assertEqual(sim.taps[0][:2], (400, 472))                # neutral wake tap first

    def test_6b_blanked_but_fb_retained(self):
        sim = Sim("home", files=files_small(), blanked=True, retain_fb_when_blank=True)
        self.assert_arrived(self.make(sim).goto_print(TARGET))
        self.assertEqual(sim.taps[0][:2], (400, 472))

    def test_7_printing_refused_by_probe(self):
        sim = Sim("status_printing", files=files_small()); sim.loaded = "cube.gcode"
        with self.assertRaises(NavAbort) as cm:
            self.make(sim).goto_print(TARGET)
        self.assertIn("streaming", str(cm.exception))
        self.assertEqual(sim.taps, [])

    def test_7b_printing_refused_by_screen(self):
        for st in ("status_printing", "status_paused", "homing"):
            sim = Sim(st, files=files_small()); sim.loaded = "cube.gcode"
            with self.assertRaises(NavAbort) as cm:
                self.make(sim, probe=False).goto_print(TARGET)
            self.assertIn("busy", str(cm.exception))
            self.assertEqual(sim.taps, [], st)

    def test_7c_bridge_active_refused(self):
        sim = Sim("home", files=files_small())
        with self.assertRaises(NavAbort):
            self.make(sim, bridge=StaticBridgeState(True)).goto_print(TARGET)
        self.assertEqual(sim.taps, [])

    # ---- extra safety -------------------------------------------------------------------------------------
    def test_not_ivi_notice_and_start(self):
        sim = Sim("home", files=files_small())
        r = self.make(sim).goto_print("laser.nc", start=True)
        self.assertEqual(sim.started, 1); self.assertEqual(sim.state, "status_printing")
        self.assertIn((585, 345, "dialog_not_ivi"), sim.taps)

    def test_start_refused_when_bridge_unknown(self):
        sim = Sim("home", files=files_small())
        with self.assertRaises(NavAbort):
            self.make(sim, bridge=StaticBridgeState(None)).goto_print(TARGET, start=True)
        self.assertEqual(sim.started, 0); self.assertEqual(sim.taps, [])

    def test_goto_without_start_allowed_when_bridge_unknown(self):
        sim = Sim("home", files=files_small())
        self.assert_arrived(self.make(sim, bridge=StaticBridgeState(None)).goto_print(TARGET))

    def test_missing_file(self):
        sim = Sim("home", files=files_small())
        with self.assertRaises(NavAbort):
            self.make(sim).goto_print("nope.gcode")
        with self.assertRaises(NavAbort):
            self.make(sim).goto_print("notes.txt")   # filtered out by the app
        self.assertEqual(sim.taps, [])

    def test_guard_mismatch_nothing_tapped_then_recovers(self):
        seen = []

        def flip(sim, n):        # right after the Files page is grabbed, the UI changes before the tap
            if sim.state == "files" and not seen:
                seen.append(n); sim.state = "page:control"
        sim = Sim("home", files=files_small())
        self.assert_arrived(self.make(sim, on_grab=flip).goto_print(TARGET))
        states = [st for _, _, st in sim.taps]
        self.assertEqual(states[:4], ["home", "home", "page:control", "home"])  # wake, Files, (guarded tap
        # on the changed screen never landed), Home from the now-different page, then the path again
        with open(os.path.join(self.log.dir, "log.txt")) as fh:
            kinds = [l for l in fh if " guard " in l]
        self.assertTrue(kinds)

    def test_guard_mismatch_repeated_aborts(self):
        def jitter(sim, n):      # the screen keeps changing after every grab
            sim.extra = "x" * (n % 7)
        sim = Sim("home", files=files_small())
        with self.assertRaises(NavAbort) as cm:
            self.make(sim, on_grab=jitter).goto_print(TARGET)
        self.assertIn("guard", str(cm.exception))
        self.assertEqual([t for t in sim.taps if t[:2] != (400, 472)], [])

    def test_dry_run(self):
        sim = Sim("home", files=files_many())
        nav = self.make(sim, dry=True)
        r = nav.goto_print(TARGET)
        self.assertEqual(sim.taps, []); self.assertEqual(sim.state, "home")
        self.assertEqual(r.label, "status_ready")
        joined = "\n".join(nav.plan)
        for t in ("home.files", "files.wifi", "wifi.drag", "wifi.make", "dialog.right", "dialog.one"):
            self.assertIn(t, joined)
        self.assertNotIn("status.center", joined)
        self.assertFalse(any(c.startswith("/tmp/ivitap2") for c in self.t.cmds))

    def test_bump(self):
        sim = Sim("home", files=files_many())
        self.assert_arrived(self.make(sim, allow_bump=True).goto_print(TARGET))
        self.assertFalse(any(st.endswith(":drag") for _, _, st in sim.taps))

    def test_pause_resume_stop(self):
        sim = Sim("status_printing", files=files_small()); sim.loaded = TARGET
        nav = self.make(sim)
        nav.pause(); self.assertEqual(sim.state, "status_paused")
        nav.resume(); self.assertEqual(sim.state, "status_printing")
        with self.assertRaises(NavAbort):
            nav.stop(confirmed=False)
        self.assertEqual(sim.state, "status_printing")
        nav.stop(confirmed=True); self.assertEqual(sim.state, "status_stopped")
        with self.assertRaises(NavAbort):          # pause on a non-printing screen is refused
            nav.pause()

    def test_cancel_backs_out(self):
        sim = Sim("home", files=files_small())
        nav = self.make(sim)
        nav.goto_print(TARGET)
        r = nav.cancel()
        self.assertEqual(r.label, "wifi_list"); self.assertEqual(sim.state, "wifi_list")
        self.assertEqual(sim.started, 0)
        with self.assertRaises(NavAbort):          # cancel off the ready page is refused
            nav.cancel()
        sim2 = Sim("status_printing", files=files_small()); sim2.loaded = "cube.gcode"
        with self.assertRaises(NavAbort):          # never 'Cancel' a running print (that is Stop + confirm)
            self.make(sim2).cancel()
        self.assertEqual(sim2.taps, [])

    def test_start_requires_ready(self):
        sim = Sim("wifi_list", files=files_small())
        with self.assertRaises(NavAbort):
            self.make(sim).start()
        self.assertEqual(sim.taps, [])


class TestProbe(Base):
    """Offline check B: one fd on the last selected file is normal; two fds = streaming."""
    def test_classify(self):
        from ivi_touch.nav import classify_probe
        self.assertEqual(classify_probe([])["verdict"], "idle")
        self.assertEqual(classify_probe(["/userdata/WifiFile/a.gcode"])["verdict"], "loaded")
        self.assertEqual(classify_probe(["/userdata/WifiFile/a.gcode"] * 2)["verdict"], "streaming")

    def test_loaded_file_on_ready_page_not_refused(self):
        sim = Sim("status_ready", files=files_small()); sim.loaded = "cube.gcode"
        sim.work_fd = "/userdata/WifiFile/cube.gcode"
        self.assert_arrived(self.make(sim).goto_print(TARGET))
        self.assertEqual(sim.open_files(), ["/userdata/WifiFile/" + TARGET])   # fd moved to the new file

    def test_fd_left_over_after_finished_print_not_refused(self):
        sim = Sim("home", files=files_small()); sim.work_fd = "/userdata/WifiFile/old.gcode"
        self.assert_arrived(self.make(sim).goto_print(TARGET))

    def test_strict_mode_refuses_on_loaded(self):
        sim = Sim("home", files=files_small()); sim.work_fd = "/userdata/WifiFile/old.gcode"
        with self.assertRaises(NavAbort) as cm:
            self.make(sim, probe="strict").goto_print(TARGET)
        self.assertIn("strict", str(cm.exception)); self.assertEqual(sim.taps, [])

    def test_streaming_refused_even_off_status_page(self):
        sim = Sim("status_printing", files=files_small()); sim.loaded = "cube.gcode"
        sim.work_fd = "/userdata/WifiFile/cube.gcode"
        nav = self.make(sim)
        with self.assertRaises(NavAbort) as cm:
            nav.goto_print(TARGET)
        self.assertIn("streaming", str(cm.exception)); self.assertEqual(sim.taps, [])

    def test_tail_of_print_caught_by_screen(self):
        sim = Sim("status_printing", files=files_small()); sim.loaded = "cube.gcode"
        sim.work_fd = "/userdata/WifiFile/cube.gcode"; sim.tail = True     # cache fd already closed
        with self.assertRaises(NavAbort) as cm:
            self.make(sim).goto_print(TARGET)
        self.assertIn("busy", str(cm.exception)); self.assertEqual(sim.taps, [])

    def test_start_refused_while_streaming(self):
        sim = Sim("status_ready", files=files_small()); sim.loaded = TARGET
        sim.work_fd = "/userdata/WifiFile/" + TARGET
        sim.open_files = lambda: ["/userdata/WifiFile/x.gcode"] * 2
        with self.assertRaises(NavAbort):
            self.make(sim).start()
        self.assertEqual(sim.started, 0)

    def test_probe_command_text(self):
        t = MockTransport(Sim())
        Device(t).printing_probe()
        self.assertIn("grep -i -E '\\.(g|gcode|nc|cnc)$'", t.cmds[-1])


class FakeKore:
    """Mimics printer_http_api.so file_upload() as disassembled (Offline check A)."""
    def __init__(self, sim):
        import threading
        from http.server import BaseHTTPRequestHandler, HTTPServer
        import email.parser, email.policy
        fk = self
        self.sim, self.requests = sim, []

        class H(BaseHTTPRequestHandler):
            def _send(self, code, msg):
                b = msg.encode()
                self.send_response(code); self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

            def do_GET(self):
                self._send(405, "no post")

            def do_POST(self):
                n = int(self.headers.get("Content-Length", 0)); body = self.rfile.read(n)
                fk.requests.append((self.path, self.headers.get("Content-Type"), body))
                if self.path != "/api/v1/upload":
                    return self._send(404, "")
                msg = email.parser.BytesParser(policy=email.policy.HTTP).parsebytes(
                    b"Content-Type: " + self.headers["Content-Type"].encode() + b"\r\n\r\n" + body)
                part = next((p for p in msg.iter_parts() if p.get_param("name", header="content-disposition")
                             == "file"), None)
                if part is None or not part.get_filename():
                    return self._send(412, "file err")
                fn = part.get_filename()
                toks = [t for t in fn.split(".") if t][:2]          # kore_split_string(.., ".", out, 3)
                if len(toks) < 2 or toks[1] not in ("gcode", "cnc", "nc"):
                    return self._send(412, "File type error")
                ivi = b";header_type" in part.get_payload(decode=True)[:400] or True
                fk.sim.files[fn] = (max([t for t, _ in fk.sim.files.values()] or [0]) + 100, ivi)
                return self._send(201, "Upload successfully")

            def log_message(self, *a):
                pass
        self.srv = HTTPServer(("127.0.0.1", 0), H)
        self.port = self.srv.server_port
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def close(self):
        self.srv.shutdown(); self.srv.server_close()


class TestUpload(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.sim = Sim("home", files=files_small())
        self.kore = FakeKore(self.sim)

    def tearDown(self):
        self.kore.close(); shutil.rmtree(self.tmp, ignore_errors=True)

    def _file(self, name, data=b"G28\nG1 X10\n"):
        p = os.path.join(self.tmp, name)
        with open(p, "wb") as fh:
            fh.write(data)
        return p

    def test_names(self):
        from ivi_touch.upload import check_name, safe_name, UploadError
        for ok in ("cube.gcode", "a-b_c.nc", "x.cnc"):
            self.assertEqual(check_name(ok), ok)
        for bad in ("benchy_0.2mm.gcode", "x.GCODE", "x.g", "../x.gcode", "a/b.gcode", ".x.gcode", "x" * 120 + ".gcode",
                    'a"b.gcode', "noext"):
            with self.assertRaises(UploadError, msg=bad):
                check_name(bad)
        self.assertEqual(safe_name("/p/benchy_0.2mm.gcode"), "benchy_0-2mm.gcode")
        self.assertEqual(safe_name("CUBE.G"), "CUBE.gcode")

    def test_upload_ok_and_wire_format(self):
        from ivi_touch.upload import upload
        txt = upload("127.0.0.1", self._file("cube_new.gcode"), port=self.kore.port)
        self.assertEqual(txt, "Upload successfully")
        self.assertIn("cube_new.gcode", self.sim.files)
        path, ctype, body = self.kore.requests[-1]
        self.assertEqual(path, "/api/v1/upload"); self.assertTrue(ctype.startswith("multipart/form-data; boundary="))
        self.assertIn(b'name="file"; filename="cube_new.gcode"', body)
        self.assertNotIn(b"token", body)

    def test_server_rejects_dotted_name(self):
        from ivi_touch.upload import upload, encode_multipart, UploadError
        import urllib.request, urllib.error
        body, ctype = encode_multipart("benchy_0.2mm.gcode", b"G28\n")      # bypass the client-side check
        req = urllib.request.Request("http://127.0.0.1:%d/api/v1/upload" % self.kore.port, data=body,
                                     headers={"Content-Type": ctype})
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req)
        self.assertEqual(cm.exception.code, 412)
        with self.assertRaises(UploadError):                                   # client refuses before sending
            upload("127.0.0.1", self._file("benchy_0.2mm.gcode"), port=self.kore.port)

    def test_unreachable(self):
        from ivi_touch.upload import upload, UploadError
        with self.assertRaises(UploadError):
            upload("127.0.0.1", self._file("a.gcode"), port=9, timeout=2)

    def test_cli_upload_then_goto(self):
        import importlib.util, contextlib
        spec = importlib.util.spec_from_file_location("ivi_cli2", os.path.join(ROOT, "ivi_touch.py"))
        cli = importlib.util.module_from_spec(spec); spec.loader.exec_module(cli)
        sim = self.sim

        def fake_build(args, dry=None):
            t = MockTransport(sim)
            return t, Device(t, dry_run=args.dry_run), Classifier(calibrate_dir()), StaticBridgeState(False)
        cli.build = fake_build; cli.STATE = self.tmp
        import time as _t
        real_sleep = _t.sleep; _t.sleep = lambda s: None
        try:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = cli.main(["--host", "127.0.0.1", "--logdir", self.tmp, "upload", self._file("fresh.gcode"),
                               "--port", str(self.kore.port), "--goto"])
            self.assertEqual(rc, 0, out.getvalue())
            self.assertEqual(sim.state, "status_ready"); self.assertEqual(sim.loaded, "fresh.gcode")
            self.assertEqual(sim.started, 0)
            with contextlib.redirect_stdout(io.StringIO()):          # same name again -> refuse overwrite
                with self.assertRaises(SystemExit):
                    cli.main(["--host", "127.0.0.1", "upload", self._file("fresh.gcode"), "--port",
                              str(self.kore.port)])
                with self.assertRaises(SystemExit):                  # bad name -> refuse with suggestion
                    cli.main(["--host", "127.0.0.1", "upload", self._file("b_0.2mm.gcode"), "--port",
                              str(self.kore.port)])
        finally:
            _t.sleep = real_sleep


class TestCLI(unittest.TestCase):
    def test_cli_dry_run_and_refusals(self):
        import importlib.util, contextlib
        spec = importlib.util.spec_from_file_location("ivi_cli", os.path.join(ROOT, "ivi_touch.py"))
        cli = importlib.util.module_from_spec(spec); spec.loader.exec_module(cli)
        tmp = tempfile.mkdtemp()
        sim = Sim("home", files=files_small())

        def fake_build(args, dry=None):
            t = MockTransport(sim)
            return t, Device(t, dry_run=args.dry_run), Classifier(calibrate_dir()), StaticBridgeState(False)
        cli.build = fake_build
        cli.STATE = tmp
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = cli.main(["--host", "x", "--logdir", tmp, "--dry-run", "goto-print", TARGET])
        self.assertEqual(rc, 0, out.getvalue()); self.assertIn("planned taps", out.getvalue())
        self.assertEqual(sim.taps, [])
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit):
                cli.main(["--host", "x", "--no-bridge-check", "goto-print", TARGET, "--start"])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = cli.main(["--host", "x", "--logdir", tmp, "goto-print", TARGET])
        self.assertEqual(rc, 0, out.getvalue()); self.assertEqual(sim.state, "status_ready")
        self.assertEqual(sim.started, 0)
        shutil.rmtree(tmp, ignore_errors=True)


class TestBridgeHook(unittest.TestCase):
    def test_http_bridge_states(self):
        import json, threading
        from http.server import BaseHTTPRequestHandler, HTTPServer
        from ivi_touch.safety import HTTPBridgeState
        resp = {}

        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.headers.get("X-Api-Key") != "k":
                    self.send_response(403); self.end_headers(); return
                b = json.dumps(resp[self.path]).encode()
                self.send_response(200); self.send_header("Content-Length", str(len(b))); self.end_headers()
                self.wfile.write(b)

            def log_message(self, *a):
                pass
        srv = HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        b = HTTPBridgeState(base="http://127.0.0.1:%d" % srv.server_port, api_key="k", config_path="/nonexistent")

        def setst(state, ready, locked):
            resp["/api/job"] = {"state": state}
            resp["/api/printer"] = {"state": {"flags": {"ready": ready}}, "ivi": {"usb_locked": locked}}
        setst("Operational", True, False); self.assertIs(b.job_active(), False)
        setst("Printing", False, False); self.assertIs(b.job_active(), True)
        setst("Paused", True, False); self.assertIs(b.job_active(), True)      # USB-monitor systat
        setst("Printing from printer storage (USB off)", True, True); self.assertIs(b.job_active(), False)
        b.api_key = "wrong"; self.assertIsNone(b.job_active())
        srv.shutdown(); srv.server_close()
        self.assertIsNone(HTTPBridgeState(base="http://127.0.0.1:9", config_path="/nonexistent").job_active())


class TestTransport(unittest.TestCase):
    def test_empty_command_refused(self):
        t = SSHTransport("192.0.2.1")
        for c in ("", "   "):
            with self.assertRaises(TransportError):
                t.run(c)

    def test_ssh_argv(self):
        t = SSHTransport("192.0.2.1", key="/k")
        a = " ".join(t.base)
        for opt in ("-T", "BatchMode=yes", "ControlMaster=auto", "ControlPersist=600",
                    "HostKeyAlgorithms=ecdsa-sha2-nistp256"):
            self.assertIn(opt, a)
        self.assertNotIn("-t ", a + " ")

    @unittest.skipUnless(shutil.which("gcc"), "gcc not available")
    def test_guard_hash_parity_with_c(self):
        exe = os.path.join(tempfile.mkdtemp(), "hh")
        subprocess.check_call(["gcc", "-O1", "-o", exe, os.path.join(HERE, "hash_harness.c")])
        s = Sim("wifi_list", files=files_small())
        f = s.render()
        fbfile = exe + ".fb"
        with open(fbfile, "wb") as fh:            # double-buffered fb: page 1 visible (yoffset 480)
            fh.write(b"\x11" * len(f.data) + f.data)
        for rect in ((484, 97, 137, 70), (0, 0, 800, 480), (300, 460, 200, 20)):
            c = subprocess.check_output([exe, fbfile] + [str(v) for v in rect], env=dict(os.environ, YOFF="480"))
            self.assertEqual(c.decode().strip(), "%08x" % f.region_hash(*rect), rect)


if __name__ == "__main__":
    unittest.main()
