# IVI3D at-home session runbook (A33 sshd test + touch navigator)

Version 2026-11-09 · navigator v0.2.0 · printer app IVI-Main-Controller v1.222 · board clock is UTC

**How to read the steps**

- **Where each command runs:**
  - **[Mac Terminal]** means the Mac.
  - **[ttyS2 console]** means the serial root shell (`screen` window).
- **Board labels:**
  - **BOARD ACTION · risk LOW / MEDIUM / HIGH** marks anything that runs on, writes to, or changes the printer.
  - **STOP: confirm before proceeding** marks a step you decide on before you run it.
- **Every step has four parts:**
  - the command;
  - **OK:** what success looks like;
  - **FAIL:** what failure looks like;
  - **BACK OUT:** how to undo or abandon the step.
- **Placeholders:**
  - `<IP>` is the printer's Wi-Fi address (Phase 2).
  - `<cu-device>` is your USB-serial adapter (Phase 0).
- **What persists:** everything on the board lives in `/tmp` (RAM) and is gone after a reboot. The only exception is a file you choose to upload in Phase 7 or 8 (it goes to `/userdata/WifiFile`).
- **Never run a bare `ssh root@<IP>` with no command.** That starts a login shell, which runs `/etc/profile` and then autorun.sh. With `-T` it would restart Wi-Fi and launch a **second printer app**. Always give a command, as every command in this runbook does.

---

## Phase 0 · Prerequisites

- [ ] **0.1 Printer idle.**
  - The touchscreen shows Home. No print is running, and no USB stick is inserted (the Files page must look the same as at calibration).
  - The build plate is clear (needed only for Phase 8).
- [ ] **0.2 No bridge job.**
  - In the ivi_bridge web UI, the state is **Operational** and no job is queued or running. Don't send anything from the slicer during the session.
  - Leave the bridge **running**: `start` and `--start` refuse to run if the navigator can't reach it.
  - Steps that don't print still work with the bridge stopped; the navigator logs `bridge job_active=None` and continues.
- [ ] **0.3 Mac on the printer's Wi-Fi.** [Mac Terminal] `ipconfig getifaddr en0`
  - **OK:** an address on the same subnet as the printer, the same subnet as the printer.
  - **FAIL:** no output. The Mac is on Ethernet or another network; join the printer's Wi-Fi.
  - **BACK OUT:** n/a.
- [ ] **0.4 Mac tools.** [Mac Terminal] `python3 --version; ssh -V`
  - **OK:** Python 3.8 or later, and OpenSSH 7.6 or later (any current macOS).
  - **FAIL:** `python3` asks to install the Command Line Tools. Accept, then rerun.
- [ ] **0.5 Files.** Use a checkout of this repo. The navigator is `tools/ivi_touch_nav/`. This runbook, [QUICKREF.md](QUICKREF.md) and [CHECKS.md](CHECKS.md) are in `docs/home_session/`.
  ```
  [Mac Terminal]
  mkdir -p ~/Desktop/IVI3D/logs
  cd /path/to/ivi3d-printer
  shasum -a 256 tools/ivi_touch_nav/device/ivitap2_armel
  ```
  - **OK:** sha256 `4ea4403987136da7936670cdb56781b7914cc03e91b8889b12d714d6baf3c0a8` (53008 bytes).
  - **FAIL:** a different hash means the helper binary does not match this runbook. Rebuild from `device/ivitap2.c` (see the tool README) or use a clean checkout.
  - **BACK OUT:** n/a. Session logs under `~/Desktop/IVI3D/logs` can be deleted; they are not part of the repo.
- [ ] **0.6 Serial wiring (printer power OFF).**
  - Use the CP2102 USB-TTL adapter, set to **3.3 V** if it has a jumper. **Leave its VCC unconnected.**
  - Connect it to the rear `DEBUGUART` pads TX/RX/GND, or to the front 3-pin header (TX, RX, GND from left to right).
  - Cross the data lines: adapter RX → board TX, adapter TX → board RX, and GND → GND.
- [ ] **0.7 Open the console before powering on.** This avoids the macOS stale-replay problem seen before.
  ```
  [Mac Terminal]
  ls /dev/cu.*            # expect /dev/cu.usbserial-XXXX or /dev/cu.SLAB_USBtoUART
  cd ~/Desktop/IVI3D/logs && screen -L <cu-device> 115200
  ```
  - Settings are 115200 8N1 with no flow control; `screen`'s defaults already match.
  - `-L` writes `screenlog.0` in the logs folder.
  - To quit `screen`: **Ctrl-A, then K, then y**.
  - **Keep this window open for the whole session.**
