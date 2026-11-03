# IVI3D Bridge plugin for OrcaSlicer 2.5 (`ivi3d_bridge_plugin.py`)

Single-file Python plugin (PEP 723 header + `[tool.orcaslicer.plugin]`), written against the official
OrcaSlicer plugin guide (Developer Reference → Plugin Development: Registry, Pages, Slicing Pipeline).
It only talks to the local **IVI Bridge** (`bridge/`, http://127.0.0.1:5001) — never to the printer — and does
not use the experimental Printer Agent.

## What it adds
| Capability | Type | What it does | Settings (Plugins dialog → Config tab, JSON) |
|---|---|---|---|
| **IVI3D FDM Header** | Slicing Pipeline (`psGCodePostProcess`) | Prepends the IVI 3licer `;Header Start … header_type: 3dp` block to exported G-code in place (same logic as `orca/ivi_fdm_header.py`). Idempotent: skips files that already start with `;Header Start`. | `enabled` (true/false), `nozzle` (fallback, `"0.3"`) |
| **IVI3D Bridge** | Pages (main-window tab) | State, file, progress bar, temperatures, plain-language alerts for *locked rotor*, *kill/halted* and *status 5*; buttons Pause / Resume / Cancel / Clear stuck job. Polls every 3 s only while the tab is visible; shows "IVI Bridge is not running…" when it can't connect. | `bridge_url` (`http://127.0.0.1:5001`), `api_key`, `poll_seconds` (≥2) |

Permissions are declared up front (one dialog at load): HTTP to `http://127.0.0.1:5001/api/{job,printer,version,ivi/clear}`
and socket `('127.0.0.1', 5001)`. Nothing else. (If you change `bridge_url`, Orca asks once for the new address.)

## Install (macOS)
A single-file `.py` plugin has **no OS/architecture suffix** in its name. Orca's docs only require platform tags
for wheel (`.whl`) plugins, e.g. `name-1.0-py3-none-any.whl` (pure Python, any OS) or a matching
`-macosx_…`/`-win_…`/`-linux_…` tag for compiled wheels. This plugin is pure Python, so it stays one `.py` file.

Pick one of these (don't use both, or you'll get two copies with the same plugin key):
- **From Orca (recommended):** open the Plugins dialog, then **Browse plugins ▾ → Install local plugin**, and pick
  `orca/plugin/ivi3d_bridge_plugin.py`.
- **Installer:** run `bridge/Install IVI Bridge.command` and click **Copy plugin**. It copies the file to the same place
  Orca's own installer uses and removes the old `orca_plugins/ivi3d_bridge/` folder from 0.1.0.
- **Manually:** quit Orca, create
  `~/Library/Application Support/OrcaSlicer/orca_plugins/ivi3d_bridge_plugin.py/` (a folder named after the file, the
  same layout Orca uses), and copy `ivi3d_bridge_plugin.py` into it. The folder must hold exactly one `.py`.

The plugin key is the file stem (`ivi3d_bridge_plugin`), so keep the file name the same when you update it.
Reinstalling resets the plugin's granted permissions, so Orca asks again.

## Enable
1. Start OrcaSlicer 2.5 and open the **Plugins** dialog. Tick **Activate** for **IVI3D Bridge** and accept the
   localhost permission dialog. Both capabilities should be listed (Slicing Pipeline + Pages).
2. `api_key` on the **IVI3D Bridge** Config tab is filled in by the bridge installer / `Fix IVI Bridge Key.command`
   (run with Orca closed). If it's empty or wrong, quit Orca and run that again; pasting the key from
   `~/.config/ivi-bridge/orca-settings.txt` also works.
3. Optional: in the **IVI3D FDM Header** Config tab, set `"enabled": false` to turn the header off.
4. If you previously added `ivi_fdm_header.py` as a post-processing script, remove it (harmless if not; the header is
   only added once).
5. If the plugin doesn't load, check the **Diagnostics** tab and `~/Library/Application Support/OrcaSlicer/log/python_*.log`.

## Use
- Slice and send/export as usual (bridge as OctoPrint host). The header is added automatically.
- **Upload and Print** streams the job over USB (live progress, Mac must stay awake and connected); **Upload**
  stores it on the printer for the touch screen, and the bridge keeps USB closed during that print (opening USB
  mid-print stalls it). The bridge's Device page shows a banner with *Printer idle, re-enable USB*.
- Open the **IVI3D Bridge** tab to watch the print and Pause / Resume / Cancel / Clear stuck job (USB prints only;
  stored prints are paused/cancelled on the touch screen).

## Tests
`python3 -m unittest discover -s orca/plugin/tests -v` — stubs the `orca` module, runs a fake bridge HTTP server,
compares header output with `orca/ivi_fdm_header.py`, checks idempotence/toggle, alerts, bad key, offline, commands.

## Untested (needs a real OrcaSlicer 2.5.0-rc)
- Actual loading by Orca: metadata parsing, `@orca.plugin` discovery, permission dialog strings matching the audit targets exactly.
- `get_config()`/`get_default_config()` behaviour with the host JSON editor (assumed JSON string / dict).
- Pages tab rendering, theme CSS variables, `window.orca` messaging, `setInterval` while the tab is hidden.
- `on_message` runs on the UI thread; each request has a 1.5 s timeout, so a hung bridge can freeze the UI for up to ~3 s per poll.
- Pipeline step during network upload (vs file export) and interaction with classic post-processing scripts.
- Pause/Resume/Cancel/Clear against the live bridge and printer from inside Orca.
- Installer's plugin-copy dialog on the Mac.
- Whether the header capability also has to be selected in the process preset (`post_process_plugin`) to run on export.
