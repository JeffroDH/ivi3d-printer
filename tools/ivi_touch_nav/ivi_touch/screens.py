"""Screen identification: structural priors from the QML layout + calibrated reference screenshots."""
import gzip, json, os, time
from . import layout as L
from .fb import Frame, color_close, grid_distance

ACCEPT = 8.0      # max masked mean-luminance difference (0..255) to accept a reference match
MARGIN = 3.0      # best label must beat the best *other* label by this much
GRID_CELL, DISC_CELL = 20, 10
DISC_TOP = 0.10   # discriminators: mean of the worst 10% cells


def family_of(label):
    if label.startswith("page:"):
        return "header"
    return L.FAMILY.get(label, label)


# ---------------------------------------------------------------- structural priors (uncalibrated) -------
def _frac(frame, pts, col, tol):
    ok = sum(1 for x, y in pts if color_close(frame.rgb(x, y), col, tol))
    return ok / len(pts)


def has_header(f):
    return _frac(f, [(x, 59) for x in range(130, 680, 25)], L.LINE, 30) >= 0.8


def prior_home(f):
    pts = []
    for cx in (122, 307, 492, 677):
        pts += [(cx - 60, 148), (cx + 60, 148), (cx - 60, 272), (cx + 60, 272)]
    return not has_header(f) and _frac(f, pts, L.TILE, 25) >= 0.85


def prior_files(f):
    seps = [(x, y) for y in (169, 279) for x in range(60, 760, 50)]
    return has_header(f) and _frac(f, seps, L.LINE, 30) >= 0.8 and not prior_wifi_list(f)


def prior_wifi_list(f):
    return has_header(f) and _frac(f, [(x, 421) for x in range(40, 760, 40)], L.LINE, 30) >= 0.8


def prior_dialog(f):
    corners = [(10, 10), (790, 10), (10, 470), (790, 470), (20, 240), (780, 240)]
    tinted = sum(1 for x, y in corners if 150 <= f.lum(x, y) <= 246)
    card = [(60, 70), (740, 70), (60, 410), (740, 410), (400, 60)]
    return tinted >= 5 and _frac(f, card, L.WHITE, 8) >= 0.8


def prior_status(f):
    pts = [(x, y) for y in (389, 453) for x in (90, 110, 130, 150)]
    return has_header(f) and _frac(f, pts, L.BLUE, 40) >= 0.75


PRIORS = {"home": prior_home, "files": prior_files, "wifi_list": prior_wifi_list,
          "dialog": prior_dialog, "status": prior_status, "header": has_header}


def prior_family(f):
    """Best-guess family from priors alone (order matters: dialogs overlay pages)."""
    if prior_dialog(f):
        return "dialog"
    for fam in ("home", "wifi_list", "files", "status"):
        if PRIORS[fam](f):
            return fam
    return "header" if has_header(f) else None


# ---------------------------------------------------------------- features ------------------------------
def _mask_grid(label, rows, cols, cell):
    m = [[False] * cols for _ in range(rows)]
    for (x, y, w, h) in L.masks_for(label) if not label.startswith("page:") else []:
        for r in range(rows):
            for c in range(cols):
                cx, cy = c * cell + cell // 2, r * cell + cell // 2
                if x <= cx < x + w and y <= cy < y + h:
                    m[r][c] = True
    return m


def features(frame, label):
    return {"grid": frame.grid(cell=GRID_CELL, step=5),
            "disc": [frame.grid(x, y, w, h, cell=DISC_CELL, step=2) for (x, y, w, h) in L.discriminators_for(label)]}


class Ident:
    def __init__(self, label, family, score=None, provisional=False, detail=""):
        self.label, self.family, self.score, self.provisional, self.detail = label, family, score, provisional, detail

    @property
    def confident(self):
        return not self.provisional and self.label not in ("unknown", "blank")

    def __repr__(self):
        p = " provisional" if self.provisional else ""
        s = "" if self.score is None else " score=%.1f" % self.score
        return "<%s%s%s %s>" % (self.label, p, s, self.detail)


