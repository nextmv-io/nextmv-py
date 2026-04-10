"""Tests for ensemble run tools."""

import asyncio
import json
import unittest
from unittest.mock import MagicMock, patch


class TestEnsembleRunTools(unittest.TestCase):
    """Smoke tests for cloud_ensemble_run and cloud_ensemble_run_submit."""

    @patch("nextmv.cli.actions.ensemble.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_ensemble_run_returns_file_path(self, mock_get_client, mock_application_cls):
        """cloud_ensemble_run polls and saves result to a temp file."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"id": "run-1", "output": {"routes": []}}
        mock_app.new_run_with_result.return_value = mock_result
        mock_application_cls.return_value = mock_app
        mock_get_client.return_value = MagicMock()

        server = create_server()
        tool = server._tool_manager._tools["cloud_ensemble_run"]
        result = asyncio.run(
            tool.run(
                {
                    "app_id": "my-app",
                    "ensemble_id": "ens-1",
                    "input": {"stops": []},
                }
            )
        )
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("Data saved to", str(text))
        mock_app.new_run_with_result.assert_called_once()
        call_kwargs = mock_app.new_run_with_result.call_args[1]
        self.assertIsNotNone(call_kwargs["configuration"].run_type)

    @patch("nextmv.cli.actions.ensemble.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_ensemble_run_submit_returns_run_id(self, mock_get_client, mock_application_cls):
        """cloud_ensemble_run_submit returns the run ID immediately."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.new_run.return_value = "run-ens-42"
        mock_application_cls.return_value = mock_app
        mock_get_client.return_value = MagicMock()

        server = create_server()
        tool = server._tool_manager._tools["cloud_ensemble_run_submit"]
        result = asyncio.run(
            tool.run(
                {
                    "app_id": "my-app",
                    "ensemble_id": "ens-1",
                    "input": {"stops": []},
                }
            )
        )
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("run-ens-42", str(text))
        mock_app.new_run.assert_called_once()

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_ensemble_run_empty_app_id_returns_error(self, mock_get_app):
        """cloud_ensemble_run returns an error for empty app_id."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool = server._tool_manager._tools["cloud_ensemble_run"]
        result = asyncio.run(
            tool.run(
                {
                    "app_id": "",
                    "ensemble_id": "ens-1",
                    "input": {"stops": []},
                }
            )
        )
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("app_id", str(text))
        mock_get_app.assert_not_called()

    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_ensemble_run_submit_empty_ensemble_id_returns_error(self, mock_get_app):
        """cloud_ensemble_run_submit returns an error for whitespace-only ensemble_id."""
        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool = server._tool_manager._tools["cloud_ensemble_run_submit"]
        result = asyncio.run(
            tool.run(
                {
                    "app_id": "my-app",
                    "ensemble_id": "   ",
                    "input": {"stops": []},
                }
            )
        )
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("ensemble_id", str(text))
        mock_get_app.assert_not_called()