- [ ] **0.8 Power on the printer.** The boot log scrolls in `screen`. Wait for the touchscreen Home screen, then press **Enter** in `screen`.
  - **OK:** a `#` root prompt. `echo hello` echoes back `hello`.
  - **FAIL:** nothing appears, or old text replays.
    - Check that TX and RX are crossed.
    - Then quit `screen`, power the printer off, unplug and replug the adapter, open `screen` again with the board off, and power on again.
  - **BACK OUT:** quit `screen`.

---

## Phase 1 · Mac key setup (Mac only, no board action)

- [ ] **1.1 Create the key, once.**
  ```
  [Mac Terminal]
  ls ~/.ssh/ivi_ecdsa 2>/dev/null || ssh-keygen -t ecdsa -b 256 -C ivi -N '' -f ~/.ssh/ivi_ecdsa
  ```
  - The navigator runs ssh with `BatchMode=yes`, so the key must have no passphrase, or have its passphrase loaded with `ssh-add --apple-use-keychain ~/.ssh/ivi_ecdsa`.
  - `-C ivi` keeps the public key line short for pasting.
  - **OK:** the files `~/.ssh/ivi_ecdsa` and `~/.ssh/ivi_ecdsa.pub` exist.
  - **FAIL:** "already exists" is fine; keep the existing key.
  - **BACK OUT:** `rm ~/.ssh/ivi_ecdsa ~/.ssh/ivi_ecdsa.pub`.
- [ ] **1.2 View the public key and its check values** (the public key is safe to show).
  ```
  [Mac Terminal]
  cat ~/.ssh/ivi_ecdsa.pub
  md5 -q ~/.ssh/ivi_ecdsa.pub; wc -c < ~/.ssh/ivi_ecdsa.pub
  cut -c1-90 ~/.ssh/ivi_ecdsa.pub     # PART1 for Phase 3.4
  cut -c91-  ~/.ssh/ivi_ecdsa.pub     # PART2 for Phase 3.4
  ```
  - **OK:** one line starting `ecdsa-sha2-nistp256 AAAA` and ending ` ivi`, about 165 bytes long. Write down the md5 and the byte count.
- [ ] **1.3 Check for an ssh config that would interfere.** [Mac Terminal] `grep -n -i -E 'host \*|^host |identityfile|controlmaster|requesttty' ~/.ssh/config 2>/dev/null`
  - **OK:** no output, or nothing that matches the printer's IP or `Host *`.
  - **FAIL:** a `Host *` block with `RequestTTY`, `RemoteCommand`, `ProxyJump` or `ControlMaster`. Comment it out for the session, or add a `Host <IP>` block above it that resets those options.
- [ ] **1.4 Shell helpers for this session.** Paste these into the Mac Terminal you will use for Phases 3–9.
  ```
  [Mac Terminal]
  export IVI_HOST=<IP>          # after Phase 2
  mkdir -p ~/.ivi_touch
  IVISSH() { ssh -i ~/.ssh/ivi_ecdsa -T -o BatchMode=yes -o UserKnownHostsFile=~/.ssh/ivi_known_hosts \
    -o StrictHostKeyChecking=accept-new -o HostKeyAlgorithms=ecdsa-sha2-nistp256 -o ConnectTimeout=8 \
    -o ControlMaster=auto -o ControlPath=~/.ivi_touch/cm-%C -o ControlPersist=600 -o ServerAliveInterval=15 \
    root@$IVI_HOST -- "PATH=/bin:/sbin:/usr/bin:/usr/sbin; $*"; }
  cd tools/ivi_touch_nav   # from a checkout of this repo
  ```
  - `IVISSH` is the navigator's exact invocation (the same options, control socket and known_hosts file), so its connection is shared with `ivi_touch.py`.

---

## Phase 2 · Find the printer IP

Use whichever is easiest; they should agree.

- [ ] **2.1 Touchscreen.** On the printer's network or Wi-Fi settings page, read the IP shown for the connected network.
- [ ] **2.2 Router.** In the router's DHCP client list, look for the printer's entry.
- [ ] **2.3 Console.** **BOARD ACTION · read-only · risk LOW**
  ```
  [ttyS2 console]
  ifconfig wlan0 | grep 'inet addr'
  ```
  - **OK:** `inet addr:<printer-ip>  Bcast:… Mask:…`.
  - **FAIL:** no `inet addr` means the app hasn't joined Wi-Fi yet. Wait 30 s after Home appears and retry. If it is still missing, `ip addr show wlan0` shows the link state; check Wi-Fi on the touchscreen.
  - **BACK OUT:** n/a.
