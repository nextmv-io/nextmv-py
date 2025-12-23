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

    @patch("nextmv.cli.main.load_config")
    def test_callback_skips_config_check_for_configure(self, mock_load_config):
        """Test that the callback skips config check when running configure."""
        mock_load_config.return_value = {}

        # Running configure should not trigger the error even with empty config
        result = self.runner.invoke(self.app, ["configure", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Configure the CLI", result.output)

    @patch("nextmv.cli.main.load_config")
    def test_callback_shows_error_when_no_config(self, mock_load_config):
        """Test that the callback shows error when no config exists for other commands."""
        mock_load_config.return_value = {}

        result = self.runner.invoke(self.app, ["version"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("No configuration found", result.output)

    @patch("nextmv.cli.main.load_config")
    def test_callback_allows_command_when_config_exists(self, mock_load_config):
        """Test that the callback allows commands when config exists."""
        mock_load_config.return_value = {"api_key": "test_key"}

        result = self.runner.invoke(self.app, ["version"])
        self.assertEqual(result.exit_code, 0)
