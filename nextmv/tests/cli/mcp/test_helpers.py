"""Tests for _save_to_file and helper functions."""

import asyncio
import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch


class TestSaveToFile(unittest.TestCase):
    """Tests for the _save_to_file helper."""

    def test_save_to_file_creates_json(self):
        """Test that _save_to_file writes valid JSON and returns a path message."""
        from nextmv.cli.mcp.server import _save_to_json_file

        data = {"stops": [{"id": "s1"}, {"id": "s2"}]}
        msg = _save_to_json_file(data, prefix="test")
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
    @patch("nextmv.cli.actions.run.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_input_returns_file_path(self, mock_get_app, mock_app_cls, mock_run_dir):
        """Test that cloud_run_input saves to file instead of returning raw data."""
        from nextmv.cli.mcp.server import create_server

        tmp_dir = tempfile.mkdtemp()
        try:
            mock_run_dir.return_value = os.path.join(tmp_dir, "api.cloud.nextmv.io", "run-1")

            mock_app = MagicMock()
            mock_app.client.url = "https://api.cloud.nextmv.io"
            mock_app.run_input.return_value = {"depot": {"lat": 0, "lon": 0}, "stops": []}
            mock_get_app.return_value = mock_app
            mock_app_cls.return_value = mock_app

            server = create_server()
            tool = server._tool_manager._tools["cloud_run_input"]
            result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
            # Result is JSON-encoded string (json_response=True).
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("Downloaded:", str(text))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    @patch("nextmv.cli.mcp.tools._helpers._cloud_run_dir")
    @patch("nextmv.cli.actions.run.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_result_returns_file_path(self, mock_get_app, mock_app_cls, mock_run_dir):
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
            mock_app_cls.return_value = mock_app

            server = create_server()
            tool = server._tool_manager._tools["cloud_run_result"]
            result = asyncio.run(tool.run({"app_id": "my-app", "run_id": "run-1"}))
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("Downloaded:", str(text))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    @patch("nextmv.cli.actions.managed_input.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_create_managed_input_with_raw_data(self, mock_get_client, mock_application_class):
        """Test that cloud_create_managed_input uploads raw data when input is provided."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_upload_url = MagicMock()
        mock_upload_url.upload_id = "upl_123"
        mock_app.upload_url.return_value = mock_upload_url
        mock_mi = MagicMock()
        mock_mi.to_dict.return_value = {"id": "mi-1", "upload_id": "upl_123"}
        mock_app.new_managed_input.return_value = mock_mi
        mock_application_class.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_managed_input"]
        asyncio.run(
            tool.run(
                {
                    "app_id": "my-app",
                    "name": "test input",
                    "input": {"stops": [{"id": "s1"}]},
                }
            )
        )
        mock_app.upload_url.assert_called_once()
        mock_app.upload_data.assert_called_once_with(
            upload_url=mock_upload_url,
            data={"stops": [{"id": "s1"}]},
        )
        mock_app.new_managed_input.assert_called_once_with(
            id=None,
            name="test input",
            description=None,
            run_id=None,
            upload_id="upl_123",
        )

    @patch("nextmv.cli.actions.input_set.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_create_input_set_with_managed_input_ids(self, mock_get_client, mock_application_class):
        """Test that cloud_create_input_set passes managed inputs correctly."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_input_set = MagicMock()
        mock_input_set.to_dict.return_value = {"id": "is-1"}
        mock_app.new_input_set.return_value = mock_input_set
        mock_application_class.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_input_set"]
        asyncio.run(
            tool.run(
                {
                    "app_id": "my-app",
                    "name": "test set",
                    "managed_input_ids": ["mi-1", "mi-2"],
                }
            )
        )
        call_kwargs = mock_app.new_input_set.call_args[1]
        self.assertEqual(len(call_kwargs["inputs"]), 2)
        self.assertEqual(call_kwargs["inputs"][0].id, "mi-1")
        self.assertEqual(call_kwargs["inputs"][1].id, "mi-2")

    @patch("nextmv.cli.actions.input_set.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_create_input_set_with_run_ids(self, mock_get_client, mock_application_class):
        """Test that cloud_create_input_set passes run_ids correctly."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_input_set = MagicMock()
        mock_input_set.to_dict.return_value = {"id": "is-1"}
        mock_app.new_input_set.return_value = mock_input_set
        mock_application_class.return_value = mock_app

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_input_set"]
        asyncio.run(
            tool.run(
                {
                    "app_id": "my-app",
                    "name": "test set",
                    "run_ids": ["run-1", "run-2"],
                }
            )
        )
        call_kwargs = mock_app.new_input_set.call_args[1]
        self.assertEqual(call_kwargs["run_ids"], ["run-1", "run-2"])
        self.assertIsNone(call_kwargs["inputs"])

    @patch("nextmv.cli.actions.scenario.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_create_scenario_test_converts_dicts(self, mock_get_client, mock_application_cls):
        """Test that cloud_create_scenario_test converts dicts to Scenario objects."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.new_scenario_test.return_value = "st-123"
        mock_application_cls.return_value = mock_app
        mock_get_client.return_value = MagicMock()

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_scenario_test"]
        asyncio.run(
            tool.run(
                {
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
                }
            )
        )
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
