#!/usr/bin/env python3
"""ivi_touch.py - drive the IVI3D touchscreen app from the Mac over SSH (virtual touch + fb0 screenshots).

  ivi_touch.py goto-print FILE [--start] [--dry-run] [--bump]   navigate to Start for FILE (stops before Start
                                                                unless --start)
  ivi_touch.py start | pause | resume | stop [--yes]            status-page actions, each screen-verified
  ivi_touch.py cancel                                           back out of a loaded job (status page
                                                                Cancel, before Start only)
  ivi_touch.py screenshot [-o out.png] | identify               grab / classify the current screen
  ivi_touch.py calibrate --manual | --label LABEL               capture reference screenshots (run first!)
  ivi_touch.py install-helper | check                           push / verify /tmp/ivitap2 on the printer
  ivi_touch.py upload FILE [--name N] [--goto [--start]]        HTTP upload to the printer's Wi-Fi list (:8080)

Nothing is installed on the printer except the static /tmp/ivitap2 helper (lost on reboot by design).
"""
import argparse, getpass, hashlib, os, sys


def _read(path):
    with open(path, "rb") as fh:
        return fh.read()

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ivi_touch import layout as L                           # noqa: E402
from ivi_touch.nav import Navigator, NavAbort                # noqa: E402
from ivi_touch.runlog import RunLog                          # noqa: E402
from ivi_touch.safety import HTTPBridgeState                 # noqa: E402
from ivi_touch.screens import Classifier, prior_family, family_of   # noqa: E402
from ivi_touch.transport import Device, SSHTransport, TransportError   # noqa: E402

HELPER_LOCAL = os.path.join(HERE, "device", "ivitap2_armel")
STATE = os.path.expanduser(os.environ.get("IVI_TOUCH_HOME", "~/.ivi_touch"))

CAL_GUIDE = [
    ("home", "the HOME screen (4 tiles: Files / Control / ...)"),
    ("files", "Files page (Home > Files) - with NO USB stick inserted"),
    ("wifi_list", "Print Files via WiFi list (Files > Print Files via WiFi), showing >= 1 file"),
    ("dialog_print", "the print dialog after tapping Make on a file sliced by IVI 3licer (do NOT confirm yet)"),
    ("dialog_plate", "the plate warning after tapping Make in the print dialog"),
    ("status_ready", "the status page with Start / Cancel after dismissing the plate warning (then tap Cancel)"),
    ("dialog_not_ivi", "[optional] the 'not sliced by IVI' notice (Make on a non-IVI file)"),
    ("page:control", "[optional] any other page with a header, e.g. Home > Control"),
    ("page:settings", "[optional] another header page, e.g. Home > Settings"),
    ("status_printing", "[optional, during a real print] status page while printing"),
    ("status_paused", "[optional, during a real print] status page while paused"),
    ("dialog_stop_confirm", "[optional, during a real print] Stop -> Warning No/Yes dialog (then tap No)"),
    ("status_complete", "[optional] status page after a print completed"),
]


def build(args, dry=None):
    host = args.host or os.environ.get("IVI_HOST")
    if not host:
        sys.exit("set --host or IVI_HOST (printer IP)")
    t = SSHTransport(host, key=args.key, control_path=os.path.join(STATE, "cm-%C"))
    dev = Device(t, dry_run=args.dry_run if dry is None else dry, settle_ms=args.settle_ms)
    clf = Classifier(args.calib)
    bridge = None if args.no_bridge_check else HTTPBridgeState(base=args.bridge_url, config_path=args.bridge_config)
    return t, dev, clf, bridge


def check_helper(dev, install=False):
    want = hashlib.md5(_read(HELPER_LOCAL)).hexdigest()
    have = dev.helper_status()
    if have == want:
        return True
    if not install:
        sys.exit("printer helper /tmp/ivitap2 is %s (want md5 %s). Run: ivi_touch.py install-helper"
                 % ("missing" if have == "MISSING" else "different", want))
    got = dev.install_helper(HELPER_LOCAL)
    if got != want:
        sys.exit("helper upload failed (md5 %s)" % got)
    print("installed /tmp/ivitap2 (md5 %s)" % got)
    return True