- [ ] **2.4 Reachability.** [Mac Terminal] `ping -c 3 <IP>`
  - **OK:** 3 replies.
  - **FAIL:** timeouts. Check that the Mac and printer are on the same SSID. Some routers isolate clients on guest networks.

---

## Phase 3 · One-time sshd test from ttyS2 (everything in /tmp)

The Mac commands here are the navigator's form: `-T`, an explicit command, and therefore a non-login shell.

- [ ] **3.1 Baseline.** **BOARD ACTION · read-only · risk LOW**
  ```
  [ttyS2 console]
  netstat -lnt | grep ':22 ' ; pidof sshd ; pidof IVI-Main-Controller
  ```
  - **OK:** nothing for `:22` and nothing for `sshd`; one PID for the app.
  - **FAIL:** an sshd is already running. Stop and work out where it came from before continuing.
- [ ] **3.2 Work folder.** **BOARD ACTION · /tmp write · risk LOW**
  ```
  [ttyS2 console]
  mkdir -p /tmp/sshtest && chmod 700 /tmp/sshtest && ls -ld /tmp/sshtest
  ```
  - **OK:** `drwx------ … /tmp/sshtest`.
  - **BACK OUT:** `rm -rf /tmp/sshtest`.
- [ ] **3.3 Throwaway host key.** **BOARD ACTION · /tmp write · risk LOW**
  ```
  [ttyS2 console]
  LD_LIBRARY_PATH= /usr/bin/ssh-keygen -t ecdsa -b 256 -N '' -f /tmp/sshtest/hk_ecdsa
  LD_LIBRARY_PATH= /usr/bin/ssh-keygen -l -f /tmp/sshtest/hk_ecdsa.pub
  ```
  - The empty `LD_LIBRARY_PATH=` is required.
  - **OK:** "Your identification has been saved…", then `256 xx:xx:…:xx … (ECDSA)`. Write down that **MD5-style** fingerprint.
  - **FAIL:** "OpenSSL version mismatch" means the `LD_LIBRARY_PATH=` prefix is missing.
  - **BACK OUT:** `rm -f /tmp/sshtest/hk_ecdsa*`.
- [ ] **3.4 Put your public key in `/tmp/sshtest/ak`.** **BOARD ACTION · /tmp write · risk LOW**
  - **Method 1 (console paste).** Paste PART1 and PART2 from step 1.2 between the single quotes:
    ```
    [ttyS2 console]
    printf '%s' 'PART1' > /tmp/sshtest/ak
    printf '%s\n' 'PART2' >> /tmp/sshtest/ak
    chmod 600 /tmp/sshtest/ak; md5sum /tmp/sshtest/ak; wc -c /tmp/sshtest/ak
    ```
    - **OK:** the md5 and byte count equal the Mac values from step 1.2.
    - **FAIL:** they differ, usually because a character was dropped or a stray line break crept in. Rerun both `printf` lines; the first one overwrites.
  - **Method 2 (fallback: upload over kore :8080).** **BOARD ACTION · writes /userdata · risk MEDIUM · STOP: confirm before proceeding.** It writes a file that the Wi-Fi list shows briefly; **don't tap Make on it.**
    ```
    [Mac Terminal]
    curl -sS -w ' HTTP %{http_code}\n' -F "file=@$HOME/.ssh/ivi_ecdsa.pub;filename=ivikey.gcode" http://<IP>:8080/api/v1/upload
    [ttyS2 console]
    cp /userdata/WifiFile/ivikey.gcode /tmp/sshtest/ak && rm /userdata/WifiFile/ivikey.gcode && chmod 600 /tmp/sshtest/ak
    md5sum /tmp/sshtest/ak; ls /userdata/WifiFile | grep -c ivikey
    ```
    - **OK:** `Upload successfully HTTP 201`, then a matching md5 and a count of `0`.
    - **FAIL:** `HTTP 412` means the name was changed (it must be exactly `ivikey.gcode`). "Connection refused" means kore isn't running (no Wi-Fi IP yet).
    - **BACK OUT:** `rm -f /userdata/WifiFile/ivikey.gcode`.
- [ ] **3.5 Start a one-connection debug sshd.** **BOARD ACTION · opens a key-only root login on port 22 of the LAN · risk MEDIUM · STOP: confirm before proceeding**
  ```
  [ttyS2 console]
  LD_LIBRARY_PATH= /usr/sbin/sshd -d -e -p 22 -h /tmp/sshtest/hk_ecdsa -o UsePrivilegeSeparation=no \
    -o StrictModes=no -o AuthorizedKeysFile=/tmp/sshtest/ak -o PermitRootLogin=without-password \
    -o PasswordAuthentication=no -o ChallengeResponseAuthentication=no -o UseDNS=no
  ```
  - **OK:** debug lines ending in `Server listening on 0.0.0.0 port 22.` The console stays busy with this process.
  - **FAIL:**
    - "/var/empty must be owned by root…" means `UsePrivilegeSeparation=no` is missing.
    - "Bind to port 22 … Address already in use" means another sshd is running (see 3.1).
  - **BACK OUT:** **Ctrl-C** in the console.
