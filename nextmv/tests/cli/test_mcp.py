"""Unit tests for the nextmv MCP server module."""

import asyncio
import json
import os
import re
import shutil
import tempfile
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

    def test_server_has_all_profile_tools(self):
        """Test that profile tools are registered."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool_names = list(server._tool_manager._tools.keys())
        for name in ["cloud_list_profiles", "cloud_set_profile", "cloud_get_profile"]:
            self.assertIn(name, tool_names, f"Missing tool: {name}")

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
            "cloud_poll_run_logs",
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
        """Test that secrets, account, managed input, cross-app tools are registered."""
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
            "cloud_sso_delete_domain",
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
            "local_run_status",
            "local_run_result",
            "local_run_poll_result",
            "local_run_input",
            "local_list_runs",
            "local_run_logs",
            "local_sync",
            "manifest_init",
        ]
        for name in expected:
            self.assertIn(name, tool_names, f"Missing tool: {name}")

    def test_server_has_workflow_guide_tool(self):
        """Test that the workflow guide tool is registered."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool_names = list(server._tool_manager._tools.keys())
        self.assertIn("nextmv_workflow_guide", tool_names)

    def test_workflow_guide_returns_content(self):
        """Test that the workflow guide tool returns the guide content."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool = server._tool_manager._tools["nextmv_workflow_guide"]
        result = asyncio.run(tool.run({}))
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        # Verify key sections are present.
        self.assertIn("Nextmv App Development Workflow", str(text))
        self.assertIn("app.yaml", str(text))
        self.assertIn("local_run", str(text))
        self.assertIn("cloud_create_app", str(text))
        self.assertIn("Checklist", str(text))

    def test_total_tool_count(self):
        """Test that the server has the expected total number of tools."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool_names = list(server._tool_manager._tools.keys())
        self.assertEqual(len(tool_names), 89, f"Expected 89 tools, got {len(tool_names)}")

    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_list_apps_calls_sdk(self, mock_get_client):
        """Test that cloud_list_apps delegates to the SDK."""
        from nextmv.cli.mcp.server import create_server

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_app = MagicMock()
        mock_app.to_dict.return_value = {"id": "test-app", "name": "Test App"}

        with patch("nextmv.cli.mcp.tools.app.list_applications", return_value=[mock_app]) as mock_list:
            server = create_server()
            tool = server._tool_manager._tools["cloud_list_apps"]
            asyncio.run(tool.run({}))
            mock_list.assert_called_once_with(mock_client)

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_cancel_run_calls_sdk(self, mock_get_app):
        """Test that cloud_cancel_run delegates to the SDK."""
        from nextmv.cli.mcp.server import create_server

        mock_app_instance = MagicMock()
        mock_get_app.return_value = mock_app_instance

        server = create_server()
        tool = server._tool_manager._tools["cloud_cancel_run"]
        asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-123"}))
        mock_app_instance.cancel_run.assert_called_once_with(run_id="run-123")

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_delete_app_calls_sdk(self, mock_get_app):
        """Test that cloud_delete_app delegates to the SDK."""
        from nextmv.cli.mcp.server import create_server

        mock_app_instance = MagicMock()
        mock_get_app.return_value = mock_app_instance

        server = create_server()
        tool = server._tool_manager._tools["cloud_delete_app"]
        asyncio.run(tool.run({"app_id": "my-app"}))
        mock_app_instance.delete.assert_called_once()

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
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
        self.assertIn("Could not build a Nextmv client", str(ctx.exception))


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

    @patch("nextmv.cli.mcp.tools._helpers._cloud_run_dir")
    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_input_returns_file_path(self, mock_get_app, mock_run_dir):
        """Test that cloud_run_input saves to file instead of returning raw data."""
        from nextmv.cli.mcp.server import create_server

        tmp_dir = tempfile.mkdtemp()
        try:
            mock_run_dir.return_value = os.path.join(tmp_dir, "api.cloud.nextmv.io", "run-1")

            mock_app = MagicMock()
            mock_app.client.url = "https://api.cloud.nextmv.io"
            mock_app.run_input.return_value = {"depot": {"lat": 0, "lon": 0}, "stops": []}
            mock_get_app.return_value = mock_app

            server = create_server()
            tool = server._tool_manager._tools["cloud_run_input"]
            result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
            # Result is JSON-encoded string (json_response=True).
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("Downloaded:", str(text))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    @patch("nextmv.cli.mcp.tools._helpers._cloud_run_dir")
    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_result_returns_file_path(self, mock_get_app, mock_run_dir):
        """Test that cloud_run_result saves to file instead of returning raw data."""
        from nextmv.cli.mcp.server import create_server

        tmp_dir = tempfile.mkdtemp()
        try:
            mock_run_dir.return_value = os.path.join(tmp_dir, "api.cloud.nextmv.io", "run-1")

            mock_app = MagicMock()
            mock_app.client.url = "https://api.cloud.nextmv.io"
            mock_result = MagicMock()
            mock_result.to_dict.return_value = {"output": {"routes": []}}
            mock_app.run_result.return_value = mock_result
            mock_get_app.return_value = mock_app

            server = create_server()
            tool = server._tool_manager._tools["cloud_run_result"]
            result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("Downloaded:", str(text))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
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

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
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

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
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

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
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


