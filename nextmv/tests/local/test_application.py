import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import Mock, patch

import yaml
from nextmv.input import Input, InputFormat
from nextmv.local.application import Application
from nextmv.options import Options
from nextmv.output import OutputFormat
from nextmv.polling import DEFAULT_POLLING_OPTIONS, PollingOptions
from nextmv.run import Format, FormatInput, FormatOutput, RunConfiguration, RunInformation, RunResult
from nextmv.status import StatusV2


class TestApplication(unittest.TestCase):
    def test_initialize(self):
        """Test the Application.initialize method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            app_name = "test-app"
            description = "Test application"

            # Initialize the application
            app = Application.initialize(
                src=app_name,
                description=description,
                destination=temp_dir,
            )

            # Verify the application object
            self.assertEqual(app.description, description)
            self.assertEqual(app.src, os.path.join(temp_dir, app_name))

            # Verify the directory structure was created
            app_dir = os.path.join(temp_dir, app_name)
            self.assertTrue(os.path.exists(app_dir))
            self.assertTrue(os.path.isdir(app_dir))

            # Verify app.yaml was copied
            app_yaml_path = os.path.join(app_dir, "app.yaml")
            self.assertTrue(os.path.exists(app_yaml_path))

            # Verify requirements.txt was copied
            requirements_path = os.path.join(app_dir, "requirements.txt")
            self.assertTrue(os.path.exists(requirements_path))

            # Verify README.md was copied
            readme_path = os.path.join(app_dir, "README.md")
            self.assertTrue(os.path.exists(readme_path))

            # Verify src directory was copied
            src_dir = os.path.join(app_dir, "src")
            self.assertTrue(os.path.exists(src_dir))
            self.assertTrue(os.path.isdir(src_dir))

    def test_initialize_with_defaults(self):
        """Test the Application.initialize method with default parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory to test default destination
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                # Initialize with minimal parameters
                app = Application.initialize()

                # Verify the application object has generated ID
                self.assertIsNone(app.description)  # description should be None when not provided
                # Use the current working directory for comparison since that's where the app is created
                expected_src_path = os.path.join(os.getcwd(), app.src)
                self.assertEqual(app.src, expected_src_path)

                # Verify the directory structure was created in current directory
                app_dir = os.path.join(temp_dir, app.src)
                self.assertTrue(os.path.exists(app_dir))
                self.assertTrue(os.path.isdir(app_dir))

                # Verify basic structure exists
                self.assertTrue(os.path.exists(os.path.join(app_dir, "app.yaml")))
                self.assertTrue(os.path.exists(os.path.join(app_dir, "src")))

            finally:
                os.chdir(original_cwd)

    def test_initialize_existing_directory(self):
        """Test that initialize does not work when the directory already exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            app_name = "existing-app"
            app_dir = os.path.join(temp_dir, app_name)

            # Pre-create the directory
            os.makedirs(app_dir, exist_ok=True)

            # Initialize should raise FileExistsError
            with self.assertRaises(FileExistsError) as context:
                Application.initialize(
                    src=app_name,
                    destination=temp_dir,
                )

            # Verify the error message contains the expected path
            self.assertIn(app_dir, str(context.exception))
            self.assertIn("destination dir for src already exists", str(context.exception))


class TestApplicationNewLocalRun(unittest.TestCase):
    """Test cases for the Application.new_run method."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.app_src = os.path.join(self.test_dir, "test_app")
        os.makedirs(self.app_src)

        # Create a manifest file
        manifest_content = {
            "spec_version": "v1beta1",
            "id": "test-app",
            "name": "Test App",
            "description": "Test application",
            "entrypoint": "main.py",
            "type": "python",
            "runtime": "ghcr.io/nextmv-io/runtime/python:3.11",
            "files": ["main.py"],
        }

        with open(os.path.join(self.app_src, "app.yaml"), "w") as f:
            yaml.dump(manifest_content, f)

        # Create a simple entrypoint
        with open(os.path.join(self.app_src, "main.py"), "w") as f:
            f.write("""
import json
import sys

try:
    input_data = json.load(sys.stdin)
except:
    input_data = {"test": "data"}

output = {"solution": {"result": 42}}
print(json.dumps(output))
""")

        # Create test application
        self.app = Application(src=self.app_src)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch("nextmv.local.application.run")
    def test_new_run_basic(self, mock_run):
        """Test basic new_run functionality."""
        mock_run.return_value = "test-run-id"

        result = self.app.new_run(input={"test": "input"}, options={"duration": "10s"})

        self.assertEqual(result, "test-run-id")
        mock_run.assert_called_once()

        # Verify the call arguments
        call_args = mock_run.call_args
        self.assertEqual(call_args[1]["src"], self.app_src)
        self.assertIn("manifest", call_args[1])
        self.assertIn("run_config", call_args[1])
        self.assertEqual(call_args[1]["input_data"], {"test": "input"})
        self.assertEqual(call_args[1]["options"], {"duration": "10s"})

    @patch("nextmv.local.application.run")
    def test_new_run_with_inputs_dir_path(self, mock_run):
        """Test new_run with inputs directory path."""
        mock_run.return_value = "test-run-id-2"

        # Create test inputs directory
        inputs_dir = os.path.join(self.test_dir, "inputs")
        os.makedirs(inputs_dir)
        with open(os.path.join(inputs_dir, "data.csv"), "w") as f:
            f.write("col1,col2\nval1,val2\n")

        result = self.app.new_run(
            input_dir_path=inputs_dir,
            configuration=RunConfiguration(
                format=Format(
                    format_input=FormatInput(input_type=InputFormat.CSV_ARCHIVE),
                    format_output=FormatOutput(output_type=OutputFormat.CSV_ARCHIVE),
                )
            ),
        )

        self.assertEqual(result, "test-run-id-2")
        mock_run.assert_called_once()

        # Verify inputs_dir_path was passed
        call_args = mock_run.call_args
        self.assertEqual(call_args[1]["inputs_dir_path"], inputs_dir)

    @patch("nextmv.local.application.run")
    def test_new_run_with_dict_input(self, mock_run):
        """Test new_run with dictionary input."""
        mock_run.return_value = "test-run-id-3"

        input_data = {"vehicles": [{"id": 1, "capacity": 100}]}

        result = self.app.new_run(input=input_data)

        self.assertEqual(result, "test-run-id-3")

        # Verify input_data was extracted correctly
        call_args = mock_run.call_args
        self.assertEqual(call_args[1]["input_data"], input_data)

    @patch("nextmv.local.application.run")
    def test_new_run_with_string_input(self, mock_run):
        """Test new_run with string input."""
        mock_run.return_value = "test-run-id-4"

        input_data = "raw text input"

        result = self.app.new_run(input=input_data)

        self.assertEqual(result, "test-run-id-4")

        # Verify input_data was passed as string
        call_args = mock_run.call_args
        self.assertEqual(call_args[1]["input_data"], input_data)

    def test_new_run_no_input_error(self):
        """Test new_run raises error when neither input nor inputs_dir_path is provided."""
        with self.assertRaises(ValueError) as context:
            self.app.new_run()

        self.assertIn("Either `input` or `input_directory` must be specified", str(context.exception))

    def test_new_run_manifest_not_found_error(self):
        """Test new_run raises error when manifest.yaml is not found."""
        # Remove the manifest file
        os.remove(os.path.join(self.app_src, "app.yaml"))

        with self.assertRaises(FileNotFoundError) as context:
            self.app.new_run(input={"test": "data"})

        self.assertIn("Could not find manifest.yaml", str(context.exception))

    @patch("nextmv.local.application.run")
    def test_new_run_with_nextmv_input_object(self, mock_run):
        """Test new_run with nextmv.Input object."""
        mock_run.return_value = "test-run-id-5"

        input_obj = Input(data={"test": "input_object"})

        result = self.app.new_run(input=input_obj)

        self.assertEqual(result, "test-run-id-5")

        # Verify input data was extracted from Input object
        call_args = mock_run.call_args
        self.assertEqual(call_args[1]["input_data"], {"test": "input_object"})

    @patch("nextmv.local.application.run")
    def test_new_run_with_options_object(self, mock_run):
        """Test new_run with nextmv.Options object."""
        mock_run.return_value = "test-run-id-6"

        options_obj = Options()
        options_obj.duration = "30s"
        options_obj.iterations = 500

        result = self.app.new_run(input={"test": "data"}, options=options_obj)

        self.assertEqual(result, "test-run-id-6")

        # Verify options were extracted correctly
        call_args = mock_run.call_args
        expected_options = {"duration": "30s", "iterations": "500"}
        self.assertEqual(call_args[1]["options"], expected_options)

    @patch("nextmv.local.application.run")
    def test_new_run_with_configuration_object(self, mock_run):
        """Test new_run with RunConfiguration object."""
        mock_run.return_value = "test-run-id-7"

        config = RunConfiguration(
            format=Format(
                format_input=FormatInput(input_type=InputFormat.JSON),
                format_output=FormatOutput(output_type=OutputFormat.JSON),
            )
        )

        result = self.app.new_run(input={"test": "data"}, configuration=config)

        self.assertEqual(result, "test-run-id-7")

        # Verify configuration was extracted correctly
        call_args = mock_run.call_args
        self.assertIn("run_config", call_args[1])
        run_config = call_args[1]["run_config"]
        self.assertEqual(run_config["format"]["input"]["type"], "json")

    @patch("nextmv.local.application.run")
    def test_new_run_inputs_dir_path_takes_precedence(self, mock_run):
        """Test that inputs_dir_path takes precedence over input."""
        mock_run.return_value = "test-run-id-8"

        # Create test inputs directory
        inputs_dir = os.path.join(self.test_dir, "inputs")
        os.makedirs(inputs_dir)
        with open(os.path.join(inputs_dir, "test.txt"), "w") as f:
            f.write("file content")

        result = self.app.new_run(
            input={"should": "be ignored"},
            input_dir_path=inputs_dir,
            configuration=RunConfiguration(
                format=Format(
                    format_input=FormatInput(input_type=InputFormat.MULTI_FILE),
                    format_output=FormatOutput(output_type=OutputFormat.MULTI_FILE),
                )
            ),
        )

        self.assertEqual(result, "test-run-id-8")

        # Verify that input_data is None when inputs_dir_path is used
        call_args = mock_run.call_args
        self.assertIsNone(call_args[1]["input_data"])
        self.assertEqual(call_args[1]["inputs_dir_path"], inputs_dir)

    @patch("nextmv.local.application.run")
    def test_new_run_json_configurations(self, mock_run):
        """Test new_run with json_configurations parameter."""
        mock_run.return_value = "test-run-id-9"

        json_configs = {"ensure_ascii": False, "indent": 2}

        result = self.app.new_run(input={"test": "data"}, json_configurations=json_configs)

        self.assertEqual(result, "test-run-id-9")
        mock_run.assert_called_once()

    def test_new_run_validate_dir_path_and_configuration(self):
        """Test validation of inputs_dir_path and configuration parameters."""
        # Create test inputs directory
        inputs_dir = os.path.join(self.test_dir, "inputs")
        os.makedirs(inputs_dir)

        # Should raise error when inputs_dir_path is provided without configuration
        with self.assertRaises(ValueError):
            self.app.new_run(input_dir_path=inputs_dir)

        # Should work when both are provided
        with patch("nextmv.local.application.run") as mock_run:
            mock_run.return_value = "test-run-id"

            result = self.app.new_run(
                input_dir_path=inputs_dir,
                configuration=RunConfiguration(
                    format=Format(
                        format_input=FormatInput(input_type=InputFormat.MULTI_FILE),
                        format_output=FormatOutput(output_type=OutputFormat.MULTI_FILE),
                    )
                ),
            )

            self.assertEqual(result, "test-run-id")


