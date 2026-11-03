import json, os, sys, tempfile, unittest, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import ivi_setup_keys as K

PH = K.PLACEHOLDER
class T(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory(); r = self.td.name
        self.cfg = os.path.join(r, "cfg", "config.json"); self.orca = os.path.join(r, "OrcaSlicer")
        self.logs = []
    def tearDown(self): self.td.cleanup()
    def w(self, rel, obj):
        p = os.path.join(self.orca, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: f.write(json.dumps(obj, indent="\t"))
        return p
    def r(self, p): return json.load(open(p))
    def run_(self, **kw):
        kw.setdefault("running", lambda: False)
        return K.setup(self.cfg, self.orca, log=self.logs.append, **kw)
    def preset(self, folder, key=PH):
        return self.w("user/%s/machine/base/IVI3D 0.3 nozzle.json" % folder,
                      {"name": "IVI3D 0.3 nozzle", "print_host": "127.0.0.1:5001", "printhost_apikey": key})

    def test_creates_key_and_keeps_it(self):
        rc, k = self.run_(); self.assertEqual(rc, 0); self.assertEqual(len(k), 32)
        self.assertEqual(oct(os.stat(self.cfg).st_mode & 0o777), "0o600")
        self.assertEqual(self.run_()[1], k)
        self.assertNotEqual(self.run_(new_key=True)[1], k)

    def test_patches_placeholder_everywhere(self):
        a = self.preset("8e27"); b = self.preset("default")
        other = self.w("user/default/machine/Other.json", {"name": "Prusa", "print_host": "1.2.3.4", "printhost_apikey": "x"})
        conf = self.w("OrcaSlicer.conf", {"app": {"preset_folder": "8e27"}, "local_machines": {"127.0.0.1:5001": {"access_code": PH, "dev_ip": "127.0.0.1:5001"}}})
        plug = self.w("orca_plugins/config.json", {"config": [{"capability": "IVI3D Bridge", "cap_config": {"api_key": PH, "bridge_url": "http://127.0.0.1:5001", "poll_seconds": 3}}, {"capability": "IVI3D FDM Header", "cap_config": {"enabled": True}}]})
        rc, k = self.run_(); self.assertEqual(rc, 0)
        for p in (a, b): self.assertEqual(self.r(p)["printhost_apikey"], k)
        self.assertEqual(self.r(other)["printhost_apikey"], "x")
        self.assertEqual(self.r(conf)["local_machines"]["127.0.0.1:5001"]["access_code"], k)
        self.assertEqual(self.r(conf)["app"]["preset_folder"], "8e27")
        pc = self.r(plug)["config"]; self.assertEqual(pc[0]["cap_config"]["api_key"], k); self.assertEqual(pc[1]["cap_config"], {"enabled": True})
        self.assertTrue(open(conf).read().startswith("{\n\t\""))  # tabs kept
        self.assertEqual(len(glob.glob(conf + ".bak-*")), 1)
        self.assertFalse(any(k in m for m in self.logs))            # key never logged in full
        self.run_(); self.assertEqual(len(glob.glob(conf + ".bak-*")), 1)  # idempotent: no rewrite

    def test_replaces_old_key(self):
        os.makedirs(os.path.dirname(self.cfg)); json.dump({"api_key": "n" * 32}, open(self.cfg, "w"))
        p = self.preset("default", key="o" * 32)
        rc, k = self.run_(); self.assertEqual(k, "n" * 32); self.assertEqual(self.r(p)["printhost_apikey"], k)

    def test_creates_missing_entries(self):
        conf = self.w("OrcaSlicer.conf", {"app": {}}); plug = self.w("orca_plugins/config.json", {"config": []})
        rc, k = self.run_()
        m = self.r(conf)["local_machines"]["127.0.0.1:5001"]; self.assertEqual(m["access_code"], k); self.assertEqual(m["printer_type"], "IVI3D")
        e = self.r(plug)["config"][0]; self.assertEqual(e["capability"], "IVI3D Bridge"); self.assertEqual(e["cap_config"]["api_key"], k)

    def test_missing_files_not_created(self):
        os.makedirs(self.orca); self.run_()
        self.assertFalse(os.path.exists(os.path.join(self.orca, "OrcaSlicer.conf")))
        self.assertFalse(os.path.exists(os.path.join(self.orca, "orca_plugins", "config.json")))

    def test_refuses_while_orca_running(self):
        p = self.preset("default"); before = open(p).read()
        rc, k = self.run_(running=lambda: True)
        self.assertEqual(rc, K.EXIT_ORCA_RUNNING); self.assertEqual(open(p).read(), before)
        self.assertFalse(glob.glob(p + ".bak-*")); self.assertTrue(os.path.exists(self.cfg))
        self.assertEqual(self.run_()[0], 0); self.assertEqual(self.r(p)["printhost_apikey"], k)

    def test_dry_run_writes_nothing(self):
        p = self.preset("default"); rc, k = self.run_(dry_run=True)
        self.assertFalse(os.path.exists(self.cfg)); self.assertEqual(self.r(p)["printhost_apikey"], PH)

if __name__ == "__main__": unittest.main()