class TestProfiles(unittest.TestCase):
    """Tests for profile management tools."""

    def test_mask_key(self):
        """Test that _mask_key masks all but the last 4 characters."""
        from nextmv.cli.mcp.server import _mask_key

        self.assertIsNone(_mask_key(None))
        self.assertEqual(_mask_key("abcd"), "abcd")
        self.assertEqual(_mask_key("abcde12345"), "XXXXXX2345")

    def test_set_and_get_profile(self):
        """Test that cloud_set_profile and cloud_get_profile work together."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        set_tool = server._tool_manager._tools["cloud_set_profile"]
        get_tool = server._tool_manager._tools["cloud_get_profile"]

        # Default profile.
        result = asyncio.run(get_tool.run({}))
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("default", str(text))

        # Set and get must run in the same async context for the
        # ContextVar state to be visible, since asyncio.run() creates
        # a fresh context each time.
        async def _set_then_get(profile: str) -> str:
            await set_tool.run({"profile": profile})
            result = await get_tool.run({})
            return json.loads(result[0].text) if hasattr(result[0], "text") else str(result)

        # Switch to a named profile.
        text = asyncio.run(_set_then_get("staging"))
        self.assertIn("staging", str(text))

        # Switch back to default.
        text = asyncio.run(_set_then_get("default"))
        self.assertIn("default", str(text))

    def test_list_profiles(self):
        """Test that cloud_list_profiles reads config correctly."""
        from nextmv.cli.mcp.server import create_server

        mock_config = {
            "apikey": "my-secret-key-1234",
            "endpoint": "api.cloud.nextmv.io",
            "staging": {
                "apikey": "stg-key-5678",
                "endpoint": "staging.api.nextmv.io",
            },
        }

        with patch(
            "nextmv.cli.configuration.config.load_config",
            return_value=mock_config,
        ):
            server = create_server()
            tool = server._tool_manager._tools["cloud_list_profiles"]
            result = asyncio.run(tool.run({}))
            profiles = json.loads(result[0].text) if hasattr(result[0], "text") else result
            self.assertEqual(len(profiles), 2)
            self.assertEqual(profiles[0]["name"], "default")
            self.assertEqual(profiles[0]["endpoint"], "api.cloud.nextmv.io")
            self.assertIn("1234", profiles[0]["api_key"])
            self.assertNotIn("my-secret", profiles[0]["api_key"])
            self.assertEqual(profiles[1]["name"], "staging")
            self.assertIn("5678", profiles[1]["api_key"])

    @patch.dict("os.environ", {}, clear=True)
    @patch("nextmv.cli.configuration.config.build_client")
    def test_get_client_uses_profile(self, mock_build_client):
        """Test that _get_client passes the profile to build_client."""
        from nextmv.cli.mcp.tools._helpers import session

        mock_build_client.return_value = MagicMock()

        # Explicit profile override.
        session.get_client(profile="staging")
        mock_build_client.assert_called_with(profile="staging")

        # Session-level profile.
        session.profile = "prod"
        try:
            session.get_client()
            mock_build_client.assert_called_with(profile="prod")
        finally:
            session.profile = None

    @patch.dict("os.environ", {"NEXTMV_API_KEY": "env-key"}, clear=False)
    def test_get_client_env_skipped_when_profile_set(self):
        """Test that env var is skipped when a profile is active."""
        from nextmv.cli.mcp.tools._helpers import session

        with patch("nextmv.cli.configuration.config.build_client") as mock_build:
            mock_build.return_value = MagicMock()
            session.profile = "staging"
            try:
                session.get_client()
                mock_build.assert_called_with(profile="staging")
            finally:
                session.profile = None


class TestBugFixes(unittest.TestCase):
    """Tests for specific bug fixes."""

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_create_ensemble_with_dicts(self, mock_get_app):
        """Bug 1: cloud_create_ensemble must accept plain dicts for run_groups and rules."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_ensemble = MagicMock()
        mock_ensemble.to_dict.return_value = {"id": "ens-1"}
        mock_app.new_ensemble_definition.return_value = mock_ensemble
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_ensemble"]
        asyncio.run(tool.run({
            "app_id": "my-app",
            "run_groups": [
                {"id": "grp-1", "instance_id": "prod", "repetitions": 1, "options": {}},
                {"id": "grp-2", "instance_id": "staging", "repetitions": 1, "options": {}},
            ],
            "rules": [
                {
                    "id": "min-cost",
                    "statistics_path": "result.value",
                    "objective": "minimize",
                    "tolerance": 0.01,
                    "index": 0,
                },
            ],
            "name": "test ensemble",
        }))
        mock_app.new_ensemble_definition.assert_called_once()
        call_kwargs = mock_app.new_ensemble_definition.call_args[1]
        # run_groups should be RunGroup objects, not dicts.
        from nextmv.cloud.ensemble import EvaluationRule, RunGroup
        self.assertIsInstance(call_kwargs["run_groups"][0], RunGroup)
        self.assertIsInstance(call_kwargs["run_groups"][1], RunGroup)
        self.assertEqual(call_kwargs["run_groups"][0].id, "grp-1")
        # rules should be EvaluationRule objects, not dicts.
        self.assertIsInstance(call_kwargs["rules"][0], EvaluationRule)
        self.assertEqual(call_kwargs["rules"][0].id, "min-cost")
        self.assertEqual(call_kwargs["rules"][0].tolerance.value, 0.01)

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_create_ensemble_with_shorthand_objective(self, mock_get_app):
        """Bug 1: objective shorthand 'min'/'max' should be accepted."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_ensemble = MagicMock()
        mock_ensemble.to_dict.return_value = {"id": "ens-1"}
        mock_app.new_ensemble_definition.return_value = mock_ensemble
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_ensemble"]
        asyncio.run(tool.run({
            "app_id": "my-app",
            "run_groups": [{"id": "grp-1", "instance_id": "prod"}],
            "rules": [
                {
                    "id": "min-cost",
                    "statistics_path": "result.value",
                    "objective": "min",
                    "tolerance": 0.01,
                    "index": 0,
                },
            ],
        }))
        call_kwargs = mock_app.new_ensemble_definition.call_args[1]
        from nextmv.cloud.ensemble import RuleObjective
        self.assertEqual(call_kwargs["rules"][0].objective, RuleObjective.MINIMIZE)

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_create_ensemble_with_dict_tolerance(self, mock_get_app):
        """Bug 1: rules with a dict tolerance should be converted correctly."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_ensemble = MagicMock()
        mock_ensemble.to_dict.return_value = {"id": "ens-1"}
        mock_app.new_ensemble_definition.return_value = mock_ensemble
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_ensemble"]
        asyncio.run(tool.run({
            "app_id": "my-app",
            "run_groups": [{"id": "grp-1", "instance_id": "prod"}],
            "rules": [
                {
                    "id": "rule-1",
                    "statistics_path": "result.value",
                    "objective": "maximize",
                    "tolerance": {"value": 5.0, "type": "absolute"},
                    "index": 1,
                },
            ],
        }))
        call_kwargs = mock_app.new_ensemble_definition.call_args[1]
        from nextmv.cloud.ensemble import RuleToleranceType
        rule = call_kwargs["rules"][0]
        self.assertEqual(rule.tolerance.value, 5.0)
        self.assertEqual(rule.tolerance.type, RuleToleranceType.ABSOLUTE)

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_create_ensemble_missing_run_group_field(self, mock_get_app):
        """Bug 1: Missing required run_group fields give a clear error string."""
        from nextmv.cli.mcp.server import create_server

        mock_get_app.return_value = MagicMock()

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_ensemble"]
        result = asyncio.run(tool.run({
            "app_id": "my-app",
            # Missing 'instance_id' in run group.
            "run_groups": [{"id": "grp-1"}],
            "rules": [
                {
                    "id": "r1",
                    "statistics_path": "result.value",
                    "objective": "min",
                    "tolerance": 0.01,
                },
            ],
        }))
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("run_groups[0]", str(text))
        self.assertIn("Error", str(text))

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_create_ensemble_missing_rule_field(self, mock_get_app):
        """Bug 1: Missing required rule fields give a clear error string."""
        from nextmv.cli.mcp.server import create_server

        mock_get_app.return_value = MagicMock()

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_ensemble"]
        result = asyncio.run(tool.run({
            "app_id": "my-app",
            "run_groups": [{"id": "grp-1", "instance_id": "prod"}],
            # Missing 'statistics_path' in rule.
            "rules": [{"id": "r1", "objective": "min", "tolerance": 0.01}],
        }))
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("rules[0]", str(text))
        self.assertIn("Error", str(text))

    def test_cloud_create_scenario_test_has_content_type_param(self):
        """Bug 2: cloud_create_scenario_test should accept a content_type parameter."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_scenario_test"]
        # Verify the tool's function accepts content_type in its signature.
        import inspect
        sig = inspect.signature(tool.fn)
        self.assertIn("content_type", sig.parameters)

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_create_scenario_test_content_type_path(self, mock_get_app):
        """Bug 2: content_type is passed through to the SDK's new_scenario_test."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.new_scenario_test.return_value = "scenario-test-123"
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_scenario_test"]
        asyncio.run(tool.run({
            "app_id": "my-app",
            "scenarios": [
                {
                    "instance_id": "stable",
                    "scenario_id": "s1",
                    "scenario_input": {
                        "input_set_id": "my-input-set",
                    },
                },
            ],
            "content_type": "multi-file",
            "name": "multi-file test",
        }))

        # Verify the SDK's new_scenario_test was called with content_type.
        mock_app.new_scenario_test.assert_called_once()
        call_kwargs = mock_app.new_scenario_test.call_args[1]
        self.assertEqual(call_kwargs["content_type"], "multi-file")

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_create_ensemble_missing_rule_fields(self, mock_get_app):
        """Bug 1: missing rule fields return a user-friendly error, not an exception."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_ensemble"]
        result = asyncio.run(tool.run({
            "app_id": "my-app",
            "run_groups": [{"id": "grp-1", "instance_id": "prod"}],
            "rules": [
                {
                    "id": "rule-missing-fields",
                    # Missing statistics_path and objective.
                },
            ],
        }))
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("Error", str(text))

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_create_scenario_test_content_type_multiple_inputs(
        self, mock_get_app,
    ):
        """Bug 2: content_type is passed to SDK for multi-input scenarios."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.new_scenario_test.return_value = "scenario-test-456"
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_scenario_test"]
        asyncio.run(tool.run({
            "app_id": "my-app",
            "scenarios": [
                {
                    "instance_id": "stable",
                    "scenario_id": "s1",
                    "scenario_input": {"input_set_id": "my-input-set"},
                },
            ],
            "content_type": "multi-file",
        }))

        # Verify the SDK was called with content_type and proper scenarios.
        mock_app.new_scenario_test.assert_called_once()
        call_kwargs = mock_app.new_scenario_test.call_args[1]
        self.assertEqual(call_kwargs["content_type"], "multi-file")
        self.assertEqual(len(call_kwargs["scenarios"]), 1)


