"""Offline simulator of the IVI3D QML UI: renders synthetic 800x480 BGRA framebuffers from the layouts in
ivi_touch.layout (QML-derived) and reacts to taps/drags like the app. Text is drawn as deterministic
pseudo-glyph bars so different strings give different pixels (enough to exercise the classifier)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ivi_touch import layout as L
from ivi_touch.fb import Frame

W, H = 800, 480
DARK, GREY6, BLACK = (0x33, 0x33, 0x33), (0x66, 0x66, 0x66), (0, 0, 0)


class Canvas:
    def __init__(self, bg=L.WHITE):
        px = bytes((bg[2], bg[1], bg[0], 255))
        self.buf = bytearray(px * (W * H))

    def rect(self, x, y, w, h, col):
        x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes((col[2], col[1], col[0], 255)) * (x1 - x0)
        for yy in range(y0, y1):
            o = (yy * W + x0) * 4
            self.buf[o:o + len(row)] = row

    def border(self, x, y, w, h, col, t=1):
        self.rect(x, y, w, t, col); self.rect(x, y + h - t, w, t, col)
        self.rect(x, y, t, h, col); self.rect(x + w - t, y, t, h, col)

    def text(self, x, y, s, col=DARK, scale=3, clip=None):
        """5x7 pseudo-glyph per char derived from the char code."""
        cx = x
        for ch in s:
            v = (ord(ch) * 2654435761) & 0xFFFFFFFF
            for gy in range(7):
                for gx in range(5):
                    if (v >> ((gy * 5 + gx) % 32)) & 1 and ch != " ":
                        px = cx + gx * scale
                        if clip and px + scale > clip:
                            continue
                        self.rect(px, y + gy * scale, scale, scale, col)
            cx += 6 * scale
        return cx

    def ctext(self, cx, y, s, col=DARK, scale=3):
        self.text(cx - len(s) * 3 * scale, y, s, col, scale)

    def tint(self, argb=(0x88, 0xD3, 0xD3, 0xD3)):
        a = argb[0] / 255.0
        tables = [bytes(int(round(v * (1 - a) + c * a)) for v in range(256)) for c in (argb[3], argb[2], argb[1])]
        b = bytes(self.buf)
        out = bytearray(len(b))
        for i in range(3):
            out[i::4] = b[i::4].translate(tables[i])
        out[3::4] = b[3::4]
        self.buf = out

    def frame(self):
        return Frame(bytes(self.buf), W, H, W * 4)


def header(c, title, home_enabled=True, back=True):
    c.rect(0, 59, W, 1, L.LINE)
    c.ctext(400, 18, title, DARK, 3)
    if back:
        c.text(20, 18, "<", DARK, 3)
    col = (0x19, 0x3A, 0xDD) if home_enabled else L.LINE
    c.rect(726, 14, 30, 4, col); c.rect(724, 18, 34, 24, col); c.rect(734, 28, 14, 14, L.WHITE)


class Sim:
    """State machine. `files`: {name: (mtime, ivi_sliced)}."""

    def __init__(self, state="home", files=None, blanked=False, retain_fb_when_blank=False):
        self.state = state
        self.files = files if files is not None else {}
        self.content_y = 0
        self.blanked = blanked
        self.retain = retain_fb_when_blank
        self.loaded = None
        self.started = 0                # number of times Start was tapped (must stay 0 unless --start)
        self.stack = []                 # what lies under a status page / dialog
        self.taps = []                  # (x, y, state_before)
        self.deleted = []
        self.under_dialog = "wifi_list"
        self.extra = ""                 # dynamic content variant
        self.home_toast = False
        self.work_fd = None             # app's Work QFile: opened at selection, never closed (check B)
        self.tail = False               # last part of a job: cache fd already closed at EOF

    # ---------------------------------------------------------------- render
    def order(self):
        return L.list_filter_sort([(t, n) for n, (t, _) in self.files.items()])

    def render(self):
        if self.blanked and not self.retain:
            return Canvas(BLACK).frame()
        return self._render(self.state).frame()

    def _render(self, st):
        if st == "home":
            c = Canvas()
            for cx, name in zip((122, 307, 492, 677), ("Files", "Control", "Tools", "Settings")):
                c.rect(cx - 72, 137, 145, 145, L.TILE)
                c.ctext(cx, 250, name, DARK, 2)
                c.rect(cx - 20, 170, 40, 40, (0x19, 0x3A, 0xDD))
            c.text(30, 420, "Head: FDM 0.4  IP 192.0.2.15" + self.extra, GREY6, 2)
            if self.extra:          # e.g. an animated badge inside the Files tile
                c.rect(60, 140, 3 * len(self.extra), 3, GREY6)
            c.ctext(400, 40, "IVI3D", DARK, 4)
            return c
        if st == "files":
            c = Canvas(); header(c, "Files")
            c.rect(0, 169, W, 1, L.LINE); c.rect(0, 279, W, 1, L.LINE)
            c.text(60, 105, "Local Files", DARK, 3)
            c.text(60, 215, "Print Files via WiFi", DARK, 3)
            if self.extra:
                c.text(60, 320, "USB Files", DARK, 3); c.rect(0, 389, W, 1, L.LINE)
            return c
        if st == "wifi_list":
            c = Canvas(); header(c, "Print Files via WiFi")
            order = self.order()
            n = len(order)
            for i, name in enumerate(order):
                top = L.LIST_TOP + i * L.ROW_H - self.content_y
                if top + L.ROW_H < L.LIST_TOP or top > L.LIST_BOTTOM:
                    continue
                c.text(30, top + 30, name[:22], DARK, 3)
                c.text(30, top + 80, "%d KB" % (len(name) * 37), GREY6, 2)
                mk_col = (0x19, 0x3A, 0xDD)
                c.rect(L.MAKE_X, top + L.MAKE_DY, L.MAKE_W, L.MAKE_H, mk_col)
                c.ctext(L.MAKE_X + L.MAKE_W // 2, top + L.MAKE_DY + 25, "Make", L.WHITE, 3)
                c.border(L.DELETE_X, top + L.MAKE_DY, 137, 70, L.STOP_RED, 2)
                c.ctext(L.DELETE_X + 68, top + L.MAKE_DY + 25, "Del", L.STOP_RED, 3)
                c.rect(0, top + L.ROW_H - 1, 780, 1, L.LINE)
            # re-draw header/info over clipped rows
            c.rect(0, 0, W, 59, L.WHITE); header(c, "Print Files via WiFi")
            c.rect(0, 420, W, 60, L.WHITE); c.rect(0, 421, W, 1, L.LINE)
            c.text(30, 440, "Used: 1.2GB  Size: 14GB", GREY6, 2)
            # scrollbar (AlwaysOn, opacity .75 over white)
            view = L.LIST_BOTTOM - L.LIST_TOP
            ch = max(view, n * L.ROW_H)
            hs = int(view * view / ch); ht = L.LIST_TOP + int(self.content_y / ch * view)
            sc = tuple(int(round(v * 0.75 + 255 * 0.25)) for v in L.SCROLL)
            c.rect(794, ht, 6, hs, sc)
            return c
        if st.startswith("dialog_"):
            c = self._render(self.under_dialog); c.tint()
            c.rect(40, 50, 720, 380, L.WHITE)
            spec = {
                "dialog_not_ivi": ("Notice", "This file was not sliced by IVI 3licer", "Cancel", "OK"),
                "dialog_print": ("Print " + (self.loaded or "?")[:20], "Time 1h20m Filament 12m", "Cancel", "Make"),
                "dialog_plate": ("Warning", "Please make sure the plate is clean", None, "OK"),
                "dialog_stop_confirm": ("Warning", "The printer will stop printing", "No", "Yes"),
                "dialog_delete_confirm": ("Notice", "Delete this file?", "Cancel", "Continue"),
                "dialog_lowtemp": ("Lower Temp", "The current low temperature", "Reset", "Cancel"),
            }[st]
            c.ctext(400, 100, spec[0], DARK, 3); c.ctext(400, 170, spec[1], GREY6, 2)
            if spec[2] is None:
                c.rect(90, 310, 620, 70, (0x19, 0x3A, 0xDD)); c.ctext(400, 335, spec[3], L.WHITE, 3)
            else:
                c.border(90, 310, 250, 70, L.LINE, 2); c.ctext(215, 335, spec[2], DARK, 3)
                c.rect(460, 310, 250, 70, (0x19, 0x3A, 0xDD)); c.ctext(585, 335, spec[3], L.WHITE, 3)
            return c
        if st.startswith("status_"):
            c = Canvas(); header(c, "Status", home_enabled=False)
            c.text(60, 90, "File: " + (self.loaded or "-")[:24], DARK, 2)
            pct = {"status_ready": 0, "status_printing": 37, "status_paused": 37, "status_stopped": 37,
                   "status_complete": 100}[st]
            c.rect(60, 130, 680, 16, L.LINE); c.rect(60, 130, int(6.8 * pct), 16, (0x19, 0x3A, 0xDD))
            c.text(60, 200, "Nozzle 210/210  Bed 60/60 " + self.extra, GREY6, 2)
            c.text(60, 300, "Left time 00:%02d:00" % (60 - pct // 2), GREY6, 2)
            blue = (0x19, 0x3A, 0xDD)
            c.rect(30, 386, 180, 70, blue); c.ctext(120, 410, "Control", L.WHITE, 2)
            centre = {"status_ready": "Start", "status_printing": "Pause", "status_paused": "Continue",
                      "status_stopped": "Reprint", "status_complete": "Reprint"}[st]
            c.rect(310, 386, 180, 70, blue); c.ctext(400, 410, centre, L.WHITE, 2)
            if st == "status_complete":
                c.rect(590, 386, 180, 70, blue); c.ctext(680, 410, "Complete", L.WHITE, 2)
            else:
                c.border(590, 386, 180, 70, L.STOP_RED, 1)
                c.ctext(680, 410, "Stop" if st in ("status_printing", "status_paused") else "Cancel", L.STOP_RED, 2)
            return c
        if st == "page:settings":
            c = Canvas(); header(c, "Settings")
            for i, s in enumerate(("Language", "Wi-Fi", "About", "Factory reset")):
                c.text(60, 90 + i * 90, s, DARK, 3); c.rect(0, 150 + i * 90, W, 1, L.LINE)
            return c
        if st == "page:control":
            c = Canvas(); header(c, "Control")
            for i in range(3):
                for j in range(4):
                    c.border(60 + j * 175, 90 + i * 110, 150, 90, L.LINE, 2)
                    c.ctext(135 + j * 175, 125 + i * 110, "X+%d" % (i * 4 + j), DARK, 2)
            return c
        if st == "page:wifi_setup":          # an unmodelled page WITH an enabled Home button
            c = Canvas(); header(c, "Network")
            c.text(60, 100, "SSID: lab-net", DARK, 3); c.text(60, 200, "Password ********", DARK, 3)
            c.rect(560, 380, 200, 60, (0x19, 0x3A, 0xDD))
            return c
        if st == "garbage":                   # something we have never seen and that has no header
            c = Canvas((0x20, 0x60, 0x20))
            c.rect(100, 100, 600, 280, (0xF0, 0xE0, 0x10)); c.ctext(400, 220, "FIRMWARE UPDATE", BLACK, 4)
            return c
        if st == "homing":
            c = Canvas(); header(c, "Homing", home_enabled=False); c.ctext(400, 240, "Homing...", DARK, 3)
            return c
        raise ValueError(st)

    # ---------------------------------------------------------------- input
    def tap(self, x, y):
        self.taps.append((x, y, self.state))
        if self.blanked:
            self.blanked = False              # first touch only wakes the panel (assumed) and is swallowed
            return
        st = self.state
        inr = lambda r: r[0] <= x < r[0] + r[2] and r[1] <= y < r[1] + r[3]
        home_btn = (680, 0, 120, 58)
        if st == "home":
            if inr((50, 137, 145, 145)):
                self.state = "files"
            elif inr((235, 137, 145, 145)):
                self.state = "page:control"
            elif inr((605, 137, 145, 145)):
                self.state = "page:settings"
        elif st == "files":
            if inr(home_btn):
                self.state = "home"
            elif inr((0, 170, 800, 110)):
                self.state = "wifi_list"; self.content_y = 0
        elif st == "wifi_list":
            if inr(home_btn):
                self.state = "home"; return
            order = self.order()
            for i, name in enumerate(order):
                top = L.LIST_TOP + i * L.ROW_H - self.content_y
                if not (L.LIST_TOP <= y < L.LIST_BOTTOM):
                    break
                if inr((L.MAKE_X, top + L.MAKE_DY, L.MAKE_W, L.MAKE_H)):
                    self.loaded = name
                    self.under_dialog = "wifi_list"
                    self.state = "dialog_print" if self.files[name][1] else "dialog_not_ivi"
                    return
                if inr((L.DELETE_X, top + L.MAKE_DY, 137, 70)):
                    self.deleted.append(name); self.under_dialog = "wifi_list"
                    self.state = "dialog_delete_confirm"; return
        elif st == "dialog_not_ivi":
            if inr(L.TAPS["dialog.right"][2]):
                self.state = "dialog_print"
            elif inr(L.TAPS["dialog.left"][2]):
                self.state = "wifi_list"
        elif st == "dialog_print":
            if inr(L.TAPS["dialog.right"][2]):
                self.under_dialog = "status_ready"; self.state = "dialog_plate"
                self.work_fd = "/userdata/WifiFile/" + self.loaded      # readyPrintint -> startWorkFile
            elif inr(L.TAPS["dialog.left"][2]):
                self.state = "wifi_list"
        elif st == "dialog_plate":
            if inr(L.TAPS["dialog.one"][2]):
                self.state = "status_ready"
        elif st == "dialog_delete_confirm":
            if inr(L.TAPS["dialog.left"][2]):
                self.state = "wifi_list"
        elif st == "dialog_stop_confirm":
            if inr(L.TAPS["dialog.left"][2]):
                self.state = self.under_dialog
            elif inr(L.TAPS["dialog.right"][2]):
                self.state = "status_stopped"
        elif st == "dialog_lowtemp":
            if inr(L.TAPS["dialog.left"][2]):
                self.reset_temp = True; self.state = self.under_dialog
            elif inr(L.TAPS["dialog.right"][2]):
                self.state = self.under_dialog
        elif st == "status_ready":
            if inr(L.TAPS["status.center"][2]):
                self.started += 1; self.state = "status_printing"
            elif inr(L.TAPS["status.right"][2]):
                self.loaded = None; self.state = "wifi_list"
        elif st == "status_printing":
            if inr(L.TAPS["status.center"][2]):
                self.state = "status_paused"
            elif inr(L.TAPS["status.right"][2]):
                self.under_dialog = st; self.state = "dialog_stop_confirm"
        elif st == "status_paused":
            if inr(L.TAPS["status.center"][2]):
                self.state = "status_printing"
            elif inr(L.TAPS["status.right"][2]):
                self.under_dialog = st; self.state = "dialog_stop_confirm"
        elif st in ("status_stopped", "status_complete"):
            if inr(L.TAPS["status.right"][2]):
                self.loaded = None; self.state = "wifi_list"
        elif st.startswith("page:"):
            if inr(home_btn):
                self.state = "home"

    def drag(self, x, y0, y1):
        self.taps.append((x, y0, self.state + ":drag"))
        if self.blanked:
            self.blanked = False; return
        if self.state != "wifi_list":
            return
        n = len(self.order())
        dist = (y0 - y1)
        dist = dist - 10 if dist > 0 else dist + 10       # Qt drag threshold eats ~10 px
        mx = max(0, n * L.ROW_H - (L.LIST_BOTTOM - L.LIST_TOP))
        self.content_y = max(0, min(mx, self.content_y + dist))

    def open_files(self):
        """Model of the app's fds (Offline check B): the Work fd on the last selected file persists;
        while printing/paused a second (cache) fd is open on the same file, except in the tail."""
        fds = [self.work_fd] if self.work_fd else []
        printing = self.state in ("status_printing", "status_paused") or (
            self.state == "dialog_stop_confirm" and self.under_dialog in ("status_printing", "status_paused"))
        if printing and not self.tail:
            fds.append("/userdata/WifiFile/" + (self.loaded or "x.gcode"))
            if not self.work_fd:
                fds.append("/userdata/WifiFile/" + (self.loaded or "x.gcode"))
        return fds