def confirm(q):
    try:
        return input(q + " [type yes]: ").strip().lower() == "yes"
    except EOFError:
        return False


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", help="printer IP (or IVI_HOST)")
    ap.add_argument("--key", default=os.environ.get("IVI_KEY", "~/.ssh/ivi_ecdsa"), help="ECDSA private key")
    ap.add_argument("--calib", default=os.path.join(STATE, "calib"))
    ap.add_argument("--logdir", default=os.path.join(STATE, "runs"))
    ap.add_argument("--dry-run", action="store_true", help="plan only: grab + classify, print taps, inject nothing")
    ap.add_argument("--no-bridge-check", action="store_true", help="skip the Mac bridge job check (NOT for --start)")
    ap.add_argument("--bridge-url", default=None, help="default from ~/.config/ivi-bridge/config.json")
    ap.add_argument("--bridge-config", default=None)
    ap.add_argument("--probe", choices=("stream", "strict", "off"), default="stream",
                    help="open-file probe: stream (default) refuses only while a file is being streamed "
                         "(2 fds); strict refuses on any open print file; off skips it")
    ap.add_argument("--no-probe", action="store_true", help="same as --probe off")
    ap.add_argument("--settle-ms", type=int, default=800)
    ap.add_argument("--max-steps", type=int, default=25)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("goto-print"); g.add_argument("file"); g.add_argument("--start", action="store_true")
    g.add_argument("--bump", action="store_true", help="touch FILE so it sorts to the top of the list")
    sub.add_parser("start"); sub.add_parser("pause"); sub.add_parser("resume"); sub.add_parser("cancel")
    s = sub.add_parser("stop"); s.add_argument("--yes", action="store_true", help="skip the typed confirmation")
    sc = sub.add_parser("screenshot"); sc.add_argument("-o", "--out", default="ivi_screen.png")
    sub.add_parser("identify")
    c = sub.add_parser("calibrate"); cg = c.add_mutually_exclusive_group(required=True)
    cg.add_argument("--manual", action="store_true"); cg.add_argument("--label")
    c.add_argument("--force", action="store_true", help="save even if the structural prior disagrees")
    sub.add_parser("install-helper"); sub.add_parser("check")
    u = sub.add_parser("upload"); u.add_argument("file"); u.add_argument("--name")
    u.add_argument("--port", type=int, default=8080)
    u.add_argument("--overwrite", action="store_true", help="allow replacing a file of the same name")
    u.add_argument("--no-ssh", action="store_true", help="don't check for an existing name over SSH")
    u.add_argument("--goto", action="store_true", help="then navigate to Start for it (stops before Start)")
    u.add_argument("--start", action="store_true", help="with --goto: also tap Start")
    args = ap.parse_args(argv)
    if args.cmd == "goto-print" and args.start and args.no_bridge_check:
        sys.exit("--start cannot be combined with --no-bridge-check")
    if args.cmd == "upload" and args.start and (args.no_bridge_check or not args.goto):
        sys.exit("upload --start needs --goto and the bridge check")
    if args.cmd == "start" and args.no_bridge_check:
        sys.exit("start requires the bridge check")
    os.makedirs(STATE, exist_ok=True)

    t, dev, clf, bridge = build(args)
    try:
        if args.cmd == "install-helper":
            check_helper(dev, install=True); return 0
        if args.cmd == "check":
            check_helper(dev); f = dev.grab()
            print("helper OK; fb", dev.fbinfo, "; screen:", clf.identify(f)); return 0
        if args.cmd == "screenshot":
            f = dev.grab(); f.to_png(args.out); print("saved", args.out, dev.fbinfo); return 0
        if args.cmd == "identify":
            f = dev.grab(); print(clf.identify(f)); return 0
        if args.cmd == "calibrate":
            return calibrate(args, dev, clf)
        if args.cmd == "upload":
            rc = do_upload(args, dev)
            if rc or not args.goto:
                return rc
            args.cmd, args.file = "goto-print", args.uploaded_name
        if not args.dry_run:
            check_helper(dev)
        log = RunLog(args.logdir, args.cmd.replace("-", "_"))
        nav = Navigator(dev, clf, bridge=bridge, log=log, max_steps=args.max_steps, settle_ms=args.settle_ms,
                        allow_bump=getattr(args, "bump", False),
                        printing_probe="off" if args.no_probe else args.probe)
        if not clf.calibrated_labels:
            print("WARNING: no calibration found in %s - every screen will be 'provisional' and NO taps will be "
                  "made. Run: ivi_touch.py calibrate --manual" % args.calib)
        try:
            if args.cmd == "goto-print":
                r = nav.goto_print(args.file, start=args.start)
            elif args.cmd == "start":
                if not args.dry_run and not confirm("Start the print that is loaded on the printer?"):
                    print("not confirmed"); return 1
                r = nav.start()
            elif args.cmd == "cancel":
                r = nav.cancel()
            elif args.cmd == "pause":
                r = nav.pause()
            elif args.cmd == "resume":
                r = nav.resume()
            elif args.cmd == "stop":
                ok = args.yes or args.dry_run or confirm("STOP the running print (cannot be resumed)?")
                r = nav.stop(confirmed=ok)
            print("OK:", r, "| log:", log.dir)
            log.close()
            if args.dry_run:
                print("planned taps:\n  " + "\n  ".join(nav.plan or ["(none)"]))
            return 0
        except NavAbort as e:
            log.event("abort", str(e))
            print("ABORTED:", e, "| log:", log.dir)
            return 2
    except TransportError as e:
        print("SSH/transport error:", e); return 3


