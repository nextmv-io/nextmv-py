"""
Unit tests for the nextmv.local.runner module.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from nextmv.local.runner import new_run, record_input, run
from nextmv.manifest import Manifest, ManifestRuntime


class TestLocalRunner(unittest.TestCase):
    """Test cases for the local runner module."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_src = os.path.join(self.test_dir, "test_app")
        os.makedirs(self.test_src)

        # Create a basic manifest file
        self.manifest_content = {
            "spec_version": "v1beta1",
            "id": "test-app",
            "name": "Test App",
            "description": "Test application",
            "entrypoint": "main.py",
            "type": "python",
            "runtime": "ghcr.io/nextmv-io/runtime/python:3.11",
            "files": ["main.py"],
        }

        # Create a basic entrypoint file
        self.entrypoint_content = """
import json
import sys

# Read input from stdin
try:
    input_data = json.load(sys.stdin)
except:
    input_data = {"test": "data"}

# Simple output
output = {
    "solution": {"result": 42},
    "statistics": {"duration": 0.1},
    "assets": []
}

print(json.dumps(output))
"""

        with open(os.path.join(self.test_src, "main.py"), "w") as f:
            f.write(self.entrypoint_content)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_new_run_creates_directory_structure(self):
        """Test that new_run creates the proper directory structure."""
        run_id = "test-run-123"
        run_config = {"format": {"input": {"type": "json"}, "output": {"type": "json"}}}

        result_dir = new_run(app_id="sample-app", src=self.test_src, run_id=run_id, run_config=run_config)

        expected_dir = os.path.join(self.test_src, ".nextmv", "runs", run_id)
        self.assertEqual(result_dir, expected_dir)
        self.assertTrue(os.path.exists(expected_dir))
        self.assertTrue(os.path.isdir(expected_dir))

    def test_new_run_creates_runs_dir_if_not_exists(self):
        """Test that new_run creates the runs directory if it doesn't exist."""
        run_id = "test-run-456"
        run_config = {"format": {"input": {"type": "json"}, "output": {"type": "json"}}}

        # Ensure .nextmv/runs doesn't exist
        runs_dir = os.path.join(self.test_src, ".nextmv", "runs")
        self.assertFalse(os.path.exists(runs_dir))

        result_dir = new_run(app_id="sample-app", src=self.test_src, run_id=run_id, run_config=run_config)

        self.assertTrue(os.path.exists(runs_dir))
        self.assertTrue(os.path.exists(result_dir))

    def test_record_input_with_dict_data(self):
        """Test record_input with dictionary input data."""
        run_dir = os.path.join(self.test_dir, "test_run")
        os.makedirs(run_dir)

        input_data = {"test": "data", "value": 42}

        # Create minimal metadata file that calculate_files_size expects
        metadata_file = os.path.join(run_dir, "test_run.json")
        with open(metadata_file, "w") as f:
            json.dump({"metadata": {}}, f)

        record_input(run_dir, run_id="test_run", input_data=input_data)

        # Check that inputs directory was created
        inputs_dir = os.path.join(run_dir, "inputs")
        self.assertTrue(os.path.exists(inputs_dir))

        # Check that input.json was created with correct content
        input_file = os.path.join(inputs_dir, "input.json")
        self.assertTrue(os.path.exists(input_file))

        with open(input_file) as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data, input_data)

    def test_record_input_with_string_data(self):
        """Test record_input with string input data."""
        run_dir = os.path.join(self.test_dir, "test_run")
        os.makedirs(run_dir)

        input_data = "test string input"

        # Create minimal metadata file that calculate_files_size expects
        metadata_file = os.path.join(run_dir, "test_run.json")
        with open(metadata_file, "w") as f:
            json.dump({"metadata": {}}, f)

        record_input(run_dir, run_id="test_run", input_data=input_data)

        # Check that inputs directory was created
        inputs_dir = os.path.join(run_dir, "inputs")
        self.assertTrue(os.path.exists(inputs_dir))

        # Check that input file was created with correct content
        input_file = os.path.join(inputs_dir, "input")
        self.assertTrue(os.path.exists(input_file))

        with open(input_file) as f:
            saved_data = f.read()

        self.assertEqual(saved_data, input_data)

    def test_record_input_with_inputs_dir_path(self):
        """Test record_input with inputs directory path."""
        run_dir = os.path.join(self.test_dir, "test_run")
        os.makedirs(run_dir)

        # Create a test inputs directory with some files
        test_inputs_dir = os.path.join(self.test_dir, "test_inputs")
        os.makedirs(test_inputs_dir)

        with open(os.path.join(test_inputs_dir, "file1.csv"), "w") as f:
            f.write("col1,col2\nval1,val2\n")

        with open(os.path.join(test_inputs_dir, "file2.txt"), "w") as f:
            f.write("test content")

        # Create subdirectory
        subdir = os.path.join(test_inputs_dir, "subdir")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "file3.json"), "w") as f:
            json.dump({"test": "data"}, f)

        # Create minimal metadata file that calculate_files_size expects
        metadata_file = os.path.join(run_dir, "test_run.json")
        with open(metadata_file, "w") as f:
            json.dump({"metadata": {}}, f)

        record_input(run_dir, run_id="test_run", inputs_dir_path=test_inputs_dir)

        # Check that inputs directory was created
        inputs_dir = os.path.join(run_dir, "inputs")
        self.assertTrue(os.path.exists(inputs_dir))

        # Check that all files were copied
        self.assertTrue(os.path.exists(os.path.join(inputs_dir, "file1.csv")))
        self.assertTrue(os.path.exists(os.path.join(inputs_dir, "file2.txt")))
        self.assertTrue(os.path.exists(os.path.join(inputs_dir, "subdir", "file3.json")))

        # Verify content
        with open(os.path.join(inputs_dir, "file1.csv")) as f:
            self.assertEqual(f.read(), "col1,col2\nval1,val2\n")

    def test_record_input_prioritizes_inputs_dir_path(self):
        """Test that inputs_dir_path takes precedence over input_data."""
        run_dir = os.path.join(self.test_dir, "test_run")
        os.makedirs(run_dir)

        # Create test inputs directory
        test_inputs_dir = os.path.join(self.test_dir, "test_inputs")
        os.makedirs(test_inputs_dir)
        with open(os.path.join(test_inputs_dir, "test.txt"), "w") as f:
            f.write("from directory")

        input_data = {"should": "be ignored"}

        # Create minimal metadata file that calculate_files_size expects
        metadata_file = os.path.join(run_dir, "test_run.json")
        with open(metadata_file, "w") as f:
            json.dump({"metadata": {}}, f)

        record_input(run_dir, run_id="test_run", input_data=input_data, inputs_dir_path=test_inputs_dir)

        inputs_dir = os.path.join(run_dir, "inputs")

        # Should have the directory file, not the JSON input
        self.assertTrue(os.path.exists(os.path.join(inputs_dir, "test.txt")))
        self.assertFalse(os.path.exists(os.path.join(inputs_dir, "input.json")))

    def test_record_input_handles_nonexistent_inputs_dir(self):
        """Test record_input handles non-existent inputs directory gracefully."""
        run_dir = os.path.join(self.test_dir, "test_run")
        os.makedirs(run_dir)

        nonexistent_dir = os.path.join(self.test_dir, "nonexistent")

        # Create minimal metadata file that calculate_files_size expects
        metadata_file = os.path.join(run_dir, "test_run.json")
        with open(metadata_file, "w") as f:
            json.dump({"metadata": {}}, f)

        # Should not raise an exception
        record_input(run_dir, run_id="test_run", inputs_dir_path=nonexistent_dir)

        # Inputs directory should still be created
        inputs_dir = os.path.join(run_dir, "inputs")
        self.assertTrue(os.path.exists(inputs_dir))

    @patch("nextmv.local.runner.subprocess.Popen")
    @patch("nextmv.local.runner.safe_id")
    def test_run_function_execution(self, mock_safe_id, mock_popen):
        """Test the main run function execution flow."""
        # Setup mocks
        mock_safe_id.return_value = "test-run-id"
        mock_process = Mock()
        mock_process.stdin = Mock()
        mock_popen.return_value = mock_process

        # Create manifest
        manifest = Manifest(
            files=["main.py"],
            runtime=ManifestRuntime.PYTHON,
        )

        run_config = {"format": {"input": {"type": "json"}, "output": {"type": "json"}}}

        input_data = {"test": "input"}
        options = {"duration": "10s"}

        result = run(
            app_id="sample-app",
            src=self.test_src,
            manifest=manifest,
            run_config=run_config,
            input_data=input_data,
            options=options,
        )

        # Verify run ID was generated
        mock_safe_id.assert_called_once_with("local")
        self.assertEqual(result, "test-run-id")

        # Verify subprocess was called
        mock_popen.assert_called_once()
        popen_args = mock_popen.call_args

        # Check the command
        self.assertEqual(popen_args[0][0], [sys.executable, "executor.py"])

        # Check that stdin was written to
        mock_process.stdin.write.assert_called_once()
        mock_process.stdin.close.assert_called_once()

        # Verify the input JSON that was sent
        stdin_data = mock_process.stdin.write.call_args[0][0]
        stdin_json = json.loads(stdin_data)

        expected_keys = [
            "run_id",
            "src",
            "manifest_dict",
            "run_dir",
            "run_config",
            "input_data",
            "inputs_dir_path",
            "options",
        ]
        for key in expected_keys:
            self.assertIn(key, stdin_json)

        self.assertEqual(stdin_json["manifest_dict"]["entrypoint"], "./main.py")
        self.assertEqual(stdin_json["input_data"], input_data)
        self.assertEqual(stdin_json["options"], options)
        self.assertEqual(stdin_json["run_config"], run_config)

    @patch("nextmv.local.runner.subprocess.Popen")
    @patch("nextmv.local.runner.safe_id")
    def test_run_with_inputs_dir_path(self, mock_safe_id, mock_popen):
        """Test run function with inputs directory path."""
        mock_safe_id.return_value = "test-run-id-2"
        mock_process = Mock()
        mock_process.stdin = Mock()
        mock_popen.return_value = mock_process

        manifest = Manifest(
            files=["main.py"],
        )

        run_config = {"format": {"input": {"type": "multi-file"}, "output": {"type": "multi-file"}}}

        # Create test inputs directory
        test_inputs_dir = os.path.join(self.test_dir, "test_inputs")
        os.makedirs(test_inputs_dir)

        result = run(
            app_id="sample-app",
            src=self.test_src,
            manifest=manifest,
            run_config=run_config,
            inputs_dir_path=test_inputs_dir,
        )

        self.assertEqual(result, "test-run-id-2")  # Verify the input JSON included the absolute path
        stdin_data = mock_process.stdin.write.call_args[0][0]
        stdin_json = json.loads(stdin_data)

        self.assertEqual(stdin_json["inputs_dir_path"], os.path.abspath(test_inputs_dir))

    @patch("nextmv.local.runner.subprocess.Popen")
    @patch("nextmv.local.runner.safe_id")
    def test_run_with_no_inputs_dir_path(self, mock_safe_id, mock_popen):
        """Test run function when inputs_dir_path is None."""
        mock_safe_id.return_value = "test-run-id-3"
        mock_process = Mock()
        mock_process.stdin = Mock()
        mock_popen.return_value = mock_process

        manifest = Manifest(
            files=["main.py"],
        )

        run_config = {"format": {"input": {"type": "json"}}}

        run(
            app_id="sample-app",
            src=self.test_src,
            manifest=manifest,
            run_config=run_config,
            input_data={"test": "data"},
        )

        # Verify the input JSON has None for inputs_dir_path
        stdin_data = mock_process.stdin.write.call_args[0][0]
        stdin_json = json.loads(stdin_data)

        self.assertIsNone(stdin_json["inputs_dir_path"])

    @patch("nextmv.local.runner.subprocess.Popen")
    @patch("nextmv.local.runner.safe_id")
    def test_run_subprocess_configuration(self, mock_safe_id, mock_popen):
        """Test that subprocess is configured correctly for detached execution."""
        mock_safe_id.return_value = "test-run-id-4"
        mock_process = Mock()
        mock_process.stdin = Mock()
        mock_popen.return_value = mock_process

        manifest = Manifest(
            files=["main.py"],
        )

        run_config = {"format": {"input": {"type": "json"}}}

        run(
            app_id="sample-app",
            src=self.test_src,
            manifest=manifest,
            run_config=run_config,
            input_data={"test": "data"},
        )

        # Verify subprocess configuration
        popen_kwargs = mock_popen.call_args[1]

        self.assertEqual(popen_kwargs["env"], os.environ)
        self.assertTrue(popen_kwargs["text"])
        self.assertEqual(popen_kwargs["stdin"], unittest.mock.ANY)  # subprocess.PIPE
        self.assertEqual(popen_kwargs["stdout"], unittest.mock.ANY)  # subprocess.DEVNULL
        self.assertEqual(popen_kwargs["stderr"], unittest.mock.ANY)  # subprocess.DEVNULL
        self.assertTrue(popen_kwargs["start_new_session"])  # For detached process


if __name__ == "__main__":
    unittest.main()