- [ ] **3.6 Test from the Mac with the navigator-style command.** `ControlPath=none` here, so the single `-d` connection isn't held open afterwards.
  ```
  [Mac Terminal]
  ssh-keygen -R <IP> -f ~/.ssh/ivi_known_hosts 2>/dev/null
  ssh -i ~/.ssh/ivi_ecdsa -T -o BatchMode=yes -o UserKnownHostsFile=~/.ssh/ivi_known_hosts \
    -o StrictHostKeyChecking=accept-new -o HostKeyAlgorithms=ecdsa-sha2-nistp256 -o ConnectTimeout=8 \
    -o ControlPath=none root@<IP> -- \
    'PATH=/bin:/sbin:/usr/bin:/usr/sbin; uname -a; id; echo "LD=[$LD_LIBRARY_PATH] apps=$(pidof IVI-Main-Controller | wc -w)"'
  ssh-keygen -l -E md5 -F <IP> -f ~/.ssh/ivi_known_hosts
  ```
  - **OK:**
    - `Warning: Permanently added '<IP>' (ECDSA)…`;
    - `Linux … armv7l GNU/Linux`;
    - `uid=0(root) gid=0(root)`;
    - `LD=[] apps=1` (empty LD shows /etc/profile **did not** run; apps=1 shows no second app);
    - possibly "Could not chdir to home directory /root", which is harmless.
    - The last command's MD5 fingerprint equals the one from step 3.3.
    - On the console, sshd -d logs the session and then exits back to `#`.
  - **FAIL:**
    - `Permission denied (publickey)`: the console log names the reason. Usually the `ak` contents (redo 3.4) or the wrong `-i` key.
    - `no matching key exchange`: add `-o KexAlgorithms=+diffie-hellman-group14-sha1`.
    - A timeout: check the IP or client isolation.
    - `apps=2`: **stop**. Reboot the printer (`reboot` on the console) and report.
  - **BACK OUT:** Ctrl-C on the console if sshd is still running. Then `ssh-keygen -R <IP> -f ~/.ssh/ivi_known_hosts`.
- [ ] **3.7 Start the background sshd for the navigator session.** `-d` serves one connection, but the navigator keeps a ControlMaster connection open and reconnects when needed, so it needs the normal, non-`-d` sshd. `-D` keeps sshd from detaching, `&` backgrounds it, and the pidfile is written.
  - **BOARD ACTION · key-only root login on the LAN until Phase 9 · risk MEDIUM · STOP: confirm before proceeding**
  ```
  [ttyS2 console]
  LD_LIBRARY_PATH= /usr/sbin/sshd -D -e -p 22 -h /tmp/sshtest/hk_ecdsa -o UsePrivilegeSeparation=no \
    -o StrictModes=no -o AuthorizedKeysFile=/tmp/sshtest/ak -o PermitRootLogin=without-password \
    -o PasswordAuthentication=no -o ChallengeResponseAuthentication=no -o UseDNS=no \
    -o PidFile=/tmp/sshtest/sshd.pid </dev/null >/tmp/sshtest/sshd.log 2>&1 &
  sleep 1; cat /tmp/sshtest/sshd.pid; netstat -lnt | grep ':22 '; tail -3 /tmp/sshtest/sshd.log
  [Mac Terminal]
  IVISSH 'echo ok; pidof IVI-Main-Controller | wc -w'
  ```
  - **OK:** a PID, `0.0.0.0:22 … LISTEN`, and "Server listening" in the log. The Mac prints `ok` and `1`.
  - **FAIL:** no pidfile, or nothing listening. Read `cat /tmp/sshtest/sshd.log`.
  - **BACK OUT (stop sshd):**
    - [Mac] `ssh -O exit -o ControlPath=~/.ivi_touch/cm-%C root@$IVI_HOST`
    - [ttyS2] `kill $(cat /tmp/sshtest/sshd.pid); sleep 1; pidof sshd || echo stopped`. If any PID is left, it is a per-connection child; run `killall sshd`.

**How this fits with the earlier sshd readiness report (§7a)**