def do_upload(args, dev):
    from ivi_touch import upload as U
    try:
        name = U.check_name(args.name or os.path.basename(args.file))
    except U.UploadError as e:
        sys.exit("%s\n  suggestion: --name %s" % (e, U.safe_name(args.file)))
    if not args.no_ssh:
        names = [n for _, n in dev.list_wifi()]
        if name in names and not args.overwrite:
            sys.exit("%s already exists on the printer (the server would overwrite it); use --overwrite or --name"
                     % name)
    host = args.host or os.environ.get("IVI_HOST")
    if args.dry_run:
        print("DRY (nothing sent):", U.curl_command(host, args.file, name, args.port))
        args.goto = False
        return 0
    try:
        txt = U.upload(host, args.file, name, port=args.port)
    except U.UploadError as e:
        print("UPLOAD FAILED:", e); return 4
    print("uploaded %s -> /userdata/WifiFile/%s (%s)" % (args.file, name, txt))
    args.uploaded_name = name
    if args.goto:
        import time
        time.sleep(2.0)            # FileSystemWatcher refresh of the Wi-Fi list
    return 0


def calibrate(args, dev, clf):
    items = [(args.label, "")] if args.label else CAL_GUIDE
    for label, desc in items:
        if args.manual:
            ans = input("\nNavigate the printer BY HAND to %s.\n  Enter = capture as '%s', s = skip, q = quit: "
                        % (desc, label)).strip().lower()
            if ans == "q":
                break
            if ans == "s":
                continue
        f = dev.grab()
        fam = family_of(label)
        pf = prior_family(f)
        exp = {"header": ("header", "files", "wifi_list", "status"), "other": (pf,)}.get(fam, (fam,))
        if pf not in exp and not args.force:
            print("  ! layout check failed: '%s' expects family %s, structure looks like %r. The QML geometry may "
                  "not match this panel - NOT saved (use --force after checking the PNG)." % (label, fam, pf))
            f.to_png(os.path.join(args.calib if os.path.isdir(args.calib) else ".", "rejected_%s.png"
                                  % label.replace(":", "_")))
            continue
        stem = clf.save_reference(label, f)
        if label in ("files", "wifi_list") or label.startswith("page:"):
            clf.save_home_icon(f)
        back = clf.identify(f)
        print("  saved %s (%s); re-identifies as %r" % (label, stem, back))
    print("calibrated labels:", ", ".join(clf.calibrated_labels))
    return 0


if __name__ == "__main__":
    sys.exit(main())