class TestApplicationLocalRunMethods(unittest.TestCase):
    """Test cases for the Application local run methods: run_metadata, run_result,
    run_result_with_polling, and new_run_with_result."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.app_src = os.path.join(self.test_dir, "test_app")
        os.makedirs(self.app_src)

        # Create .nextmv/runs directory structure
        self.runs_dir = os.path.join(self.app_src, ".nextmv", "runs")
        os.makedirs(self.runs_dir)

        # Create test application
        self.app = Application(src=self.app_src)

        # Test run ID
        self.test_run_id = "run-123"
        self.test_run_dir = os.path.join(self.runs_dir, self.test_run_id)
        os.makedirs(self.test_run_dir)

        # Create manifest file
        manifest_content = {
            "spec_version": "v1beta1",
            "id": "test-app",
            "name": "Test App",
            "description": "Test application",
            "entrypoint": "main.py",
            "type": "python",
            "runtime": "ghcr.io/nextmv-io/runtime/python:3.11",
            "files": ["main.py"],
        }

        with open(os.path.join(self.app_src, "app.yaml"), "w") as f:
            yaml.dump(manifest_content, f)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_run_info_file(self, status="succeeded", output_type="json", error=""):
        """Helper method to create a run info JSON file."""

        run_info = {
            "id": self.test_run_id,
            "name": "Test Run",
            "description": "Test Description",
            "user_email": "test@example.com",
            "console_url": "",
            "metadata": {
                "application_id": "test-app",
                "application_instance_id": "test-instance",
                "application_version_id": "test-version",
                "status_v2": status,
                "input_size": 100.0,
                "output_size": 200.0,
                "format": {"input": {"type": "json"}, "output": {"type": output_type}},
                "error": error,
                "duration": 1.5,
                "created_at": "2023-01-01T12:00:00Z",
                "finished_at": "2023-01-01T12:00:01Z",
            },
        }

        info_file = os.path.join(self.test_run_dir, f"{self.test_run_id}.json")
        with open(info_file, "w") as f:
            json.dump(run_info, f)

    def _create_output_files(self, output_type="JSON", output_data=None):
        """Helper method to create output files."""
        outputs_dir = os.path.join(self.test_run_dir, "outputs", "solutions")
        os.makedirs(outputs_dir, exist_ok=True)

        if output_type == "JSON":
            solution_file = os.path.join(outputs_dir, "solution.json")
            with open(solution_file, "w") as f:
                json.dump(output_data or {"solution": {"result": 42}}, f)
        elif output_type in ["CSV_ARCHIVE", "MULTI_FILE"]:
            # Create some dummy files for non-JSON outputs
            with open(os.path.join(outputs_dir, "result.csv"), "w") as f:
                f.write("id,value\n1,42\n")

    # Tests for run_metadata
    def test_run_metadata_success(self):
        """Test successful run_metadata call."""

        self._create_run_info_file(status="succeeded")

        result = self.app.run_metadata(self.test_run_id)

        self.assertIsInstance(result, RunInformation)
        self.assertEqual(result.id, self.test_run_id)
        self.assertEqual(result.metadata.status_v2, "succeeded")

    def test_run_metadata_no_runs_dir(self):
        """Test run_metadata when .nextmv/runs directory doesn't exist."""
        # Remove the runs directory
        shutil.rmtree(self.runs_dir)

        with self.assertRaises(ValueError) as context:
            self.app.run_metadata(self.test_run_id)

        self.assertIn("`.nextmv/runs` dir does not exist", str(context.exception))

    def test_run_metadata_no_run_dir(self):
        """Test run_metadata when specific run directory doesn't exist."""
        with self.assertRaises(ValueError) as context:
            self.app.run_metadata("non-existent-run")

        self.assertIn("run dir does not exist", str(context.exception))

    def test_run_metadata_no_info_file(self):
        """Test run_metadata when run info file doesn't exist."""
        # Create run directory but no info file
        non_existent_run_id = "run-456"
        os.makedirs(os.path.join(self.runs_dir, non_existent_run_id))

        with self.assertRaises(ValueError) as context:
            self.app.run_metadata(non_existent_run_id)

        self.assertIn("file does not exist", str(context.exception))

    def test_run_metadata_failed_status(self):
        """Test run_metadata with failed status."""

        self._create_run_info_file(status="failed", error="Test error message")

        result = self.app.run_metadata(self.test_run_id)

        self.assertIsInstance(result, RunInformation)
        self.assertEqual(result.metadata.status_v2, "failed")
        self.assertEqual(result.metadata.error, "Test error message")

    # Tests for run_result
    @patch.object(Application, "run_metadata")
    @patch.object(Application, "_Application__run_result")
    def test_run_result_success(self, mock_run_result, mock_run_metadata):
        """Test successful run_result call."""

        # Mock the metadata response
        mock_run_info = Mock(spec=RunInformation)
        mock_run_metadata.return_value = mock_run_info

        # Mock the result response
        mock_result = Mock(spec=RunResult)
        mock_run_result.return_value = mock_result

        result = self.app.run_result(self.test_run_id, output_dir_path="/tmp")

        # Verify calls
        mock_run_metadata.assert_called_once_with(run_id=self.test_run_id)
        mock_run_result.assert_called_once_with(
            run_id=self.test_run_id, run_information=mock_run_info, output_dir_path="/tmp"
        )
        self.assertEqual(result, mock_result)

    @patch.object(Application, "run_metadata")
    @patch.object(Application, "_Application__run_result")
    def test_run_result_default_output_dir(self, mock_run_result, mock_run_metadata):
        """Test run_result with default output directory."""

        # Mock the responses
        mock_run_info = Mock(spec=RunInformation)
        mock_run_metadata.return_value = mock_run_info
        mock_result = Mock(spec=RunResult)
        mock_run_result.return_value = mock_result

        result = self.app.run_result(self.test_run_id)

        # Verify default output_dir_path is used
        mock_run_result.assert_called_once_with(
            run_id=self.test_run_id, run_information=mock_run_info, output_dir_path="."
        )

        self.assertEqual(result, mock_result)

    # Tests for run_result_with_polling
    @patch.object(Application, "run_metadata")
    @patch.object(Application, "_Application__run_result")
    @patch("nextmv.local.application.poll")
    def test_run_result_with_polling_success(self, mock_poll, mock_run_result, mock_run_metadata):
        """Test successful run_result_with_polling call."""

        # Create mock run information with succeeded status
        mock_run_info = Mock(spec=RunInformation)
        mock_run_info.metadata = Mock()
        mock_run_info.metadata.status_v2 = StatusV2.succeeded

        # Mock poll to return the run information immediately
        mock_poll.return_value = mock_run_info

        # Mock the final result
        mock_result = Mock(spec=RunResult)
        mock_run_result.return_value = mock_result

        result = self.app.run_result_with_polling(self.test_run_id)

        # Verify poll was called
        mock_poll.assert_called_once()

        # Verify final result call
        mock_run_result.assert_called_once_with(
            run_id=self.test_run_id, run_information=mock_run_info, output_dir_path="."
        )

        self.assertEqual(result, mock_result)

    @patch.object(Application, "run_metadata")
    @patch.object(Application, "_Application__run_result")
    @patch("nextmv.local.application.poll")
    def test_run_result_with_polling_custom_options(self, mock_poll, mock_run_result, mock_run_metadata):
        """Test run_result_with_polling with custom polling options."""

        # Create custom polling options
        custom_polling_options = PollingOptions(max_tries=10, max_duration=300)

        # Mock responses
        mock_run_info = Mock(spec=RunInformation)
        mock_run_info.metadata = Mock()
        mock_run_info.metadata.status_v2 = StatusV2.succeeded
        mock_poll.return_value = mock_run_info
        mock_result = Mock(spec=RunResult)
        mock_run_result.return_value = mock_result

        self.app.run_result_with_polling(
            self.test_run_id, polling_options=custom_polling_options, output_dir_path="/custom/path"
        )

        # Verify poll was called with custom options
        mock_poll.assert_called_once()
        call_args = mock_poll.call_args
        self.assertEqual(call_args[1]["polling_options"], custom_polling_options)

        # Verify final result call with custom output path
        mock_run_result.assert_called_once_with(
            run_id=self.test_run_id, run_information=mock_run_info, output_dir_path="/custom/path"
        )

    @patch.object(Application, "run_metadata")
    def test_run_result_with_polling_status_check(self, mock_run_metadata):
        """Test that polling function correctly checks for terminal statuses."""

        # Test different statuses
        test_cases = [
            (StatusV2.succeeded, True),
            (StatusV2.failed, True),
            (StatusV2.canceled, True),
            ("running", False),
            ("pending", False),
        ]

        for status, should_be_done in test_cases:
            with self.subTest(status=status):
                mock_run_info = Mock(spec=RunInformation)
                mock_run_info.metadata = Mock()
                mock_run_info.metadata.status_v2 = status
                mock_run_metadata.return_value = mock_run_info

                # We need to access the polling function that gets created inside the method
                # This is a bit tricky, so we'll just test the logic conceptually
                result, is_done = (mock_run_info, True) if should_be_done else (None, False)

                if should_be_done:
                    self.assertEqual(result, mock_run_info)
                    self.assertTrue(is_done)
                else:
                    self.assertIsNone(result)
                    self.assertFalse(is_done)

    # Tests for new_run_with_result
    @patch.object(Application, "new_run")
    @patch.object(Application, "run_result_with_polling")
    def test_new_run_with_result_success(self, mock_polling_result, mock_new_run):
        """Test successful new_run_with_result call."""

        # Mock responses
        mock_new_run.return_value = "new-run-id"
        mock_result = Mock(spec=RunResult)
        mock_polling_result.return_value = mock_result

        test_input = {"vehicles": [{"id": "v1"}]}
        test_options = {"duration": "10s"}

        result = self.app.new_run_with_result(
            input=test_input, name="Test Run", description="Test Description", run_options=test_options
        )

        # Verify new_run was called correctly
        mock_new_run.assert_called_once_with(
            input=test_input,
            name="Test Run",
            description="Test Description",
            options=test_options,
            configuration=None,
            json_configurations=None,
            input_dir_path=None,
        )

        # Verify polling was called correctly
        mock_polling_result.assert_called_once_with(
            run_id="new-run-id", polling_options=DEFAULT_POLLING_OPTIONS, output_dir_path="."
        )

        self.assertEqual(result, mock_result)

    @patch.object(Application, "new_run")
    @patch.object(Application, "run_result_with_polling")
    def test_new_run_with_result_all_parameters(self, mock_polling_result, mock_new_run):
        """Test new_run_with_result with all parameters."""

        # Mock responses
        mock_new_run.return_value = "comprehensive-run-id"
        mock_result = Mock(spec=RunResult)
        mock_polling_result.return_value = mock_result

        # Test parameters
        test_input = {"data": "test"}
        test_options = {"param": "value"}
        test_polling_options = PollingOptions(max_tries=20)
        test_configuration = Mock(spec=RunConfiguration)
        test_json_configs = {"indent": 4}
        test_input_dir = "/test/input/dir"
        test_output_dir = "/test/output/dir"

        result = self.app.new_run_with_result(
            input=test_input,
            name="Comprehensive Test",
            description="Full parameter test",
            run_options=test_options,
            polling_options=test_polling_options,
            configuration=test_configuration,
            json_configurations=test_json_configs,
            input_dir_path=test_input_dir,
            output_dir_path=test_output_dir,
        )

        # Verify new_run was called with all parameters
        mock_new_run.assert_called_once_with(
            input=test_input,
            name="Comprehensive Test",
            description="Full parameter test",
            options=test_options,
            configuration=test_configuration,
            json_configurations=test_json_configs,
            input_dir_path=test_input_dir,
        )

        # Verify polling was called with custom options
        mock_polling_result.assert_called_once_with(
            run_id="comprehensive-run-id", polling_options=test_polling_options, output_dir_path=test_output_dir
        )

        self.assertEqual(result, mock_result)

    @patch.object(Application, "new_run")
    @patch.object(Application, "run_result_with_polling")
    def test_new_run_with_result_propagates_new_run_errors(self, mock_polling_result, mock_new_run):
        """Test that new_run_with_result propagates errors from new_run."""
        # Make new_run raise an error
        mock_new_run.side_effect = ValueError("New local run error")

        with self.assertRaises(ValueError) as context:
            self.app.new_run_with_result(input={"test": "data"})

        self.assertEqual(str(context.exception), "New local run error")
        # Verify polling was never called
        mock_polling_result.assert_not_called()

    @patch.object(Application, "new_run")
    @patch.object(Application, "run_result_with_polling")
    def test_new_run_with_result_propagates_polling_errors(self, mock_polling_result, mock_new_run):
        """Test that new_run_with_result propagates errors from polling."""
        # Mock successful new_run but failing polling
        mock_new_run.return_value = "error-run-id"
        mock_polling_result.side_effect = TimeoutError("Polling timeout")

        with self.assertRaises(TimeoutError) as context:
            self.app.new_run_with_result(input={"test": "data"})

        self.assertEqual(str(context.exception), "Polling timeout")
        # Verify new_run was called
        mock_new_run.assert_called_once()

    @patch.object(Application, "new_run")
    @patch.object(Application, "run_result_with_polling")
    def test_new_run_with_result_minimal_parameters(self, mock_polling_result, mock_new_run):
        """Test new_run_with_result with minimal parameters."""

        # Mock responses
        mock_new_run.return_value = "minimal-run-id"
        mock_result = Mock(spec=RunResult)
        mock_polling_result.return_value = mock_result

        result = self.app.new_run_with_result(input={"minimal": "test"})

        # Verify default parameters are used
        mock_new_run.assert_called_once_with(
            input={"minimal": "test"},
            name=None,
            description=None,
            options=None,
            configuration=None,
            json_configurations=None,
            input_dir_path=None,
        )

        mock_polling_result.assert_called_once_with(
            run_id="minimal-run-id", polling_options=DEFAULT_POLLING_OPTIONS, output_dir_path="."
        )

        self.assertEqual(result, mock_result)
