"""Screen geometry derived from the stock QML (qrc_full, app v1.222). All values are UNVERIFIED on the real
panel until `ivi_touch.py calibrate` has captured reference screenshots (see README)."""
import fnmatch

W, H = 800, 480

# ---- colours from the QML ----------------------------------------------------------------------------
WHITE = (0xFF, 0xFF, 0xFF)
TILE = (0xE7, 0xF0, 0xFF)          # home tiles  (main.qml filesBtn/controlBtn/... color)
LINE = (0xDD, 0xDD, 0xDD)          # Pagehead bottom line / list separators / disabled button
BLUE = (0x19, 0x3A, 0xDD)          # enabled TTextBtn / TImgTextBtn2 (Make, Start/Pause, Control, OK)
SCROLL = (0xBE, 0xD1, 0xFF)        # WifiFileListPage ScrollBar handle
STOP_RED = (0xF4, 0x61, 0x3B)      # Stop/Cancel border
DIALOG_TINT = "#88D3D3D3"          # TTextDialog/TTitleDialog Window colour (ARGB, blended over the page)

# ---- tap targets: name -> (tap_x, tap_y, guard_rect(x,y,w,h)) --------------------------------------------
TAPS = {
    "home.files":    (122, 209, (50, 137, 145, 145)),
    "files.wifi":    (400, 225, (200, 180, 400, 90)),     # "Print Files via WiFi" row (0,170,800,110)
    "page.home":     (740, 29, (680, 0, 120, 58)),        # Pagehead Home button
    "dialog.left":   (215, 345, (90, 310, 250, 70)),
    "dialog.right":  (585, 345, (460, 310, 250, 70)),
    "dialog.one":    (400, 345, (90, 310, 620, 70)),
    "status.center": (400, 421, (310, 386, 180, 70)),     # Start / Pause / Continue / Reprint
    "status.right":  (680, 421, (590, 386, 180, 70)),     # Cancel / Stop / Complete
    "wake":          (400, 472, (300, 460, 200, 20)),     # inert on every page we model [I]
}

# ---- Wi-Fi list (WifiFileListPage.qml) -------------------------------------------------------------------
LIST_TOP, LIST_BOTTOM = 60, 420          # ListView: y 60, height 480-60-60
ROW_H = 128
MAKE_X, MAKE_W, MAKE_DY, MAKE_H = 484, 137, 37, 70   # Make button: x 30+417+37, top = row_top+37
DELETE_X = 633                            # Delete button starts here - NEVER tap x > MAKE_X+MAKE_W (621)
MAX_LIST_TAP_X = MAKE_X + MAKE_W          # 621
SCROLL_X = 796                            # ScrollBar (x 792..800), handle colour SCROLL
DRAG_X = 250                              # drag column inside the file-name text (no buttons there)
NAME_FILTERS = ["*.g", "*.gcode", "*.Gcode", "*.NC", "*.CNC", "*.nc", "*.cnc"]


def list_filter_sort(entries):
    """entries: [(mtime_epoch, name)] from /userdata/WifiFile. Mimics FolderListModel{showDirs:false,
    sortField: Time, sortReversed:false, nameFilters, showOnlyReadable}: QDir::Time = newest first [I];
    ties broken by name [I]. Hidden (dot) files are excluded."""
    keep = [(t, n) for t, n in entries if not n.startswith(".") and any(fnmatch.fnmatchcase(n, p) for p in NAME_FILTERS)]
    keep.sort(key=lambda e: (-e[0], e[1]))
    return [n for _, n in keep]


def make_rect(row_index, content_y):
    top = LIST_TOP + row_index * ROW_H - content_y + MAKE_DY
    return (MAKE_X, top, MAKE_W, MAKE_H)


def make_fully_visible(rect):
    x, y, w, h = rect
    return y >= LIST_TOP + 2 and y + h <= LIST_BOTTOM - 2


# ---- regions ignored by the global signature (dynamic content) -------------------------------------------
MASKS = {
    "home":   [(0, 400, 800, 80), (180, 20, 440, 100)],                  # head type / IP / toast
    "files":  [(0, 280, 800, 110), (180, 20, 440, 100)],                 # USB row (optional) / toast
    "wifi_list": [(0, 60, 800, 420)],                                    # rows + disk usage (dynamic)
    "dialog": [(0, 0, 800, 50), (0, 430, 800, 50), (0, 50, 40, 380), (760, 50, 40, 380)],  # tinted page around card
    "dialog_print": [(80, 90, 640, 200)],                                # title w/ file name + info row
    "status": [(0, 60, 800, 322)],                                       # progress, file, temps, time
}
# label -> family; family selects the structural prior and the default masks
FAMILY = {
    "home": "home", "files": "files", "wifi_list": "wifi_list",
    "dialog_not_ivi": "dialog", "dialog_print": "dialog", "dialog_plate": "dialog",
    "dialog_stop_confirm": "dialog", "dialog_delete_confirm": "dialog",
    "status_ready": "status", "status_printing": "status", "status_paused": "status",
    "status_stopped": "status", "status_complete": "status",
    "forbidden": "other", "homing": "header",
}
# finer regions that must ALSO match the reference (they carry the distinguishing text/images)
DISCRIMINATORS = {
    "dialog": [(90, 300, 620, 90), (100, 90, 600, 60)],        # button row (texts) + title row
    "dialog_print": [(90, 300, 620, 90)],
    "status": [(30, 386, 740, 70)],                            # Control/Start|Pause|Continue|Reprint / Cancel|Stop|Complete
    "wifi_list": [(120, 0, 560, 58)],                          # header title text
    "files": [(0, 60, 800, 220)],
    "home": [(50, 137, 700, 200)],
    "header": [(120, 0, 560, 58)],                             # page title (homing, page:* pages)
}

PRINTING_LABELS = {"status_printing", "status_paused", "forbidden", "homing"}
DIALOG_LABELS = {k for k, v in FAMILY.items() if v == "dialog"}


def masks_for(label):
    fam = FAMILY.get(label, label)
    return MASKS.get(label, []) + (MASKS.get(fam, []) if label != fam else [])


def discriminators_for(label):
    fam = "header" if label.startswith("page:") else FAMILY.get(label, label)
    return DISCRIMINATORS.get(label) or DISCRIMINATORS.get(fam, [])