| # | Readiness report says | This runbook | Why |
|---|---|---|---|
| 1 | Mac: `-t … root@ip /bin/sh -i` | `-T … -- 'PATH=…; cmd'` | The navigator's form. Both are non-login, so `/etc/profile` doesn't run. For an interactive shell, the report's `-t … /bin/sh -i` is still correct. |
| 2 | known_hosts `/tmp/ivi_known_hosts`, no StrictHostKeyChecking | `~/.ssh/ivi_known_hosts` with `accept-new` | Matches the navigator. **The host key is regenerated in /tmp every session**, so run `ssh-keygen -R <IP> -f ~/.ssh/ivi_known_hosts` each session (step 3.6); otherwise you get "REMOTE HOST IDENTIFICATION HAS CHANGED". |
| 3 | `sshd -d` "exits on its own after the session" | True only without connection sharing | With the navigator's ControlPersist=600 the one connection stays open for 10 minutes. So test with `ControlPath=none` (3.6) and use `-D` for the navigator (3.7). |
| 4 | `-d` with `-o PidFile=…`; stop with `kill $(cat …sshd.pid)` | Pidfile used only with `-D` | sshd doesn't write a pidfile in `-d` mode, so stop a `-d` sshd with Ctrl-C. |
| 5 | (no `UseDNS`) | `-o UseDNS=no` | Avoids a reverse-DNS wait at login on a board with no working resolver. Harmless. |
| 6 | (none) | `ssh-keygen -l -E md5` cross-check | 5.8 prints MD5 fingerprints and macOS prints SHA256 by default. |
| 7 | Navigator README: ControlPath `~/.ssh/ivi-cm-%C` (transport default) | CLI uses `~/.ivi_touch/cm-%C` | The CLI overrides the library default. `IVISSH` uses the CLI path, so both share one socket. |

---

## Phase 4 · Install the helper (`/tmp/ivitap2`)

- [ ] **4.1 Install.** **BOARD ACTION · /tmp write · risk LOW** [Mac Terminal] `python3 ivi_touch.py install-helper`
  - **OK:** `installed /tmp/ivitap2 (md5 …)`.
  - **FAIL:** `SSH/transport error` means sshd isn't running (go back to 3.7). `helper upload failed` means a truncated write; rerun.
  - **BACK OUT:** `IVISSH 'rm -f /tmp/ivitap2'`.
- [ ] **4.2 Verify size and sha256.** **BOARD ACTION · read-only · risk LOW**
  ```
  [Mac Terminal]
  IVISSH 'ls -l /tmp/ivitap2; sha256sum /tmp/ivitap2'
  ```
  - **OK:** `-rwxr-xr-x … 53008 … /tmp/ivitap2` and `4ea4403987136da7936670cdb56781b7914cc03e91b8889b12d714d6baf3c0a8`.
  - **FAIL:** anything else. Remove the file (`rm -f /tmp/ivitap2`) and repeat 4.1.
- [ ] **4.3 Dry-run self-check** (no input device is opened, nothing is injected). **BOARD ACTION · read-only · risk LOW**
  ```
  [Mac Terminal]
  IVISSH '/tmp/ivitap2 -n 400 240; /tmp/ivitap2 -n 900 240; echo rc=$?; /tmp/ivitap2 -H 0,0,800,40'
  python3 ivi_touch.py check
  ```
  - **OK:**
    - `dry-run: tap 400,240`;
    - `refusing: coordinates/time out of range` followed by `rc=2`;
    - one 8-hex-digit hash;
    - `helper OK; fb {'stride': 3200, 'pan': '0,0' or '0,480', 'bpp': 32, …} ; screen: …`.
  - **FAIL:**
    - `unsupported framebuffer` means the fb isn't 32 bpp or xoffset ≠ 0. **Stop Phases 5–8** and report.
    - `Exec format error` means the wrong binary.

---

## Phase 5 · Read-only checks

All steps here: **BOARD ACTION · read-only · risk LOW**

- [ ] **5.1 Touch device.** [Mac Terminal] `IVISSH 'cat /proc/bus/input/devices'`
  - **OK:** a block with `N: Name="gt9xx…"` and `H: Handlers=… event3`.
  - **FAIL:** gt9xx is on another eventN. The helper will refuse (`refusing: /dev/input/event3 is …`). Report the block; don't tap.
- [ ] **5.2 Framebuffer sysfs values.** [Mac Terminal] `IVISSH 'cd /sys/class/graphics/fb0 && for f in virtual_size stride bits_per_pixel pan; do echo "$f=$(cat $f)"; done'`
  - **OK:** `virtual_size=800,960` (or 800,480), `stride=3200`, `bits_per_pixel=32`, `pan=0,0` or `0,480`.
