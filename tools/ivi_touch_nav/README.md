# ivi_touch_nav: screen-aware virtual-touch navigation for the IVI3D

`ivi_touch.py` runs **on the Mac**, next to `ivi_bridge.py`. It drives the stock Qt touchscreen app (IVI-Main-Controller v1.222 on the Allwinner A33) the same way a finger would:

1. It grabs `/dev/fb0` over SSH and works out which screen is showing.
2. It injects a guarded tap through a tiny static helper.
3. It repeats until the **Print/Start button for the file you named** is in front of it.

> **Mac or printer?** All the logic, calibration data, logs and screenshots stay on the Mac. The only thing that goes onto the printer is the 53 KB static `ivitap2` binary, copied to `/tmp/ivitap2` (RAM, gone after a reboot) with `ivi_touch.py install-helper`. BusyBox `dd`, `gzip`, `date`, `ls` and `pidof`, which are already on the printer, do the rest. Nothing is installed persistently, and the printer's startup scripts and app are not changed.

Status: everything below was built and tested **offline**. It ran against synthetic framebuffers drawn from the QML layouts, through a mocked SSH transport. Nothing has run on the printer, the board or the Mac. Tags used below: **[O]** observed in the firmware, QML or binaries; **[I]** inferred and still needs checking on the real printer.

---

## 1. Files

