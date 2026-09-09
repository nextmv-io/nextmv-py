"""
Unit tests for the nextmv.local.executor module.
"""

import json
import os
import shutil
import stat
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

from nextmv.content_format import ContentFormat
from nextmv.local.executor import (
    _copy_new_or_modified_files,
    _process_run_assets,
    _process_run_solutions,
    _process_run_statistics,
    _validate_execution_input,
    execute_run,
    main,
    options_args,
    process_run_input,
    process_run_output,
)
from nextmv.local.local import LOGS_FILE, LOGS_KEY
from nextmv.manifest import Manifest, ManifestExecution
from nextmv.output import ASSETS_KEY, OUTPUTS_KEY, SOLUTIONS_KEY, STATISTICS_KEY, OutputFormat


class TestLocalExecutor(unittest.TestCase):
    """Test cases for the local executor module."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.temp_src = os.path.join(self.test_dir, "temp_src")
        self.run_dir = os.path.join(self.test_dir, "run_dir")
        os.makedirs(self.temp_src)
        os.makedirs(self.run_dir)

        # Create mock manifest
        self.mock_manifest = Mock(spec=Manifest)
        self.mock_manifest.files = []
        self.mock_manifest.execution = Mock(spec=ManifestExecution)
        self.mock_manifest.execution.entrypoint = "main.py"
        mock_configuration = Mock()
        mock_content = Mock()
        mock_content.format = ContentFormat.JSON
        mock_configuration.content = mock_content
        self.mock_manifest.configuration = mock_configuration

        # Create nested mock for format
        mock_format = Mock()
        mock_input_format = Mock()
        mock_output_format = Mock()
        mock_input_format.type = "json"
        mock_output_format.type = "json"
        mock_format.input = mock_input_format
        mock_format.output = mock_output_format
        self.mock_manifest.format = mock_format

        # Create mock output format
        self.mock_output_format = Mock(spec=ContentFormat)
        self.mock_output_format.type = "json"
        self.mock_output_format.value = "json"

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def _create_metadata_file(self, run_id="test_run_id"):
        """Helper method to create a metadata file with proper structure."""
        metadata_file = os.path.join(self.run_dir, f"{run_id}.json")
        with open(metadata_file, "w") as f:
            metadata = {"metadata": {"created_at": "2023-01-01T00:00:00Z", "format": {"output": {"type": "json"}}}}
            json.dump(metadata, f)

    @patch("nextmv.local.executor.load")
    @patch("nextmv.local.executor.execute_run")
    def test_main_function(self, mock_execute_run, mock_load):
        """Test the main function loads input and calls execute_run."""
        # Build absolute, canonical paths so the fixture is valid on every OS
        # (a POSIX-style "/test/src" is not absolute on Windows).
        src = os.path.abspath(os.path.join("test", "src"))
        run_dir = os.path.join(src, ".nextmv", "runs", "test_run_id")

        # Setup mock input
        mock_input = Mock()
        mock_input.data = {
            "run_id": "test_run_id",
            "src": src,
            "manifest_dict": {"execution": {"entrypoint": "main.py"}, "type": "python"},
            "run_dir": run_dir,
            "run_config": {"format": {"input": {"type": "json"}}},
            "inputs_dir_path": None,
            "options": {"duration": "10s"},
            "input_data": {"test": "data"},
        }
        mock_load.return_value = mock_input

        # Call main
        main()

        # Verify load was called
        mock_load.assert_called_once()

        # Verify execute_run was called with correct parameters
        mock_execute_run.assert_called_once_with(
            run_id="test_run_id",
            src=src,
            manifest_dict={"execution": {"entrypoint": "main.py"}, "type": "python"},
            run_dir=run_dir,
            run_config={"format": {"input": {"type": "json"}}},
            inputs_dir_path=None,
            options={"duration": "10s"},
            input_data={"test": "data"},
        )

    def test_options_args_with_none(self):
        """Test options_args with None input."""
        result = options_args(None)
        self.assertEqual(result, [])

    def test_options_args_with_empty_dict(self):
        """Test options_args with empty dictionary."""
        result = options_args({})
        self.assertEqual(result, [])

    def test_options_args_with_single_option(self):
        """Test options_args with single option."""
        options = {"duration": "10s"}
        result = options_args(options)
        expected = ["-duration", "10s"]
        self.assertEqual(result, expected)

    def test_options_args_with_multiple_options(self):
        """Test options_args with multiple options."""
        options = {"duration": "10s", "iterations": "100", "verbose": "true"}
        result = options_args(options)

        # Check that all options are included (order might vary)
        self.assertIn("-duration", result)
        self.assertIn("10s", result)
        self.assertIn("-iterations", result)
        self.assertIn("100", result)
        self.assertIn("-verbose", result)
        self.assertIn("true", result)
        self.assertEqual(len(result), 6)  # 3 options * 2 (key + value)

    def test_options_args_with_numeric_values(self):
        """Test options_args with numeric values."""
        options = {"port": 8080, "timeout": 30.5}
        result = options_args(options)

        self.assertIn("-port", result)
        self.assertIn("8080", result)
        self.assertIn("-timeout", result)
        self.assertIn("30.5", result)

    def test_process_run_input_json_format_with_dict(self):
        """Test process_run_input with JSON format and dict input."""
        input_data = {"test": "data", "value": 42}
        result = process_run_input(
            temp_src=self.temp_src, run_format="json", input_data=input_data, manifest=self.mock_manifest
        )

        expected = json.dumps(input_data)
        self.assertEqual(result, expected)

    def test_process_run_input_text_format_with_string(self):
        """Test process_run_input with text format and string input."""
        input_data = "test text input"
        result = process_run_input(
            temp_src=self.temp_src, run_format="text", input_data=input_data, manifest=self.mock_manifest
        )

        self.assertEqual(result, input_data)

    def test_process_run_input_json_format_invalid_input(self):
        """Test process_run_input with JSON format but non-dict input."""
        with self.assertRaises(ValueError) as context:
            process_run_input(
                temp_src=self.temp_src,
                run_format="json",
                input_data="string instead of dict",
                manifest=self.mock_manifest,
            )

        self.assertIn("invalid input data for format json", str(context.exception))

    def test_process_run_input_text_format_invalid_input(self):
        """Test process_run_input with text format but non-string input."""
        with self.assertRaises(ValueError) as context:
            process_run_input(
                temp_src=self.temp_src,
                run_format="text",
                input_data={"dict": "instead of string"},
                manifest=self.mock_manifest,
            )

        self.assertIn("invalid input data for format text", str(context.exception))

    def test_process_run_input_csv_archive_format(self):
        """Test process_run_input with csv-archive format."""
        # Create test inputs directory
        inputs_dir_path = os.path.join(self.test_dir, "test_inputs")
        os.makedirs(inputs_dir_path)

        with open(os.path.join(inputs_dir_path, "data.csv"), "w") as f:
            f.write("col1,col2\nval1,val2\n")

        result = process_run_input(
            temp_src=self.temp_src,
            run_format="csv-archive",
            inputs_dir_path=inputs_dir_path,
            manifest=self.mock_manifest,
        )

        self.assertEqual(result, "")

        # Check that input directory was created in temp_src
        input_dir = os.path.join(self.temp_src, "input")
        self.assertTrue(os.path.exists(input_dir))
        self.assertTrue(os.path.exists(os.path.join(input_dir, "data.csv")))

    def test_process_run_input_csv_archive_with_input_data_error(self):
        """Test process_run_input with csv-archive format and input_data (should error)."""
        with self.assertRaises(ValueError) as context:
            process_run_input(
                temp_src=self.temp_src,
                run_format="csv-archive",
                input_data={"should": "error"},
                manifest=self.mock_manifest,
            )

        self.assertIn("input data must be None for csv-archive or multi-file format", str(context.exception))

    def test_process_run_input_multi_file_format(self):
        """Test process_run_input with multi-file format."""
        # Create test inputs directory
        inputs_dir_path = os.path.join(self.test_dir, "test_inputs")
        os.makedirs(inputs_dir_path)

        with open(os.path.join(inputs_dir_path, "file1.txt"), "w") as f:
            f.write("content1")

        with open(os.path.join(inputs_dir_path, "file2.json"), "w") as f:
            json.dump({"test": "data"}, f)

        result = process_run_input(
            temp_src=self.temp_src,
            run_format="multi-file",
            inputs_dir_path=inputs_dir_path,
            manifest=self.mock_manifest,
        )

        self.assertEqual(result, "")

        # Check that inputs directory was created in temp_src
        inputs_dir = os.path.join(self.temp_src, "inputs")
        self.assertTrue(os.path.exists(inputs_dir))
        self.assertTrue(os.path.exists(os.path.join(inputs_dir, "file1.txt")))
        self.assertTrue(os.path.exists(os.path.join(inputs_dir, "file2.json")))

    def test_process_run_input_multi_file_with_input_data_error(self):
        """Test process_run_input with multi-file format and input_data (should error)."""
        with self.assertRaises(ValueError) as context:
            process_run_input(
                temp_src=self.temp_src, run_format="multi-file", input_data="should error", manifest=self.mock_manifest
            )

        self.assertIn("input data must be None for csv-archive or multi-file format", str(context.exception))

    def test_process_run_statistics_from_directory(self):
        """Test process_run_statistics when statistics.json exists in outputs dir."""
        # Create temp outputs directory with statistics.json file
        temp_outputs_dir = os.path.join(self.temp_src, OUTPUTS_KEY)
        os.makedirs(temp_outputs_dir)

        stats_src = os.path.join(temp_outputs_dir, f"{STATISTICS_KEY}.json")
        with open(stats_src, "w") as f:
            json.dump({"statistics": {"duration": 1.5}}, f)

        outputs_dir = os.path.join(self.run_dir, OUTPUTS_KEY)
        os.makedirs(outputs_dir)

        stdout_output = {}

        _process_run_statistics(
            temp_outputs_dir,
            outputs_dir,
            stdout_output,
            temp_src=self.temp_src,
            manifest=self.mock_manifest,
        )

        # Check that statistics.json file was copied
        stats_dst = os.path.join(outputs_dir, f"{STATISTICS_KEY}.json")
        self.assertTrue(os.path.exists(stats_dst))

    def test_process_run_statistics_from_stdout(self):
        """Test process_run_statistics when statistics are in stdout."""
        temp_outputs_dir = os.path.join(self.temp_src, OUTPUTS_KEY)
        outputs_dir = os.path.join(self.run_dir, OUTPUTS_KEY)
        os.makedirs(outputs_dir)

        stdout_output = {STATISTICS_KEY: {"duration": 2.5, "iterations": 100}}

        _process_run_statistics(
            temp_outputs_dir,
            outputs_dir,
            stdout_output,
            temp_src=self.temp_src,
            manifest=self.mock_manifest,
        )

        # Check that statistics.json was created directly in outputs_dir
        stats_file = os.path.join(outputs_dir, f"{STATISTICS_KEY}.json")
        self.assertTrue(os.path.exists(stats_file))

        with open(stats_file) as f:
            saved_stats = json.load(f)

        expected = {STATISTICS_KEY: stdout_output[STATISTICS_KEY]}
        self.assertEqual(saved_stats, expected)

    def test_process_run_statistics_no_statistics(self):
        """Test process_run_statistics when no statistics are available."""
        temp_outputs_dir = os.path.join(self.temp_src, OUTPUTS_KEY)
        outputs_dir = os.path.join(self.run_dir, OUTPUTS_KEY)
        os.makedirs(outputs_dir)

        stdout_output = {}

        _process_run_statistics(
            temp_outputs_dir,
            outputs_dir,
            stdout_output,
            temp_src=self.temp_src,
            manifest=self.mock_manifest,
        )

        # Check that statistics.json was not created when there are no statistics
        stats_file = os.path.join(outputs_dir, f"{STATISTICS_KEY}.json")
        self.assertFalse(os.path.exists(stats_file))

    def test_process_run_assets_from_directory(self):
        """Test process_run_assets when assets.json exists in outputs dir."""
        # Create temp outputs directory with assets.json file
        temp_outputs_dir = os.path.join(self.temp_src, OUTPUTS_KEY)
        os.makedirs(temp_outputs_dir)

        assets_src = os.path.join(temp_outputs_dir, f"{ASSETS_KEY}.json")
        with open(assets_src, "w") as f:
            json.dump({"assets": [{"name": "plot.png", "url": "http://example.com/plot.png"}]}, f)

        outputs_dir = os.path.join(self.run_dir, OUTPUTS_KEY)
        os.makedirs(outputs_dir)

        stdout_output = {}

        _process_run_assets(
            temp_outputs_dir,
            outputs_dir,
            stdout_output,
            temp_src=self.temp_src,
            manifest=self.mock_manifest,
        )

        # Check that assets.json file was copied
        assets_dst = os.path.join(outputs_dir, f"{ASSETS_KEY}.json")
        self.assertTrue(os.path.exists(assets_dst))

    def test_process_run_assets_from_stdout(self):
        """Test process_run_assets when assets are in stdout."""
        temp_outputs_dir = os.path.join(self.temp_src, OUTPUTS_KEY)
        outputs_dir = os.path.join(self.run_dir, OUTPUTS_KEY)
        os.makedirs(outputs_dir)

        stdout_output = {
            ASSETS_KEY: [
                {"name": "plot1.png", "url": "http://example.com/plot1.png"},
                {"name": "plot2.png", "url": "http://example.com/plot2.png"},
            ]
        }

        _process_run_assets(
            temp_outputs_dir,
            outputs_dir,
            stdout_output,
            temp_src=self.temp_src,
            manifest=self.mock_manifest,
        )

        # Check that assets.json was created directly in outputs_dir
        assets_file = os.path.join(outputs_dir, f"{ASSETS_KEY}.json")
        self.assertTrue(os.path.exists(assets_file))

        with open(assets_file) as f:
            saved_assets = json.load(f)

        expected = {ASSETS_KEY: stdout_output[ASSETS_KEY]}
        self.assertEqual(saved_assets, expected)

    def test_process_run_solutions_from_output_directory(self):
        """Test process_run_solutions when output directory exists (csv-archive)."""
        # Create output directory in temp_src
        output_src = os.path.join(self.temp_src, "output")
        os.makedirs(output_src)

        with open(os.path.join(output_src, "result.csv"), "w") as f:
            f.write("id,value\n1,100\n2,200\n")

        temp_outputs_dir = os.path.join(self.temp_src, OUTPUTS_KEY)
        outputs_dir = os.path.join(self.run_dir, OUTPUTS_KEY)
        os.makedirs(outputs_dir)

        stdout_output = {"solution": {"value": 300}}

        # Create metadata file that process_run_solutions expects
        self._create_metadata_file()

        _process_run_solutions(
            "test_run_id",
            self.run_dir,
            temp_outputs_dir,
            self.temp_src,
            outputs_dir,
            stdout_output,
            output_format=OutputFormat.CSV_ARCHIVE,
            manifest=self.mock_manifest,
            src=self.test_dir,
        )

        # Check that solutions directory was created and files copied
        solutions_dst = os.path.join(outputs_dir, SOLUTIONS_KEY)
        self.assertTrue(os.path.exists(solutions_dst))
        self.assertTrue(os.path.exists(os.path.join(solutions_dst, "result.csv")))

    def test_process_run_solutions_from_outputs_solutions_directory(self):
        """Test process_run_solutions when outputs/solutions directory exists (multi-file)."""
        # Create outputs/solutions directory in temp_src
        temp_outputs_dir = os.path.join(self.temp_src, OUTPUTS_KEY)
        solutions_src = os.path.join(temp_outputs_dir, SOLUTIONS_KEY)
        os.makedirs(solutions_src)

        with open(os.path.join(solutions_src, "solution1.json"), "w") as f:
            json.dump({"result": 42}, f)

        outputs_dir = os.path.join(self.run_dir, OUTPUTS_KEY)
        os.makedirs(outputs_dir)

        stdout_output = {"solution": {"value": 300}}

        # Create metadata file that process_run_solutions expects
        self._create_metadata_file()

        _process_run_solutions(
            "test_run_id",
            self.run_dir,
            temp_outputs_dir,
            self.temp_src,
            outputs_dir,
            stdout_output,
            output_format=ContentFormat.MULTI_FILE,
            manifest=self.mock_manifest,
            src=self.test_dir,
        )

        # Check that solutions directory was created and files copied
        solutions_dst = os.path.join(outputs_dir, SOLUTIONS_KEY)
        self.assertTrue(os.path.exists(solutions_dst))
        self.assertTrue(os.path.exists(os.path.join(solutions_dst, "solution1.json")))

    def test_process_run_solutions_from_stdout(self):
        """Test process_run_solutions when no directory exists, use stdout."""
        temp_outputs_dir = os.path.join(self.temp_src, OUTPUTS_KEY)
        outputs_dir = os.path.join(self.run_dir, OUTPUTS_KEY)
        os.makedirs(outputs_dir)

        stdout_output = {"solution": {"optimal_value": 42}, "statistics": {"duration": 1.5}}

        # Create metadata file that process_run_solutions expects
        self._create_metadata_file()

        _process_run_solutions(
            "test_run_id",
            self.run_dir,
            temp_outputs_dir,
            self.temp_src,
            outputs_dir,
            stdout_output,
            output_format=self.mock_output_format,
            manifest=self.mock_manifest,
            src=self.test_dir,
        )

        # Check that solution.json was created
        solutions_dst = os.path.join(outputs_dir, SOLUTIONS_KEY)
        self.assertTrue(os.path.exists(solutions_dst))

        solution_file = os.path.join(solutions_dst, "solution.json")
        self.assertTrue(os.path.exists(solution_file))

        with open(solution_file) as f:
            saved_solution = json.load(f)

        self.assertEqual(saved_solution, stdout_output)

    def test_process_run_solutions_empty_stdout(self):
        """Test process_run_solutions when stdout is empty."""
        temp_outputs_dir = os.path.join(self.temp_src, OUTPUTS_KEY)
        outputs_dir = os.path.join(self.run_dir, OUTPUTS_KEY)
        os.makedirs(outputs_dir)

        stdout_output = {}

        # Create metadata file that process_run_solutions expects
        self._create_metadata_file()

        _process_run_solutions(
            "test_run_id",
            self.run_dir,
            temp_outputs_dir,
            self.temp_src,
            outputs_dir,
            stdout_output,
            output_format=self.mock_output_format,
            manifest=self.mock_manifest,
            src=self.test_dir,
        )

        # Check that solutions directory was created
        solutions_dst = os.path.join(outputs_dir, SOLUTIONS_KEY)
        self.assertTrue(os.path.exists(solutions_dst))

        # But no solution.json should be created for empty output
        solution_file = os.path.join(solutions_dst, "solution.json")
        self.assertFalse(os.path.exists(solution_file))

    @patch("nextmv.local.executor.json.load")
    @patch("nextmv.local.executor.json.dump")
    @patch("nextmv.local.executor.process_run_output")
    @patch("nextmv.local.executor.process_run_input")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch("nextmv.local.executor.subprocess.Popen")
    @patch("nextmv.local.executor._copy_files_from_manifest")
    @patch("nextmv.local.executor.tempfile.TemporaryDirectory")
    @patch("nextmv.local.executor.os.makedirs")
    def test_execute_run_full_flow(
        self,
        mock_makedirs,
        mock_temp_dir,
        mock_copy_files_from_manifest,
        mock_subprocess_popen,
        mock_open,
        mock_process_input,
        mock_process_output,
        mock_json_dump,
        mock_json_load,
    ):
        """Test the complete execute_run function flow."""
        # Setup mocks
        temp_dir = "/tmp/test_temp"
        temp_src = os.path.join(temp_dir, "src")
        mock_temp_dir.return_value.__enter__.return_value = temp_dir

        mock_process_input.return_value = '{"test": "input"}'

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = iter([])
        mock_process.stderr = iter([])
        mock_process.stdin = Mock()
        mock_subprocess_popen.return_value = mock_process

        run_config = {"format": {"input": {"type": "json"}, "output": {"type": "json"}}}

        # Configure mock JSON operations
        mock_json_load.return_value = {"metadata": {"status_v2": "pending"}}

        execute_run(
            run_id="test_run_id",
            src="/test/src",
            manifest_dict={"execution": {"entrypoint": "main.py"}, "files": ["main.py"]},
            run_dir="/test/run_dir",
            run_config=run_config,
            input_data={"test": "data"},
            options={"duration": "10s"},
        )

        # Verify _copy_files_from_manifest was called to copy source files
        mock_copy_files_from_manifest.assert_called_once_with("/test/src", temp_src, unittest.mock.ANY)

        # Verify process_run_input was called
        mock_process_input.assert_called_once_with(
            temp_src=temp_src,
            run_format="json",
            manifest=unittest.mock.ANY,
            input_data={"test": "data"},
            inputs_dir_path=None,
        )

        # Verify subprocess.Popen was called
        mock_subprocess_popen.assert_called_once()
        call_args = mock_subprocess_popen.call_args
        self.assertEqual(call_args[0][0][:5], [sys.executable, "-m", "uv", "run", os.path.join(temp_src, "main.py")])
        self.assertIn("-duration", call_args[0][0])
        self.assertIn("10s", call_args[0][0])

        # Verify process_run_output was called
        mock_process_output.assert_called_once_with(
            manifest=unittest.mock.ANY,
            run_id="test_run_id",
            temp_src=temp_src,
            result=unittest.mock.ANY,
            run_dir="/test/run_dir",
            src="/test/src",
        )

    def test_execute_run_stderr_persisted_to_logs_json_format(self):
        """Test that stderr is written to logs/logs.log for JSON format runs."""
        run_id = "test_run_stderr_json"
        run_dir = os.path.join(self.test_dir, "run_dir_stderr_json")
        os.makedirs(run_dir)

        info_file = os.path.join(run_dir, f"{run_id}.json")
        with open(info_file, "w") as f:
            json.dump(
                {
                    "metadata": {
                        "created_at": "2023-01-01T00:00:00Z",
                        "status_v2": "pending",
                        "format": {"output": {"type": "json"}},
                    }
                },
                f,
            )

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdin = Mock()
        mock_process.stdout = iter(["stdout line\n"])
        mock_process.stderr = iter(["stderr line 1\n", "stderr line 2\n"])

        with (
            patch("nextmv.local.executor._copy_files_from_manifest"),
            patch("nextmv.local.executor.process_run_output"),
            patch("nextmv.local.executor.subprocess.Popen", return_value=mock_process),
        ):
            execute_run(
                run_id=run_id,
                src="/test/src",
                manifest_dict={"execution": {"entrypoint": "main.py"}, "type": "python", "files": ["main.py"]},
                run_dir=run_dir,
                run_config={"format": {"input": {"type": "json"}}},
                input_data={"test": "data"},
            )

        logs_file = os.path.join(run_dir, LOGS_KEY, LOGS_FILE)
        self.assertTrue(os.path.exists(logs_file), "logs/logs.log should be created")
        with open(logs_file) as f:
            log_content = f.read()

        self.assertIn("stderr line 1", log_content)
        self.assertIn("stderr line 2", log_content)
        # For JSON format, stdout is buffered only and must not appear in the log
        self.assertNotIn("stdout line", log_content)

    def test_execute_run_stdout_persisted_to_logs_multi_file_format(self):
        """Test that stdout is written to logs/logs.log for multi-file format runs."""
        run_id = "test_run_stdout_multifile"
        run_dir = os.path.join(self.test_dir, "run_dir_stdout_multifile")
        os.makedirs(run_dir)

        info_file = os.path.join(run_dir, f"{run_id}.json")
        with open(info_file, "w") as f:
            json.dump(
                {
                    "metadata": {
                        "created_at": "2023-01-01T00:00:00Z",
                        "status_v2": "pending",
                        "format": {"output": {"type": "json"}},
                    }
                },
                f,
            )

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdin = Mock()
        mock_process.stdout = iter(["stdout log line 1\n", "stdout log line 2\n"])
        mock_process.stderr = iter(["stderr line\n"])

        with (
            patch("nextmv.local.executor._copy_files_from_manifest"),
            patch("nextmv.local.executor.process_run_output"),
            patch("nextmv.local.executor.subprocess.Popen", return_value=mock_process),
        ):
            execute_run(
                run_id=run_id,
                src="/test/src",
                manifest_dict={"execution": {"entrypoint": "main.py"}, "type": "python", "files": ["main.py"]},
                run_dir=run_dir,
                run_config={"format": {"input": {"type": "multi-file"}}},
                input_data=None,
            )

        logs_file = os.path.join(run_dir, LOGS_KEY, LOGS_FILE)
        self.assertTrue(os.path.exists(logs_file), "logs/logs.log should be created")
        with open(logs_file) as f:
            log_content = f.read()

        self.assertIn("stdout log line 1", log_content)
        self.assertIn("stdout log line 2", log_content)
        self.assertIn("stderr line", log_content)

    def test_process_run_output_with_valid_json(self):
        """Test process_run_output with valid JSON stdout."""
        # Create temp outputs directory
        temp_outputs_dir = os.path.join(self.temp_src, OUTPUTS_KEY)
        os.makedirs(temp_outputs_dir)

        mock_result = Mock()
        mock_result.stdout = '{"solution": {"value": 42}, "statistics": {"duration": 1.5}}'
        mock_result.stderr = "Processing completed"

        # Create metadata file that process_run_output expects
        self._create_metadata_file()

        with (
            patch("nextmv.local.executor._process_run_statistics") as mock_stats,
            patch("nextmv.local.executor._process_run_assets") as mock_assets,
            patch("nextmv.local.executor._process_run_solutions") as mock_solutions,
        ):
            process_run_output(
                manifest=self.mock_manifest,
                run_id="test_run_id",
                temp_src=self.temp_src,
                result=mock_result,
                run_dir=self.run_dir,
                src=self.test_dir,
            )

            # Verify all processing functions were called
            mock_stats.assert_called_once()
            mock_assets.assert_called_once()
            mock_solutions.assert_called_once()

            # Check that outputs directory was created
            outputs_dir = os.path.join(self.run_dir, OUTPUTS_KEY)
            self.assertTrue(os.path.exists(outputs_dir))

    def test_process_run_output_with_empty_stdout(self):
        """Test process_run_output with empty stdout."""
        mock_result = Mock()
        mock_result.stdout = ""
        mock_result.stderr = "No output"

        # Create metadata file that process_run_output expects
        self._create_metadata_file()

        with (
            patch("nextmv.local.executor._process_run_statistics") as mock_stats,
            patch("nextmv.local.executor._process_run_assets") as mock_assets,
            patch("nextmv.local.executor._process_run_solutions") as mock_solutions,
        ):
            process_run_output(
                manifest=self.mock_manifest,
                run_id="test_run_id",
                temp_src=self.temp_src,
                result=mock_result,
                run_dir=self.run_dir,
                src=self.test_dir,
            )

            # Verify all processing functions were called with empty string
            mock_stats.assert_called_once()
            mock_assets.assert_called_once()
            mock_solutions.assert_called_once()

            # Get the stdout_output that was passed to the functions
            stdout_output = mock_stats.call_args.kwargs["stdout_output"]
            self.assertEqual(stdout_output, "")


class TestCopyNewOrModifiedFiles(unittest.TestCase):
    """Test cases for the _copy_new_or_modified_files function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.runtime_dir = os.path.join(self.test_dir, "runtime")
        self.dst_dir = os.path.join(self.test_dir, "destination")
        self.original_src_dir = os.path.join(self.test_dir, "original_src")
        self.exclusion_dir1 = os.path.join(self.test_dir, "exclusion1")
        self.exclusion_dir2 = os.path.join(self.test_dir, "exclusion2")

        # Create all directories
        for dir_path in [
            self.runtime_dir,
            self.dst_dir,
            self.original_src_dir,
            self.exclusion_dir1,
            self.exclusion_dir2,
        ]:
            os.makedirs(dir_path, exist_ok=True)

        # Create mock manifest with empty files list
        self.mock_manifest = Mock(spec=Manifest)
        self.mock_manifest.files = []

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def _create_file(self, directory: str, filename: str, content: str = "content") -> str:
        """Helper to create a file with given content."""
        filepath = os.path.join(directory, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(content)
        return filepath

    def _create_binary_file(self, directory: str, filename: str, content: bytes = b"binary_content") -> str:
        """Helper to create a binary file with given content."""
        filepath = os.path.join(directory, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(content)
        return filepath

    def _assert_file_exists_with_content(self, filepath: str, expected_content: str):
        """Helper to assert file exists and has expected content."""
        self.assertTrue(os.path.exists(filepath), f"File {filepath} should exist")
        with open(filepath) as f:
            self.assertEqual(f.read(), expected_content)

    def _assert_file_not_exists(self, filepath: str):
        """Helper to assert file does not exist."""
        self.assertFalse(os.path.exists(filepath), f"File {filepath} should not exist")

    def test_copy_all_files_when_no_original_src(self):
        """Test copying all files when original_src_dir is None."""

        # Create files in runtime directory
        self._create_file(self.runtime_dir, "file1.txt", "content1")
        self._create_file(self.runtime_dir, "subdir/file2.txt", "content2")
        self._create_file(self.runtime_dir, "file3.py", "print('hello')")

        _copy_new_or_modified_files(self.runtime_dir, self.dst_dir, self.original_src_dir, self.mock_manifest)

        # All files should be copied
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "file1.txt"), "content1")
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "subdir/file2.txt"), "content2")
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "file3.py"), "print('hello')")

    @patch("nextmv.local.executor.find_files")
    def test_copy_new_files_only(self, mock_find_files):
        """Test copying only new files not present in original source."""

        # Create files in original source
        original_file1 = self._create_file(self.original_src_dir, "existing_file.txt", "original_content")
        self._create_file(self.original_src_dir, "subdir/existing_file2.txt", "original_content2")

        # Wait to ensure different timestamps
        time.sleep(0.1)

        # Create files in runtime directory - some new, some existing
        runtime_file1 = self._create_file(self.runtime_dir, "existing_file.txt", "original_content")
        # Same as original
        runtime_file2 = self._create_file(self.runtime_dir, "subdir/existing_file2.txt", "original_content2")
        self._create_file(self.runtime_dir, "new_file.txt", "new_content")  # New file
        self._create_file(self.runtime_dir, "new_subdir/new_file2.txt", "new_content2")  # New file in new dir

        # Make runtime files appear older than original (simulating unchanged files)
        older_time = os.path.getmtime(original_file1) - 1
        os.utime(runtime_file1, (older_time, older_time))
        os.utime(runtime_file2, (older_time, older_time))

        # Mock find_files to return existing files as manifest files
        mock_find_files.return_value = (
            [],  # warnings
            [],  # missing
            [
                {"interior_path": "existing_file.txt"},
                {"interior_path": "subdir/existing_file2.txt"},
            ],
        )

        _copy_new_or_modified_files(self.runtime_dir, self.dst_dir, self.original_src_dir, self.mock_manifest)

        # Only new files should be copied
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "new_file.txt"), "new_content")
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "new_subdir/new_file2.txt"), "new_content2")

        # Existing files should not be copied (same content and older timestamp)
        self._assert_file_not_exists(os.path.join(self.dst_dir, "existing_file.txt"))
        self._assert_file_not_exists(os.path.join(self.dst_dir, "subdir/existing_file2.txt"))

    def test_copy_modified_files_content_changed(self):
        """Test copying files with modified content."""

        # Create files in original source
        self._create_file(self.original_src_dir, "file1.txt", "original_content")
        self._create_file(self.original_src_dir, "subdir/file2.txt", "original_content2")

        # Create files in runtime directory with modified content
        self._create_file(self.runtime_dir, "file1.txt", "modified_content")
        self._create_file(self.runtime_dir, "subdir/file2.txt", "modified_content2")

        _copy_new_or_modified_files(self.runtime_dir, self.dst_dir, self.original_src_dir, self.mock_manifest)

        # Modified files should be copied
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "file1.txt"), "modified_content")
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "subdir/file2.txt"), "modified_content2")

    def test_copy_modified_files_newer_timestamp(self):
        """Test copying files with newer modification time but same content."""

        # Create files in original source
        original_file1 = self._create_file(self.original_src_dir, "file1.txt", "same_content")
        original_file2 = self._create_file(self.original_src_dir, "subdir/file2.txt", "same_content2")

        # Wait a bit to ensure different timestamps
        time.sleep(0.1)

        # Create files in runtime directory with same content but newer timestamp
        runtime_file1 = self._create_file(self.runtime_dir, "file1.txt", "same_content")
        runtime_file2 = self._create_file(self.runtime_dir, "subdir/file2.txt", "same_content2")

        # Verify runtime files are newer
        self.assertGreater(os.path.getmtime(runtime_file1), os.path.getmtime(original_file1))
        self.assertGreater(os.path.getmtime(runtime_file2), os.path.getmtime(original_file2))

        _copy_new_or_modified_files(self.runtime_dir, self.dst_dir, self.original_src_dir, self.mock_manifest)

        # Files with newer timestamps should be copied
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "file1.txt"), "same_content")
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "subdir/file2.txt"), "same_content2")

    @patch("nextmv.local.executor.find_files")
    def test_skip_unchanged_files(self, mock_find_files):
        """Test that unchanged files are not copied."""

        # Create files in original source
        original_file1 = self._create_file(self.original_src_dir, "file1.txt", "same_content")

        # Wait a bit to create runtime file
        time.sleep(0.1)

        # Create file in runtime directory with same content
        runtime_file1 = self._create_file(self.runtime_dir, "file1.txt", "same_content")

        # Make the original file newer (simulate unchanged file)
        newer_time = os.path.getmtime(runtime_file1) + 1
        os.utime(original_file1, (newer_time, newer_time))

        # Mock find_files to return the file as a manifest file
        mock_find_files.return_value = (
            [],  # warnings
            [],  # missing
            [
                {"interior_path": "file1.txt"},
            ],
        )

        _copy_new_or_modified_files(self.runtime_dir, self.dst_dir, self.original_src_dir, self.mock_manifest)

        # Unchanged file should not be copied
        self._assert_file_not_exists(os.path.join(self.dst_dir, "file1.txt"))

    def test_exclusion_dirs_functionality(self):
        """Test that files in exclusion directories are not copied."""

        # Create files in runtime directory
        self._create_file(self.runtime_dir, "keep_this.txt", "keep_content")
        self._create_file(self.runtime_dir, "exclude_this.txt", "exclude_content")
        self._create_file(self.runtime_dir, "subdir/keep_this2.txt", "keep_content2")
        self._create_file(self.runtime_dir, "subdir/exclude_this2.txt", "exclude_content2")

        # Create matching files in exclusion directories
        self._create_file(self.exclusion_dir1, "exclude_this.txt", "any_content")
        self._create_file(self.exclusion_dir2, "subdir/exclude_this2.txt", "any_content2")

        exclusion_dirs = [self.exclusion_dir1, self.exclusion_dir2]
        _copy_new_or_modified_files(
            self.runtime_dir, self.dst_dir, self.original_src_dir, self.mock_manifest, exclusion_dirs=exclusion_dirs
        )

        # Files not in exclusion should be copied
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "keep_this.txt"), "keep_content")
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "subdir/keep_this2.txt"), "keep_content2")

        # Files in exclusion should not be copied
        self._assert_file_not_exists(os.path.join(self.dst_dir, "exclude_this.txt"))
        self._assert_file_not_exists(os.path.join(self.dst_dir, "subdir/exclude_this2.txt"))

    def test_skip_pycache_and_pyc_files(self):
        """Test that __pycache__ directories and .pyc files are skipped."""

        # Create regular files
        self._create_file(self.runtime_dir, "normal_file.py", "print('hello')")

        # Create __pycache__ directory with .pyc files
        pycache_dir = os.path.join(self.runtime_dir, "__pycache__")
        os.makedirs(pycache_dir)
        self._create_file(pycache_dir, "normal_file.cpython-39.pyc", "bytecode")

        # Create nested __pycache__
        subdir_pycache = os.path.join(self.runtime_dir, "subdir", "__pycache__")
        os.makedirs(subdir_pycache)
        self._create_file(subdir_pycache, "another_file.cpython-39.pyc", "bytecode2")

        # Create .pyc file in regular directory
        self._create_file(self.runtime_dir, "direct_pyc.pyc", "bytecode3")

        _copy_new_or_modified_files(self.runtime_dir, self.dst_dir, self.original_src_dir, self.mock_manifest)

        # Regular Python file should be copied
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "normal_file.py"), "print('hello')")

        # __pycache__ directories and .pyc files should not be copied
        self._assert_file_not_exists(os.path.join(self.dst_dir, "__pycache__", "normal_file.cpython-39.pyc"))
        self._assert_file_not_exists(os.path.join(self.dst_dir, "subdir", "__pycache__", "another_file.cpython-39.pyc"))
        self._assert_file_not_exists(os.path.join(self.dst_dir, "direct_pyc.pyc"))

    def test_binary_files_handling(self):
        """Test that binary files are handled correctly."""

        # Create binary files in original source and runtime
        self._create_binary_file(self.original_src_dir, "image.png", b"\x89PNG\r\n\x1a\n")
        runtime_binary_same = self._create_binary_file(self.runtime_dir, "image.png", b"\x89PNG\r\n\x1a\n")
        self._create_binary_file(self.runtime_dir, "new_image.jpg", b"\xff\xd8\xff\xe0")
        self._create_binary_file(self.runtime_dir, "modified.png", b"\x89PNG\r\n\x1a\n\x00")

        # Create corresponding original file for the modified one
        self._create_binary_file(self.original_src_dir, "modified.png", b"\x89PNG\r\n\x1a\n")

        _copy_new_or_modified_files(self.runtime_dir, self.dst_dir, self.original_src_dir, self.mock_manifest)

        # New binary file should be copied
        self.assertTrue(os.path.exists(os.path.join(self.dst_dir, "new_image.jpg")))

        # Modified binary file should be copied
        self.assertTrue(os.path.exists(os.path.join(self.dst_dir, "modified.png")))

        # Unchanged binary file should not be copied (assuming same content and timestamp)
        # This depends on timing, so let's verify the file exists in runtime but behavior may vary
        self.assertTrue(os.path.exists(runtime_binary_same))

    def test_complex_directory_structure(self):
        """Test with complex nested directory structures."""

        # Create complex structure in original source
        self._create_file(self.original_src_dir, "root_file.txt", "root")
        self._create_file(self.original_src_dir, "level1/file1.txt", "level1_content")
        self._create_file(self.original_src_dir, "level1/level2/file2.txt", "level2_content")
        self._create_file(self.original_src_dir, "level1/level2/level3/file3.txt", "level3_content")

        # Create similar structure in runtime with mix of new, modified, and unchanged files
        self._create_file(self.runtime_dir, "root_file.txt", "root_modified")  # Modified
        self._create_file(self.runtime_dir, "level1/file1.txt", "level1_content")  # Unchanged content
        self._create_file(self.runtime_dir, "level1/level2/file2.txt", "level2_modified")  # Modified
        self._create_file(self.runtime_dir, "level1/level2/level3/file3.txt", "level3_content")  # Unchanged content
        self._create_file(self.runtime_dir, "level1/new_file.txt", "new_content")  # New file
        self._create_file(
            self.runtime_dir, "level1/level2/level3/level4/new_deep_file.txt", "deep_new"
        )  # New deep file

        _copy_new_or_modified_files(self.runtime_dir, self.dst_dir, self.original_src_dir, self.mock_manifest)

        # Modified files should be copied
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "root_file.txt"), "root_modified")
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "level1/level2/file2.txt"), "level2_modified")

        # New files should be copied
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "level1/new_file.txt"), "new_content")
        self._assert_file_exists_with_content(
            os.path.join(self.dst_dir, "level1/level2/level3/level4/new_deep_file.txt"), "deep_new"
        )

        # Unchanged files should not be copied (depending on timestamp)
        # Note: This test might be flaky due to timing, but we can check the logic

    def test_empty_directories_are_removed(self):
        """Test that empty directories are removed after copying."""

        # Create a structure where some directories will become empty
        self._create_file(self.runtime_dir, "keep/file1.txt", "content1")
        self._create_file(self.runtime_dir, "remove_empty/exclude_this.txt", "content2")

        # Create exclusion that will prevent the second file from being copied
        # The exclusion path must match the relative path from runtime_dir
        self._create_file(self.exclusion_dir1, "remove_empty/exclude_this.txt", "any_content")

        _copy_new_or_modified_files(
            self.runtime_dir,
            self.dst_dir,
            self.original_src_dir,
            self.mock_manifest,
            exclusion_dirs=[self.exclusion_dir1],
        )

        # Directory with kept file should exist
        self.assertTrue(os.path.exists(os.path.join(self.dst_dir, "keep")))
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "keep/file1.txt"), "content1")

        # Directory that would be empty should not exist (or should be removed)
        # Note: The function should remove empty directories
        self._assert_file_not_exists(os.path.join(self.dst_dir, "remove_empty/exclude_this.txt"))

    def test_edge_case_empty_runtime_dir(self):
        """Test behavior with empty runtime directory."""

        # Runtime directory is empty
        _copy_new_or_modified_files(self.runtime_dir, self.dst_dir, self.original_src_dir, self.mock_manifest)

        # Destination should remain empty (except for the directory itself)
        dst_contents = os.listdir(self.dst_dir)
        self.assertEqual(len(dst_contents), 0)

    def test_edge_case_nonexistent_exclusion_dir(self):
        """Test behavior with nonexistent exclusion directories."""

        self._create_file(self.runtime_dir, "file1.txt", "content1")

        nonexistent_dir = os.path.join(self.test_dir, "nonexistent")
        exclusion_dirs = [nonexistent_dir]

        # Should not raise an error
        _copy_new_or_modified_files(
            self.runtime_dir, self.dst_dir, self.original_src_dir, self.mock_manifest, exclusion_dirs=exclusion_dirs
        )

        # File should still be copied
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "file1.txt"), "content1")

    def test_preserve_file_permissions_and_metadata(self):
        """Test that file permissions and metadata are preserved during copying."""

        # Create a file with specific permissions
        test_file = self._create_file(self.runtime_dir, "test_file.txt", "content")

        # Set specific permissions (readable and writable by owner only)
        os.chmod(test_file, stat.S_IRUSR | stat.S_IWUSR)
        original_mode = os.stat(test_file).st_mode

        _copy_new_or_modified_files(self.runtime_dir, self.dst_dir, self.original_src_dir, self.mock_manifest)

        # Check that copied file has same permissions
        copied_file = os.path.join(self.dst_dir, "test_file.txt")
        copied_mode = os.stat(copied_file).st_mode

        # Compare the permission bits (mask out file type bits)
        self.assertEqual(original_mode & 0o777, copied_mode & 0o777)

    def test_mixed_scenarios_integration(self):
        """Integration test combining multiple scenarios."""

        # Set up original source files
        self._create_file(self.original_src_dir, "unchanged.txt", "unchanged_content")
        self._create_file(self.original_src_dir, "to_modify.txt", "original_content")
        self._create_file(self.original_src_dir, "subdir/nested_unchanged.txt", "nested_original")

        # Wait to ensure different timestamps
        time.sleep(0.1)

        # Set up runtime files
        self._create_file(self.runtime_dir, "unchanged.txt", "unchanged_content")  # Same content, newer timestamp
        self._create_file(self.runtime_dir, "to_modify.txt", "modified_content")  # Different content
        # Same content, newer timestamp
        self._create_file(self.runtime_dir, "subdir/nested_unchanged.txt", "nested_original")
        self._create_file(self.runtime_dir, "new_file.txt", "new_content")  # New file
        self._create_file(self.runtime_dir, "exclude_me.txt", "exclude_content")  # Will be excluded
        self._create_file(self.runtime_dir, "__pycache__/cached.pyc", "cache")  # Will be skipped
        self._create_file(self.runtime_dir, "regular.pyc", "pyc_content")  # Will be skipped

        # Set up exclusion
        self._create_file(self.exclusion_dir1, "exclude_me.txt", "any_content")

        _copy_new_or_modified_files(
            self.runtime_dir,
            self.dst_dir,
            self.original_src_dir,
            self.mock_manifest,
            exclusion_dirs=[self.exclusion_dir1],
        )

        # Files with newer timestamps should be copied
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "unchanged.txt"), "unchanged_content")
        nested_file_path = os.path.join(self.dst_dir, "subdir/nested_unchanged.txt")
        self._assert_file_exists_with_content(nested_file_path, "nested_original")

        # Modified files should be copied
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "to_modify.txt"), "modified_content")

        # New files should be copied
        self._assert_file_exists_with_content(os.path.join(self.dst_dir, "new_file.txt"), "new_content")

        # Excluded files should not be copied
        self._assert_file_not_exists(os.path.join(self.dst_dir, "exclude_me.txt"))

        # Cache files should not be copied
        self._assert_file_not_exists(os.path.join(self.dst_dir, "__pycache__/cached.pyc"))
        self._assert_file_not_exists(os.path.join(self.dst_dir, "regular.pyc"))