- [ ] **5.3 Screenshot.** [Mac Terminal] `python3 ivi_touch.py screenshot -o ~/Desktop/IVI3D/logs/home.png && open ~/Desktop/IVI3D/logs/home.png`
  - **OK:** the PNG matches the panel, the right way up, with normal colours.
  - **FAIL:** swapped red and blue, a shifted image or a torn image. Report it with the PNG; don't calibrate.
- [ ] **5.4 Identify.** [Mac Terminal] `python3 ivi_touch.py identify`
  - **OK (before calibration):** `<provisional home …>` or similar. "Provisional" is expected until Phase 6.
- [ ] **5.5 Upload folder and the large-upload spool folder.** [Mac Terminal] `IVISSH 'ls -la /userdata/WifiFile/ | head -30; df -h /userdata'`
  - **OK:** you see the Wi-Fi files and the free space. Note whether **`tmp_files`** exists; uploads over ~1 MB need it (see CHECKS_A_B.md).
  - **DECISION:** if `tmp_files` is missing, either keep test uploads under 1 MB, or create the folder.
    - Creating it is a **BOARD ACTION · persistent /userdata write · risk MEDIUM · STOP: confirm before proceeding**: `IVISSH 'mkdir /userdata/WifiFile/tmp_files'`.
    - To back out: `IVISSH 'rmdir /userdata/WifiFile/tmp_files'`.
- [ ] **5.6 Check B baseline: the app's open print files.** [Mac Terminal]
  ```
  IVISSH 'ls -l /proc/$(pidof IVI-Main-Controller)/fd | grep -i -E "\.(g|gcode|nc|cnc)$"; echo end'
  ```
  - **Expected right after boot:** only `end`, meaning 0 fds.
  - If a file was already selected since boot, expect 1 line. Write down the count; it is checked again in 7.4 and 8.3.

---

## Phase 6 · Calibration (you navigate by hand, the tool only takes screenshots)

- [ ] **6.1 Choose the test file.** It must be sliced by IVI 3licer and have a plain name with exactly one dot, e.g. `test_cube.gcode`. [Mac Terminal] `IVISSH 'ls -lt /userdata/WifiFile | head'`
  - **If none is suitable:** upload one with step 7.1 first.
- [ ] **6.2 Run the guided capture.** **BOARD ACTION · read-only screenshots; you tap the panel · risk LOW** [Mac Terminal] `python3 ivi_touch.py calibrate --manual`
  - At each prompt, navigate **on the touchscreen by hand**, then press Enter (`s` skips, `q` quits). The sequence:
    1. `home`;
    2. `files` (Home › Files, **no USB stick inserted**);
    3. `wifi_list` (Files › Print Files via WiFi);
    4. `dialog_print` (tap Make on the test file's row; **don't go further yet**);
    5. `dialog_plate` (tap Make in the print dialog, so the plate warning shows);
    6. `status_ready` (dismiss the plate warning; Start/Cancel shows). **Then tap Cancel by hand.**
    7. Optional: `dialog_not_ivi`, `page:control`, `page:settings`.
    8. Skip the `status_printing` … `status_complete` prompts with `s`. They are captured in Phase 8.
  - **OK:** each step prints `saved <label> (…); re-identifies as <label … score≤8>`. The final line lists the calibrated labels.
  - **FAIL:** `layout check failed … NOT saved` writes `rejected_<label>.png`. Make sure the right screen was showing and retake it. If it fails again, report the PNG; use `--force` only after checking it.
  - **BACK OUT:** delete `~/.ivi_touch/calib/` to start calibration over.
- [ ] **6.3 Spot checks.** [Mac Terminal] Run `python3 ivi_touch.py identify` on Home, Files and the Wi-Fi list.
  - **OK:** each shows the right label with score ≤ 8 and margin ≥ 3.

---

## Phase 7 · Navigation (stops before Start)

- [ ] **7.1 (Optional) Upload a test file.** **BOARD ACTION · persistent write to /userdata/WifiFile · risk MEDIUM · STOP: confirm before proceeding**
  ```
  [Mac Terminal]
  python3 ivi_touch.py --dry-run upload ~/path/to/cube.gcode --name test_cube.gcode   # prints the curl command only
  python3 ivi_touch.py upload ~/path/to/cube.gcode --name test_cube.gcode
  ```
  - **OK:** `uploaded … -> /userdata/WifiFile/test_cube.gcode (Upload successfully)`. The file appears at the top of the Wi-Fi list within about 2 s.
  - **FAIL:**
    - A name error: the tool suggests a fixed `--name`, e.g. dots inside the name become `-`.
    - `already exists`: pick another name, or add `--overwrite` deliberately.
    - `HTTP 500`: an I/O problem. If the file is over 1 MB, check `tmp_files` (step 5.5).
  - **BACK OUT:** delete the file from the Wi-Fi list on the touchscreen (Delete), or `IVISSH 'rm /userdata/WifiFile/test_cube.gcode'`.
