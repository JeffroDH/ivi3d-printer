import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import ivi_bridge as B
import ivi_setup_keys as K

class SerialDetect(unittest.TestCase):
    def test_defaults_per_os(self):
        self.assertEqual(B.default_serial_pattern("darwin"), "/dev/tty.usbmodem*")
        self.assertEqual(B.default_serial_pattern("linux"), "/dev/ttyACM*,/dev/ttyUSB*")
        self.assertEqual(B.default_serial_pattern("win32"), "COM*")
    def test_linux_acm_before_usb(self):
        g = {"/dev/ttyACM*": ["/dev/ttyACM1", "/dev/ttyACM0"], "/dev/ttyUSB*": ["/dev/ttyUSB0"]}
        self.assertEqual(B.find_usb_port("auto", globber=lambda p: g.get(p, []), platform="linux"), "/dev/ttyACM0")
        g.pop("/dev/ttyACM*")
        self.assertEqual(B.find_usb_port("auto", globber=lambda p: g.get(p, []), platform="linux"), "/dev/ttyUSB0")
        self.assertIsNone(B.find_usb_port("auto", globber=lambda p: [], platform="linux"))
    def test_mac_glob_unchanged(self):
        self.assertEqual(B.find_usb_port("/dev/tty.usbmodem*", globber=lambda p: ["/dev/tty.usbmodemX"], platform="darwin"), "/dev/tty.usbmodemX")
    def test_exact_path(self):
        self.assertEqual(B.find_usb_port("/dev/ttyACM3", exists=lambda p: True, platform="linux"), "/dev/ttyACM3")
        self.assertIsNone(B.find_usb_port("/dev/ttyACM3", exists=lambda p: False, platform="linux"))
    def test_windows_com(self):
        ports = ["COM10", "COM3"]
        self.assertEqual(B.find_usb_port("auto", ports=ports, platform="win32"), "COM3")
        self.assertEqual(B.find_usb_port("com10", ports=ports, platform="win32"), "COM10")
        self.assertIsNone(B.find_usb_port("COM*", ports=[], platform="win32"))
        # a Windows path is a file path, not a COM name
        self.assertIsNone(B.find_usb_port(r"C:\nope\x", exists=lambda p: False, ports=ports, platform="win32"))
    def test_open_serial_backend(self):
        self.assertTrue(B.termios is not None or B.PySerialPort)

class OrcaDirs(unittest.TestCase):
    def test_dirs(self):
        self.assertEqual(K.orca_dirs("darwin", {}, "/h"), ["/h/Library/Application Support/OrcaSlicer"])
        self.assertEqual(K.orca_dirs("linux", {}, "/h")[0], "/h/.config/OrcaSlicer")
        self.assertIn("io.github.softfever.OrcaSlicer", K.orca_dirs("linux", {}, "/h")[1])
        self.assertEqual(K.orca_dirs("linux", {"XDG_CONFIG_HOME": "/x"}, "/h")[0], "/x/OrcaSlicer")
        self.assertEqual(K.orca_dirs("win32", {"APPDATA": "C:/AD"}, "/h"), [os.path.join("C:/AD", "OrcaSlicer")])

if __name__ == "__main__": unittest.main()
