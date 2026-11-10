"""Safety hooks: bridge job state.

Hook point for ivi_bridge.py integration: anything with a `job_active()` method returning True / False /
None (unknown). The default asks the running bridge's own HTTP API (GET /api/job + /api/printer,
default http://127.0.0.1:5001) - no changes to ivi_bridge.py needed. Inside the bridge process you would instead
pass `CallableBridgeState(lambda: bridge.busy())`.
"""
import json, os, urllib.request

IDLE_STATES = {"operational"}


def bridge_settings(config_path=None):
    """(url_base, api_key) from the bridge's own config (~/.config/ivi-bridge/config.json or
    $IVI_BRIDGE_CONFIG). The key is used only as a request header and is never logged or printed."""
    path = config_path or os.environ.get("IVI_BRIDGE_CONFIG") or os.path.expanduser("~/.config/ivi-bridge/config.json")
    cfg = {}
    try:
        with open(path) as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        pass
    host = cfg.get("listen_host", "127.0.0.1")
    if host in ("0.0.0.0", "", "::"):
        host = "127.0.0.1"
    return "http://%s:%s" % (host, cfg.get("listen_port", 5001)), cfg.get("api_key") or None


class HTTPBridgeState:
    """Reads GET /api/job and GET /api/printer of the running bridge.
      * flags.ready == False (bridge.busy(): a USB/PC job Starting/Printing/Paused/Stopping) -> ACTIVE
      * ivi.usb_locked (after a Wi-Fi upload the bridge releases USB and reports
        'Printing from printer storage (USB off)' whether or not the printer has started) -> NOT a bridge job;
        the printer's own state is then judged from the screen + the on-printer open-file probe
      * otherwise state != 'Operational' (incl. USB-monitor systat Printing/Pausing/Paused/Cancelling) -> ACTIVE
      * unreachable -> None (unknown)."""

    def __init__(self, base=None, api_key=None, timeout=3, config_path=None):
        b, k = bridge_settings(config_path)
        self.base, self.api_key, self.timeout = (base or b).rstrip("/"), api_key or k, timeout
        self.last = None

    def _get(self, path):
        req = urllib.request.Request(self.base + path)
        if self.api_key:
            req.add_header("X-Api-Key", self.api_key)
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read().decode())

    def job_active(self):
        try:
            job = self._get("/api/job")
            prn = self._get("/api/printer")
        except Exception as e:
            self.last = "unreachable (%s)" % e.__class__.__name__
            return None
        st = str(job.get("state", ""))
        flags = (prn.get("state") or {}).get("flags") or {}
        ivi = prn.get("ivi") or {}
        self.last = "state=%r ready=%r usb_locked=%r" % (st, flags.get("ready"), ivi.get("usb_locked"))
        if flags.get("ready") is False:
            return True
        if ivi.get("usb_locked"):
            return False
        return st.strip().lower() not in IDLE_STATES


class CallableBridgeState:
    def __init__(self, fn):
        self.fn, self.last = fn, None

    def job_active(self):
        v = self.fn(); self.last = v
        return None if v is None else bool(v)


class StaticBridgeState:
    """For tests / --no-bridge-check."""
    def __init__(self, active):
        self.active, self.last = active, "static %r" % active

    def job_active(self):
        return self.active
