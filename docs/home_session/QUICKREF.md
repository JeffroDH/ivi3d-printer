# IVI3D session quick reference (one page)

**Setup.** Console: `screen -L <cu-device> 115200` (8N1; quit with Ctrl-A K y). Open it **before** powering the printer. Tool directory: `tools/ivi_touch_nav` in a checkout of this repo. Logs: `~/Desktop/IVI3D/logs`. Then `export IVI_HOST=<IP>` and define `IVISSH` (RUNBOOK 1.4).

**Rules.**
- Never run a bare `ssh root@<IP>`; always give a command.
- Prefix sshd and ssh-keygen with `LD_LIBRARY_PATH=` on the console.
- Run `ssh-keygen -R <IP> -f ~/.ssh/ivi_known_hosts` each session (the host key is new each time).

**Board setup, on the [ttyS2 console]** (BOARD ACTION; /tmp only):
```
ifconfig wlan0 | grep 'inet addr'
mkdir -p /tmp/sshtest && chmod 700 /tmp/sshtest
LD_LIBRARY_PATH= /usr/bin/ssh-keygen -t ecdsa -b 256 -N '' -f /tmp/sshtest/hk_ecdsa
printf '%s' 'PART1' > /tmp/sshtest/ak ; printf '%s\n' 'PART2' >> /tmp/sshtest/ak ; chmod 600 /tmp/sshtest/ak ; md5sum /tmp/sshtest/ak
```
Then start sshd (**STOP: confirm first**; MEDIUM risk, key-only root login on the LAN):
```
LD_LIBRARY_PATH= /usr/sbin/sshd -D -e -p 22 -h /tmp/sshtest/hk_ecdsa -o UsePrivilegeSeparation=no -o StrictModes=no \
 -o AuthorizedKeysFile=/tmp/sshtest/ak -o PermitRootLogin=without-password -o PasswordAuthentication=no \
 -o ChallengeResponseAuthentication=no -o UseDNS=no -o PidFile=/tmp/sshtest/sshd.pid </dev/null >/tmp/sshtest/sshd.log 2>&1 &
```
(One-connection test variant: replace `-D … &` with `-d -e` and the same options, then connect from the Mac with `-o ControlPath=none`.)

**Navigator, on the [Mac Terminal]**:

| Step | Command | OK when |
|---|---|---|
| Helper | `python3 ivi_touch.py install-helper` · `IVISSH 'sha256sum /tmp/ivitap2'` | sha256 `4ea44039…c0a8`, 53008 bytes |
| Check | `python3 ivi_touch.py check` | `bpp 32`, stride 3200 |
| Look | `python3 ivi_touch.py screenshot -o x.png` · `identify` | correct image / label |
| Calibrate | `python3 ivi_touch.py calibrate --manual` (or `--label L`) | `saved <label>` |
| Upload (**STOP**) | `python3 ivi_touch.py upload FILE --name test_cube.gcode` | `Upload successfully` |
| Plan | `python3 ivi_touch.py --dry-run goto-print test_cube.gcode` | `planned taps:` |
| Go (**STOP**) | `python3 ivi_touch.py goto-print test_cube.gcode` | `OK: <status_ready…>` |
| Back out | `python3 ivi_touch.py cancel` | `OK: <wifi_list…>` |
| Print (**STOP**, HIGH) | `python3 ivi_touch.py start` (type yes) | printing page |
| Pause / resume | `python3 ivi_touch.py pause` / `resume` | `OK` |
| Stop | `python3 ivi_touch.py stop` (type yes) or `--yes` | `OK` |
| Open-file probe | `IVISSH 'ls -l /proc/$(pidof IVI-Main-Controller)/fd \| grep -i -E "\.(g\|gcode\|nc\|cnc)$"'` | 0 lines after boot, 1 when loaded, 2 while printing |
| Upload by hand | `curl -sS -w ' HTTP %{http_code}\n' -F 'file=@cube.gcode;filename=cube.gcode' http://<IP>:8080/api/v1/upload` | `HTTP 201` |

**Upload names** must look like `name.gcode`, `.nc` or `.cnc`: exactly one dot, lower-case extension, at most 100 bytes. A same-named file is overwritten. Files over 1 MB need `/userdata/WifiFile/tmp_files`.

**Abort a print.**
1. Tap Stop, then Yes (or `python3 ivi_touch.py stop --yes`).
2. **Last resort:** hold the power button about 3 s. This is a hard power cut (HIGH risk; fsck at the next boot).

**Navigator exit codes.** 0 OK · 2 `ABORTED` (no further taps; read the log under `~/.ivi_touch/runs/`) · 3 SSH or transport error · 4 upload failed.

**Teardown.**
- [Mac] `ssh -O exit -o ControlPath=~/.ivi_touch/cm-%C root@$IVI_HOST`
- [ttyS2] `kill $(cat /tmp/sshtest/sshd.pid); pidof sshd && killall sshd; rm -rf /tmp/sshtest /tmp/ivitap2` (or `reboot`)
- Afterwards, only uploaded files persist on the printer.

**Recovery.**
- Panel confused: Home, Cancel, or No by hand.
- Wi-Fi lost: check the IP on the console, `export IVI_HOST`, `rm -f ~/.ivi_touch/cm-*`.
- `apps=2`: `reboot`.
