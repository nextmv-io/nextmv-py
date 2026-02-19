"""Unit tests for the nextmv MCP server module."""

import asyncio
import json
import os
import re
import unittest
from unittest.mock import MagicMock, patch

from nextmv.cli.main import app
from typer.testing import CliRunner

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    return _ANSI_RE.sub("", text)


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


class TestMCPServerTools(unittest.TestCase):
    """Tests for the MCP server tool registration."""

    def test_create_server_returns_fastmcp(self):
        """Test that create_server returns a FastMCP instance."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        self.assertEqual(server.name, "nextmv")

    def test_server_has_all_cloud_app_tools(self):
        """Test that cloud app tools are registered."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool_names = list(server._tool_manager._tools.keys())
        expected = [
            "cloud_list_apps",
            "cloud_get_app",
            "cloud_create_app",
            "cloud_delete_app",
            "cloud_app_exists",
            "cloud_update_app",
            "cloud_push_app",
        ]
        for name in expected:
            self.assertIn(name, tool_names, f"Missing tool: {name}")

    def test_server_has_all_cloud_run_tools(self):
        """Test that cloud run tools are registered."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool_names = list(server._tool_manager._tools.keys())
        expected = [
            "cloud_run",
            "cloud_run_submit",
            "cloud_run_status",
            "cloud_run_result",
            "cloud_cancel_run",
            "cloud_list_runs",
            "cloud_run_input",
            "cloud_run_logs",
        ]
        for name in expected:
            self.assertIn(name, tool_names, f"Missing tool: {name}")

    def test_server_has_all_version_instance_tools(self):
        """Test that version and instance tools are registered."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool_names = list(server._tool_manager._tools.keys())
        expected = [
            "cloud_list_versions",
            "cloud_get_version",
            "cloud_create_version",
            "cloud_update_version",
            "cloud_delete_version",
            "cloud_list_instances",
            "cloud_get_instance",
            "cloud_create_instance",
            "cloud_update_instance",
            "cloud_delete_instance",
        ]
        for name in expected:
            self.assertIn(name, tool_names, f"Missing tool: {name}")

    def test_server_has_all_experiment_tools(self):
        """Test that batch, input set, acceptance, scenario tools are registered."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool_names = list(server._tool_manager._tools.keys())
        expected = [
            "cloud_create_batch",
            "cloud_get_batch",
            "cloud_list_batches",
            "cloud_batch_metadata",
            "cloud_delete_batch",
            "cloud_list_input_sets",
            "cloud_get_input_set",
            "cloud_create_input_set",
            "cloud_update_input_set",
            "cloud_delete_input_set",
            "cloud_list_acceptance_tests",
            "cloud_get_acceptance_test",
            "cloud_create_acceptance_test",
            "cloud_delete_acceptance_test",
            "cloud_list_scenario_tests",
            "cloud_get_scenario_test",
            "cloud_create_scenario_test",
            "cloud_delete_scenario_test",
        ]
        for name in expected:
            self.assertIn(name, tool_names, f"Missing tool: {name}")

    def test_server_has_all_ensemble_shadow_switchback_tools(self):
        """Test that ensemble, shadow, and switchback tools are registered."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool_names = list(server._tool_manager._tools.keys())
        expected = [
            "cloud_list_ensembles",
            "cloud_get_ensemble",
            "cloud_create_ensemble",
            "cloud_delete_ensemble",
            "cloud_list_shadow_tests",
            "cloud_get_shadow_test",
            "cloud_create_shadow_test",
            "cloud_start_shadow_test",
            "cloud_stop_shadow_test",
            "cloud_delete_shadow_test",
            "cloud_list_switchback_tests",
            "cloud_get_switchback_test",
            "cloud_create_switchback_test",
            "cloud_start_switchback_test",
            "cloud_stop_switchback_test",
            "cloud_delete_switchback_test",
        ]
        for name in expected:
            self.assertIn(name, tool_names, f"Missing tool: {name}")

    def test_server_has_all_admin_tools(self):
        """Test that secrets, account, managed input tools are registered."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool_names = list(server._tool_manager._tools.keys())
        expected = [
            "cloud_list_secrets_collections",
            "cloud_get_secrets_collection",
            "cloud_create_secrets_collection",
            "cloud_delete_secrets_collection",
            "cloud_get_account",
            "cloud_get_queue",
            "cloud_list_managed_inputs",
            "cloud_get_managed_input",
            "cloud_create_managed_input",
            "cloud_delete_managed_input",
        ]
        for name in expected:
            self.assertIn(name, tool_names, f"Missing tool: {name}")

    def test_server_has_all_community_tools(self):
        """Test that community tools are registered."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool_names = list(server._tool_manager._tools.keys())
        for name in ["community_list", "community_clone"]:
            self.assertIn(name, tool_names, f"Missing tool: {name}")

    def test_server_has_all_local_tools(self):
        """Test that local tools are registered."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool_names = list(server._tool_manager._tools.keys())
        expected = [
            "local_run",
            "local_run_submit",
            "local_run_result",
            "local_list_runs",
            "local_run_logs",
            "local_sync",
        ]
        for name in expected:
            self.assertIn(name, tool_names, f"Missing tool: {name}")

    def test_total_tool_count(self):
        """Test that the server has the expected total number of tools."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool_names = list(server._tool_manager._tools.keys())
        # Should have 65+ tools covering all CLI commands.
        self.assertGreaterEqual(len(tool_names), 65, f"Only {len(tool_names)} tools registered")

    @patch("nextmv.cli.mcp.server._get_client")
    def test_cloud_list_apps_calls_sdk(self, mock_get_client):
        """Test that cloud_list_apps delegates to the SDK."""
        from nextmv.cli.mcp.server import create_server

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_app = MagicMock()
        mock_app.to_dict.return_value = {"id": "test-app", "name": "Test App"}

        with patch("nextmv.cli.mcp.server.list_applications", return_value=[mock_app]) as mock_list:
            server = create_server()
            tool = server._tool_manager._tools["cloud_list_apps"]
            asyncio.run(tool.run({}))
            mock_list.assert_called_once_with(mock_client)

    @patch("nextmv.cli.mcp.server._get_app")
    def test_cloud_cancel_run_calls_sdk(self, mock_get_app):
        """Test that cloud_cancel_run delegates to the SDK."""
        from nextmv.cli.mcp.server import create_server

        mock_app_instance = MagicMock()
        mock_get_app.return_value = mock_app_instance

        server = create_server()
        tool = server._tool_manager._tools["cloud_cancel_run"]
        asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-123"}))
        mock_app_instance.cancel_run.assert_called_once_with(run_id="run-123")

    @patch("nextmv.cli.mcp.server._get_app")
    def test_cloud_delete_app_calls_sdk(self, mock_get_app):
        """Test that cloud_delete_app delegates to the SDK."""
        from nextmv.cli.mcp.server import create_server

        mock_app_instance = MagicMock()
        mock_get_app.return_value = mock_app_instance

        server = create_server()
        tool = server._tool_manager._tools["cloud_delete_app"]
        asyncio.run(tool.run({"app_id": "my-app"}))
        mock_app_instance.delete.assert_called_once()

    @patch("nextmv.cli.mcp.server._get_app")
    def test_cloud_list_runs_calls_sdk(self, mock_get_app):
        """Test that cloud_list_runs delegates to the SDK."""
        from nextmv.cli.mcp.server import create_server

        mock_app_instance = MagicMock()
        mock_run = MagicMock()
        mock_run.to_dict.return_value = {"id": "run-1"}
        mock_app_instance.list_runs.return_value = [mock_run]
        mock_get_app.return_value = mock_app_instance

        server = create_server()
        tool = server._tool_manager._tools["cloud_list_runs"]
        asyncio.run(tool.run({"app_id": "my-app"}))
        mock_app_instance.list_runs.assert_called_once_with(status=None)


