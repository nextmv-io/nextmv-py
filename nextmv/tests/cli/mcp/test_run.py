"""Tests for bug fixes, multi-file run support, and cloud run cache."""

import asyncio
import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch


class TestBugFixes(unittest.TestCase):
    """Tests for specific bug fixes."""

    @patch("nextmv.cli.actions.ensemble.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_create_ensemble_with_dicts(self, mock_get_client, mock_application_cls):
        """Bug 1: cloud_create_ensemble must accept plain dicts for run_groups and rules."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_ensemble = MagicMock()
        mock_ensemble.to_dict.return_value = {"id": "ens-1"}
        mock_app.new_ensemble_definition.return_value = mock_ensemble
        mock_application_cls.return_value = mock_app
        mock_get_client.return_value = MagicMock()

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_ensemble"]
        asyncio.run(
            tool.run(
                {
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
                }
            )
        )
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

    @patch("nextmv.cli.actions.ensemble.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_create_ensemble_with_shorthand_objective(self, mock_get_client, mock_application_cls):
        """Bug 1: objective shorthand 'min'/'max' should be accepted."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_ensemble = MagicMock()
        mock_ensemble.to_dict.return_value = {"id": "ens-1"}
        mock_app.new_ensemble_definition.return_value = mock_ensemble
        mock_application_cls.return_value = mock_app
        mock_get_client.return_value = MagicMock()

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_ensemble"]
        asyncio.run(
            tool.run(
                {
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
                }
            )
        )
        call_kwargs = mock_app.new_ensemble_definition.call_args[1]
        from nextmv.cloud.ensemble import RuleObjective

        self.assertEqual(call_kwargs["rules"][0].objective, RuleObjective.MINIMIZE)

    @patch("nextmv.cli.actions.ensemble.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_create_ensemble_with_dict_tolerance(self, mock_get_client, mock_application_cls):
        """Bug 1: rules with a dict tolerance should be converted correctly."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_ensemble = MagicMock()
        mock_ensemble.to_dict.return_value = {"id": "ens-1"}
        mock_app.new_ensemble_definition.return_value = mock_ensemble
        mock_application_cls.return_value = mock_app
        mock_get_client.return_value = MagicMock()

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_ensemble"]
        asyncio.run(
            tool.run(
                {
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
                }
            )
        )
        call_kwargs = mock_app.new_ensemble_definition.call_args[1]
        from nextmv.cloud.ensemble import RuleToleranceType

        rule = call_kwargs["rules"][0]
        self.assertEqual(rule.tolerance.value, 5.0)
        self.assertEqual(rule.tolerance.type, RuleToleranceType.ABSOLUTE)

    @patch("nextmv.cli.actions.ensemble.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_create_ensemble_missing_run_group_field(self, mock_get_client, mock_application_cls):
        """Bug 1: Missing required run_group fields give a clear error string."""
        from nextmv.cli.mcp.server import create_server

        mock_get_client.return_value = MagicMock()
        mock_application_cls.return_value = MagicMock()

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_ensemble"]
        result = asyncio.run(
            tool.run(
                {
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
                }
            )
        )
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("run_groups[0]", str(text))
        self.assertIn("Error", str(text))

    @patch("nextmv.cli.actions.ensemble.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_create_ensemble_missing_rule_field(self, mock_get_client, mock_application_cls):
        """Bug 1: Missing required rule fields give a clear error string."""
        from nextmv.cli.mcp.server import create_server

        mock_get_client.return_value = MagicMock()
        mock_application_cls.return_value = MagicMock()

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_ensemble"]
        result = asyncio.run(
            tool.run(
                {
                    "app_id": "my-app",
                    "run_groups": [{"id": "grp-1", "instance_id": "prod"}],
                    # Missing 'statistics_path' in rule.
                    "rules": [{"id": "r1", "objective": "min", "tolerance": 0.01}],
                }
            )
        )
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("rules[0]", str(text))
        self.assertIn("Error", str(text))

    def test_cloud_create_scenario_test_has_content_type_param(self):
        """Bug 2: cloud_create_scenario_test should accept a content_type parameter."""
        import inspect

        from nextmv.cli.mcp.server import create_server

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_scenario_test"]
        # Verify the tool's function accepts content_type in its signature.
        sig = inspect.signature(tool.fn)
        self.assertIn("content_type", sig.parameters)

    @patch("nextmv.cli.actions.scenario.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_create_scenario_test_content_type_path(self, mock_get_client, mock_application_cls):
        """Bug 2: content_type is passed through to the SDK's new_scenario_test."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.new_scenario_test.return_value = "scenario-test-123"
        mock_application_cls.return_value = mock_app
        mock_get_client.return_value = MagicMock()

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_scenario_test"]
        asyncio.run(
            tool.run(
                {
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
                }
            )
        )

        # Verify the SDK's new_scenario_test was called with content_type.
        mock_app.new_scenario_test.assert_called_once()
        call_kwargs = mock_app.new_scenario_test.call_args[1]
        self.assertEqual(call_kwargs["content_type"], "multi-file")

    @patch("nextmv.cli.actions.ensemble.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_create_ensemble_missing_rule_fields(self, mock_get_client, mock_application_cls):
        """Bug 1: missing rule fields return a user-friendly error, not an exception."""
        from nextmv.cli.mcp.server import create_server

        mock_get_client.return_value = MagicMock()
        mock_application_cls.return_value = MagicMock()

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_ensemble"]
        result = asyncio.run(
            tool.run(
                {
                    "app_id": "my-app",
                    "run_groups": [{"id": "grp-1", "instance_id": "prod"}],
                    "rules": [
                        {
                            "id": "rule-missing-fields",
                            # Missing statistics_path and objective.
                        },
                    ],
                }
            )
        )
        text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
        self.assertIn("Error", str(text))

    @patch("nextmv.cli.actions.scenario.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_create_scenario_test_content_type_multiple_inputs(
        self,
        mock_get_client,
        mock_application_cls,
    ):
        """Bug 2: content_type is passed to SDK for multi-input scenarios."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.new_scenario_test.return_value = "scenario-test-456"
        mock_application_cls.return_value = mock_app
        mock_get_client.return_value = MagicMock()

        server = create_server()
        tool = server._tool_manager._tools["cloud_create_scenario_test"]
        asyncio.run(
            tool.run(
                {
                    "app_id": "my-app",
                    "scenarios": [
                        {
                            "instance_id": "stable",
                            "scenario_id": "s1",
                            "scenario_input": {"input_set_id": "my-input-set"},
                        },
                    ],
                    "content_type": "multi-file",
                }
            )
        )

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
        asyncio.run(
            tool.run(
                {
                    "app_dir": "/some/app",
                    "input": {"stops": []},
                }
            )
        )
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
        asyncio.run(
            tool.run(
                {
                    "app_dir": "/some/app",
                    "input_dir_path": "/some/input-dir",
                    "content_format": "multi-file",
                }
            )
        )
        mock_app.new_run.assert_called_once()
        call_kwargs = mock_app.new_run.call_args[1]
        self.assertEqual(call_kwargs["input_dir_path"], "/some/input-dir")
        config = call_kwargs.get("configuration")
        self.assertIsNotNone(config)
        self.assertEqual(config.format.format_input.input_type, InputFormat.MULTI_FILE)

    @patch("nextmv.cli.actions.run.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_run_submit_json_input(self, mock_get_client, mock_app_cls):
        """cloud_run_submit passes input dict to new_run for JSON apps."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.new_run.return_value = "run-789"
        mock_app_cls.return_value = mock_app
        mock_get_client.return_value = MagicMock()

        server = create_server()
        tool = server._tool_manager._tools["cloud_run_submit"]
        asyncio.run(
            tool.run(
                {
                    "app_id": "my-app",
                    "input": {"stops": []},
                }
            )
        )
        mock_app.new_run.assert_called_once()
        call_kwargs = mock_app.new_run.call_args[1]
        self.assertEqual(call_kwargs["input"], {"stops": []})
        self.assertIsNone(call_kwargs.get("input_dir_path"))
        self.assertIsNone(call_kwargs.get("configuration"))

    @patch("nextmv.cli.actions.run.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_client")
    def test_cloud_run_submit_multifile_input(self, mock_get_client, mock_app_cls):
        """cloud_run_submit passes input_dir_path + configuration for multi-file apps."""
        from nextmv.cli.mcp.server import create_server
        from nextmv.input import InputFormat

        mock_app = MagicMock()
        mock_app.new_run.return_value = "run-mf-1"
        mock_app_cls.return_value = mock_app
        mock_get_client.return_value = MagicMock()

        server = create_server()
        tool = server._tool_manager._tools["cloud_run_submit"]
        asyncio.run(
            tool.run(
                {
                    "app_id": "my-app",
                    "input_dir_path": "/some/input-dir",
                    "content_format": "multi-file",
                }
            )
        )
        mock_app.new_run.assert_called_once()
        call_kwargs = mock_app.new_run.call_args[1]
        self.assertEqual(call_kwargs["input_dir_path"], "/some/input-dir")
        config = call_kwargs.get("configuration")
        self.assertIsNotNone(config)
        self.assertEqual(config.format.format_input.input_type, InputFormat.MULTI_FILE)


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
        expected = os.path.join(str(os.path.expanduser("~")), ".nextmv", "runs", "api.cloud.nextmv.io", "run-123")
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

    @patch("nextmv.cli.actions.run.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_result_downloads_on_miss(self, mock_get_app, mock_app_cls):
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
        mock_app_cls.return_value = mock_app

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
            _extract_cloud_run_outputs({"output": {"solution": {"x": 1}}}, "ep", "run-partial")

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
            _extract_cloud_run_outputs({"output": {"solution": {}, "assets": []}}, "ep", "run-empty-sol")

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

        with (
            patch(
                "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
                return_value=run_dir,
            ),
            patch(
                "nextmv.local.executor.process_run_visuals",
                side_effect=RuntimeError("plotly exploded"),
            ),
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

    @patch("nextmv.cli.actions.run.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_input_downloads_on_miss(self, mock_get_app, mock_app_cls):
        """Test that cloud_run_input downloads and saves as inputs/input.json on miss."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.client.url = "https://api.cloud.nextmv.io"
        mock_app.run_input.return_value = {"stops": []}
        mock_get_app.return_value = mock_app
        mock_app_cls.return_value = mock_app

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

    @patch("nextmv.cli.actions.run.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_logs_downloads_on_miss(self, mock_get_app, mock_app_cls):
        """Test that cloud_run_logs downloads and caches as plain text."""
        from nextmv.cli.mcp.server import create_server

        mock_app = MagicMock()
        mock_app.client.url = "https://api.cloud.nextmv.io"
        mock_logs = MagicMock()
        mock_logs.to_dict.return_value = {"log": "solver started\nsolver finished"}
        mock_app.run_logs.return_value = mock_logs
        mock_get_app.return_value = mock_app
        mock_app_cls.return_value = mock_app

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

    @patch("nextmv.cli.actions.run.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_multifile_moves_outputs(self, mock_get_app, mock_app_cls):
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
        mock_app_cls.return_value = mock_app

        run_dir = os.path.join(self.tmp_dir, "run-csv")
        # Track the pending dir created by safe_id so we can verify it was moved.
        pending_dirs_created: list[str] = []

        def fake_cloud_run_dir(endpoint, run_id):
            if run_id.startswith("pending-"):
                d = os.path.join(self.tmp_dir, run_id)
                pending_dirs_created.append(d)
                return d
            return run_dir

        def fake_new_run(
            *,
            input,
            input_dir_path,
            configuration,
            instance_id,
            run_options,
            polling_options,
            managed_input_id,
            output_dir_path,
        ):
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
            result = asyncio.run(
                tool.run(
                    {
                        "app_id": "my-app",
                        "input_dir_path": "/some/csvs",
                        "content_format": "csv-archive",
                    }
                )
            )
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

    @patch("nextmv.cli.actions.run.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_input_multifile_downloads(self, mock_get_app, mock_app_cls):
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
        mock_app_cls.return_value = mock_app

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

    @patch("nextmv.cli.actions.run.Application")
    @patch("nextmv.cli.mcp.tools._helpers._get_app")
    def test_cloud_run_result_multifile_extracts_output(self, mock_get_app, mock_app_cls):
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
        mock_app_cls.return_value = mock_app

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