class TestMultiFileRunSupport(unittest.TestCase):
    """Tests for multi-file run support in local and cloud run tools."""

    def test_build_run_configuration_none(self):
        """_build_run_configuration returns None when content_format is None."""
        from nextmv.cli.mcp.tools._helpers import _build_run_configuration

        self.assertIsNone(_build_run_configuration(None))

    def test_build_run_configuration_multi_file(self):
        """_build_run_configuration builds a RunConfiguration for 'multi-file'."""
        from nextmv.cli.mcp.tools._helpers import _build_run_configuration
        from nextmv.input import InputFormat

        config = _build_run_configuration("multi-file")
        self.assertIsNotNone(config)
        self.assertEqual(
            config.format.format_input.input_type,
            InputFormat.MULTI_FILE,
        )

    @patch("nextmv.cli.mcp.tools._helpers._get_local_app")
    def test_local_run_submit_json_input(self, mock_get_local_app):
        """local_run_submit passes input dict to new_run for JSON apps."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.new_run.return_value = "run-123"
        mock_get_local_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["local_run_submit"]
        asyncio.run(tool.run({
            "app_dir": "/some/app",
            "input": {"stops": []},
        }))
        mock_app.new_run.assert_called_once()
        call_kwargs = mock_app.new_run.call_args[1]
        self.assertEqual(call_kwargs["input"], {"stops": []})
        self.assertIsNone(call_kwargs.get("input_dir_path"))
        self.assertIsNone(call_kwargs.get("configuration"))

    @patch("nextmv.cli.mcp.tools._helpers._get_local_app")
    def test_local_run_submit_multifile_input(self, mock_get_local_app):
        """local_run_submit passes input_dir_path + configuration for multi-file apps."""
        from nextmv.cli.mcp.server import create_server
        from nextmv.input import InputFormat

        mock_app = MagicMock()
        mock_app.new_run.return_value = "run-456"
        mock_get_local_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["local_run_submit"]
        asyncio.run(tool.run({
            "app_dir": "/some/app",
            "input_dir_path": "/some/input-dir",
            "content_format": "multi-file",
        }))
        mock_app.new_run.assert_called_once()
        call_kwargs = mock_app.new_run.call_args[1]
        self.assertEqual(call_kwargs["input_dir_path"], "/some/input-dir")
        config = call_kwargs.get("configuration")
        self.assertIsNotNone(config)
        self.assertEqual(config.format.format_input.input_type, InputFormat.MULTI_FILE)

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_submit_json_input(self, mock_get_app):
        """cloud_run_submit passes input dict to new_run for JSON apps."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.new_run.return_value = "run-789"
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_run_submit"]
        asyncio.run(tool.run({
            "app_id": "my-app",
            "input": {"stops": []},
        }))
        mock_app.new_run.assert_called_once()
        call_kwargs = mock_app.new_run.call_args[1]
        self.assertEqual(call_kwargs["input"], {"stops": []})
        self.assertIsNone(call_kwargs.get("input_dir_path"))
        self.assertIsNone(call_kwargs.get("configuration"))

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_submit_multifile_input(self, mock_get_app):
        """cloud_run_submit passes input_dir_path + configuration for multi-file apps."""
        from nextmv.cli.mcp.server import create_server
        from nextmv.input import InputFormat

        mock_app = MagicMock()
        mock_app.new_run.return_value = "run-mf-1"
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_run_submit"]
        asyncio.run(tool.run({
            "app_id": "my-app",
            "input_dir_path": "/some/input-dir",
            "content_format": "multi-file",
        }))
        mock_app.new_run.assert_called_once()
        call_kwargs = mock_app.new_run.call_args[1]
        self.assertEqual(call_kwargs["input_dir_path"], "/some/input-dir")
        config = call_kwargs.get("configuration")
        self.assertIsNotNone(config)
        self.assertEqual(config.format.format_input.input_type, InputFormat.MULTI_FILE)