| Path | What |
|---|---|
| `ivi_touch.py` | Command-line tool: `goto-print FILE`, `start`, `cancel`, `pause`, `resume`, `stop`, `upload FILE`, `screenshot`, `identify`, `calibrate`, `install-helper`, `check` |
| `ivi_touch/upload.py` | HTTP upload to the printer's own kore server (`POST :8080/api/v1/upload`, see §12) |
| `ivi_touch/api.py` | Importable API: `with session(host) as nav: nav.goto_print(...)` |
| `ivi_touch/nav.py` | The navigator: state machine, recovery, list scrolling, file selection, status-page actions |
| `ivi_touch/screens.py` | Screen classifier: QML structural priors plus calibrated reference signatures |
| `ivi_touch/layout.py` | Geometry and colours taken from the QML: tap targets, guard rectangles, list maths, masks |
| `ivi_touch/transport.py` | SSH transport (ControlMaster, non-login exec only) and the on-device command set |
| `ivi_touch/safety.py` | Bridge-state hook (reads the running bridge's HTTP API; `ivi_bridge.py` is not modified) |
| `ivi_touch/fb.py`, `runlog.py` | Framebuffer decoding, region hash, pure-Python PNG writer, per-run logs |
| `device/ivitap2.c`, `device/ivitap2_armel` | On-device helper: static, armel soft-float EABI5, sha256 `4ea44039…f3c0a8` |
| `tests/` | Simulator (`sim.py`), mock SSH (`mock_transport.py`), fake kore upload server, 49 unit tests (`test_nav.py`), C/Python hash parity harness, `test_results.txt` |
| `sample_run/` | Four logged runs from the simulator, each with a PNG for every step |

Requirements: Python 3.8 or later on the Mac (standard library only) and the system `ssh` (OpenSSH 7.6 or later, for `accept-new`).

---

## 2. Quick start (in order)

1. **sshd on the printer**: follow [docs/a33.md](../../docs/a33.md) and [docs/home_session/RUNBOOK.md](../../docs/home_session/RUNBOOK.md): ephemeral sshd, ECDSA user key `~/.ssh/ivi_ecdsa`.
2. `export IVI_HOST=<printer-ip>`, plus `IVI_KEY` if the key isn't at `~/.ssh/ivi_ecdsa`.
3. `./ivi_touch.py install-helper`, then `./ivi_touch.py check`. Check prints the fb geometry (`stride`, `pan`, `bpp`) and the current screen.
4. `./ivi_touch.py screenshot -o now.png`. Open the PNG and confirm the colours and orientation look right.
5. **Calibrate**: `./ivi_touch.py calibrate --manual` (see §7). Until this is done every screen comes back "provisional" and **no taps are made**.
6. `./ivi_touch.py identify` on a few screens. Each should print a confident label (score ≤ 8, margin ≥ 3).
7. `./ivi_touch.py --dry-run goto-print benchy.gcode`. This plans the taps, saves screenshots and injects nothing.
8. `./ivi_touch.py goto-print benchy.gcode`. This stops on the status page with Start showing.
9. When you are happy: `./ivi_touch.py start` (asks you to type `yes`), or in one go `./ivi_touch.py goto-print benchy.gcode --start`.

Other commands:
- `./ivi_touch.py cancel`: on a confirmed status page *before* Start, taps Cancel and checks that the Wi-Fi list is back.
- `./ivi_touch.py pause`, `resume`, `stop`. `stop` asks you to type `yes`, or takes `--yes`.
- `./ivi_touch.py upload FILE [--name NAME] [--goto [--start]]`: HTTP upload into the Wi-Fi list (§12).

Logs go to `~/.ivi_touch/runs/<timestamp>_<cmd>/`:
- `log.txt` (readable log);
- `steps.jsonl` (one JSON record per step);
- one PNG per grabbed frame.

---

## 3. The SSH invocation (and why)

```
ssh -i ~/.ssh/ivi_ecdsa -T \
    -o BatchMode=yes -o UserKnownHostsFile=~/.ssh/ivi_known_hosts -o StrictHostKeyChecking=accept-new \
    -o HostKeyAlgorithms=ecdsa-sha2-nistp256 -o ConnectTimeout=8 \
    -o ControlMaster=auto -o ControlPath=~/.ivi_touch/cm-%C -o ControlPersist=600 -o ServerAliveInterval=15 \
    root@$IVI_HOST -- 'PATH=/bin:/sbin:/usr/bin:/usr/sbin; <command>'
```

**Always send a non-empty remote command.**
- With a command, OpenSSH 5.8 runs `/bin/sh -c '<command>'` as root's shell, which is BusyBox ash. That shell is **non-login and non-interactive**, so `/etc/profile` is **not** read [O: readiness report]. That matters because `/etc/profile` runs `setup_module.sh`, extra watchdogs, and `autorun.sh`, which restarts wlan0 and starts a *second* IVI-Main-Controller.
- There is no `/etc/sshrc` and no `~/.ssh/rc` in the image [O], so nothing else runs either.
- A session *without* a command would be a login shell (`-sh`) and would run all of the above. `SSHTransport.run()` therefore **refuses an empty or blank command** (this is unit-tested).

**`-T` (no pty)** keeps stdout byte-exact for the gzip'd framebuffer. Never use `-t`.

**ControlMaster/ControlPersist**: one TCP connection and one key exchange (slow on the A33) per 10 minutes. After that, each step is one exec channel.

**One round trip per step**:
- Guarded tap + `usleep` settle + fb grab go in **a single command**.
- The grab that comes back with the tap is reused as the next screen check.
- A typical `goto-print` from Home is about 10–14 SSH exec calls in total.

**`PATH=` is pinned** because sshd gives exec sessions a minimal environment. The applets used (`dd gzip date ls pidof md5sum usleep touch sed grep`) are all in this BusyBox 1.18.3 build [O].

**ECDSA nistp256** for both the host key and the user key: OpenSSH 5.8 has no ed25519, and modern clients reject `ssh-rsa`. `accept-new` pins the host key on first use, in a separate known_hosts file.

**If the key exchange fails** on a newer macOS, add `-o KexAlgorithms=+diffie-hellman-group14-sha1` (see the readiness report). It should not be needed, because 5.8 offers `ecdh-sha2-nistp256`.

### Commands sent to the printer (complete list)

| Purpose | Command (abridged) |
|---|---|
| Screenshot | `S=$(cat …/fb0/stride); P=$(cat …/fb0/pan); …; echo "FBINFO $S $P $B $V"; dd if=/dev/fb0 bs=$S skip=${P#*,} count=480 \| gzip -1`. This is the *visible* page: the double-buffer `yoffset` comes from `pan`. |
| Tap (guarded) + grab | `/tmp/ivitap2 -G x,y,w,h,HASH X Y; echo "TAPRC=$?" >&2; usleep 800000; <screenshot>` |
| Drag (list scroll) + grab | `/tmp/ivitap2 -G … -S X2,Y2,600 X Y; …` (slow drag, held still for 150 ms before release, so there is no flick) |
| File list | `cd /userdata/WifiFile && for f in *; do … printf 'T\t%s\t%s\n' "$(date -r "$f" +%s)" "$f"; done; ls -1t \| …` |
| Printing probe | `P=$(pidof IVI-Main-Controller); ls -l /proc/$P/fd \| sed -n 's/.*-> //p' \| grep -i -E '\.(g\|gcode\|nc\|cnc)$'`. This gives one line per fd; duplicates matter (§8). |
| Helper check / install | `[ -x /tmp/ivitap2 ] && md5sum /tmp/ivitap2` and `cat > /tmp/ivitap2.new && chmod 755 … && mv …` (stdin) |
| `--bump` only | `touch /userdata/WifiFile/'<name>'`. This is the only write outside /tmp, and only if you ask for it. |

---

## 4. How screens are identified

1. **Blank check**: if every sampled pixel has luminance ≤ 24, the screen is `blank`.
2. **Structural priors**, taken from the QML with no calibration needed. They name a *family* only:
   - Home: four `#E7F0FF` tiles and no Pagehead.
   - Header pages: a `#DDDDDD` Pagehead line at y = 59.
   - Files: separators at y 169 and 279.
   - Wi-Fi list: info-bar line at y 421.
   - Status: blue `#193ADD` Control button at y 386–456.
   - Dialog: `#88D3D3D3` tint at the corners and a white 720×380 card at (40, 50).
3. **Calibrated signatures** (from `calibrate`) name the exact *state*. Each reference stores:
   - a 40×24 grid of grayscale 20 px cells, compared by mean absolute difference, with per-family masks over dynamic areas (file names, temperatures, progress, the tinted page behind a dialog);
   - finer **discriminator** regions, compared by the mean of the worst 10 % of cells, so one changed word ("Pause" vs "Continue", "OK" vs "Make") stands out:
     - the dialog button row and title;
     - the status button row;
     - the page title;
     - the Files rows;
     - the Home tiles.
4. **Score** = max(global, discriminators). A state is accepted only if all three hold:
   - score ≤ 8;
   - it beats the next-best *different* label by at least 3;
   - the family prior agrees.

   Otherwise the result is "provisional (family)" or `unknown`. **Provisional and unknown states never get an action tap.**

Labels:
- Path screens: `home`, `files`, `wifi_list`, `dialog_not_ivi`, `dialog_print`, `dialog_plate`, `status_ready`.
- Recovery screens: `dialog_stop_confirm`, `dialog_delete_confirm`, `status_stopped`, `status_complete`.
- Busy screens: `status_printing`, `status_paused`, `homing`, `forbidden`.
- Any other header page you capture as `page:<name>`.
- A separate **enabled-Home-button template** (680, 0, 120, 58) is stored from Files, the Wi-Fi list and `page:*` captures. It lets the tool press Home on a page it has never seen. The Status and Homing pages show the *disabled* Home image, so they don't match.

---

## 5. Navigation logic (`Navigator.goto_print`)

**Pre-flight** (no taps):
1. Bridge check.
2. On-printer open-file probe.
3. Read `/userdata/WifiFile` and confirm FILE is in the list the app will show.

Then up to 25 steps. Each step is:

1. Observe (grab + classify). If `blank`, do a neutral wake tap first. On the first confident screen of a session, also do one wake tap at (400, 472). That point sits below every modelled button and is inert [I]. It covers the case where `closeScreen` blanked the panel but fb0 still holds the old image.
2. **Busy screen** (`status_printing`, `status_paused`, `homing`, `forbidden`): **refuse, with no tap**.
3. Act on the state:

| State | Action |
|---|---|
| `home` | Files tile (122, 209) |
| `files` | "Print Files via WiFi" (400, 225), continuing from here with no Home detour |
| `wifi_list` | Select FILE **by name** (§6) → Make |
| `dialog_not_ivi` | OK (585, 345), only if we picked FILE this run |
| `dialog_print` | Make (585, 345) if we picked FILE this run; otherwise **Cancel** (215, 345) and re-select |
| `dialog_plate` | OK (400, 345) |
| `dialog_stop_confirm`, `dialog_delete_confirm` | The safe left button (No / Cancel). Never Yes or Continue. |
| `status_ready` | If FILE was loaded this run: **stop and report** (default), or tap Start with `--start`. Otherwise Cancel (680, 421), which returns to the Wi-Fi list (`StatusPage` is created over the list, which is not destroyed [O]), then re-select. |
| `status_stopped`, `status_complete` | Cancel or Complete (680, 421). Benign: `stopPrinting` plus destroy [O]. |
| `page:*` (calibrated) | Home (740, 29) |
| unknown or provisional, with a matching **enabled Home button** | Home (740, 29) |
| unknown, provisional dialog, or anything else | **No tap**. Wait 1.5 s and grab again. Abort after 4 in a row. Unconfirmed dialogs are never tapped because button roles differ: the Lower-Temp dialog has **Reset** on the left and Cancel on the right [O]. |

The run aborts in any of these cases:
- the same state four times in a row (a tap had no effect);
- more than 25 steps;
- three guard mismatches;
- FILE missing, or its Make button disabled (wrong head type);
- the list on screen doesn't match the directory listing.

Status-page commands:
- `start`: screen must be `status_ready`, the bridge must be idle, and you type `yes`. Then tap (400, 421) and wait up to 90 s for `status_printing` or `homing`.
- `pause`: requires `status_printing`, then taps (400, 421) and waits for `status_paused`.
- `resume`: requires `status_paused`, then taps (400, 421) and waits for `status_printing`.
- `stop`: requires `status_printing` or `status_paused`. It taps Stop (680, 421) and then **confirms the Warning No/Yes dialog is showing**. It taps Yes (585, 345) only if you confirmed; otherwise it taps No. Then it waits for `status_stopped`.

---

## 6. Selecting the file by name, and scrolling

- **Sort order.** `WifiFileListPage` uses `FolderListModel { sortField: Time; sortReversed: false; showDirs: false; nameFilters: *.g *.gcode *.Gcode *.NC *.CNC *.nc *.cnc }` [O]. In Qt this means QDir::Time, newest first [I]. Ties are assumed broken by name [I], and dotfiles are hidden.
- **Listing.** The tool lists the directory with `date -r FILE +%s` (falling back to `ls -1t` order) and applies the same filter and sort (`layout.list_filter_sort`) to get FILE's row N.
- **Row geometry** [O]:
  - rows are 128 px tall, in a list area from y 60 to 420;
  - the Make button is at x 484–621, top = row top + 37, height 70;
  - Delete starts at x 633.
  - **No list tap may land at x > 621.** This is enforced in code and asserted in tests.
- **Current scroll position.** It is read from the always-on ScrollBar handle (`#BED1FF` at 0.75 opacity, x 792–800): `contentY = (handleTop − 60) / 360 × (N × 128)`.
- **Scrolling.** A slow drag at x = 250, in the file-name column where there are no buttons, of at most 300 px per drag. Position is re-measured after every drag, up to 10 drags.
- **Before tapping Make**, the Make capsules are scanned in column x = 504:
  - runs of ≥ 50 px of blue (enabled) or `#DDDDDD` (disabled);
  - one must sit within 8 px of the predicted spot;
  - otherwise the run aborts with "layout mismatch".
- **`--bump`** (optional): `touch` the file so it becomes row 0, so no scrolling is needed.

---

## 7. What must be calibrated or checked on the real printer first

Run `calibrate --manual`. It walks through each screen: you navigate **by hand**, press Enter, and it grabs the screen and checks it against the QML prior. If the prior check fails it refuses to save (overridable with `--force`) and writes `rejected_<label>.png`, because that means the QML geometry doesn't match the panel.

**Required:**
- `home`, `files` (with no USB stick inserted), `wifi_list`;
- `dialog_print`, `dialog_plate`, `status_ready` (then tap Cancel).

**Strongly recommended:**
- `dialog_not_ivi`;
- one or two `page:*` screens (Control, Settings). These also store the Home-button template.

**During the first supervised print:**
- `status_printing`, `status_paused`, `dialog_stop_confirm`, `status_complete`.

Without these the tool still refuses while printing, using the open-file probe and the bridge check, but it can't pause or stop by screen.

Then check these items, all [I] until seen:

1. The `check` output: `bpp 32`, `pan 0,0` or `0,480` (double buffer), and a stride of 3200. The tool refuses any other bpp or an xoffset ≠ 0.
2. The ScrollBar handle is visible at x ≈ 796 on a list with more than 3 files, and `contentY` estimates match.
3. One drag scrolls by about the drag distance minus the ~10 px Qt drag threshold, with no flick and no tap on release. Try `--dry-run` first, then a real `goto-print` on a list longer than 3 files.
4. List sort really is newest-first with name tie-breaks (compare `ls -lt /userdata/WifiFile` with the screen).
5. The wake point (400, 472) does nothing on any screen. Also check what happens to the first touch while blanked; if it is swallowed, the tool simply retries.
6. The open-file probe: the app disassembly (§12) predicts **0 fds** right after boot, **1 fd** from the first selection onward (it stays open even after Cancel or a finished print), and **2 fds** on the same file while a print streams. Confirm this with the `ls -l /proc/$(pidof IVI-Main-Controller)/fd` runbook check. If the counts differ, use `--probe strict` or `--probe off` and tell me.
7. Settle time: the default is 800 ms. Raise `--settle-ms` if transitions are still animating in screenshots, which shows up as repeated "provisional" results.

---

## 8. Safety checks (summary)

- **Before every tap**, the screen is re-identified as a confident, calibrated state, and the target must be on that state's allow-list (`nav.ALLOWED`). Start, Pause, Stop and dialog Yes also need an explicit command, and nothing taps them by accident.
- **TOCTOU guard.** Each tap carries an FNV-1a hash of its target rectangle, computed from the screenshot that was just classified. `ivitap2 -G` re-hashes the *live* fb right before injecting and exits with 4 (`GUARD_MISMATCH`) if anything changed. Nothing is tapped in that case; the tool re-identifies and retries, and aborts after 3 mismatches. The C and Python hashes are proven identical by a parity test that runs the real `fb_hash()` code.
- `ivitap2` keeps the old safety checks: the device name must contain `gt9xx` and the axis maximums must be 800×480.
- Unknown screen ⇒ never an action tap. Unconfirmed dialogs are never tapped. Abort after N attempts.
- **Stop before Start** is the default. `--start` is explicit and cannot be combined with `--no-bridge-check`.
- **Refuses** when any of these holds:
  - the bridge reports an active job (`/api/printer` `flags.ready == false`, or `/api/job` state not `Operational`, unless USB is locked for a Wi-Fi/storage print);
  - the bridge is unreachable, for `start` (navigation without Start is allowed);
  - the printer app has a print file open **twice**, meaning the streaming cache is reading it (`--probe stream`, the default). A single open fd is the app's leftover handle on the last selected file and is **not** treated as printing. `--probe strict` refuses on any open print file; `--probe off` skips the check;
  - the screen is `status_printing`, `status_paused`, `homing` or `forbidden`.
- **Dry run** (`--dry-run`) grabs and classifies, plans the whole path using expected next states, saves PNGs, and sends **no** `ivitap2` command. This is tested.
- **Logs**: every grab, decision, tap, guard result and abort, with a screenshot.
- **No secrets.** The bridge `api_key` is read from `~/.config/ivi-bridge/config.json` and used only as a request header; it is never logged.

---

## 9. Bridge integration points (`ivi_bridge.py` is NOT modified)

**By default it works with no changes.** `safety.HTTPBridgeState` asks the running bridge for `GET /api/job` (`job_info()`, around line 1669 of `ivi_bridge.py`) and `GET /api/printer` (`flags.ready = not bridge.busy()`, about line 1564, and `ivi.usb_locked`). It finds the address and API key in the bridge's own config.

**Optional in-process hooks**, if you later choose to wire it in:

1. **After a Wi-Fi upload.** In `Bridge.submit()`, right after `self.lock_usb(name)` (around line 1595), the file is in `/userdata/WifiFile` and USB is released, which avoids the M2001 S1 start problem. You could call:

   ```python
   from ivi_touch.api import session, CallableBridgeState
   with session(cfg["printer_host"], bridge=CallableBridgeState(lambda: self.busy())) as nav:
       nav.goto_print(name)            # or nav.goto_print(name, start=True) once trusted
   ```

   Run it in a thread: a full navigation takes about 10–30 s.
2. **A "Start on printer" button** on the bridge status page could call the same thing through a new `POST /api/ivi/touch/goto` handler next to the other `/api/ivi/*` routes (around lines 2200–2280).
3. **Pause, Resume and Stop** for storage prints (USB locked) could use `nav.pause()`, `nav.resume()` and `nav.stop(confirmed=True)`. For USB jobs, keep using the bridge's own serial commands.

---

## 10. Tests

Run `python3 -m unittest discover -s tests -v`, with no printer needed. **49 tests, all passing** (`tests/test_results.txt`). Since v0.1 the suite also covers the probe rules from check B (one fd vs two fds, strict mode, the tail end of a print caught by the screen check, Start refused while streaming), `cancel`, and the upload client against a fake server that copies the disassembled `file_upload()` rules, including the CLI `upload --goto` path.

**Simulator** (`tests/sim.py`):
- Renders every modelled screen from the QML geometry and colours: Home tiles, Pagehead, Files rows, Wi-Fi list rows with Make/Delete and a scrollbar, dialogs with the tinted overlay, the status page in each state, plus never-calibrated pages.
- Text is drawn as deterministic pseudo-glyphs.
- Reacts to taps and drags as the app does.
- Calibration in the tests uses *different* files and names from the scenarios, to exercise the masks.

**Mock SSH** (`tests/mock_transport.py`):
- Parses exactly the commands the tool sends.
- Checks guard hashes against the live simulated fb.
- Asserts that no remote command is ever empty.

**Required scenarios** (all pass):

| # | Start state | Result |
|---|---|---|
| 1 | Home | Reaches Start, no Start tap |
| 2 | Files | Continues from Files with no Home detour |
| 3 | Wi-Fi list, target on row 8 of 11 | Scrolls and selects by name; also from an already-scrolled list |
| 4 | Inside a dialog: print dialog for the wrong file, delete-confirm | Cancel / safe button, then re-select. Status page holding another file: Cancel, then re-select. |
| 5 | Unknown page with a Home button | Home, then the path. Unknown screen with no Home button: **zero taps, abort**. Unconfirmed Lower-Temp dialog: **zero taps, abort**. |
| 6 | Blanked screen (black fb, or old content retained) | Wake tap at (400, 472), then the path |
| 7 | Printing, paused or homing | **Refused with zero taps**, both by the probe and, with the probe off, by the screen. Bridge active: refused. |

**Extra tests:**
- not-IVI notice followed by `--start`;
- Start refused when the bridge is unknown, while navigation is still allowed;
- missing or filtered file;
- guard mismatch: nothing tapped, then recovery; repeated mismatches abort;
- dry run injects nothing;
- `--bump`;
- pause, resume and stop, including an unconfirmed stop (taps No);
- Start refused off `status_ready`;
- an uncalibrated classifier never taps;
- the bridge HTTP hook against a local fake server (key header, usb_locked, unreachable);
- the CLI end to end against the mock;
- empty-command refusal;
- C/Python guard-hash parity on a double-buffered fake fb.

**Sample logs** (`sample_run/`):
1. A blanked, uncalibrated Settings page: the first Home tap is swallowed by the wake, then Home, then the path, with three drags down to row 8, stopping before Start. 14 SSH calls.
2. A dry run from Home.
3. Refused while printing.
4. Unknown screen: aborts without tapping.

Limitation: the simulator follows the same QML reading as the code, so the tests show the logic is consistent and safe, **not** that the geometry is right on the real panel. That is what §7 is for.

---

## 11. Known limits

- There is no generic Back or Escape. Recovery uses calibrated Home buttons, safe dialog buttons and the status-page Cancel. A screen with neither a calibrated label nor an enabled Home button stops the run, by design, for manual help.
- `homing` and other header pages need their own references to be told apart reliably. Uncalibrated, they are "provisional header": the tool presses Home only if the enabled-Home template matches.
- Sorting ties, wake behaviour, probe semantics, drag physics and ScrollBar opacity are inferred [I]. See the §7 checklist.

---

## 12. Findings behind v0.2 (offline checks A and B, 2026-11-09)

**A. Upload into the Wi-Fi list.** Sources: `printer_http_api.conf` from the rootfs backup, plus a disassembly of `printer_http_api.so` `file_upload()` at 0x1186c [O].
- **Request:** `POST http://<printer>:8080/api/v1/upload`, `multipart/form-data`, with one part named **`file`**.
  - No token or other field is read on this route.
  - Any other method returns 405 "no post". A missing part returns 412 "file err".
- **Where it is written:** `"/userdata/WifiFile/" + filename`, opened with `O_WRONLY|O_CREAT|O_TRUNC`, so a file of the same name is **overwritten**. Success returns **201 "Upload successfully"**.
- **Extension check:** the name is split on `.` (at most 2 parts), and the **second part must be exactly `gcode`, `cnc` or `nc`**.
  - Accepted: `cube.gcode`.
  - Rejected with 412 "File type error": **`benchy_0.2mm.gcode`**, `x.GCODE`, `x.g`.
  - The bridge passes the slicer's file name through unchanged, so dotted names from the slicer would be rejected on Wi-Fi upload.
- **Name length and paths:** the name is `strcpy`'d into a 128-byte buffer, and nothing stops `/` or `..`. The client therefore limits names to 100 bytes and plain names.
- **Size limits:**
  - `http_body_max` is 1 024 000 000 bytes.
  - Bodies over 1 024 000 bytes are spooled to `/userdata/WifiFile/tmp_files`, which must exist [I]. Nothing in the image creates it, so check with `ls`.
  - There is no free-space check on this route.
- **List refresh:** the app's FileSystemWatcher refreshes the Wi-Fi list automatically [O].
- **Command line:** `curl -sS -w ' HTTP %{http_code}\n' -F 'file=@cube.gcode;filename=cube.gcode' http://<printer>:8080/api/v1/upload`.
- **In this tool:** `ivi_touch/upload.py` (`upload()`, `check_name()`, `safe_name()`, `curl_command()`) and `ivi_touch.py upload`. It checks the name, refuses to overwrite an existing file unless `--overwrite` (it lists the folder over SSH first), and with `--goto` navigates to the Start screen (stopping before Start).

**B. Does the app keep the selected file open before Start?** Yes. The evidence is in `IVI-Main-Controller` [O]:
- **Selection:** `readyPrintint` (0x43b28), which runs when the status page loads, emits `startGcodeFileReadTask`.
  - `GlobalFuntions::GlobalFuntions` connects that signal to **`Work::startWorkFile`** (0x46e68), resolved through the GOT.
  - `startWorkFile` runs in a worker thread. It does `QFile::setFileName` and `QFile::open(ReadOnly|Text)` on its *member* QFile at `Work+0x30`, reads the whole file to compute the bounding box, emits `workFinished`, and **never closes it**.
  - The file is closed only by the next selection (Qt's `setFileName` closes an open file) or when the app exits. So **1 fd stays open from the first selection onward**: on the ready page, after Cancel, and after a finished print.
- **Printing:**
  - `cachegcodeFromFile` (0x428b0) opens `GlobalFuntions+0xa0` if needed and reads 50 lines per call, so a **2nd fd on the same file** is open while streaming.
  - It closes that fd at end of file. `stopPrinting` (0x42600) and `PrintgcodefileFinish` (0x42330) also close it.
- **Other opens:** `checkGcodePrinterHeadType` (on Make) and `checkFileMD5` only open briefly, using local QFiles.
- **Consequence:** the old probe (any open file means refuse) would have refused every `goto-print` after the first use. The default is now `--probe stream`: refuse only when 2 fds point at the same print file.
  - For the last few cached lines of a job the cache fd is already closed. There the screen check (`status_printing`) and the bridge check still refuse.
  - Confidence is high:
    - `startWorkFile` makes no indirect calls and no `close()`: all 60 call sites were checked in the raw ARM disassembly.
    - The connection was resolved from the GOT.
    - The live fd counts are still [I] until the runbook step confirms them.
