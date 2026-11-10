"""Upload a G-code file to the printer's own HTTP server (kore + printer_http_api.so on TCP 8080) so it lands
in /userdata/WifiFile/ and appears in the touchscreen's "Print Files via WiFi" list (Offline check A).

Facts from the backup (printer_http_api.conf + printer_http_api.so disassembly) [O]:
  * route  POST /api/v1/upload  -> file_upload(); any other method -> 405 "no post"
  * multipart/form-data, ONE file part named "file"; its filename is used verbatim:
        path = "/userdata/WifiFile/" + filename ; open(path, O_WRONLY|O_CREAT|O_TRUNC, 0700)
    (=> an existing file of the same name is silently OVERWRITTEN)
  * no token or other field is read by this handler (the conf has no params block for /upload, and
    file_upload() calls no http_argument_get) - connect/disconnect are not needed
  * extension check: filename is split on "." (kore_split_string, max 2 parts) and the SECOND part must be
    exactly "gcode", "cnc" or "nc" (case-sensitive). So "part.gcode" is OK but "benchy_0.2mm.gcode",
    "x.GCODE" and "x.g" are rejected with 412 "File type error"
  * filename copied with strcpy into a 128-byte stack buffer: names >= 128 bytes overflow it -> keep short
  * no path sanitising (a "/" or ".." would escape the folder) - this client refuses such names
  * replies: 201 "Upload successfully"; 412 "file err" (no file part); 412 "File type error"; 500 on I/O error
  * limits: http_body_max 1024000000 (~976 MiB); bodies > 1024000 B are spooled by kore to
    /userdata/WifiFile/tmp_files (that folder must exist [I]); no free-space check on this route
    (sliceUpload has one)
  * the app's FileSystemWatcher on /userdata/WifiFile refreshes the Wi-Fi list automatically
"""
import os, re, urllib.error, urllib.request, uuid

ALLOWED_EXT = ("gcode", "cnc", "nc")
FAT_BAD = set('<>:"/\\|?*')
MAX_NAME = 100


class UploadError(RuntimeError):
    pass


def check_name(name):
    """Raise UploadError unless `name` will be accepted by file_upload() AND shown by the app."""
    if not name or name != os.path.basename(name) or name in (".", ".."):
        raise UploadError("name must be a plain file name (no folders): %r" % name)
    if len(name.encode("utf-8")) > MAX_NAME:
        raise UploadError("name too long (%d bytes; keep <= %d - the server copies it into a 128-byte buffer)"
                          % (len(name.encode("utf-8")), MAX_NAME))
    if any(c in FAT_BAD or ord(c) < 32 for c in name) or ".." in name:
        raise UploadError("name contains characters the printer's FAT storage / server can't take: %r" % name)
    if name.startswith("."):
        raise UploadError("hidden names (leading '.') are not shown by the app")
    parts = [p for p in name.split(".") if p]
    if len(parts) != 2 or parts[1] not in ALLOWED_EXT:
        raise UploadError("the printer only accepts NAME.gcode / NAME.nc / NAME.cnc with exactly one dot and a "
                          "lower-case extension (it checks the text after the FIRST dot): %r" % name)
    return name


def safe_name(path):
    """Suggest an acceptable name for a local file: 'benchy_0.2mm.gcode' -> 'benchy_0-2mm.gcode'."""
    base = os.path.basename(path)
    stem, ext = os.path.splitext(base)
    ext = ext.lstrip(".").lower()
    ext = {"g": "gcode"}.get(ext, ext)
    if ext not in ALLOWED_EXT:
        ext = "gcode"
    stem = re.sub(r"[^A-Za-z0-9_\-]+", "-", stem).strip("-") or "print"
    return check_name(stem[:MAX_NAME - len(ext) - 1] + "." + ext)


def encode_multipart(filename, data):
    b = "----ivitouch" + uuid.uuid4().hex
    head = ('--%s\r\nContent-Disposition: form-data; name="file"; filename="%s"\r\n'
            'Content-Type: application/octet-stream\r\n\r\n' % (b, filename)).encode("utf-8")
    return head + data + ("\r\n--%s--\r\n" % b).encode(), "multipart/form-data; boundary=" + b


def upload(host, path, name=None, port=8080, timeout=300):
    """POST `path` to http://host:port/api/v1/upload as `name` (default: basename). Returns the reply text.
    Raises UploadError on a bad name or a non-201 reply."""
    name = check_name(name or os.path.basename(path))
    with open(path, "rb") as fh:
        data = fh.read()
    body, ctype = encode_multipart(name, data)
    req = urllib.request.Request("http://%s:%d/api/v1/upload" % (host, port), data=body, method="POST",
                                 headers={"Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            status, text = r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        status, text = e.code, e.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as e:
        raise UploadError("printer unreachable on %s:%d (%s)" % (host, port, e))
    if status != 201:
        raise UploadError("upload refused: HTTP %d %s" % (status, text.strip()[:200]))
    return text.strip()


def curl_command(host, path, name=None, port=8080):
    """The equivalent one-liner (for the runbook)."""
    name = check_name(name or os.path.basename(path))
    return "curl -sS -w ' HTTP %%{http_code}\\n' -F 'file=@%s;filename=%s' http://%s:%d/api/v1/upload" % (
        path, name, host, port)