class TestHelperFunctions(unittest.TestCase):
    """Tests for _none_if_empty and _require_non_empty helper functions."""

    def test_none_if_empty_with_none(self):
        from nextmv.cli.mcp.tools._helpers import _none_if_empty

        self.assertIsNone(_none_if_empty(None))

    def test_none_if_empty_with_empty_string(self):
        from nextmv.cli.mcp.tools._helpers import _none_if_empty

        self.assertIsNone(_none_if_empty(""))

    def test_none_if_empty_with_whitespace(self):
        from nextmv.cli.mcp.tools._helpers import _none_if_empty

        self.assertIsNone(_none_if_empty("   "))

    def test_none_if_empty_with_value(self):
        from nextmv.cli.mcp.tools._helpers import _none_if_empty

        self.assertEqual(_none_if_empty("hello"), "hello")

    def test_none_if_empty_strips_whitespace(self):
        from nextmv.cli.mcp.tools._helpers import _none_if_empty

        self.assertEqual(_none_if_empty("  hello  "), "hello")

    def test_require_non_empty_with_valid_value(self):
        from nextmv.cli.mcp.tools._helpers import _require_non_empty

        self.assertEqual(_require_non_empty("hello", "field"), "hello")

    def test_require_non_empty_strips_whitespace(self):
        from nextmv.cli.mcp.tools._helpers import _require_non_empty

        self.assertEqual(_require_non_empty("  hello  ", "field"), "hello")

    def test_require_non_empty_with_empty_string(self):
        from nextmv.cli.mcp.tools._helpers import _require_non_empty

        with self.assertRaises(ValueError) as ctx:
            _require_non_empty("", "field")
        self.assertIn("field", str(ctx.exception))

    def test_require_non_empty_with_whitespace(self):
        from nextmv.cli.mcp.tools._helpers import _require_non_empty

        with self.assertRaises(ValueError) as ctx:
            _require_non_empty("   ", "field")
        self.assertIn("field", str(ctx.exception))

    def test_require_non_empty_with_none(self):
        from nextmv.cli.mcp.tools._helpers import _require_non_empty

        with self.assertRaises(ValueError):
            _require_non_empty(None, "field")


class TestEnsembleRunTools(unittest.TestCase):
    """Smoke tests for cloud_ensemble_run and cloud_ensemble_run_submit."""

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_ensemble_run_returns_file_path(self, mock_get_app):
        """cloud_ensemble_run polls and saves result to a temp file."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"id": "run-1", "output": {"routes": []}}
        mock_app.new_run_with_result.return_value = mock_result
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_ensemble_run"]
        result = asyncio.run(tool.run({
            "app_id": "my-app",
            "ensemble_id": "ens-1",
            "input": {"stops": []},
        }))
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("Data saved to", str(text))
        mock_app.new_run_with_result.assert_called_once()
        call_kwargs = mock_app.new_run_with_result.call_args[1]
        self.assertIsNotNone(call_kwargs["configuration"].run_type)

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_ensemble_run_submit_returns_run_id(self, mock_get_app):
        """cloud_ensemble_run_submit returns the run ID immediately."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.new_run.return_value = "run-ens-42"
        mock_get_app.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_ensemble_run_submit"]
        result = asyncio.run(tool.run({
            "app_id": "my-app",
            "ensemble_id": "ens-1",
            "input": {"stops": []},
        }))
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("run-ens-42", str(text))
        mock_app.new_run.assert_called_once()

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_ensemble_run_empty_app_id_returns_error(self, mock_get_app):
        """cloud_ensemble_run returns an error for empty app_id."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool = server._tool_manager._tools["cloud_ensemble_run"]
        result = asyncio.run(tool.run({
            "app_id": "",
            "ensemble_id": "ens-1",
            "input": {"stops": []},
        }))
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("app_id", str(text))
        mock_get_app.assert_not_called()

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_ensemble_run_submit_empty_ensemble_id_returns_error(self, mock_get_app):
        """cloud_ensemble_run_submit returns an error for whitespace-only ensemble_id."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool = server._tool_manager._tools["cloud_ensemble_run_submit"]
        result = asyncio.run(tool.run({
            "app_id": "my-app",
            "ensemble_id": "   ",
            "input": {"stops": []},
        }))
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("ensemble_id", str(text))
        mock_get_app.assert_not_called()


