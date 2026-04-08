"""Tests for the MCP serve command and optional dependency handling."""

import importlib
import sys
import unittest
from unittest.mock import patch

from nextmv.cli.main import app
from typer.testing import CliRunner

from .conftest import _strip_ansi


class TestMCPServeCommand(unittest.TestCase):
    """Tests for the `nextmv mcp serve` command."""

    def setUp(self):
        self.runner = CliRunner()

    @patch("nextmv.cli.main.go_cli_exists")
    @patch("nextmv.cli.main.load_config")
    def test_mcp_help(self, mock_load_config, mock_go_cli_exists):
        """Test that `nextmv mcp --help` shows the MCP help text."""
        mock_go_cli_exists.return_value = False
        mock_load_config.return_value = {}

        result = self.runner.invoke(app, ["mcp", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Model Context Protocol", result.output)

    @patch("nextmv.cli.main.go_cli_exists")
    @patch("nextmv.cli.main.load_config")
    def test_mcp_serve_help(self, mock_load_config, mock_go_cli_exists):
        """Test that `nextmv mcp serve --help` shows serve help text."""
        mock_go_cli_exists.return_value = False
        mock_load_config.return_value = {}

        result = self.runner.invoke(app, ["mcp", "serve", "--help"])
        self.assertEqual(result.exit_code, 0)
        output = _strip_ansi(result.output)
        self.assertIn("Start the Nextmv MCP server", output)
        self.assertIn("--transport", output)
        self.assertIn("--port", output)

    @patch("nextmv.cli.main.go_cli_exists")
    @patch("nextmv.cli.main.load_config")
    def test_mcp_skips_config_check(self, mock_load_config, mock_go_cli_exists):
        """Test that `nextmv mcp` skips config existence check."""
        mock_go_cli_exists.return_value = False
        mock_load_config.return_value = {}

        result = self.runner.invoke(app, ["mcp", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn("No configuration found", result.output)


class TestMCPOptionalDependency(unittest.TestCase):
    """Tests for MCP as an optional dependency."""

    def test_mcp_init_raises_when_mcp_missing(self):
        """Importing nextmv.cli.mcp raises ImportError when mcp is not installed."""
        with patch("importlib.util.find_spec", return_value=None):
            # Remove cached module so the guard re-executes.
            saved = {}
            for key in list(sys.modules):
                if key.startswith("nextmv.cli.mcp"):
                    saved[key] = sys.modules.pop(key)
            try:
                with self.assertRaises(ImportError) as ctx:
                    importlib.import_module("nextmv.cli.mcp")
                self.assertIn("nextmv[mcp]", str(ctx.exception))
            finally:
                sys.modules.update(saved)

    def test_cli_works_without_mcp(self):
        """The CLI still works when the mcp subcommand cannot be imported."""

        runner = CliRunner()

        with (
            patch(
                "nextmv.cli.main.go_cli_exists",
                return_value=False,
            ),
            patch(
                "nextmv.cli.main.load_config",
                return_value={},
            ),
        ):
            result = runner.invoke(app, ["--help"])
            self.assertEqual(result.exit_code, 0)
            # Core subcommands should still be present.
            output = _strip_ansi(result.output)
            self.assertIn("cloud", output)
            self.assertIn("local", output)
            self.assertIn("community", output)
