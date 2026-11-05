import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ivi_bridge as B

class Clock:
    def __init__(self): self.t = 0.0
    def __call__(self): return self.t

class EstimateTests(unittest.TestCase):
    def test_parse_m73(self):
        self.assertEqual(B.parse_m73("M73 P12 R34"), (12.0, 34.0))
        self.assertEqual(B.parse_m73("m73 r5 p1 ; c"), (1.0, 5.0))
        self.assertEqual(B.parse_m73("M73 P50"), (50.0, None))
        self.assertIsNone(B.parse_m73("M730 P1")); self.assertIsNone(B.parse_m73("G1 X1"))
    def test_parse_feedrate(self):
        self.assertEqual(B.parse_feedrate("FR:100%"), 100.0)
        self.assertEqual(B.parse_feedrate("echo:FR:150%"), 150.0)
        self.assertIsNone(B.parse_feedrate("ok")); self.assertIsNone(B.parse_feedrate("T:200 /200"))
    def test_scaling(self):
        self.assertEqual(B.estimate_left(600, 60, 100, 999), (540.0, "slicer M73"))
        left, src = B.estimate_left(600, 0, 200, None); self.assertEqual(left, 300.0); self.assertIn("200", src)
        self.assertEqual(B.estimate_left(600, 0, 50, None)[0], 1200.0)
        self.assertEqual(B.estimate_left(60, 120, None, None)[0], 0.0)
        self.assertEqual(B.estimate_left(600, 0, 0, None)[0], 600.0)   # bad FR ignored
    def test_fallback(self):
        self.assertEqual(B.estimate_left(None, None, 150, 42.0), (42.0, "line rate"))
        self.assertEqual(B.estimate_left(None, None, None, None), (None, None))
    def test_job_info_uses_m73_and_feedrate(self):
        c = Clock(); j = B.SerialJob(None, ["G28", "M73 P10 R20", "G1 X1", "G1 X2"], clock=c)
        j.started = 1.0; c.t = 31.0; j.sent = 2; j._m73 = (1200.0, 11.0)
        d = j.info(); self.assertEqual(d["left"], 1180.0); self.assertEqual(d["left_source"], "slicer M73")
        j.feedrate = B.parse_feedrate("FR:200%")
        self.assertEqual(j.info()["left"], 590.0)
        j._m73 = None; d = j.info(); self.assertEqual(d["left_source"], "line rate"); self.assertEqual(d["left"], 30.0)
    def test_poll_feedrate_flag_and_no_reply(self):
        class S:
            def __init__(s): s.w = []
            def write(s, b): s.w.append(b.decode().strip())
            def readline(s): return b""
        c = Clock(); s = S(); j = B.SerialJob(s, [], clock=c, poll_feedrate=True, feedrate_poll_s=30)
        tick = lambda: setattr(c, "t", c.t + 0.5) or b""
        s.readline = tick
        j._maybe_poll_feedrate(); self.assertEqual(s.w, [])          # first call only arms the timer
        c.t = 31; j._maybe_poll_feedrate(); self.assertEqual(s.w, ["M220"])   # sent; no reply tolerated
        off = B.SerialJob(s, [], clock=c, poll_feedrate=False); c.t = 999; off._maybe_poll_feedrate(); off._maybe_poll_feedrate()
        self.assertEqual(s.w, ["M220"])
    def test_stream_reads_m73(self):
        class S:
            def __init__(s): s.out = []
            def write(s, b): s.out.append(b"ok")
            def readline(s): return (s.out.pop(0) + b"\n") if s.out else b""
        j = B.SerialJob(S(), ["M73 P0 R10", "G1 X1"], line_timeout=2)
        j.handshake = lambda: None; j._start = lambda: None; j.run()
        self.assertEqual(j.state, "Operational"); self.assertEqual(j._m73[0], 600.0)

    def test_slicer_estimate_fallback(self):
        self.assertEqual(B.estimate_left(None, None, None, 99999.0, 1000, 0.25), (750.0, "slicer estimate"))
        left, src = B.estimate_left(None, None, 200, 99999.0, 1000, 0.5); self.assertEqual(left, 250.0); self.assertIn("200", src)
        self.assertEqual(B.estimate_left(None, None, None, None, 1000, 1.5)[0], 0.0)
        self.assertEqual(B.estimate_left(600, 0, None, None, 1000, 0.5), (600.0, "slicer M73"))   # M73 wins
        self.assertEqual(B.estimate_left(None, None, None, 5.0, None, 0.5), (5.0, "line rate"))  # no header
    def test_job_info_slicer_estimate_by_bytes(self):
        c = Clock(); lines = ["G28", "M109 S220", "G1 X1 E1", "G1 X2 E2"]
        j = B.SerialJob(None, lines, clock=c, estimate_s=1000)
        j.started = 0.0; c.t = 3000.0; j.sent = 2      # long heat wait must not inflate the estimate
        tot = sum(len(l) + 1 for l in lines); done = len("G28") + 1 + len("M109 S220") + 1
        d = j.info(); self.assertEqual(d["left_source"], "slicer estimate")
        self.assertAlmostEqual(d["left"], 1000 * (1 - done / tot))
        j._m73 = (300.0, 3000.0); self.assertEqual(j.info()["left_source"], "slicer M73")
    def test_usb_job_passes_header_estimate(self):
        import inspect
        self.assertIn("estimate_s", inspect.signature(B.SerialJob).parameters)

if __name__ == "__main__": unittest.main()