class TestCloudRunCache(unittest.TestCase):
    """Tests for the cloud run local cache feature."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_cloud_run_dir(self):
        """Test that _cloud_run_dir returns the expected path."""
        from nextmv.cli.mcp.tools._helpers import _cloud_run_dir

        result = _cloud_run_dir("api.cloud.nextmv.io", "run-123")
        expected = os.path.join(
            str(os.path.expanduser("~")), ".nextmv", "runs", "api.cloud.nextmv.io", "run-123"
        )
        self.assertEqual(result, expected)

    def test_cloud_run_file_exists_returns_path(self):
        """Test that _cloud_run_file_exists returns the path when the file exists."""
        from nextmv.cli.mcp.tools._helpers import _cloud_run_file_exists

        # Create a file inside the temp dir.
        run_dir = os.path.join(self.tmp_dir, "run-1")
        os.makedirs(run_dir, exist_ok=True)
        file_path = os.path.join(run_dir, "run-1.json")
        with open(file_path, "w") as f:
            f.write("{}")

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            result = _cloud_run_file_exists("ep", "run-1", "run-1.json")
            self.assertEqual(result, file_path)

    def test_cloud_run_file_exists_returns_none(self):
        """Test that _cloud_run_file_exists returns None for nonexistent files."""
        from nextmv.cli.mcp.tools._helpers import _cloud_run_file_exists

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=os.path.join(self.tmp_dir, "no-such-run"),
        ):
            result = _cloud_run_file_exists("ep", "run-999", "run-999.json")
            self.assertIsNone(result)

    def test_endpoint_from_app(self):
        """Test that _endpoint_from_app strips the URL scheme."""
        from nextmv.cli.mcp.tools._helpers import _endpoint_from_app

        mock_app = MagicMock()
        mock_app.client.url = "https://api.cloud.nextmv.io"
        self.assertEqual(_endpoint_from_app(mock_app), "api.cloud.nextmv.io")

        mock_app.client.url = "http://localhost:9000"
        self.assertEqual(_endpoint_from_app(mock_app), "localhost:9000")

    def test_save_cloud_run_file(self):
        """Test that _save_cloud_run_file creates the file with correct JSON."""
        from nextmv.cli.mcp.tools._helpers import _save_cloud_run_file

        run_dir = os.path.join(self.tmp_dir, "run-1")
        data = {"output": {"routes": []}}

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            path = _save_cloud_run_file(data, "ep", "run-1", "run-1.json")
            self.assertTrue(os.path.exists(path))
            with open(path) as f:
                loaded = json.load(f)
            self.assertEqual(loaded, data)

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_result_uses_cache(self, mock_get_app):
        """Test that cloud_run_result returns cached data without calling the SDK."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.client.url = "https://api.cloud.nextmv.io"
        mock_get_app.return_value = mock_app

        # Pre-populate cache.
        run_dir = os.path.join(self.tmp_dir, "run-1")
        os.makedirs(run_dir, exist_ok=True)
        cached_file = os.path.join(run_dir, "run-1.json")
        with open(cached_file, "w") as f:
            json.dump({"output": {}}, f)

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            server = create_server()
            tool = server._tool_manager._tools["cloud_run_result"]
            result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("Cached:", str(text))
            mock_app.run_result.assert_not_called()

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_result_downloads_on_miss(self, mock_get_app):
        """Test that cloud_run_result downloads, caches, and extracts outputs."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.client.url = "https://api.cloud.nextmv.io"
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {
            "output": {
                "solution": {"items": [1, 2, 3], "value": 100},
                "statistics": {"duration": 0.5},
                "metrics": {"cost": 42},
                "assets": [{"name": "chart"}],
            },
        }
        mock_result.id = "run-1"
        mock_app.run_result.return_value = mock_result
        mock_get_app.return_value = mock_app

        run_dir = os.path.join(self.tmp_dir, "run-1")

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            server = create_server()
            tool = server._tool_manager._tools["cloud_run_result"]
            result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("Downloaded:", str(text))
            mock_app.run_result.assert_called_once()

            # Verify outputs were extracted into local run layout.
            output_data = {
                "solution": {"items": [1, 2, 3], "value": 100},
                "statistics": {"duration": 0.5},
                "metrics": {"cost": 42},
                "assets": [{"name": "chart"}],
            }

            # solution.json contains the full output dict (matching local behavior).
            sol_path = os.path.join(run_dir, "outputs", "solutions", "solution.json")
            self.assertTrue(os.path.exists(sol_path))
            with open(sol_path) as f:
                self.assertEqual(json.load(f), output_data)

            # statistics.json is wrapped with {"statistics": ...} (matching local).
            stats_path = os.path.join(run_dir, "outputs", "statistics", "statistics.json")
            self.assertTrue(os.path.exists(stats_path))
            with open(stats_path) as f:
                self.assertEqual(json.load(f), {"statistics": {"duration": 0.5}})

            # metrics.json is raw (matching local).
            metrics_path = os.path.join(run_dir, "outputs", "metrics", "metrics.json")
            self.assertTrue(os.path.exists(metrics_path))
            with open(metrics_path) as f:
                self.assertEqual(json.load(f), {"cost": 42})

            # assets.json is wrapped with {"assets": ...} (matching local).
            assets_path = os.path.join(run_dir, "outputs", "assets", "assets.json")
            self.assertTrue(os.path.exists(assets_path))
            with open(assets_path) as f:
                self.assertEqual(json.load(f), {"assets": [{"name": "chart"}]})

    def test_extract_cloud_run_outputs_skips_missing(self):
        """Test that _extract_cloud_run_outputs skips components that are absent."""
        from nextmv.cli.mcp.tools._helpers import _extract_cloud_run_outputs

        run_dir = os.path.join(self.tmp_dir, "run-partial")

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            # Only solution present, no metrics/statistics/assets.
            _extract_cloud_run_outputs(
                {"output": {"solution": {"x": 1}}}, "ep", "run-partial"
            )

            # solution.json contains the full output dict.
            sol_path = os.path.join(run_dir, "outputs", "solutions", "solution.json")
            self.assertTrue(os.path.exists(sol_path))
            with open(sol_path) as f:
                self.assertEqual(json.load(f), {"solution": {"x": 1}})

            # These should not exist.
            self.assertFalse(os.path.exists(os.path.join(run_dir, "outputs", "metrics")))
            self.assertFalse(os.path.exists(os.path.join(run_dir, "outputs", "statistics")))
            self.assertFalse(os.path.exists(os.path.join(run_dir, "outputs", "assets")))

    def test_extract_cloud_run_outputs_empty_solution(self):
        """Test that _extract_cloud_run_outputs writes solution.json even for empty solution."""
        from nextmv.cli.mcp.tools._helpers import _extract_cloud_run_outputs

        run_dir = os.path.join(self.tmp_dir, "run-empty-sol")

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            _extract_cloud_run_outputs(
                {"output": {"solution": {}, "assets": []}}, "ep", "run-empty-sol"
            )

            # Even empty solution should be written (full output dict).
            sol_path = os.path.join(run_dir, "outputs", "solutions", "solution.json")
            self.assertTrue(os.path.exists(sol_path))
            with open(sol_path) as f:
                self.assertEqual(json.load(f), {"solution": {}, "assets": []})

            # Empty list assets should be skipped (matching local executor).
            self.assertFalse(os.path.exists(os.path.join(run_dir, "outputs", "assets")))

    def test_extract_cloud_run_outputs_csv_archive_noop(self):
        """Test that _extract_cloud_run_outputs is a no-op for csv-archive results."""
        from nextmv.cli.mcp.tools._helpers import _extract_cloud_run_outputs

        run_dir = os.path.join(self.tmp_dir, "run-csv-noop")

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            # csv-archive results have a URL, not inline solution data.
            _extract_cloud_run_outputs(
                {"output": {"url": "https://s3.example.com/output.tar.gz"}}, "ep", "run-csv-noop"
            )
            self.assertFalse(os.path.exists(os.path.join(run_dir, "outputs")))

    def test_extract_cloud_run_outputs_no_output_key(self):
        """Test that _extract_cloud_run_outputs is a no-op when output is missing."""
        from nextmv.cli.mcp.tools._helpers import _extract_cloud_run_outputs

        run_dir = os.path.join(self.tmp_dir, "run-empty")

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            _extract_cloud_run_outputs({}, "ep", "run-empty")
            self.assertFalse(os.path.exists(os.path.join(run_dir, "outputs")))

    def test_extract_cloud_run_outputs_generates_visuals(self):
        """Test that _extract_cloud_run_outputs generates HTML visuals from Plotly assets."""
        from nextmv.cli.mcp.tools._helpers import _extract_cloud_run_outputs

        run_dir = os.path.join(self.tmp_dir, "run-visuals")

        # Minimal Plotly figure JSON that plotly.io can parse.
        plotly_content = {
            "data": [{"type": "scatter", "x": [1, 2], "y": [3, 4]}],
            "layout": {"title": "Test"},
        }

        result_dict = {
            "output": {
                "solution": {"value": 42},
                "assets": [
                    {
                        "name": "my_chart",
                        "content": plotly_content,
                        "content_type": "json",
                        "visual": {
                            "visual_schema": "plotly",
                            "label": "test_chart",
                        },
                    },
                ],
            },
        }

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            _extract_cloud_run_outputs(result_dict, "ep", "run-visuals")

            # Verify assets.json was written.
            assets_path = os.path.join(run_dir, "outputs", "assets", "assets.json")
            self.assertTrue(os.path.exists(assets_path))

            # Verify visuals/ directory was created with HTML file.
            visuals_dir = os.path.join(run_dir, "visuals")
            self.assertTrue(os.path.isdir(visuals_dir))
            html_file = os.path.join(visuals_dir, "test_chart.html")
            self.assertTrue(os.path.exists(html_file))
            with open(html_file, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("<html>", content.lower())

    def test_extract_cloud_run_outputs_visual_failure_is_ignored(self):
        """Test that visual generation failure does not lose the run result."""
        from nextmv.cli.mcp.tools._helpers import _extract_cloud_run_outputs

        run_dir = os.path.join(self.tmp_dir, "run-bad-visual")

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ), patch(
            "nextmv.local.executor.process_run_visuals",
            side_effect=RuntimeError("plotly exploded"),
        ):
            # Should not raise despite visual generation failure.
            _extract_cloud_run_outputs(
                {"output": {"solution": {"x": 1}, "statistics": {"duration": 0.5}}},
                "ep",
                "run-bad-visual",
            )

            # Core data should still be written.
            sol_path = os.path.join(run_dir, "outputs", "solutions", "solution.json")
            self.assertTrue(os.path.exists(sol_path))
            stats_path = os.path.join(run_dir, "outputs", "statistics", "statistics.json")
            self.assertTrue(os.path.exists(stats_path))

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_input_uses_cache(self, mock_get_app):
        """Test that cloud_run_input returns cached data without calling the SDK."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.client.url = "https://api.cloud.nextmv.io"
        mock_get_app.return_value = mock_app

        # Pre-populate cache.
        run_dir = os.path.join(self.tmp_dir, "run-1")
        inputs_dir = os.path.join(run_dir, "inputs")
        os.makedirs(inputs_dir, exist_ok=True)
        cached_file = os.path.join(inputs_dir, "input.json")
        with open(cached_file, "w") as f:
            json.dump({"stops": []}, f)

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            server = create_server()
            tool = server._tool_manager._tools["cloud_run_input"]
            result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("Cached:", str(text))
            mock_app.run_input.assert_not_called()

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_input_downloads_on_miss(self, mock_get_app):
        """Test that cloud_run_input downloads and saves as inputs/input.json on miss."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.client.url = "https://api.cloud.nextmv.io"
        mock_app.run_input.return_value = {"stops": []}
        mock_get_app.return_value = mock_app

        run_dir = os.path.join(self.tmp_dir, "run-1")

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            server = create_server()
            tool = server._tool_manager._tools["cloud_run_input"]
            result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("Downloaded:", str(text))
            mock_app.run_input.assert_called_once()
            # Verify the file was saved.
            saved = os.path.join(run_dir, "inputs", "input.json")
            self.assertTrue(os.path.exists(saved))
            with open(saved) as f:
                self.assertEqual(json.load(f), {"stops": []})

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_logs_uses_cache(self, mock_get_app):
        """Test that cloud_run_logs returns cached data without calling the SDK."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.client.url = "https://api.cloud.nextmv.io"
        mock_get_app.return_value = mock_app

        # Pre-populate cache.
        run_dir = os.path.join(self.tmp_dir, "run-1")
        logs_dir = os.path.join(run_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        cached_file = os.path.join(logs_dir, "logs.log")
        with open(cached_file, "w") as f:
            f.write("some log output\n")

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            server = create_server()
            tool = server._tool_manager._tools["cloud_run_logs"]
            result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("Cached:", str(text))
            mock_app.run_logs.assert_not_called()

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_logs_downloads_on_miss(self, mock_get_app):
        """Test that cloud_run_logs downloads and caches as plain text."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.client.url = "https://api.cloud.nextmv.io"
        mock_logs = MagicMock()
        mock_logs.to_dict.return_value = {"log": "solver started\nsolver finished"}
        mock_app.run_logs.return_value = mock_logs
        mock_get_app.return_value = mock_app

        run_dir = os.path.join(self.tmp_dir, "run-1")

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            server = create_server()
            tool = server._tool_manager._tools["cloud_run_logs"]
            result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("Downloaded:", str(text))
            mock_app.run_logs.assert_called_once()

            # Verify file was written as plain text at the correct path.
            logs_file = os.path.join(run_dir, "logs", "logs.log")
            self.assertTrue(os.path.exists(logs_file))
            with open(logs_file) as f:
                content = f.read()
            self.assertIn("solver started", content)
            self.assertIn("solver finished", content)

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_poll_run_logs_writes_plain_text(self, mock_get_app):
        """Test that cloud_poll_run_logs writes timestamped entries as plain text."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.client.url = "https://api.cloud.nextmv.io"

        # Simulate poll_logs calling log_func with timestamped entries.
        def fake_poll_logs(run_id, polling_options, log_func):
            entry1 = MagicMock()
            entry1.timestamp = "2026-03-21T10:00:00Z"
            entry1.log = "starting solver"
            entry2 = MagicMock()
            entry2.timestamp = "2026-03-21T10:00:05Z"
            entry2.log = "solver complete"
            log_func(entry1)
            log_func(entry2)

        mock_app.poll_logs.side_effect = fake_poll_logs
        mock_get_app.return_value = mock_app

        run_dir = os.path.join(self.tmp_dir, "run-poll")

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            server = create_server()
            tool = server._tool_manager._tools["cloud_poll_run_logs"]
            result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("Downloaded:", str(text))

            # Verify file content is plain text with timestamps.
            logs_file = os.path.join(run_dir, "logs", "logs.log")
            self.assertTrue(os.path.exists(logs_file))
            with open(logs_file) as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertIn("2026-03-21T10:00:00Z", lines[0])
            self.assertIn("starting solver", lines[0])
            self.assertIn("solver complete", lines[1])

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_multifile_moves_outputs(self, mock_get_app):
        """Test that cloud_run with csv-archive extracts outputs into outputs/ dir."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.client.url = "https://api.cloud.nextmv.io"
        mock_result = MagicMock()
        mock_result.id = "run-csv"
        # For csv-archive, output is a URL, not inline data.
        mock_result.to_dict.return_value = {
            "output": {"url": "https://s3.example.com/output.tar.gz"},
        }
        mock_get_app.return_value = mock_app

        run_dir = os.path.join(self.tmp_dir, "run-csv")
        # Track the pending dir created by safe_id so we can verify it was moved.
        pending_dirs_created: list[str] = []

        def fake_cloud_run_dir(endpoint, run_id):
            if run_id.startswith("pending-"):
                d = os.path.join(self.tmp_dir, run_id)
                pending_dirs_created.append(d)
                return d
            return run_dir

        def fake_new_run(*, input, input_dir_path, configuration, instance_id,
                         run_options, polling_options, managed_input_id, output_dir_path):
            # Simulate SDK extracting tar.gz into output_dir_path.
            if output_dir_path:
                os.makedirs(output_dir_path, exist_ok=True)
                with open(os.path.join(output_dir_path, "solution.csv"), "w") as f:
                    f.write("item,chosen\nA,1\nB,0\n")
            return mock_result

        mock_app.new_run_with_result.side_effect = fake_new_run

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            side_effect=fake_cloud_run_dir,
        ):
            server = create_server()
            tool = server._tool_manager._tools["cloud_run"]
            result = asyncio.run(tool.run({
                "app_id": "my-app",
                "input_dir_path": "/some/csvs",
                "content_format": "csv-archive",
            }))
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("Downloaded:", str(text))

            # Verify output was moved from pending dir to run-csv/outputs/.
            outputs_dir = os.path.join(run_dir, "outputs")
            self.assertTrue(os.path.isdir(outputs_dir))
            sol_file = os.path.join(outputs_dir, "solution.csv")
            self.assertTrue(os.path.exists(sol_file))
            with open(sol_file) as f:
                self.assertIn("item,chosen", f.read())

            # The pending dir's outputs should no longer exist (it was renamed).
            self.assertTrue(len(pending_dirs_created) > 0)
            for d in pending_dirs_created:
                self.assertFalse(os.path.exists(os.path.join(d, "outputs")))

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_input_multifile_downloads(self, mock_get_app):
        """Test that cloud_run_input extracts multifile inputs into inputs/ dir."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.client.url = "https://api.cloud.nextmv.io"

        run_dir = os.path.join(self.tmp_dir, "run-csv-input")

        def fake_run_input(run_id, output_dir_path):
            # Simulate SDK extracting tar.gz into output_dir_path.
            os.makedirs(output_dir_path, exist_ok=True)
            with open(os.path.join(output_dir_path, "items.csv"), "w") as f:
                f.write("item,weight,value\nA,10,60\n")
            with open(os.path.join(output_dir_path, "capacity.csv"), "w") as f:
                f.write("capacity\n50\n")
            return None  # Non-JSON: SDK returns None.

        mock_app.run_input.side_effect = fake_run_input
        mock_get_app.return_value = mock_app

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            server = create_server()
            tool = server._tool_manager._tools["cloud_run_input"]
            result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("Downloaded:", str(text))

            # Verify extracted files.
            inputs_dir = os.path.join(run_dir, "inputs")
            self.assertTrue(os.path.exists(os.path.join(inputs_dir, "items.csv")))
            self.assertTrue(os.path.exists(os.path.join(inputs_dir, "capacity.csv")))

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_input_multifile_uses_cache(self, mock_get_app):
        """Test that cloud_run_input returns cached multifile inputs without re-downloading."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.client.url = "https://api.cloud.nextmv.io"
        mock_get_app.return_value = mock_app

        # Pre-populate cache with multifile inputs.
        run_dir = os.path.join(self.tmp_dir, "run-csv-cached")
        inputs_dir = os.path.join(run_dir, "inputs")
        os.makedirs(inputs_dir, exist_ok=True)
        with open(os.path.join(inputs_dir, "items.csv"), "w") as f:
            f.write("item,weight\nA,10\n")

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            server = create_server()
            tool = server._tool_manager._tools["cloud_run_input"]
            result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("Cached:", str(text))
            mock_app.run_input.assert_not_called()

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_result_multifile_extracts_output(self, mock_get_app):
        """Test that cloud_run_result for non-JSON extracts into outputs/ dir."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.client.url = "https://api.cloud.nextmv.io"

        run_dir = os.path.join(self.tmp_dir, "run-csv-result")

        def fake_run_result(run_id, output_dir_path):
            # Simulate SDK extracting tar.gz into output_dir_path.
            os.makedirs(output_dir_path, exist_ok=True)
            with open(os.path.join(output_dir_path, "solution.csv"), "w") as f:
                f.write("item,chosen\nA,1\n")
            mock_result = MagicMock()
            # For csv-archive, output has a URL not inline data.
            mock_result.to_dict.return_value = {
                "output": {"url": "https://s3.example.com/output.tar.gz"},
            }
            return mock_result

        mock_app.run_result.side_effect = fake_run_result
        mock_get_app.return_value = mock_app

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ):
            server = create_server()
            tool = server._tool_manager._tools["cloud_run_result"]
            result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("Downloaded:", str(text))

            # Verify the output was extracted.
            outputs_dir = os.path.join(run_dir, "outputs")
            self.assertTrue(os.path.isdir(outputs_dir))
            sol_file = os.path.join(outputs_dir, "solution.csv")
            self.assertTrue(os.path.exists(sol_file))
            with open(sol_file) as f:
                self.assertIn("item,chosen", f.read())