- [ ] **7.2 Dry run.** **BOARD ACTION · read-only · risk LOW** [Mac Terminal] `python3 ivi_touch.py --dry-run goto-print test_cube.gcode`
  - **OK:** `OK: …` followed by `planned taps:` with a sensible list (Home › Files › Wi-Fi › row › Make …). Nothing moves on the panel.
  - **FAIL:**
    - `ABORTED: file … is not listed`: check the name.
    - `screen not recognised`: calibrate that screen.
    - `refusing … streaming`: a print is running; don't continue.
- [ ] **7.3 Real navigation.** **BOARD ACTION · injected taps · risk MEDIUM · STOP: confirm before proceeding**
  - Watch the panel. Start from Home or the Wi-Fi list.
  - [Mac Terminal] `python3 ivi_touch.py goto-print test_cube.gcode`
  - **OK:** `OK: <status_ready …> | log: ~/.ivi_touch/runs/…`. The panel shows the status page with Start, and **Start is not tapped**.
  - **FAIL:** `ABORTED: …` names the reason and log folder, and no further taps are made. See "If something goes wrong".
  - **BACK OUT:** step 7.5 (Cancel).
- [ ] **7.4 Check B live, loaded state.** **BOARD ACTION · read-only · risk LOW** Rerun the command from step 5.6.
  - **Expected:** **1 line** naming `/userdata/WifiFile/test_cube.gcode`.
  - If you see 0 or 2 lines, note it; the probe defaults rely on this (see CHECKS_A_B.md).
- [ ] **7.5 Back out with Cancel.** **BOARD ACTION · one guarded tap · risk LOW** [Mac Terminal] `python3 ivi_touch.py cancel`
  - **OK:** `OK: <wifi_list …>`. Rerun step 5.6 and still expect **1 line**: the app keeps the last selected file open.
  - **FAIL:** `refusing cancel` means the screen isn't a confirmed status_ready. Tap Cancel by hand.
- [ ] **7.6 Repeatability.** Run 7.3 and 7.5 once more, starting from Settings or another page.
  - **OK:** the same result.

---

## Phase 8 · Optional supervised print (stay at the printer)

**Abort at any time:**

1. **On-screen Stop:** tap **Stop**, then **Yes** in the Warning dialog. From the Mac: `python3 ivi_touch.py stop --yes`.
2. **Last resort, if Stop doesn't respond or there is any physical danger:** hold the **power button about 3 s**.
   - This is a **hard power cut**, not a shutdown. The GD32 drops PB1 and then PA4 about 10 ms later (medium confidence on the pin roles). Pulling the mains plug has the same effect.
   - **BOARD ACTION · risk HIGH.** The rootfs uses `barrier=0`, and `fsck -y` runs at the next boot, so a recent write could be lost or "repaired". Use it only when Stop is not enough.

- [ ] **8.1 Start.** **BOARD ACTION · starts heating and motion · risk HIGH · STOP: confirm before proceeding**
  - Check first: plate clear, filament loaded, bridge Operational (step 0.2).
  - [Mac Terminal] `python3 ivi_touch.py goto-print test_cube.gcode`, then `python3 ivi_touch.py start` (type `yes`).
  - **OK:** `OK: …`, and the panel shows the printing status page.
  - **FAIL:** `refusing start: bridge state unknown` means the bridge isn't running or reachable; start it, or tap Start by hand.
  - **BACK OUT:** abort with Stop (above).
- [ ] **8.2 Capture the printing screens.** **BOARD ACTION · read-only screenshots; you tap the panel · risk LOW**
  ```
  [Mac Terminal]
  python3 ivi_touch.py calibrate --label status_printing
  ```
  - **Paused:** tap Pause by hand, wait until the panel shows Paused, then `python3 ivi_touch.py calibrate --label status_paused`. Tap Resume by hand. After that, `python3 ivi_touch.py pause` and `resume` can be tested.
  - **Stop dialog:** tap Stop by hand so the Warning No/Yes dialog shows, run `python3 ivi_touch.py calibrate --label dialog_stop_confirm`, then **tap No**.
  - **OK:** each prints `saved <label>`.
- [ ] **8.3 Check B live, streaming state.** **BOARD ACTION · read-only · risk LOW** Rerun the command from step 5.6.
  - **Expected:** **2 lines** for the same file.
  - Also try `python3 ivi_touch.py --dry-run goto-print test_cube.gcode`. **OK:** `ABORTED: refusing goto-print: the printer app is streaming …`.
