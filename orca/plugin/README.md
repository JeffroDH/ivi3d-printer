# IVI3D Bridge plugin for OrcaSlicer 2.5 (`ivi3d_bridge_plugin.py`)

Single-file Python plugin (PEP 723 header + `[tool.orcaslicer.plugin]`), written against the official
OrcaSlicer plugin guide (Developer Reference → Plugin Development: Registry, Pages, Slicing Pipeline).
It only talks to the local **IVI Bridge** (`bridge/`, http://127.0.0.1:5000) — never to the printer — and does
not use the experimental Printer Agent.

## What it adds
| Capability | Type | What it does | Settings (JSON, Plugins → ⚙) |
|---|---|---|---|
| **IVI3D FDM Header** | Slicing Pipeline (`psGCodePostProcess`) | Prepends the IVI 3licer `;Header Start … header_type: 3dp` block to exported G-code in place (same logic as `orca/ivi_fdm_header.py`). Idempotent: skips files that already start with `;Header Start`. | `enabled` (true/false), `nozzle` (fallback, `"0.3"`) |
| **IVI3D Bridge** | Pages (main-window tab) | State, file, progress bar, temperatures, plain-language alerts for *locked rotor*, *kill/halted* and *status 5*; buttons Pause / Resume / Cancel / Clear stuck job. Polls every 3 s only while the tab is visible; shows "IVI Bridge is not running…" when it can't connect. | `bridge_url` (`http://127.0.0.1:5000`), `api_key`, `poll_seconds` (≥2) |

Permissions are declared up front (one dialog at load): HTTP to `http://127.0.0.1:5000/api/{job,printer,version,ivi/clear}`
and socket `('127.0.0.1', 5000)`. Nothing else. (If you change `bridge_url`, Orca asks once for the new address.)

## Install (macOS)
Easiest: run `bridge/Install IVI Bridge.command` and click **Copy plugin**. Manually:
1. Quit OrcaSlicer.
2. Create `~/Library/Application Support/OrcaSlicer/orca_plugins/ivi3d_bridge/` (each plugin must be in its own subfolder containing exactly one `.py`).
3. Copy `orca/plugin/ivi3d_bridge_plugin.py` into it.

## Enable
1. Start OrcaSlicer 2.5 → **Plugins** (plugin manager). Find **IVI3D Bridge** and enable it; accept the localhost permission dialog.
2. Open the settings (⚙) of the **IVI3D Bridge** capability and paste the API key (the installer copied it to the clipboard; also in `~/.config/ivi-bridge/orca-settings.txt`).
3. Optional: in **IVI3D FDM Header** settings set `"enabled": false` to turn the header off.
4. If you previously added `ivi_fdm_header.py` as a post-processing script, remove it (harmless if not — the header is only added once).

## Use
- Slice and send/export as usual (bridge as OctoPrint host). The header is added automatically.
- Open the **IVI3D Bridge** tab to watch the print and Pause / Resume / Cancel / Clear stuck job.

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