class TestMCPOptionalDependency(unittest.TestCase):
    """Tests for MCP as an optional dependency."""

    def test_mcp_init_raises_when_mcp_missing(self):
        """Importing nextmv.cli.mcp raises ImportError when mcp is not installed."""
        import importlib
        import sys

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

        with patch(
            "nextmv.cli.main.go_cli_exists", return_value=False,
        ), patch(
            "nextmv.cli.main.load_config", return_value={},
        ):
            result = runner.invoke(app, ["--help"])
            self.assertEqual(result.exit_code, 0)
            # Core subcommands should still be present.
            output = _strip_ansi(result.output)
            self.assertIn("cloud", output)
            self.assertIn("local", output)
            self.assertIn("community", output)


class TestProfileSessionIsolation(unittest.TestCase):
    """Tests for ProfileSession async context isolation."""

    def test_profile_default_is_none(self):
        """A fresh ProfileSession starts with profile=None."""
        from nextmv.cli.mcp.tools._helpers import ProfileSession

        s = ProfileSession()
        self.assertIsNone(s.profile)

    def test_profile_set_get(self):
        """Setting and getting profile works."""
        from nextmv.cli.mcp.tools._helpers import ProfileSession

        s = ProfileSession()
        s.profile = "staging"
        self.assertEqual(s.profile, "staging")
        s.profile = None
        self.assertIsNone(s.profile)

    def test_async_context_isolation(self):
        """Profile set in one asyncio.run() does not leak to the next."""
        from nextmv.cli.mcp.tools._helpers import ProfileSession

        s = ProfileSession()

        async def set_profile():
            s.profile = "isolated"
            return s.profile

        # Set profile inside async context.
        result = asyncio.run(set_profile())
        self.assertEqual(result, "isolated")

        # Outside that context (new asyncio.run), the profile should be default.
        async def get_profile():
            return s.profile

        result = asyncio.run(get_profile())
        self.assertIsNone(result)

    def test_copied_contexts_are_isolated(self):
        """Two copied contexts have independent profile state."""
        import contextvars

        from nextmv.cli.mcp.tools._helpers import ProfileSession

        s = ProfileSession()
        results = {}

        def run_a():
            s.profile = "alpha"
            results["a"] = s.profile

        def run_b():
            s.profile = "beta"
            results["b"] = s.profile

        ctx_a = contextvars.copy_context()
        ctx_b = contextvars.copy_context()
        ctx_a.run(run_a)
        ctx_b.run(run_b)

        self.assertEqual(results["a"], "alpha")
        self.assertEqual(results["b"], "beta")


