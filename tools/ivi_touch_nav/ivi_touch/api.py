"""Importable API (e.g. from ivi_bridge.py or a script on the Mac):

    from ivi_touch.api import session
    with session("<printer-ip>", key="~/.ssh/ivi_ecdsa") as nav:
        nav.goto_print("benchy.gcode")          # stops before Start
        nav.start()                             # explicit, screen- and bridge-checked
"""
import contextlib, os
from .nav import Navigator, NavAbort, GuardMismatch          # noqa: F401 (re-export)
from .runlog import RunLog
from .safety import HTTPBridgeState, CallableBridgeState, StaticBridgeState   # noqa: F401
from .screens import Classifier
from .transport import Device, SSHTransport

HOME = os.path.expanduser(os.environ.get("IVI_TOUCH_HOME", "~/.ivi_touch"))


@contextlib.contextmanager
def session(host, key="~/.ssh/ivi_ecdsa", calib=None, logdir=None, dry_run=False, bridge="http",
            name="api", echo=None, **nav_kw):
    """bridge: "http" (ask the running bridge), None (no check), or any object with job_active()."""
    t = SSHTransport(host, key=key, control_path=os.path.join(HOME, "cm-%C"))
    if bridge == "http":
        bridge = HTTPBridgeState()
    log = RunLog(logdir or os.path.join(HOME, "runs"), name, echo=echo)
    nav = Navigator(Device(t, dry_run=dry_run), Classifier(calib or os.path.join(HOME, "calib")),
                    bridge=bridge, log=log, **nav_kw)
    try:
        yield nav
    finally:
        log.close()
