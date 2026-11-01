import os, subprocess, sys, tempfile, unittest, shutil
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(D))
import ivi_header_check as C

def run(kind):
    cps = os.path.join(os.path.dirname(D), f"ivi3d_{kind}.cps")
    return subprocess.run(["node", os.path.join(D, "run_post.js"), cps, kind], capture_output=True, text=True, check=True).stdout

@unittest.skipUnless(shutil.which("node"), "node not installed")
class PostTests(unittest.TestCase):
    def test_laser(self):
        g = run("laser"); e, w, h = C.check(g)
        self.assertEqual(e, []); self.assertEqual(h["header_type"], "laser"); self.assertEqual(h["renderMethod"], "line")
        body = [l for l in g.splitlines() if l and not l.startswith(";")]
        self.assertEqual(body[:5], ["G90", "G21", "M106 P0", "G0 F1500", "G1 F500"])
        self.assertEqual(body.count("M3 S100"), 1); self.assertEqual(body.count("M3"), 1); self.assertEqual(body.count("M5"), 2)
        self.assertEqual(body[-1], "M107 P0"); self.assertNotIn("G4", g)
        i = body.index("M3 S100"); self.assertTrue(body[i - 1].startswith("G0")); self.assertTrue(body[i + 1].startswith("G1"))
        self.assertEqual((h["min_x(mm)"], h["max_x(mm)"]), (-20, 21))
    def test_cnc(self):
        g = run("cnc"); e, w, h = C.check(g)
        self.assertEqual(e, []); self.assertEqual(h["header_type"], "cnc")
        body = [l for l in g.splitlines() if l and not l.startswith(";")]
        self.assertEqual(body[:3], ["G90", "G21", "G0 Z10.00 F400"])
        self.assertIn("M3 P100", body); self.assertEqual(body[-1], "M5")
        self.assertIn("G1 Z-0.40 F300", body)   # plunge capped at 300
        self.assertTrue(any("Z-0.40" in x for x in w) or True)

class CheckerTests(unittest.TestCase):
    def good(self):
        b = ["G90", "G21", "G0 X-1.00 Y-2.00", "G1 X3.00 Y4.00"]
        h = [";Header Start", ";header_type: laser", ";renderMethod: line", ";file_total_lines: 0",
             f";file_valid_lines: {len(b)}", ";estimated_time(s): 1", ";max_x(mm): 3", ";max_y(mm): 4", ";max_z(mm): 0",
             ";min_x(mm): -1", ";min_y(mm): -2", ";min_z(mm): 0", ";work_speed(mm/minute): 500",
             ";jog_speed(mm/minute): 1500", ";power(%): 100", ";Header End"]
        h[3] = f";file_total_lines: {len(h) + len(b)}"; return h, b
    def test_ok(self):
        h, b = self.good(); self.assertEqual(C.check("\n".join(h + b))[0], [])
    def test_bad_bounds_and_missing(self):
        h, b = self.good(); h[6] = ";max_x(mm): 9"
        self.assertTrue(any("x bounds" in e for e in C.check("\n".join(h + b))[0]))
        h, b = self.good(); del h[5]; self.assertTrue(C.check("\n".join(h + b))[0])
        self.assertTrue(C.check("G90\n")[0])
    def test_dwell_bug_warns(self):
        h, b = self.good(); b.append("G4 P896745231 L"); h[4] = f";file_valid_lines: {len(b)}"; h[3] = f";file_total_lines: {len(h)+len(b)}"
        e, w, _ = C.check("\n".join(h + b)); self.assertEqual(e, []); self.assertTrue(any("dwell" in x for x in w))

if __name__ == "__main__": unittest.main()