class TestGetClient(unittest.TestCase):
    """Tests for the _get_client helper."""

    @patch.dict("os.environ", {"NEXTMV_API_KEY": "test-key-123"}, clear=False)
    def test_get_client_from_env(self):
        """Test that _get_client uses NEXTMV_API_KEY env var."""
        from nextmv.cli.mcp.server import _get_client

        client = _get_client()
        self.assertEqual(client.api_key, "test-key-123")
        self.assertEqual(client.url, "https://api.cloud.nextmv.io")

    @patch.dict("os.environ", {"NEXTMV_API_KEY": "key", "NEXTMV_ENDPOINT": "custom.api.io"}, clear=False)
    def test_get_client_custom_endpoint(self):
        """Test that _get_client respects NEXTMV_ENDPOINT env var."""
        from nextmv.cli.mcp.server import _get_client

        client = _get_client()
        self.assertEqual(client.url, "https://custom.api.io")

    @patch.dict("os.environ", {}, clear=True)
    @patch("nextmv.cli.configuration.config.build_client", side_effect=Exception("no config"))
    def test_get_client_no_key_no_config_raises(self, mock_build):
        """Test that _get_client raises when no API key or config is available."""
        from nextmv.cli.mcp.server import _get_client

        with self.assertRaises(ValueError) as ctx:
            _get_client()
        self.assertIn("No Nextmv API key found", str(ctx.exception))


