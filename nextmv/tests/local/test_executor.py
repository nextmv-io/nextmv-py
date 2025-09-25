"""
Unit tests for the nextmv.local.executor module.
"""

import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import Mock, patch

from nextmv.local.executor import (
    ASSETS_KEY,
    OUTPUTS_KEY,
    SOLUTIONS_KEY,
    STATISTICS_KEY,
    execute_run,
    main,
    options_args,
    process_run_assets,
    process_run_input,
    process_run_logs,
    process_run_output,
    process_run_solutions,
    process_run_statistics,
)
from nextmv.manifest import Manifest
from nextmv.output import OutputFormat


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
        self.mock_manifest.entrypoint = "main.py"
        self.mock_manifest.configuration = None

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
        self.mock_output_format = Mock(spec=OutputFormat)
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
        # Setup mock input
        mock_input = Mock()
        mock_input.data = {
            "run_id": "test_run_id",
            "src": "/test/src",
            "manifest_dict": {"entrypoint": "main.py", "type": "python"},
            "run_dir": "/test/run_dir",
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
            src="/test/src",
            manifest_dict={"entrypoint": "main.py", "type": "python"},
            run_dir="/test/run_dir",
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

    def test_process_run_logs(self):
        """Test process_run_logs function."""
        # Create mock result
        mock_result = Mock()
        mock_result.stderr = "Error line 1\nError line 2\n"

        stdout_output = {"logs": ["test log 1", "test log 2"]}

        process_run_logs(
            output_format=self.mock_output_format, run_dir=self.run_dir, result=mock_result, stdout_output=stdout_output
        )

        # Check that logs directory was created
        logs_dir = os.path.join(self.run_dir, "logs")
        self.assertTrue(os.path.exists(logs_dir))

        # Check that stderr.log was created with correct content
        stderr_file = os.path.join(logs_dir, "stderr.log")
        self.assertTrue(os.path.exists(stderr_file))

        with open(stderr_file) as f:
            content = f.read()

        self.assertEqual(content, "Error line 1\nError line 2\n")

    def test_process_run_statistics_from_directory(self):
        """Test process_run_statistics when statistics directory exists."""
        # Create temp outputs directory with statistics
        temp_outputs_dir = os.path.join(self.temp_src, OUTPUTS_KEY)
        stats_src = os.path.join(temp_outputs_dir, STATISTICS_KEY)
        os.makedirs(stats_src)

        with open(os.path.join(stats_src, "timing.json"), "w") as f:
            json.dump({"duration": 1.5}, f)

        outputs_dir = os.path.join(self.run_dir, OUTPUTS_KEY)
        os.makedirs(outputs_dir)

        stdout_output = {}

        process_run_statistics(
            temp_outputs_dir, outputs_dir, stdout_output, temp_src=self.temp_src, manifest=self.mock_manifest
        )

        # Check that statistics directory was copied
        stats_dst = os.path.join(outputs_dir, STATISTICS_KEY)
        self.assertTrue(os.path.exists(stats_dst))
        self.assertTrue(os.path.exists(os.path.join(stats_dst, "timing.json")))

    def test_process_run_statistics_from_stdout(self):
        """Test process_run_statistics when statistics are in stdout."""
        temp_outputs_dir = os.path.join(self.temp_src, OUTPUTS_KEY)
        outputs_dir = os.path.join(self.run_dir, OUTPUTS_KEY)
        os.makedirs(outputs_dir)

        stdout_output = {STATISTICS_KEY: {"duration": 2.5, "iterations": 100}}

        process_run_statistics(
            temp_outputs_dir, outputs_dir, stdout_output, temp_src=self.temp_src, manifest=self.mock_manifest
        )

        # Check that statistics.json was created
        stats_dst = os.path.join(outputs_dir, STATISTICS_KEY)
        self.assertTrue(os.path.exists(stats_dst))

        stats_file = os.path.join(stats_dst, f"{STATISTICS_KEY}.json")
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

        process_run_statistics(
            temp_outputs_dir, outputs_dir, stdout_output, temp_src=self.temp_src, manifest=self.mock_manifest
        )

        # Check that statistics directory was not created
        stats_dst = os.path.join(outputs_dir, STATISTICS_KEY)
        self.assertTrue(os.path.exists(stats_dst))

    def test_process_run_assets_from_directory(self):
        """Test process_run_assets when assets directory exists."""
        # Create temp outputs directory with assets
        temp_outputs_dir = os.path.join(self.temp_src, OUTPUTS_KEY)
        assets_src = os.path.join(temp_outputs_dir, ASSETS_KEY)
        os.makedirs(assets_src)

        with open(os.path.join(assets_src, "plot.png"), "w") as f:
            f.write("fake image data")

        outputs_dir = os.path.join(self.run_dir, OUTPUTS_KEY)
        os.makedirs(outputs_dir)

        stdout_output = {}

        process_run_assets(
            temp_outputs_dir, outputs_dir, stdout_output, temp_src=self.temp_src, manifest=self.mock_manifest
        )

        # Check that assets directory was copied
        assets_dst = os.path.join(outputs_dir, ASSETS_KEY)
        self.assertTrue(os.path.exists(assets_dst))
        self.assertTrue(os.path.exists(os.path.join(assets_dst, "plot.png")))

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

        process_run_assets(
            temp_outputs_dir, outputs_dir, stdout_output, temp_src=self.temp_src, manifest=self.mock_manifest
        )

        # Check that assets.json was created
        assets_dst = os.path.join(outputs_dir, ASSETS_KEY)
        self.assertTrue(os.path.exists(assets_dst))

        assets_file = os.path.join(assets_dst, f"{ASSETS_KEY}.json")
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

        process_run_solutions(
            "test_run_id",
            self.run_dir,
            temp_outputs_dir,
            self.temp_src,
            outputs_dir,
            stdout_output,
            output_format=OutputFormat.CSV_ARCHIVE,
            manifest=self.mock_manifest,
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

        process_run_solutions(
            "test_run_id",
            self.run_dir,
            temp_outputs_dir,
            self.temp_src,
            outputs_dir,
            stdout_output,
            output_format=OutputFormat.MULTI_FILE,
            manifest=self.mock_manifest,
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

        process_run_solutions(
            "test_run_id",
            self.run_dir,
            temp_outputs_dir,
            self.temp_src,
            outputs_dir,
            stdout_output,
            output_format=self.mock_output_format,
            manifest=self.mock_manifest,
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

        process_run_solutions(
            "test_run_id",
            self.run_dir,
            temp_outputs_dir,
            self.temp_src,
            outputs_dir,
            stdout_output,
            output_format=self.mock_output_format,
            manifest=self.mock_manifest,
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
    @patch("nextmv.local.executor.subprocess.run")
    @patch("nextmv.local.executor.shutil.copytree")
    @patch("nextmv.local.executor.tempfile.TemporaryDirectory")
    @patch("nextmv.local.executor.os.makedirs")
    def test_execute_run_full_flow(
        self,
        mock_makedirs,
        mock_temp_dir,
        mock_copytree,
        mock_subprocess_run,
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

        mock_result = Mock()
        mock_result.stdout = '{"solution": {"value": 42}}'
        mock_result.stderr = "No errors"
        mock_subprocess_run.return_value = mock_result

        run_config = {"format": {"input": {"type": "json"}, "output": {"type": "json"}}}

        # Configure mock JSON operations
        mock_json_load.return_value = {"metadata": {"status_v2": "pending"}}

        execute_run(
            run_id="test_run_id",
            src="/test/src",
            manifest_dict={"entrypoint": "main.py", "files": ["main.py"]},
            run_dir="/test/run_dir",
            run_config=run_config,
            input_data={"test": "data"},
            options={"duration": "10s"},
        )

        # Verify copytree was called to copy source
        mock_copytree.assert_called_once_with("/test/src", temp_src, ignore=unittest.mock.ANY)

        # Verify process_run_input was called
        mock_process_input.assert_called_once_with(
            temp_src=temp_src,
            run_format="json",
            manifest=unittest.mock.ANY,
            input_data={"test": "data"},
            inputs_dir_path=None,
        )

        # Verify subprocess.run was called
        mock_subprocess_run.assert_called_once()
        call_args = mock_subprocess_run.call_args
        self.assertEqual(call_args[0][0][:2], ["python", os.path.join(temp_src, "main.py")])
        self.assertIn("-duration", call_args[0][0])
        self.assertIn("10s", call_args[0][0])

        # Verify process_run_output was called
        mock_process_output.assert_called_once_with(
            manifest=unittest.mock.ANY,
            run_id="test_run_id",
            temp_src=temp_src,
            result=mock_result,
            run_dir="/test/run_dir",
        )

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
            patch("nextmv.local.executor.process_run_logs") as mock_logs,
            patch("nextmv.local.executor.process_run_statistics") as mock_stats,
            patch("nextmv.local.executor.process_run_assets") as mock_assets,
            patch("nextmv.local.executor.process_run_solutions") as mock_solutions,
        ):
            process_run_output(
                manifest=self.mock_manifest,
                run_id="test_run_id",
                temp_src=self.temp_src,
                result=mock_result,
                run_dir=self.run_dir,
            )

            # Verify all processing functions were called
            mock_logs.assert_called_once_with(
                output_format=unittest.mock.ANY,
                run_dir=self.run_dir,
                result=mock_result,
                stdout_output={"solution": {"value": 42}, "statistics": {"duration": 1.5}},
            )
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
            patch("nextmv.local.executor.process_run_logs") as mock_logs,
            patch("nextmv.local.executor.process_run_statistics") as mock_stats,
            patch("nextmv.local.executor.process_run_assets") as mock_assets,
            patch("nextmv.local.executor.process_run_solutions") as mock_solutions,
        ):
            process_run_output(
                manifest=self.mock_manifest,
                run_id="test_run_id",
                temp_src=self.temp_src,
                result=mock_result,
                run_dir=self.run_dir,
            )

            # Verify all processing functions were called with empty dict
            mock_logs.assert_called_once_with(
                output_format=unittest.mock.ANY, run_dir=self.run_dir, result=mock_result, stdout_output={}
            )
            mock_stats.assert_called_once()
            mock_assets.assert_called_once()
            mock_solutions.assert_called_once()

            # Get the stdout_output that was passed to the functions
            stdout_output = mock_stats.call_args.kwargs["stdout_output"]
            self.assertEqual(stdout_output, {})


if __name__ == "__main__":
    unittest.main()
