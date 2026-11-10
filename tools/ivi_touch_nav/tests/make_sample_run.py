"""Produce sample_run/ logs (with PNG screenshots) from the simulator - no printer involved."""
import os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
from ivi_touch.nav import Navigator, NavAbort
from ivi_touch.runlog import RunLog
from ivi_touch.safety import StaticBridgeState
from ivi_touch.screens import Classifier
from ivi_touch.transport import Device
from sim import Sim
from mock_transport import MockTransport
import test_nav as T

out = os.path.join(ROOT, "sample_run")
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
calib = T.calibrate_dir()


def run(name, sim, fn, dry=False):
    log = RunLog(out, name, save_png=True, echo=None)
    t = MockTransport(sim)
    nav = Navigator(Device(t, dry_run=dry), Classifier(calib), bridge=StaticBridgeState(False), log=log,
                    sleep=lambda s: None)
    try:
        r = fn(nav)
        log.event("result", "OK %r%s" % (r, ("; planned: " + " | ".join(nav.plan)) if dry else ""))
    except NavAbort as e:
        log.event("abort", str(e))
    log.event("summary", "%d SSH commands, %d taps injected: %s" % (len(t.cmds), len(sim.taps), sim.taps))
    log.close()
    os.rename(log.dir, os.path.join(out, name))


sim = Sim("page:settings", files=T.files_many(), blanked=True, retain_fb_when_blank=True)
run("1_goto_print_from_unknown_blanked_page", sim, lambda n: n.goto_print(T.TARGET))
run("2_dry_run_from_home", Sim("home", files=T.files_many()), lambda n: n.goto_print(T.TARGET), dry=True)
s = Sim("status_printing", files=T.files_small()); s.loaded = "cube.gcode"
run("3_refuse_while_printing", s, lambda n: n.goto_print(T.TARGET))
run("4_unknown_screen_abort", Sim("garbage", files=T.files_small()), lambda n: n.goto_print(T.TARGET))
print(open(os.path.join(out, "1_goto_print_from_unknown_blanked_page", "log.txt")).read())
