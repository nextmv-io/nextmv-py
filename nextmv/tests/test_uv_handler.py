"""
Unit tests for the _find_uv_binary() function in nextmv.uv_handler.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from nextmv.uv_handler import _find_uv_binary


class TestFindUvBinary(unittest.TestCase):
    """Tests for _find_uv_binary()."""

    # ------------------------------------------------------------------
    # PyInstaller (frozen) branch
    # ------------------------------------------------------------------

    def test_frozen_returns_bundled_path(self):
        """When running as a frozen bundle the path inside _MEIPASS is returned."""
        with tempfile.TemporaryDirectory() as tmp:
            uv_bin_dir = os.path.join(tmp, "uv_bin")
            os.makedirs(uv_bin_dir)
            fake_uv = os.path.join(uv_bin_dir, "uv")
            open(fake_uv, "w").close()  # create the file

            with (
                patch.object(sys, "frozen", True, create=True),
                patch.object(sys, "_MEIPASS", tmp, create=True),
                patch("platform.system", return_value="Linux"),
            ):
                result = _find_uv_binary()

        self.assertEqual(result, fake_uv)

    def test_frozen_windows_uses_exe_suffix(self):
        """On Windows the bundled binary name ends with .exe."""
        with tempfile.TemporaryDirectory() as tmp:
            uv_bin_dir = os.path.join(tmp, "uv_bin")
            os.makedirs(uv_bin_dir)
            fake_uv = os.path.join(uv_bin_dir, "uv.exe")
            open(fake_uv, "w").close()

            with (
                patch.object(sys, "frozen", True, create=True),
                patch.object(sys, "_MEIPASS", tmp, create=True),
                patch("platform.system", return_value="Windows"),
            ):
                result = _find_uv_binary()

        self.assertEqual(result, fake_uv)

    def test_frozen_missing_binary_raises(self):
        """FileNotFoundError is raised when the bundled binary is absent."""
        with tempfile.TemporaryDirectory() as tmp:
            # uv_bin directory exists but the binary itself is missing
            os.makedirs(os.path.join(tmp, "uv_bin"))

            with (
                patch.object(sys, "frozen", True, create=True),
                patch.object(sys, "_MEIPASS", tmp, create=True),
                patch("platform.system", return_value="Linux"),
            ):
                with self.assertRaises(FileNotFoundError):
                    _find_uv_binary()

    def test_frozen_missing_uv_bin_dir_raises(self):
        """FileNotFoundError is raised when the entire uv_bin directory is missing."""
        with tempfile.TemporaryDirectory() as tmp:
            with (
                patch.object(sys, "frozen", True, create=True),
                patch.object(sys, "_MEIPASS", tmp, create=True),
                patch("platform.system", return_value="Linux"),
            ):
                with self.assertRaises(FileNotFoundError):
                    _find_uv_binary()

    # ------------------------------------------------------------------
    # uv module branch
    # ------------------------------------------------------------------

    def test_uv_module_used_when_available(self):
        """find_uv_bin() from the uv module is used when import succeeds."""
        fake_module = MagicMock()
        fake_module.find_uv_bin.return_value = "/usr/local/bin/uv"

        # Ensure we are NOT in a frozen bundle.
        with patch.object(sys, "frozen", False, create=True), patch.dict("sys.modules", {"uv": fake_module}):
            result = _find_uv_binary()

        self.assertEqual(result, "/usr/local/bin/uv")
        fake_module.find_uv_bin.assert_called_once()

    def test_uv_module_import_error_falls_through(self):
        """An ImportError from the uv module causes fallback to PATH lookup."""
        with (
            patch.object(sys, "frozen", False, create=True),
            patch.dict("sys.modules", {"uv": None}),
            patch("shutil.which", return_value="/opt/bin/uv"),
        ):
            result = _find_uv_binary()

        self.assertEqual(result, "/opt/bin/uv")

    def test_uv_module_attribute_error_falls_through(self):
        """An AttributeError (missing find_uv_bin attr) causes fallback to PATH lookup."""
        bad_module = MagicMock(spec=[])  # no find_uv_bin attribute

        with (
            patch.object(sys, "frozen", False, create=True),
            patch.dict("sys.modules", {"uv": bad_module}),
            patch("shutil.which", return_value="/opt/bin/uv"),
        ):
            result = _find_uv_binary()

        self.assertEqual(result, "/opt/bin/uv")

    # ------------------------------------------------------------------
    # PATH branch
    # ------------------------------------------------------------------

    def test_path_lookup_used_as_last_resort(self):
        """shutil.which is used as the last fallback when the uv module is absent."""
        with (
            patch.object(sys, "frozen", False, create=True),
            patch.dict("sys.modules", {"uv": None}),
            patch("shutil.which", return_value="/usr/bin/uv") as mock_which,
        ):
            result = _find_uv_binary()

        self.assertEqual(result, "/usr/bin/uv")
        mock_which.assert_called_once_with("uv")

    def test_raises_when_nothing_found(self):
        """FileNotFoundError is raised when neither the module nor PATH provide uv."""
        with (
            patch.object(sys, "frozen", False, create=True),
            patch.dict("sys.modules", {"uv": None}),
            patch("shutil.which", return_value=None),
        ):
            with self.assertRaises(FileNotFoundError) as ctx:
                _find_uv_binary()

        self.assertIn("uv binary not found", str(ctx.exception))

    def test_error_message_mentions_path_and_module(self):
        """The FileNotFoundError message hints at both PATH and module installation."""
        with (
            patch.object(sys, "frozen", False, create=True),
            patch.dict("sys.modules", {"uv": None}),
            patch("shutil.which", return_value=None),
        ):
            with self.assertRaises(FileNotFoundError) as ctx:
                _find_uv_binary()

        msg = str(ctx.exception)
        self.assertIn("PATH", msg)
        self.assertIn("module", msg)


if __name__ == "__main__":
    unittest.main()
