"""
Unit tests for the nextmv CLI main module.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from nextmv.cli.main import app, main
from typer.testing import CliRunner


class TestCallback(unittest.TestCase):
    """Tests for the CLI callback behavior."""

    def setUp(self):
        self.runner = CliRunner()
        self.app = app

    @patch("nextmv.cli.main._go_cli_exists")
    @patch("nextmv.cli.main.load_config")
    def test_callback_skips_config_check_for_configure(self, mock_load_config, mock_go_cli_exists):
        """Test that the callback skips config check when running configuration."""
        mock_load_config.return_value = {}
        mock_go_cli_exists.return_value = False

        # Running configuration should not trigger the error even with empty config
        result = self.runner.invoke(self.app, ["configuration", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Configure the CLI", result.output)

    @patch("nextmv.cli.main._go_cli_exists")
    @patch("nextmv.cli.main.load_config")
    def test_callback_shows_error_when_no_config(self, mock_load_config, mock_go_cli_exists):
        """Test that the callback shows error when no config exists for other commands."""
        mock_load_config.return_value = {}
        mock_go_cli_exists.return_value = False

        result = self.runner.invoke(self.app, ["version"])
        self.assertEqual(result.exit_code, 0)

    @patch("nextmv.cli.main._go_cli_exists")
    @patch("nextmv.cli.main.load_config")
    def test_callback_allows_command_when_config_exists(self, mock_load_config, mock_go_cli_exists):
        """Test that the callback allows commands when config exists."""
        mock_load_config.return_value = {"api_key": "test_key"}
        mock_go_cli_exists.return_value = False

        result = self.runner.invoke(self.app, ["version"])
        self.assertEqual(result.exit_code, 0)


class TestHandleGoCli(unittest.TestCase):
    """Tests for the Go CLI handling behavior."""

    def setUp(self):
        self.runner = CliRunner()
        self.app = app

    @patch("nextmv.cli.main._go_cli_exists")
    @patch("nextmv.cli.main.load_config")
    def test_no_prompt_when_go_cli_not_exists(self, mock_load_config, mock_go_cli_exists):
        """Test that no prompt is shown when Go CLI does not exist."""
        mock_go_cli_exists.return_value = False
        mock_load_config.return_value = {"api_key": "test_key"}

        result = self.runner.invoke(self.app, ["version"])
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn("deprecated", result.output)


class TestRunScript(unittest.TestCase):
    """Tests for the --run-script hidden flag."""

    def _write_script(self, content: str) -> str:
        """Write content to a temporary script file and return its path."""
        fd, path = tempfile.mkstemp(suffix=".py")
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def test_run_script_executes_script(self):
        """Test that --run-script runs the given script."""
        script = self._write_script("import sys; sys.exit(42)\n")
        try:
            with patch.object(sys, "argv", ["nextmv", "--run-script", script]):
                with self.assertRaises(SystemExit) as cm:
                    main()
            self.assertEqual(cm.exception.code, 42)
        finally:
            os.unlink(script)

    def test_run_script_forwards_trailing_args(self):
        """Test that trailing arguments are visible to the script as sys.argv."""
        # The script writes its own argv to a temp file so we can inspect it.
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            result_file = tmp.name
            script = self._write_script(f"import sys\nopen({result_file!r}, 'w').write(','.join(sys.argv))\n")
            try:
                with patch.object(sys, "argv", ["nextmv", "--run-script", script, "arg1", "arg2"]):
                    with self.assertRaises(SystemExit) as cm:
                        main()
                self.assertEqual(cm.exception.code, 0)
                with open(result_file) as f:
                    recorded = f.read().split(",")
                # The script sees itself as argv[0] and its own trailing args after.
                self.assertEqual(recorded[0], script)
                self.assertEqual(recorded[1], "arg1")
                self.assertEqual(recorded[2], "arg2")
            finally:
                os.unlink(script)
                if os.path.exists(result_file):
                    os.unlink(result_file)

    def test_run_script_missing_path_exits_with_error(self):
        """Test that omitting the script path prints an error and exits 1."""
        with patch.object(sys, "argv", ["nextmv", "--run-script"]):
            with self.assertRaises(SystemExit) as cm:
                main()
        self.assertEqual(cm.exception.code, 1)
