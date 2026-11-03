#!/usr/bin/env python3
"""Put the IVI Bridge API key everywhere OrcaSlicer 2.5 needs it (stdlib only, Python 3.9+).

  python3 ivi_setup_keys.py [--new-key] [--wait] [--config PATH] [--orca-dir DIR] [--dry-run]

Locations (each is patched only if the file exists; the placeholder or any old key is replaced):
  * bridge config  ~/.config/ivi-bridge/config.json           -> api_key (created if missing)
  * printer presets <orca>/user/*/machine/**/*.json (IVI3D or 127.0.0.1:5001) -> printhost_apikey
  * Device tab     <orca>/OrcaSlicer.conf local_machines["127.0.0.1:5001"].access_code
  * plugin         <orca>/orca_plugins/config.json  capability "IVI3D Bridge" -> cap_config.api_key
Orca files are backed up (<file>.bak-YYYYmmdd-HHMMSS) and written atomically. Orca rewrites its
files on quit, so this refuses to touch them while OrcaSlicer is running. The key is never printed
in full. Re-run it after importing IVI3D.orca_printer again (or use 'Fix IVI Bridge Key.command').
"""
import argparse, glob, json, os, secrets, shutil, subprocess, sys, tempfile, time
from collections import OrderedDict

PLACEHOLDER = "PASTE-API-KEY-FROM-IVI-BRIDGE-INSTALLER"
CAPABILITY = "IVI3D Bridge"
PLUGIN_KEY = "ivi3d_bridge_plugin"
DEFAULT_HOST = "127.0.0.1:5001"
EXIT_ORCA_RUNNING = 3

def mask(key):
    return (key[:4] + "…" + key[-2:]) if key and len(key) > 8 else "****"

def default_orca_dir():
    return os.path.expanduser("~/Library/Application Support/OrcaSlicer")

def default_config():
    return os.environ.get("IVI_BRIDGE_CONFIG") or os.path.expanduser("~/.config/ivi-bridge/config.json")

def orca_running():
    try:
        return subprocess.run(["pgrep", "-x", "OrcaSlicer"], stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL).returncode == 0
    except OSError:
        return False

def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=OrderedDict)

def write_atomic(path, text, mode=None, backup=False, stamp=None):
    if backup and os.path.exists(path):
        shutil.copy2(path, "%s.bak-%s" % (path, stamp or time.strftime("%Y%m%d-%H%M%S")))
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    if mode is None:
        mode = (os.stat(path).st_mode & 0o777) if os.path.exists(path) else 0o644
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text); f.flush(); os.fsync(f.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp): os.unlink(tmp)
        raise

def dump_tabs(obj):
    return json.dumps(obj, indent="\t", ensure_ascii=False) + "\n"

# ---------------------------------------------------------------- bridge key
def get_or_create_key(config_path, new_key=False, dry_run=False):
    """Returns (key, host, changed). Keeps an existing key unless new_key."""
    cfg = read_json(config_path) if os.path.exists(config_path) else OrderedDict()
    key = cfg.get("api_key")
    changed = False
    if new_key or not key or key == PLACEHOLDER:
        key = secrets.token_hex(16); cfg["api_key"] = key; changed = True
        if not dry_run:
            write_atomic(config_path, json.dumps(cfg, indent=2) + "\n", mode=0o600)
    host = "%s:%s" % (cfg.get("listen_host", "127.0.0.1"), cfg.get("listen_port", 5001))
    if host.startswith("0.0.0.0:"): host = "127.0.0.1:" + host.split(":", 1)[1]
    return key, host, changed

# ---------------------------------------------------------------- Orca files
def preset_files(orca_dir):
    out = []
    for p in sorted(glob.glob(os.path.join(orca_dir, "user", "*", "machine", "**", "*.json"), recursive=True)):
        try: d = read_json(p)
        except (ValueError, OSError): continue
        if not isinstance(d, dict) or "printhost_apikey" not in d: continue
        ours = ("IVI3D" in str(d.get("name", "")) or "IVI3D" in str(d.get("inherits", ""))
                or str(d.get("print_host", "")).startswith(("127.0.0.1:5001", "localhost:5001", "127.0.0.1:5000", "localhost:5000"))
                or d.get("printhost_apikey") == PLACEHOLDER)
        if ours: out.append((p, d))
    return out

