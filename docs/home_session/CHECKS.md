# Offline checks A and B (2026-11-09)

Sources:
- the rootfs backup (`printer_http_api.conf`);
- the disassembly of `printer_http_api.so` and of `IVI-Main-Controller` v1.222;
- the box copy of `ivi_bridge.py`. The Mac copy may differ (M20/M21 additions).

Tags: [O] means observed in the binary or config, [I] means inferred. Nothing was run on the printer, the board or the Mac.


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

### A, continued: a tiny Python function (standard library only; tested against the fake server in tests/)

```python
import uuid, urllib.request, urllib.error

def ivi_upload(host, path, name):
    """POST one file to the printer's kore server; returns (http_status, reply text)."""
    b = uuid.uuid4().hex
    head = ('--%s\r\nContent-Disposition: form-data; name="file"; filename="%s"\r\n'
            'Content-Type: application/octet-stream\r\n\r\n' % (b, name)).encode()
    body = head + open(path, 'rb').read() + ('\r\n--%s--\r\n' % b).encode()
    req = urllib.request.Request('http://%s:8080/api/v1/upload' % host, data=body,
                                 headers={'Content-Type': 'multipart/form-data; boundary=' + b})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.status, r.read().decode(errors='replace')      # 201 "Upload successfully"
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors='replace')            # 412 "File type error" / "file err", 500
```
Example: `ivi_upload('<IP>', 'cube.gcode', 'cube.gcode')` returns `(201, 'Upload successfully')`.

### A, continued: what this means for ivi_bridge.py (box copy) [O]
- **What the bridge does:** `WifiPrinter.upload` sends `POST /api/v1/connect`, then `/api/v1/upload` (multipart with `token` plus `file`), then `/api/v1/disconnect`.
- **Token:** the upload handler ignores the extra `token` field, so the request still works.
- **Filename:** the bridge passes the slicer's file name unchanged.
  - An Orca or IVI 3licer name such as `Cube_0.2mm_PLA.gcode` contains extra dots, so the printer **rejects it with 412 "File type error"**.
  - Names with one dot work.
- **Not changed:** the bridge was not modified. A one-line fix would be to replace every `.` except the last with `-` before upload; the same rule is in `ivi_touch/upload.py:safe_name`.

### B, continued: navigator probe modes
| `--probe` | What gets refused |
|---|---|
| `stream` (default) | 2 or more fds on the same print file (the print is streaming) |
| `strict` | any open print file. After any earlier selection this refuses until the app restarts. |
| `off` | nothing from the probe. The bridge check and screen check still apply. |