class TestVisualGenerationWarning(unittest.TestCase):
    """Test that visual generation failure logs a warning."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_visual_failure_logs_warning(self):
        """_extract_cloud_run_outputs logs a warning when visuals fail."""
        from nextmv.cli.mcp.tools._helpers import _extract_cloud_run_outputs

        run_dir = os.path.join(self.tmp_dir, "run-warn")

        with patch(
            "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
            return_value=run_dir,
        ), patch(
            "nextmv.local.executor.process_run_visuals",
            side_effect=RuntimeError("plotly exploded"),
        ), patch(
            "nextmv.cli.mcp.tools._helpers.logger",
        ) as mock_logger:
            _extract_cloud_run_outputs(
                {"output": {"solution": {"x": 1}}},
                "ep",
                "run-warn",
            )
            mock_logger.warning.assert_called_once()
            args = mock_logger.warning.call_args[0]
            self.assertIn("run-warn", args[1])
            self.assertIn("plotly exploded", str(args[2]))


class TestSDKContentType(unittest.TestCase):
    """Tests for the content_type parameter added to SDK batch/scenario methods."""

    def _make_app(self):
        """Create an Application with a mock client."""
        from nextmv.cloud import Application, Client

        client = Client(api_key="test-key", url="https://api.test.io")
        client.request = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "test-id"}
        client.request.return_value = mock_response
        return Application(client=client, id="test-app")

    def test_new_batch_experiment_passes_content_type(self):
        """new_batch_experiment includes content_type in the API payload."""
        app = self._make_app()
        app.new_batch_experiment(
            name="test",
            type="scenario",
            content_type="multi-file",
            runs=[],
        )

        payload = app.client.request.call_args[1]["payload"]
        self.assertEqual(payload["content_type"], "multi-file")

    def test_new_batch_experiment_omits_content_type_when_none(self):
        """new_batch_experiment does not include content_type when None."""
        app = self._make_app()
        app.new_batch_experiment(name="test")

        payload = app.client.request.call_args[1]["payload"]
        self.assertNotIn("content_type", payload)

    def test_new_scenario_test_passes_content_type(self):
        """new_scenario_test forwards content_type to new_batch_experiment.

        We verify this through the MCP tool layer, which calls the SDK's
        new_scenario_test. The tool-level tests in TestBugFixes already
        confirm content_type is passed. Here we test the SDK method
        directly by checking the API payload.
        """
        app = self._make_app()

        # Mock the instance and input_set lookups that new_scenario_test needs.
        mock_instance = MagicMock()
        mock_input_set = MagicMock()
        mock_input_set.id = "is-1"
        mock_input_set.input_ids = ["inp-1"]
        mock_input_set.inputs = []

        from nextmv.cloud.scenario import Scenario, ScenarioInput, ScenarioInputType

        scenario = Scenario(
            scenario_input=ScenarioInput(
                scenario_input_type=ScenarioInputType.INPUT_SET,
                scenario_input_data="is-1",
            ),
            instance_id="inst-1",
        )

        with patch.object(type(app), "instance", return_value=mock_instance), \
             patch.object(type(app), "input_set", return_value=mock_input_set):
            app.new_scenario_test(
                scenarios=[scenario],
                content_type="multi-file",
            )

        # The SDK should have made the API POST with content_type in the payload.
        payload = app.client.request.call_args[1]["payload"]
        self.assertEqual(payload.get("content_type"), "multi-file")