class Classifier:
    def __init__(self, calib_dir=None):
        self.calib_dir = calib_dir
        self.refs = {}        # label -> [features]
        if calib_dir and os.path.exists(os.path.join(calib_dir, "refs.json")):
            with open(os.path.join(calib_dir, "refs.json")) as fh:
                self.refs = json.load(fh)

    HOME_ICON = "__home_icon__"          # template of an ENABLED Pagehead Home button (680,0,120,58)
    HOME_RECT = (680, 0, 120, 58)

    @property
    def calibrated_labels(self):
        return sorted(k for k in self.refs if not k.startswith("__"))

    def _dump(self):
        with open(os.path.join(self.calib_dir, "refs.json"), "w") as fh:
            json.dump(self.refs, fh)

    def save_home_icon(self, frame):
        self.refs.setdefault(self.HOME_ICON, []).append(frame.grid(*self.HOME_RECT, cell=DISC_CELL, step=2))
        self._dump()

    def home_icon_present(self, frame):
        """True only if a calibrated enabled-Home template matches (used for the unknown-page fallback)."""
        refs = self.refs.get(self.HOME_ICON)
        if not refs:
            return False
        g = frame.grid(*self.HOME_RECT, cell=DISC_CELL, step=2)
        return min(grid_distance(g, r, top=DISC_TOP) for r in refs) <= ACCEPT

    def save_reference(self, label, frame, note=""):
        os.makedirs(self.calib_dir, exist_ok=True)
        stem = "%s_%s" % (label.replace(":", "_"), time.strftime("%Y%m%d_%H%M%S"))
        n = 0
        while os.path.exists(os.path.join(self.calib_dir, stem + ".png")):
            n += 1; stem = stem.split("~")[0] + "~%d" % n
        frame.to_png(os.path.join(self.calib_dir, stem + ".png"))
        with gzip.open(os.path.join(self.calib_dir, stem + ".raw.gz"), "wb") as g:
            g.write(frame.data)
        feat = features(frame, label); feat.update(file=stem, note=note, stride=frame.stride)
        self.refs.setdefault(label, []).append(feat)
        self._dump()
        return stem

    def _score(self, frame, label, refs, cache):
        fg = cache.setdefault("grid", frame.grid(cell=GRID_CELL, step=5))
        mask = _mask_grid(label, len(fg), len(fg[0]), GRID_CELL)
        best = 255.0
        for ref in refs:
            g = grid_distance(fg, ref["grid"], mask)
            d = 0.0
            for (rect, rg) in zip(L.discriminators_for(label), ref["disc"]):
                key = ("disc",) + tuple(rect)
                if key not in cache:
                    cache[key] = frame.grid(*rect, cell=DISC_CELL, step=2)
                d = max(d, grid_distance(cache[key], rg, top=DISC_TOP))
            best = min(best, max(g, d))
        return best

    def identify(self, frame):
        if frame.is_blank():
            return Ident("blank", "blank", detail="uniform dark framebuffer")
        fam_prior = prior_family(frame)
        if self.calibrated_labels:
            cache = {}
            scored = sorted((self._score(frame, lab, refs, cache), lab) for lab, refs in self.refs.items()
                            if not lab.startswith("__"))
            best_s, best_l = scored[0]
            other = next((s for s, l in scored[1:] if l != best_l), 255.0)
            fam = family_of(best_l)
            prior_ok = fam in ("other",) or PRIORS.get(fam, lambda f: True)(frame)
            if best_s <= ACCEPT and other - best_s >= MARGIN and prior_ok:
                return Ident(best_l, fam, best_s, detail="ref match (next %.1f)" % other)
            why = "no ref <= %.1f" % ACCEPT if best_s > ACCEPT else (
                "ambiguous (next %.1f)" % other if other - best_s < MARGIN else "prior '%s' failed" % fam)
            if fam_prior:
                return Ident(fam_prior, fam_prior, best_s, provisional=True, detail="best ref %s: %s" % (best_l, why))
            return Ident("unknown", None, best_s, detail="best ref %s: %s" % (best_l, why))
        if fam_prior:
            return Ident(fam_prior, fam_prior, provisional=True, detail="uncalibrated (priors only)")
        return Ident("unknown", None, detail="no prior matched, uncalibrated")