- [ ] **8.4 Finish.** Either let the print complete and then run `python3 ivi_touch.py calibrate --label status_complete`, or end it with `python3 ivi_touch.py stop` (type `yes`, **BOARD ACTION · risk MEDIUM**).
  - **OK:** the stop command prints `OK: …`, and the panel leaves the printing state.

---

## Phase 9 · Teardown

- [ ] **9.1 Close the Mac connection.** [Mac Terminal] `ssh -O exit -o ControlPath=~/.ivi_touch/cm-%C root@$IVI_HOST`
  - **OK:** `Exit request sent.`, or "No such file" if it had already closed.
- [ ] **9.2 Stop sshd and remove the /tmp files.** **BOARD ACTION · risk LOW**
  ```
  [ttyS2 console]
  kill $(cat /tmp/sshtest/sshd.pid); sleep 1; pidof sshd && killall sshd
  rm -f /tmp/ivitap2; rm -rf /tmp/sshtest
  netstat -lnt | grep ':22 '; ls /tmp/ivitap2 /tmp/sshtest 2>&1
  ```
  - **OK:** nothing listening on :22, and both paths report "No such file or directory".
  - Instead of 9.2 you can type `reboot` on the console (**BOARD ACTION · risk MEDIUM**, with fsck at boot). This clears `/tmp` and the helper too.
- [ ] **9.3 (Decision) Test uploads.** Delete them from the Wi-Fi list on the touchscreen, or keep them.
- [ ] **9.4 Close the console.** Ctrl-A, K, y. `~/Desktop/IVI3D/logs/screenlog.0` holds the console log.

**What persists afterwards**

- **Board rootfs:** nothing. No startup files were changed and no host keys were written to `/etc`.
- **Board /userdata/WifiFile:** any file uploaded in 7.1, plus `tmp_files` if you created it in 5.5.
- **Mac:**
  - `~/.ssh/ivi_ecdsa{,.pub}`;
  - the host entry in `~/.ssh/ivi_known_hosts`, which is stale next session; remove it with `ssh-keygen -R`;
  - `~/.ivi_touch/calib/` (keep it: next time skips Phase 6);
  - `~/.ivi_touch/runs/` logs;
  - `~/Desktop/IVI3D/logs/`.

---

## If something goes wrong

| Symptom | Do this |
|---|---|
| **The navigator printed `ABORTED: …`** | No more taps are coming. Read the reason and look at the last PNG in the log folder it names. Recover by hand on the panel (Home; Cancel on a status page; No in dialogs). |
| **Wrong tap / unexpected screen** | Recover by hand as above. If a print started by mistake, tap Stop, then Yes. Keep the log folder for the report. |
| **`GUARD_MISMATCH` in the log** | The screen changed between grab and tap, and the tap was skipped by design. The tool retries once. If it keeps happening, raise `--settle-ms 1200`. |
| **App frozen (panel unresponsive)** | `IVISSH 'pidof IVI-Main-Controller; uptime'`, then `python3 ivi_touch.py screenshot -o frozen.png`. Don't inject taps. **If idle:** `reboot` on the console. **If printing and Stop doesn't respond:** power button about 3 s (last resort). Don't restart the app by hand from the console; it needs the autorun environment. |
| **Wi-Fi dropped** (`SSH/transport error`, exit 3) | The run has stopped. On the console: `ifconfig wlan0 \| grep 'inet addr'`. The app reconnects Wi-Fi by itself. If the IP changed, set `export IVI_HOST=<new IP>`, then `rm -f ~/.ivi_touch/cm-*` and run `python3 ivi_touch.py check`. sshd keeps running through the drop. |
| **`REMOTE HOST IDENTIFICATION HAS CHANGED`** | Expected after regenerating the host key: `ssh-keygen -R <IP> -f ~/.ssh/ivi_known_hosts`. |
| **`Permission denied (publickey)`** | Check the `ak` md5 (step 3.4) and run `tail /tmp/sshtest/sshd.log` on the console. |
| **Console shows garbage, replays old text, or nothing** | Press Enter, then Ctrl-C. Otherwise: quit `screen`, replug the adapter, reopen `screen`. If it is still bad, power-cycle the board with the port already open. |
| **`apps=2` or two IVI-Main-Controller PIDs** | A login shell ran autorun. Stop using SSH and `reboot` from the console. |
| **Print heading somewhere wrong / crash noise** | Stop, then Yes. If that isn't immediate, power button about 3 s. |