class TestSaveToFile(unittest.TestCase):
    """Tests for the _save_to_file helper."""

    def test_save_to_file_creates_json(self):
        """Test that _save_to_file writes valid JSON and returns a path message."""
        from nextmv.cli.mcp.server import _save_to_file

        data = {"stops": [{"id": "s1"}, {"id": "s2"}]}
        msg = _save_to_file(data, prefix="test")
        self.assertIn("Data saved to", msg)

        # Extract path from message.
        path = msg.split("Data saved to ")[1].split(" —")[0]
        try:
            with open(path) as f:
                loaded = json.load(f)
            self.assertEqual(loaded, data)
        finally:
            os.unlink(path)

    @patch("nextmv.cli.mcp.server._get_app")
    def test_cloud_run_input_returns_file_path(self, mock_get_app):
        """Test that cloud_run_input saves to file instead of returning raw data."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.run_input.return_value = {"depot": {"lat": 0, "lon": 0}, "stops": []}
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_run_input"]
        result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
        # Result is JSON-encoded string (json_response=True).
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("Data saved to", str(text))

    @patch("nextmv.cli.mcp.server._get_app")
    def test_cloud_run_result_returns_file_path(self, mock_get_app):
        """Test that cloud_run_result saves to file instead of returning raw data."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"output": {"routes": []}}
        mock_app.run_result.return_value = mock_result
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_run_result"]
        result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("Data saved to", str(text))

    @patch("nextmv.cli.mcp.server._get_app")
    def test_cloud_create_managed_input_with_raw_data(self, mock_get_app):
        """Test that cloud_create_managed_input uploads raw data when input is provided."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_upload_url = MagicMock()
        mock_upload_url.upload_id = "upl_123"
        mock_app.upload_url.return_value = mock_upload_url
        mock_mi = MagicMock()
        mock_mi.to_dict.return_value = {"id": "mi-1", "upload_id": "upl_123"}
        mock_app.new_managed_input.return_value = mock_mi
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_managed_input"]
        asyncio.run(tool.run({
            "app_id": "my-app",
            "name": "test input",
            "input": {"stops": [{"id": "s1"}]},
        }))
        mock_app.upload_url.assert_called_once()
        mock_app.upload_data.assert_called_once_with(
            upload_url=mock_upload_url,
            data={"stops": [{"id": "s1"}]},
        )
        mock_app.new_managed_input.assert_called_once_with(
            id=None, name="test input", description=None,
            run_id=None, upload_id="upl_123",
        )

    @patch("nextmv.cli.mcp.server._get_app")
    def test_cloud_create_input_set_with_managed_input_ids(self, mock_get_app):
        """Test that cloud_create_input_set passes managed inputs correctly."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_input_set = MagicMock()
        mock_input_set.to_dict.return_value = {"id": "is-1"}
        mock_app.new_input_set.return_value = mock_input_set
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_input_set"]
        asyncio.run(tool.run({
            "app_id": "my-app",
            "name": "test set",
            "managed_input_ids": ["mi-1", "mi-2"],
        }))
        call_kwargs = mock_app.new_input_set.call_args[1]
        self.assertEqual(len(call_kwargs["inputs"]), 2)
        self.assertEqual(call_kwargs["inputs"][0].id, "mi-1")
        self.assertEqual(call_kwargs["inputs"][1].id, "mi-2")

    @patch("nextmv.cli.mcp.server._get_app")
    def test_cloud_create_input_set_with_run_ids(self, mock_get_app):
        """Test that cloud_create_input_set passes run_ids correctly."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_input_set = MagicMock()
        mock_input_set.to_dict.return_value = {"id": "is-1"}
        mock_app.new_input_set.return_value = mock_input_set
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_input_set"]
        asyncio.run(tool.run({
            "app_id": "my-app",
            "name": "test set",
            "run_ids": ["run-1", "run-2"],
        }))
        call_kwargs = mock_app.new_input_set.call_args[1]
        self.assertEqual(call_kwargs["run_ids"], ["run-1", "run-2"])
        self.assertIsNone(call_kwargs["inputs"])

    @patch("nextmv.cli.mcp.server._get_app")
    def test_cloud_create_scenario_test_converts_dicts(self, mock_get_app):
        """Test that cloud_create_scenario_test converts dicts to Scenario objects."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.new_scenario_test.return_value = "st-123"
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_scenario_test"]
        asyncio.run(tool.run({
            "app_id": "my-app",
            "name": "test",
            "scenarios": [
                {
                    "instance_id": "stable",
                    "scenario_id": "s1",
                    "scenario_input": {
                        "input_set_id": "my-input-set",
                    },
                    "configuration": {
                        "options": {"duration": "30", "objective": "cost"},
                    },
                },
                {
                    "instance_id": "stable",
                    "scenario_id": "s2",
                    "scenario_input": {
                        "scenario_input_type": "input_set",
                        "scenario_input_data": "other-set",
                    },
                    "configuration": [
                        {"name": "duration", "values": ["10", "30"]},
                    ],
                },
            ],
        }))
        call_kwargs = mock_app.new_scenario_test.call_args[1]
        scenarios = call_kwargs["scenarios"]
        self.assertEqual(len(scenarios), 2)
        # First scenario: shorthand input_set_id + options dict.
        self.assertEqual(scenarios[0].instance_id, "stable")
        self.assertEqual(scenarios[0].scenario_id, "s1")
        self.assertEqual(scenarios[0].scenario_input.scenario_input_data, "my-input-set")
        self.assertEqual(len(scenarios[0].configuration), 2)
        # Second scenario: explicit type + list config.
        self.assertEqual(scenarios[1].scenario_input.scenario_input_data, "other-set")
        self.assertEqual(scenarios[1].configuration[0].values, ["10", "30"])
