"""Screen-aware navigation to the Print/Start button for the IVI3D touchscreen app (A33, QML app v1.222).

From ANY screen, reach the StatusPage Start button for a named file:
  * identify the current screen from an fb0 grab (screens.Classifier);
  * already on Files or further along the Wi-Fi path -> continue from there;
  * somewhere random/unknown -> recover (Home / close a known dialog), CONFIRM Home, start the path over.
Before EVERY real tap the screen is re-identified and must be the confidently-identified state the tap is
allowed on (ALLOWED below). Each tap carries a guard hash of its target rect that ivitap2 re-checks on the
device immediately before injecting (exit 4 = screen changed -> abort). Unknown or provisional states never
get an action tap; repeated failures abort after max_steps.

Path (virtual-touch report): Home -Files(122,209)-> Files -"Print Files via WiFi"(400,225)-> Wi-Fi list
 -Make(552,row)-> [not-IVI dialog: OK right] -> Print dialog: Make(right) -> [plate warning: OK centre]
 -> StatusPage (Start at 400,421).
"""
import time
from . import layout as L
from .screens import Ident, family_of

# which named targets may be tapped on which (confidently identified) screen
ALLOWED = {
    "home": {"home.files", "wake"},
    "files": {"files.wifi", "page.home", "wake"},
    "wifi_list": {"wifi.make", "wifi.drag", "page.home", "wake"},
    "dialog_not_ivi": {"dialog.right"},
    "dialog_print": {"dialog.left", "dialog.right"},
    "dialog_plate": {"dialog.one"},
    "dialog_stop_confirm": {"dialog.left", "dialog.right"},
    "dialog_delete_confirm": {"dialog.left"},
    "status_ready": {"status.center", "status.right", "wake"},
    "status_printing": {"status.center", "status.right", "wake"},
    "status_paused": {"status.center", "status.right", "wake"},
    "status_stopped": {"status.right", "wake"},
    "status_complete": {"status.right", "wake"},
    "blank": {"wake"},
}
ACTION_TARGETS = {"status.center", "status.right", "dialog.right"}   # need an explicit arm flag where relevant


def allowed(label, target):
    if label.startswith("page:"):
        return target in ("page.home", "wake")
    return target in ALLOWED.get(label, ())


class NavError(RuntimeError):
    pass


class NavAbort(NavError):
    """Safety stop: unknown state, loop, guard mismatch, active job, missing file..."""


class GuardMismatch(NavAbort):
    """ivitap2 found the target rect changed since the screenshot; NOTHING was tapped."""


def _guard(frame, rect):
    x, y, w, h = rect
    return (x, y, w, h, frame.region_hash(x, y, w, h) if frame is not None else 0)


def _close(c, col, tol):
    return abs(c[0] - col[0]) <= tol and abs(c[1] - col[1]) <= tol and abs(c[2] - col[2]) <= tol


def classify_probe(fds):
    """fds: list of fd targets (one per fd). -> {'counts': {path: n}, 'verdict': idle|loaded|streaming, ...}"""
    counts = {}
    for p in fds:
        counts[p] = counts.get(p, 0) + 1
    streaming = sorted(p for p, n in counts.items() if n >= 2)
    loaded = sorted(p for p, n in counts.items() if n == 1)
    verdict = "streaming" if streaming else ("loaded" if loaded else "idle")
    return {"counts": counts, "verdict": verdict, "streaming": streaming, "loaded": loaded}


def _shq(s):
    return "'" + s.replace("'", "'\\''") + "'"


# expected next screen after a tap (used for dry-run planning and for post-tap sanity logging)
EXPECT = {
    ("home", "home.files"): "files",
    ("files", "files.wifi"): "wifi_list",
    ("wifi_list", "wifi.make"): "dialog_print",          # or dialog_not_ivi first
    ("dialog_not_ivi", "dialog.right"): "dialog_print",
    ("dialog_print", "dialog.right"): "dialog_plate",     # or status_ready directly
    ("dialog_print", "dialog.left"): "wifi_list",
    ("dialog_plate", "dialog.one"): "status_ready",
    ("files", "page.home"): "home", ("wifi_list", "page.home"): "home",
    ("status_ready", "status.right"): "wifi_list",
    ("status_stopped", "status.right"): "home", ("status_complete", "status.right"): "home",
}


