#!/usr/bin/env python3
"""Enter the motion-controller bootloader over USB-C, check its reply, and start the app.

The 2026-11-10 session on the printer did this and nothing more. It does not
erase or program flash: the only bytes it will write are ``M997\\n`` and the
eight-byte run frame ``A4 02 AA AA AA AA 9F BD``. A1, A2 and A3 are refused.

Stop ``ivi_bridge.py`` first. While it is running it holds the USB serial port
(LaunchAgent ``com.ivi3d.bridge`` on macOS). Start it again after this script
exits.

    python3 tools/stm32/bootloader_probe.py /dev/cu.usbmodem*          # print only
    python3 tools/stm32/bootloader_probe.py /dev/cu.usbmodem1234 --go  # do it

Without ``--go`` nothing is sent. On the Mac the verified node is
``/dev/cu.usbmodem*`` (the bridge's own pattern is ``/dev/tty.usbmodem*``,
the same CDC device). Linux is typically ``/dev/ttyACM*``. 115200 8N1, raw,
stdlib ``termios`` only.
"""
import glob
import os
import select
import sys
import time

M997 = b"M997\n"
A4 = bytes.fromhex("a402aaaaaaaa9fbd")
ENTRY_REPLY = bytes.fromhex("c405b019a2")
ALLOWED = (M997, A4)


def crc16_xmodem(data, crc=0):
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def assert_safe(payload):
    """Raise unless payload is one of the two frames this tool is allowed to send."""
    if payload not in ALLOWED:
        raise RuntimeError("refusing to send %s (this tool never sends A1, A2 or A3)" % payload.hex())
    return payload


def reply_seen(buf, reply=ENTRY_REPLY):
    return reply in buf


def resolve_port(spec):
    if os.path.exists(spec):
        return spec
    matches = sorted(glob.glob(spec))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise SystemExit("no serial node matches %s" % spec)
    raise SystemExit("several nodes match %s: %s" % (spec, ", ".join(matches)))


def open_raw(path, baud=115200):
    import fcntl
    import termios
    fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if hasattr(termios, "TIOCEXCL"):
            fcntl.ioctl(fd, termios.TIOCEXCL)
        attr = termios.tcgetattr(fd)
        speed = getattr(termios, "B%d" % baud)
        attr[0] = 0
        attr[1] = 0
        attr[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
        attr[3] = 0
        attr[4] = attr[5] = speed
        termios.tcsetattr(fd, termios.TCSANOW, attr)
        termios.tcflush(fd, termios.TCIOFLUSH)
    except Exception:
        os.close(fd)
        raise
    return fd


def write_all(fd, payload, timeout=1.0):
    assert_safe(payload)
    view = memoryview(payload)
    deadline = time.monotonic() + timeout
    while view:
        left = deadline - time.monotonic()
        if left <= 0:
            raise TimeoutError("write timed out")
        select.select([], [fd], [], left)
        try:
            n = os.write(fd, view)
        except BlockingIOError:
            continue
        if n <= 0:
            raise TimeoutError("write returned no bytes")
        view = view[n:]


def read_for(fd, seconds):
    deadline = time.monotonic() + seconds
    buf = b""
    while time.monotonic() < deadline:
        left = deadline - time.monotonic()
        ready, _, _ = select.select([fd], [], [], left)
        if not ready:
            continue
        try:
            chunk = os.read(fd, 256)
        except BlockingIOError:
            continue
        except OSError:
            break
        if not chunk:
            break
        buf += chunk
    return buf


def reopen(path, timeout=5.0, earliest=1.0):
    """Open path again after the CDC device has dropped and returned."""
    start = time.monotonic()
    gap = False
    last_error = None
    while time.monotonic() - start < timeout:
        exists = os.path.exists(path)
        elapsed = time.monotonic() - start
        if not exists:
            gap = True
        elif gap or elapsed >= earliest:
            try:
                return open_raw(path)
            except OSError as exc:
                last_error = exc
        time.sleep(0.05)
    detail = (" (%s)" % last_error) if last_error else ""
    raise TimeoutError("port %s did not come back within %.0f s%s" % (path, timeout, detail))


def port_dropped_and_returned(path, timeout=5.0):
    start = time.monotonic()
    gap = False
    while time.monotonic() - start < timeout:
        if not os.path.exists(path):
            gap = True
        elif gap:
            return True
        time.sleep(0.05)
    return False


def describe(port=None):
    if port:
        print("port:", port)
    print("send: M997\\n  to the running app, then wait for the bootloader")
    print("expect: C4 05 B0 19 A2  after a second M997\\n")
    print("send: A4 02 AA AA AA AA 9F BD  (start the app; no erase, no program)")
    print("Stop ivi_bridge.py first if it is running, and start it again afterwards.")


def run(path):
    describe(path)
    try:
        fd = open_raw(path)
    except OSError as exc:
        print("cannot open %s: %s" % (path, exc))
        print("If the bridge is running it holds this port. Stop it and retry.")
        return 1
    try:
        write_all(fd, M997)
    finally:
        os.close(fd)
    print("M997 sent to the app. Waiting for the bootloader to re-enumerate.")
    try:
        fd = reopen(path)
    except TimeoutError as exc:
        print(exc)
        print("The board may still be in the bootloader. A4 was not sent.")
        return 1
    try:
        write_all(fd, M997)
        heard = read_for(fd, 1.5)
        if not reply_seen(heard):
            print("bootloader reply was %s" % (heard.hex(" ") if heard else "silence"))
            print("expected C4 05 B0 19 A2. A4 was not sent.")
            print("The board may still be in the bootloader. A power cycle starts the app when no update is pending.")
            return 1
        print("bootloader answered C4 05 B0 19 A2")
        write_all(fd, A4)
        extra = read_for(fd, 0.5)
    finally:
        os.close(fd)
    if extra:
        print("bytes after A4: %s" % extra.hex(" "))
        print("The verified session got no reply. A4 was already sent. No erase or program frame was sent.")
        return 1
    print("no reply after A4")
    if port_dropped_and_returned(path, timeout=5.0):
        print("the app port dropped and returned")
        return 0
    print("the port did not drop and return within 5 s. A4 was sent. No erase or program frame was sent.")
    return 1


def main(argv):
    if crc16_xmodem(A4[:-2]) != int.from_bytes(A4[-2:], "little"):
        raise RuntimeError("A4 CRC mismatch")
    if crc16_xmodem(ENTRY_REPLY[:3]) != int.from_bytes(ENTRY_REPLY[-2:], "little"):
        raise RuntimeError("entry-reply CRC mismatch")
    go = "--go" in argv
    args = [a for a in argv[1:] if a != "--go"]
    if len(args) != 1 or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 2 if not args else 0
    if not go:
        describe()
        try:
            print("resolved:", resolve_port(args[0]))
        except SystemExit as exc:
            print(exc)
        print("Dry run. Pass --go to send those two frames.")
        return 0
    return run(resolve_port(args[0]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