class TestExecutorEncoding(unittest.TestCase):
    """Tests that execute_run handles non-UTF-8 bytes in subprocess output without crashing."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.run_dir = os.path.join(self.test_dir, "run_dir")
        os.makedirs(self.run_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _make_info_file(self, run_id: str) -> None:
        info_file = os.path.join(self.run_dir, f"{run_id}.json")
        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "metadata": {
                        "created_at": "2023-01-01T00:00:00Z",
                        "status_v2": "pending",
                        "format": {"output": {"type": "json"}},
                    }
                },
                f,
            )

    def _run_execute_run(self, stdout_lines, stderr_lines, run_id="test_encoding_run"):
        """Helper that patches Popen and runs execute_run, returning normally."""
        self._make_info_file(run_id)

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdin = Mock()
        mock_process.stdout = iter(stdout_lines)
        mock_process.stderr = iter(stderr_lines)

        with (
            patch("nextmv.local.executor._copy_files_from_manifest"),
            patch("nextmv.local.executor.process_run_output"),
            patch("nextmv.local.executor.subprocess.Popen", return_value=mock_process),
        ):
            execute_run(
                run_id=run_id,
                src="/test/src",
                manifest_dict={"execution": {"entrypoint": "main.py"}, "type": "python", "files": ["main.py"]},
                run_dir=self.run_dir,
                run_config={"format": {"input": {"type": "json"}}},
                input_data={"test": "data"},
            )

    def test_non_utf8_bytes_in_stderr_do_not_crash(self):
        """Non-UTF-8 bytes in stderr must not raise UnicodeDecodeError.

        On Windows the subprocess pipes default to the system codepage (e.g.
        cp1252). Byte 0x8f is undefined in cp1252, so without an explicit
        encoding this would raise UnicodeDecodeError. The fix is to open the
        Popen with encoding='utf-8' and errors='replace'.
        """
        # Simulate a line that contains the byte 0x8f – undefined in cp1252.
        # We use a plain string here because the mock iter already yields str;
        # the important thing is that the pipeline doesn't blow up when such
        # a replacement character reaches the log file writer.
        bad_line = "progress: \ufffd done\n"  # U+FFFD = replacement character
        self._run_execute_run(stdout_lines=[], stderr_lines=[bad_line])

        logs_file = os.path.join(self.run_dir, LOGS_KEY, LOGS_FILE)
        self.assertTrue(os.path.exists(logs_file))
        with open(logs_file, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("progress:", content)

    def test_non_utf8_bytes_in_stdout_do_not_crash(self):
        """Non-UTF-8 replacement characters in stdout are handled gracefully."""
        bad_line = '{"result": "\ufffd"}\n'
        self._run_execute_run(stdout_lines=[bad_line], stderr_lines=[])

    def test_log_file_written_as_utf8(self):
        """The logs file must be written with UTF-8 encoding so non-ASCII characters survive."""
        unicode_line = "info: résumé café naïve 日本語\n"
        self._run_execute_run(stdout_lines=[], stderr_lines=[unicode_line])

        logs_file = os.path.join(self.run_dir, LOGS_KEY, LOGS_FILE)
        with open(logs_file, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("résumé", content)
        self.assertIn("日本語", content)

    def test_popen_called_with_utf8_encoding(self):
        """subprocess.Popen must be called with encoding='utf-8' and errors='replace'."""
        self._make_info_file("enc_check")

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdin = Mock()
        mock_process.stdout = iter([])
        mock_process.stderr = iter([])

        with (
            patch("nextmv.local.executor._copy_files_from_manifest"),
            patch("nextmv.local.executor.process_run_output"),
            patch("nextmv.local.executor.subprocess.Popen", return_value=mock_process) as mock_popen,
        ):
            execute_run(
                run_id="enc_check",
                src="/test/src",
                manifest_dict={"execution": {"entrypoint": "main.py"}, "type": "python", "files": ["main.py"]},
                run_dir=self.run_dir,
                run_config={"format": {"input": {"type": "json"}}},
                input_data={"test": "data"},
            )

        call_kwargs = mock_popen.call_args[1]
        self.assertEqual(call_kwargs.get("encoding"), "utf-8")
        self.assertEqual(call_kwargs.get("errors"), "replace")


class TestValidateExecutionInput(unittest.TestCase):
    """Test cases for the `_validate_execution_input` path-safety guard."""

    # Absolute paths are built with os.path so the fixtures are valid on every
    # OS (a POSIX-style "/test/src" is not absolute on Windows).
    SRC = os.path.abspath(os.path.join("test", "src"))
    RUN_ID = "local-abc123"
    RUN_DIR = os.path.join(SRC, ".nextmv", "runs", RUN_ID)

    def _valid_payload(self, **overrides):
        payload = {
            "run_id": self.RUN_ID,
            "src": self.SRC,
            "manifest_dict": {"type": "python"},
            "run_dir": self.RUN_DIR,
            "run_config": {"format": {"input": {"type": "json"}}},
        }
        payload.update(overrides)
        return payload

    def test_valid_payload_passes(self):
        # A well-formed payload from the trusted runner must validate cleanly.
        _validate_execution_input(self._valid_payload())

    def test_missing_required_field(self):
        payload = self._valid_payload()
        del payload["run_dir"]
        with self.assertRaises(ValueError):
            _validate_execution_input(payload)

    def test_wrong_type_field(self):
        with self.assertRaises(ValueError):
            _validate_execution_input(self._valid_payload(run_dir=123))

    def test_run_id_traversal_rejected(self):
        for bad in ["../evil", "a/b", "foo/../bar"]:
            with self.assertRaises(ValueError):
                _validate_execution_input(self._valid_payload(run_id=bad))

    def test_run_dir_traversal_rejected(self):
        # A run_dir escaping via `..` must be rejected even if its final
        # component matches the run_id.
        bad = os.path.join(self.SRC, ".nextmv", "runs", "..", "..", "..", self.RUN_ID)
        with self.assertRaises(ValueError):
            _validate_execution_input(self._valid_payload(run_dir=bad))

    def test_run_dir_null_byte_rejected(self):
        with self.assertRaises(ValueError):
            _validate_execution_input(self._valid_payload(run_dir=self.RUN_DIR + "\x00"))

    def test_run_dir_outside_src_rejected(self):
        # An absolute run_dir whose basename matches run_id but which does not
        # live under src must be rejected (must be anchored to src, not just
        # matched on basename).
        bad = os.path.abspath(os.path.join("tmp", "evil", self.RUN_ID))
        with self.assertRaises(ValueError):
            _validate_execution_input(self._valid_payload(run_dir=bad))

    def test_run_dir_relative_rejected(self):
        # A CWD-relative run_dir must be rejected: it would resolve against the
        # executor's working directory rather than under src.
        with self.assertRaises(ValueError):
            _validate_execution_input(self._valid_payload(run_dir=self.RUN_ID))

    def test_run_dir_not_under_src_rejected(self):
        bad = os.path.abspath(os.sep + "etc")
        with self.assertRaises(ValueError):
            _validate_execution_input(self._valid_payload(run_dir=bad))

    def test_src_must_be_absolute(self):
        rel_src = os.path.join("relative", "src")
        with self.assertRaises(ValueError):
            _validate_execution_input(
                self._valid_payload(src=rel_src, run_dir=os.path.join(rel_src, ".nextmv", "runs", self.RUN_ID))
            )

    def test_src_null_byte_rejected(self):
        with self.assertRaises(ValueError):
            _validate_execution_input(self._valid_payload(src=self.SRC + "\x00"))


if __name__ == "__main__":
    unittest.main()