class Navigator:
    def __init__(self, device, classifier, bridge=None, log=None, max_steps=25, max_unknown=4,
                 settle_ms=800, allow_bump=False, printing_probe=True, sleep=time.sleep):
        self.dev, self.clf, self.bridge, self.log = device, classifier, bridge, log
        self.max_steps, self.max_unknown, self.settle_ms = max_steps, max_unknown, settle_ms
        self.allow_bump, self.sleep = allow_bump, sleep
        # probe mode: "stream" (default) refuse only when a print file is open TWICE (= being streamed);
        # "strict" refuse on any open print file (pre-check-B behaviour); "off" skip.
        self.probe_mode = {True: "stream", False: "off", None: "off"}.get(printing_probe, printing_probe)
        if self.probe_mode not in ("stream", "strict", "off"):
            raise ValueError("printing_probe must be stream/strict/off")
        self.selected = None           # file we tapped Make for during THIS run
        self.content_y = 0
        self._planned = None           # dry-run: Ident we expect next instead of grabbing
        self._next_frame = None        # frame grabbed in the same SSH call as the last tap
        self.plan = []                 # dry-run: list of planned taps

    @property
    def dry(self):
        return self.dev.dry_run

    # ---------------------------------------------------------------- observation ------------------------
    def _emit(self, kind, msg, frame=None, **k):
        if self.log:
            self.log.event(kind, msg, frame=frame, **k)

    def observe(self):
        """(frame, Ident). In dry-run after a planned tap, returns the planned state with frame None."""
        if self._planned is not None:
            ident, self._planned = self._planned, None
            self._emit("plan", "assume next screen = %s" % ident.label)
            return None, ident
        f, self._next_frame = self._next_frame, None
        if f is None:
            f = self.dev.grab()
        ident = self.clf.identify(f)
        self._emit("identify", repr(ident), frame=f, label=ident.label, score=ident.score,
                   provisional=ident.provisional)
        return f, ident

    # ---------------------------------------------------------------- tapping ---------------------------
    def tap(self, target, frame, ident, xy=None, rect=None, drag_to=None, armed=False, expect=None):
        """The ONLY tap entry point. Verifies the screen (`ident` must be confident and the target allowed
        on it), refuses list taps at x>621, guards the target rect, logs. Returns frame after the tap."""
        if not (ident.confident or ident.label == "blank" or (self.dry and frame is None)):
            raise NavAbort("internal: refusing tap %s on unconfirmed screen %r" % (target, ident))
        if not allowed(ident.label, target):
            raise NavAbort("internal: target %s not allowed on %s" % (target, ident.label))
        if target in ACTION_TARGETS and ident.label.startswith("status_") and not armed:
            raise NavAbort("internal: action %s on %s requires an explicit command" % (target, ident.label))
        if xy is None:
            x, y, rect = L.TAPS[target]
        else:
            x, y = xy
        if target.startswith("wifi.") and x > L.MAX_LIST_TAP_X:
            raise NavAbort("refusing list tap at x=%d (> %d would hit Delete)" % (x, L.MAX_LIST_TAP_X))
        nxt = expect or EXPECT.get((ident.label, target))
        desc = "%s @ (%d,%d)%s on %s" % (target, x, y, (" drag->(%d,%d)" % drag_to[:2]) if drag_to else "",
                                         ident.label)
        if self.dry:
            self.plan.append(desc)
            self._emit("tap", "DRY " + desc + (" -> expect %s" % nxt if nxt else ""), frame=frame,
                       target=target, x=x, y=y)
            if nxt:
                self._planned = Ident(nxt, family_of(nxt), detail="planned")
            return None
        if frame is None:
            raise NavAbort("internal: no frame for guard")
        status, f2 = self.dev.tap(x, y, _guard(frame, rect), drag_to=drag_to,
                                  settle_ms=400 if drag_to else self.settle_ms)
        self._emit("tap", "%s -> %s" % (desc, status), frame=f2, target=target, x=x, y=y, status=status,
                   expect=nxt)
        if status == "GUARD":
            self._next_frame = f2
            raise GuardMismatch("guard mismatch before %s: the screen changed between check and tap (nothing tapped)"
                                % target)
        if status != "OK":
            raise NavAbort("tap %s failed: %s" % (target, status))
        self._next_frame = f2            # the post-tap grab doubles as the next observation (1 round trip/step)
        return f2

    def wake(self, frame, ident):
        """Neutral tap at (400,472): inert on every modelled page [I]. Used for a blank panel and once at
        session start (closeScreen blanks via fb0/blank and the fb may keep its old content)."""
        x, y, rect = L.TAPS["wake"]
        if frame is None:
            return None
        return self.tap("wake", frame, ident, expect=None)

    # ---------------------------------------------------------------- safety ----------------------------
    def check_bridge(self, action, required=True):
        if self.bridge is None:
            self._emit("safety", "bridge check disabled for %s" % action)
            return
        active = self.bridge.job_active()
        self._emit("safety", "bridge job_active=%r (%s)" % (active, getattr(self.bridge, "last", "")))
        if active is True:
            raise NavAbort("refusing %s: the Mac bridge reports an active job" % action)
        if active is None and required:
            raise NavAbort("refusing %s: bridge state unknown/unreachable (use --no-bridge-check to override)"
                           % action)

    def check_probe(self, action):
        """Open-file probe (Offline check B). The app keeps ONE fd on the last selected file from selection
        until the next selection or app restart, so a single fd is NOT evidence of printing. Two fds on the
        same file = the streaming cache is reading it = a print is running. Near the very end of a job the
        cache fd closes (EOF) while the last cached lines are still sent - the screen check covers that."""
        if self.probe_mode == "off":
            return
        try:
            fds = self.dev.printing_probe()
        except Exception as e:
            raise NavAbort("refusing %s: printing probe failed (%s)" % (action, e))
        v = classify_probe(fds)
        self._emit("safety", "app print-file fds: %s -> %s" % (v["counts"] or "none", v["verdict"]),
                   probe=v)
        if v["verdict"] == "streaming":
            raise NavAbort("refusing %s: the printer app is streaming %s (2 open fds) - a print is running"
                           % (action, v["streaming"][0]))
        if self.probe_mode == "strict" and v["verdict"] == "loaded":
            raise NavAbort("refusing %s (strict probe): the printer app holds %s open"
                           % (action, v["loaded"][0]))

    # ---------------------------------------------------------------- main routine -----------------------
    def goto_print(self, filename, start=False):
        """Navigate to the StatusPage for `filename` and stop before Start (start=False, default) or tap
        Start (start=True). Returns the final Ident."""
        self.check_bridge("goto-print", required=start)
        self.check_probe("goto-print")
        order = self._wifi_order()
        if filename not in order:
            raise NavAbort("file %r is not listed in /userdata/WifiFile (after the app's filters). Present: %s"
                           % (filename, ", ".join(order[:10]) or "(none)"))
        self.selected, unknown, woke, guards = None, 0, False, 0
        history = []
        for step in range(1, self.max_steps + 1):
            f, ident = self.observe()
            history.append(ident.label)
            if ident.label in L.PRINTING_LABELS:
                raise NavAbort("refusing: printer is busy (%s)" % ident.label)
            if ident.label == "blank" or (not woke and ident.confident and f is not None):
                woke = True
                if allowed(ident.label, "wake"):
                    f2 = self.wake(f, ident)
                    if f2 is not None:
                        ident = self.clf.identify(f2); f = f2
                        self._emit("identify", "after wake: %r" % ident, label=ident.label)
                        history[-1] = ident.label
            if not ident.confident:
                unknown += 1
                if unknown > self.max_unknown:
                    raise NavAbort("screen not recognised %d times in a row (last %r); aborting" % (unknown, ident))
                self._recover_unknown(f, ident)
                continue
            unknown = 0
            if self._looping(history):
                raise NavAbort("no progress: %s" % history[-6:])
            try:
                res = self._advance(f, ident, filename, order, start)
            except GuardMismatch as e:
                guards += 1
                self._emit("guard", "%s - re-identifying (%d/3)" % (e, guards))
                if guards >= 3:
                    raise
                continue
            if res is not None:
                return res
        raise NavAbort("gave up after %d steps; last states %s" % (self.max_steps, history[-6:]))

    def _looping(self, h, n=4):
        return len(h) >= n and len(set(h[-n:])) == 1

    def _advance(self, f, ident, filename, order, start):
        lab = ident.label
        if lab == "home":
            self.selected = None
            self.tap("home.files", f, ident)
        elif lab == "files":
            self.selected = None
            self.tap("files.wifi", f, ident)
        elif lab == "wifi_list":
            self._pick(f, ident, filename, order)
        elif lab == "dialog_not_ivi":
            if self.selected != filename:
                raise NavAbort("not-IVI notice for a file we did not pick; aborting (close it by hand)")
            self.tap("dialog.right", f, ident)
        elif lab == "dialog_print":
            if self.selected == filename:
                self.tap("dialog.right", f, ident)             # "Make" -> loads the file
            else:
                self._emit("recover", "print dialog for a selection we did not make -> Cancel (left)")
                self.tap("dialog.left", f, ident)
        elif lab == "dialog_plate":
            self.tap("dialog.one", f, ident)
        elif lab in ("dialog_stop_confirm", "dialog_delete_confirm"):
            self._emit("recover", "%s unexpected -> safe left button (No/Cancel)" % lab)
            self.tap("dialog.left", f, ident, expect=None)
        elif lab == "status_ready":
            if self.selected != filename:
                self._emit("recover", "StatusPage has a file we did not load this run -> Cancel (right) and reselect")
                self.tap("status.right", f, ident, armed=True)
                return None
            if not start:
                self._emit("arrive", "Start button ready for %r (stop-before-Start; use --start)" % filename,
                           frame=f)
                return ident
            return self.start(f, ident)
        elif lab in ("status_stopped", "status_complete"):
            self.tap("status.right", f, ident, armed=True)
        elif lab.startswith("page:"):
            self.tap("page.home", f, ident, expect="home")
        else:
            raise NavAbort("no rule for state %s" % lab)
        return None

    def _recover_unknown(self, f, ident):
        """Unknown/provisional: never an action tap. Allowed: Home on a page whose ENABLED Home button matches
        the calibrated template; otherwise just wait and re-grab (transitions, toasts, animations)."""
        if f is not None and ident.family != "dialog" and self.clf.home_icon_present(f):
            self._emit("recover", "unrecognised page with an enabled Home button -> Home", frame=f)
            fake = Ident("page:unknown", "header", detail="home icon matched")
            self.tap("page.home", f, fake, expect="home")
            return
        why = ("unconfirmed dialog (button roles unknown; e.g. Lower-Temp puts 'Reset' on the left)"
               if ident.family == "dialog" else "unrecognised screen")
        self._emit("recover", "%s -> no tap, re-grab in 1.5 s" % why, frame=f)
        if self.dry:
            raise NavAbort("dry-run: cannot plan from an unrecognised screen (%r)" % ident)
        self.sleep(1.5)

    # ---------------------------------------------------------------- Wi-Fi list --------------------------
    def _wifi_order(self):
        ents = self.dev.list_wifi()
        order = L.list_filter_sort(ents)
        self._emit("list", "/userdata/WifiFile: %d entries, %d shown by the app" % (len(ents), len(order)),
                   order=order[:40])
        return order

    def _pick(self, f, ident, filename, order):
        row = order.index(filename)
        if self.allow_bump and row:
            self._emit("bump", "touching %r so it becomes row 0 (--bump)" % filename)
            if not self.dry:
                self.dev.t.run("touch /userdata/WifiFile/%s" % _shq(filename))
                self.sleep(1.0)
                f = self.dev.grab()
            order.remove(filename); order.insert(0, filename); row = 0
        n = len(order)
        f = self._scroll_into_view(f, ident, row, n)
        rect = L.make_rect(row, self.content_y)
        if f is not None:
            if not self.clf.identify(f).label == "wifi_list":
                raise NavAbort("left the Wi-Fi list while scrolling")
            caps = self.make_capsules(f)
            if not any(abs(top - rect[1]) <= 8 for top, en in caps):
                raise NavAbort("list layout mismatch: expected a Make button at y=%d, saw %s (listing out of sync?)"
                               % (rect[1], caps))
            if not any(abs(top - rect[1]) <= 8 and en for top, en in caps):
                raise NavAbort("Make for %r is DISABLED (head type mismatch?)" % filename)
        x, y = rect[0] + rect[2] // 2, rect[1] + rect[3] // 2
        self._emit("select", "file %r = row %d of %d, Make at (%d,%d), contentY=%d" % (filename, row, n, x, y,
                                                                                      self.content_y))
        self.tap("wifi.make", f, ident, xy=(x, y), rect=rect)
        self.selected = filename

    def make_capsules(self, f):
        """Scan a column inside the Make capsule but clear of its centred label (x = MAKE_X+20 = 504) for
        runs >= 50 px of BLUE (enabled) or LINE grey (disabled). Returns [(top_y, enabled)]."""
        x = L.MAKE_X + 20
        out, run, kind, start = [], 0, None, 0
        for y in range(L.LIST_TOP, L.LIST_BOTTOM + 1):
            c = f.rgb(x, y) if y < L.LIST_BOTTOM else (255, 255, 255)
            k = "en" if _close(c, L.BLUE, 50) else ("dis" if _close(c, L.LINE, 12) else None)
            if k == kind and k is not None:
                run += 1
            else:
                if kind and run >= 50:
                    out.append((start, kind == "en"))
                kind, run, start = k, 1, y
        return out

    def read_content_y(self, f, n):
        """contentY from the AlwaysOn ScrollBar (x 792..800, handle colour #BED1FF at 0.75 opacity)."""
        content_h = n * L.ROW_H
        view = L.LIST_BOTTOM - L.LIST_TOP
        if content_h <= view:
            return 0
        ys = [y for y in range(L.LIST_TOP, L.LIST_BOTTOM) if _close(f.rgb(L.SCROLL_X, y), L.SCROLL, 40)]
        if not ys:
            return None
        return int(round((min(ys) - L.LIST_TOP) / view * content_h))

    def _scroll_into_view(self, f, ident, row, n):
        if self.dry and f is None:
            self.content_y = 0
        for _ in range(10):
            if f is not None:
                cy = self.read_content_y(f, n)
                if cy is None:
                    raise NavAbort("cannot locate the list ScrollBar handle - calibrate the Wi-Fi list")
                self.content_y = cy
            rect = L.make_rect(row, self.content_y)
            if L.make_fully_visible(rect):
                return f
            view = L.LIST_BOTTOM - L.LIST_TOP
            want = max(0, min(n * L.ROW_H - view, row * L.ROW_H - (view - L.ROW_H) // 2))
            delta = want - self.content_y                    # >0: content must move up -> finger moves up
            move = max(-300, min(300, delta))
            y0 = L.LIST_BOTTOM - 20 if move > 0 else L.LIST_TOP + 20
            y1 = y0 - move
            x = L.DRAG_X
            # drag guard: a strip of the Make column over the drag span must still look like the list we
            # analysed (Make column is static; the name text may be elided/animated, so it is not used)
            g = (L.MAKE_X + 10, min(y0, y1), 20, abs(y1 - y0) + 1)
            f2 = self.tap("wifi.drag", f, ident, xy=(x, y0), rect=g, drag_to=(x, y1, 600), expect="wifi_list")
            if self.dry:
                self.content_y += move
                self._planned = None
            else:
                f = f2
        raise NavAbort("could not scroll row %d into view" % row)

    # ---------------------------------------------------------------- status-page commands ----------------
    def _status(self, want, what):
        f, ident = self.observe()
        if ident.label == "blank":
            self.wake(f, ident); f, ident = self.observe()
        if not ident.confident or ident.label not in want:
            raise NavAbort("%s refused: screen is %r, expected %s" % (what, ident, "/".join(sorted(want))))
        return f, ident

    def _await(self, labels, timeout, what):
        if self.dry:
            return None
        t0 = time.monotonic()
        while time.monotonic() - t0 < timeout:
            self.sleep(1.0)
            f, ident = self.observe()
            if ident.confident and ident.label in labels:
                return ident
        raise NavAbort("%s: did not reach %s within %ds" % (what, "/".join(labels), timeout))

    def start(self, f=None, ident=None):
        """Tap Start on a confirmed status_ready page. Requires the bridge to be idle (M2001 S1 start bug)."""
        self.check_bridge("start", required=True)
        self.check_probe("start")
        if f is None:
            f, ident = self._status({"status_ready"}, "start")
        self.tap("status.center", f, ident, armed=True, expect="status_printing")
        self._emit("start", "Start tapped")
        return self._await({"status_printing", "homing"}, 90, "start") or ident

    def cancel(self):
        """Back out of a loaded-but-not-started job: confirmed status_ready -> Cancel (680,421). In the QML
        Cancel (text 'Cancel' before Start) calls stopPrintBtnClicked + setPrintStatus(operational) and
        destroys the status page, revealing the Wi-Fi list it was opened from [O]."""
        f, ident = self._status({"status_ready"}, "cancel")
        self.tap("status.right", f, ident, armed=True, expect="wifi_list")
        if self.dry:
            return None
        self.sleep(0.5)
        f, ident = self.observe()
        if not (ident.confident and ident.label in ("wifi_list", "files", "home")):
            raise NavAbort("after Cancel the screen is %r (expected the Wi-Fi list)" % ident)
        return ident

    def pause(self):
        f, ident = self._status({"status_printing"}, "pause")
        self.tap("status.center", f, ident, armed=True, expect="status_paused")
        return self._await({"status_paused"}, 120, "pause")

    def resume(self):
        f, ident = self._status({"status_paused"}, "resume")
        self.check_bridge("resume", required=False)
        self.tap("status.center", f, ident, armed=True, expect="status_printing")
        return self._await({"status_printing"}, 120, "resume")

    def stop(self, confirmed=False):
        """Stop: tap Stop, VERIFY the stop-confirm dialog, then Yes (right) only if `confirmed`; else No."""
        f, ident = self._status({"status_printing", "status_paused"}, "stop")
        self.tap("status.right", f, ident, armed=True, expect="dialog_stop_confirm")
        if self.dry:
            self.tap("dialog.right" if confirmed else "dialog.left", None,
                     Ident("dialog_stop_confirm", "dialog", detail="planned"), expect="status_stopped")
            return None
        self.sleep(0.5)
        f, ident = self.observe()
        if not (ident.confident and ident.label == "dialog_stop_confirm"):
            raise NavAbort("after Stop the confirmation dialog was not recognised (%r); not tapping" % ident)
        if not confirmed:
            self.tap("dialog.left", f, ident)
            raise NavAbort("stop not confirmed: tapped No")
        self.tap("dialog.right", f, ident, expect="status_stopped")
        return self._await({"status_stopped", "status_complete", "home"}, 120, "stop")