def patch_presets(orca_dir, key):
    jobs = []
    for p, d in preset_files(orca_dir):
        if d.get("printhost_apikey") != key:
            d["printhost_apikey"] = key; jobs.append((p, d))
    return jobs

def patch_conf(orca_dir, key, host):
    p = os.path.join(orca_dir, "OrcaSlicer.conf")
    if not os.path.exists(p): return []
    c = read_json(p)
    lm = c.get("local_machines")
    if not isinstance(lm, dict): lm = c["local_machines"] = OrderedDict()
    m = lm.get(host)
    if not isinstance(m, dict):
        m = lm[host] = OrderedDict([("access_code", key), ("dev_ip", host), ("dev_name", host),
                                    ("printer_agent_id", "orca"), ("printer_type", "IVI3D")])
        return [(p, c)]
    if m.get("access_code") == key: return []
    m["access_code"] = key
    return [(p, c)]

def patch_plugin(orca_dir, key, host):
    p = os.path.join(orca_dir, "orca_plugins", "config.json")
    if not os.path.exists(p): return []
    c = read_json(p)
    lst = c.get("config")
    if not isinstance(lst, list): lst = c["config"] = []
    ent = next((e for e in lst if isinstance(e, dict) and e.get("capability") == CAPABILITY), None)
    if ent is None:
        ent = OrderedDict([("cap_config", OrderedDict([("api_key", key), ("bridge_url", "http://" + host),
                           ("poll_seconds", 3)])), ("capability", CAPABILITY),
                           ("capability_type", "pages"), ("plugin_key", PLUGIN_KEY), ("plugin_version", "")])
        lst.append(ent); return [(p, c)]
    cc = ent.get("cap_config")
    if not isinstance(cc, dict): cc = ent["cap_config"] = OrderedDict()
    if cc.get("api_key") == key and cc.get("bridge_url"): return []
    cc["api_key"] = key
    cc.setdefault("bridge_url", "http://" + host)
    return [(p, c)]

def setup(config_path, orca_dir, new_key=False, dry_run=False, running=None, log=print):
    """Returns (exit_code, key). exit 3 = Orca running (bridge key still created/kept)."""
    key, host, changed = get_or_create_key(config_path, new_key, dry_run)
    log("Bridge key %s (%s)" % (mask(key), "new" if changed else "kept"))
    if not os.path.isdir(orca_dir):
        log("OrcaSlicer folder not found; nothing else to patch."); return 0, key
    jobs = patch_presets(orca_dir, key) + patch_conf(orca_dir, key, host) + patch_plugin(orca_dir, key, host)
    if not jobs:
        log("Orca already has the current key everywhere."); return 0, key
    if (orca_running() if running is None else running()):
        log("OrcaSlicer is running. Quit it (Cmd-Q) and run this again; %d file(s) need the key." % len(jobs))
        return EXIT_ORCA_RUNNING, key
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for p, d in jobs:
        rel = os.path.relpath(p, orca_dir)
        if dry_run: log("would update " + rel); continue
        write_atomic(p, dump_tabs(d), backup=True, stamp=stamp)
        log("updated " + rel)
    return 0, key

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=default_config())
    ap.add_argument("--orca-dir", default=default_orca_dir())
    ap.add_argument("--new-key", action="store_true", help="replace the existing bridge key")
    ap.add_argument("--wait", action="store_true", help="wait for OrcaSlicer to quit instead of failing")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--key-only", action="store_true", help="only create/keep the bridge key; skip Orca")
    ap.add_argument("--print-key", action="store_true", help="print only the key on stdout (for the installer)")
    a = ap.parse_args(argv)
    log = (lambda m: print(m, file=sys.stderr)) if a.print_key else print
    if a.key_only:
        key, _, changed = get_or_create_key(a.config, a.new_key, a.dry_run)
        log("Bridge key %s (%s)" % (mask(key), "new" if changed else "kept"))
        if a.print_key: print(key)
        return 0
    if a.wait:
        warned = False
        while orca_running():
            if not warned: log("Waiting for OrcaSlicer to quit (Cmd-Q)…"); warned = True
            time.sleep(2)
    rc, key = setup(a.config, a.orca_dir, a.new_key, a.dry_run, log=log)
    if a.print_key: print(key)
    return rc

if __name__ == "__main__":
    sys.exit(main())
