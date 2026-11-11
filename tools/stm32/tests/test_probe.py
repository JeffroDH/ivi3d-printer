"""Frames the USB bootloader probe is allowed to send. No serial port is opened."""
import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bootloader_probe as probe


class ProbeFrames(unittest.TestCase):
    def test_a4_and_entry_reply_crcs(self):
        self.assertEqual(probe.A4.hex(), "a402aaaaaaaa9fbd")
        self.assertEqual(probe.crc16_xmodem(probe.A4[:-2]), 0xBD9F)
        self.assertEqual(probe.ENTRY_REPLY.hex(), "c405b019a2")
        self.assertEqual(probe.crc16_xmodem(probe.ENTRY_REPLY[:3]), 0xA219)

    def test_only_m997_and_a4_are_sendable(self):
        probe.assert_safe(probe.M997)
        probe.assert_safe(probe.A4)
        for cmd in (0xA1, 0xA2, 0xA3, 0xA0):
            with self.assertRaises(RuntimeError):
                probe.assert_safe(bytes([cmd, 0x02, 0, 0, 0, 0, 0, 0]))

    def test_reply_can_sit_among_other_bytes(self):
        noise = b" software reset, now in bootloader\r\n" + probe.ENTRY_REPLY + b"\x00"
        self.assertTrue(probe.reply_seen(noise))
        self.assertFalse(probe.reply_seen(b"ok\n"))

    def test_dry_run_sends_nothing(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(probe.main(["bootloader_probe.py", "-h"]), 0)
            self.assertEqual(probe.main(["bootloader_probe.py", "/dev/does-not-exist"]), 0)
        text = buf.getvalue()
        self.assertIn("A4 02 AA AA AA AA 9F BD", text)
        self.assertIn("Dry run. Pass --go", text)


if __name__ == "__main__":
    unittest.main()
