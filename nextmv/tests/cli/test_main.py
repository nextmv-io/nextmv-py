"""
Unit tests for the nextmv CLI main module.
"""

import unittest
from unittest.mock import patch

from nextmv.cli.main import app
from typer.testing import CliRunner


class TestCallback(unittest.TestCase):
    """Tests for the CLI callback behavior."""

    def setUp(self):
        self.runner = CliRunner()
        self.app = app

    @patch("nextmv.cli.main.go_cli_exists")
    @patch("nextmv.cli.main.load_config")
    def test_callback_skips_config_check_for_configure(self, mock_load_config, mock_go_cli_exists):
        """Test that the callback skips config check when running configuration."""
        mock_load_config.return_value = {}
        mock_go_cli_exists.return_value = False

        # Running configuration should not trigger the error even with empty config
        result = self.runner.invoke(self.app, ["configuration", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Configure the CLI", result.output)

    @patch("nextmv.cli.main.go_cli_exists")
    @patch("nextmv.cli.main.load_config")
    def test_callback_shows_error_when_no_config(self, mock_load_config, mock_go_cli_exists):
        """Test that the callback shows error when no config exists for other commands."""
        mock_load_config.return_value = {}
        mock_go_cli_exists.return_value = False

        result = self.runner.invoke(self.app, ["version"])
        self.assertEqual(result.exit_code, 0)

    @patch("nextmv.cli.main.go_cli_exists")
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

    @patch("nextmv.cli.main.go_cli_exists")
    @patch("nextmv.cli.main.load_config")
    def test_no_prompt_when_go_cli_not_exists(self, mock_load_config, mock_go_cli_exists):
        """Test that no prompt is shown when Go CLI does not exist."""
        mock_go_cli_exists.return_value = False
        mock_load_config.return_value = {"api_key": "test_key"}

        result = self.runner.invoke(self.app, ["version"])
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn("deprecated", result.output)

    @patch("nextmv.cli.main.remove_go_cli")
    @patch("nextmv.cli.main.go_cli_exists")
    @patch("nextmv.cli.main.load_config")
    def test_prompt_shown_when_go_cli_exists_user_accepts(
        self, mock_load_config, mock_go_cli_exists, mock_remove_go_cli
    ):
        """Test that prompt is shown when Go CLI exists and removal happens on accept."""
        mock_go_cli_exists.return_value = True
        mock_load_config.return_value = {"api_key": "test_key"}

        # Simulate user accepting the prompt (y)
        result = self.runner.invoke(self.app, ["version"], input="y\n")
        self.assertEqual(result.exit_code, 0)
        mock_remove_go_cli.assert_called_once()

    @patch("nextmv.cli.main.remove_go_cli")
    @patch("nextmv.cli.main.go_cli_exists")
    @patch("nextmv.cli.main.load_config")
    def test_prompt_shown_when_go_cli_exists_user_declines(
        self, mock_load_config, mock_go_cli_exists, mock_remove_go_cli
    ):
        """Test that prompt is shown when Go CLI exists and no removal on decline."""
        mock_go_cli_exists.return_value = True
        mock_load_config.return_value = {"api_key": "test_key"}

        # Simulate user declining the prompt (n)
        result = self.runner.invoke(self.app, ["version"], input="n\n")
        self.assertEqual(result.exit_code, 0)
        mock_remove_go_cli.assert_not_called()
        self.assertIn("later by removing", result.output)
