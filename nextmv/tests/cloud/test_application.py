import os
import tempfile
import unittest
from typing import Any
from unittest.mock import Mock, patch

from nextmv.cloud.application import Application, PollingOptions, poll
from nextmv.cloud.client import Client
from nextmv.cloud.run import Format, FormatInput, FormatOutput, RunConfiguration
from nextmv.input import InputFormat
from nextmv.output import OutputFormat


# This is a dummy function to avoid actually sleeping during tests.
def no_sleep(value: float) -> None:
    return


class TestApplication(unittest.TestCase):
    def test_poll(self):
        counter = 0

        def polling_func() -> tuple[Any, bool]:
            nonlocal counter
            counter += 1

            if counter < 4:
                return "result", False

            return "result", True

        polling_options = PollingOptions()

        result = poll(polling_options, polling_func, no_sleep)

        self.assertEqual(result, "result")

    def test_initialize(self):
        """Test the Application.initialize method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            app_name = "test-app"
            app_id = "test-app-id"
            description = "Test application"

            # Mock client
            mock_client = Mock(spec=Client)

            # Initialize the application
            app = Application.initialize(
                name=app_name,
                id=app_id,
                description=description,
                destination=temp_dir,
                client=mock_client,
            )

            # Verify the application object
            self.assertEqual(app.id, app_id)
            self.assertEqual(app.client, mock_client)
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

                app_name = "default-test-app"

                # Initialize with minimal parameters
                app = Application.initialize(name=app_name)

                # Verify the application object has generated ID
                self.assertIsNotNone(app.id)
                self.assertIsNone(app.client)
                self.assertIsNone(app.description)  # description should be None when not provided
                # Use the current working directory for comparison since that's where the app is created
                expected_src_path = os.path.join(os.getcwd(), app_name)
                self.assertEqual(app.src, expected_src_path)

                # Verify the directory structure was created in current directory
                app_dir = os.path.join(temp_dir, app_name)
                self.assertTrue(os.path.exists(app_dir))
                self.assertTrue(os.path.isdir(app_dir))

                # Verify basic structure exists
                self.assertTrue(os.path.exists(os.path.join(app_dir, "app.yaml")))
                self.assertTrue(os.path.exists(os.path.join(app_dir, "src")))

            finally:
                os.chdir(original_cwd)

    def test_initialize_existing_directory(self):
        """Test that initialize works when the directory already exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            app_name = "existing-app"
            app_dir = os.path.join(temp_dir, app_name)

            # Pre-create the directory
            os.makedirs(app_dir, exist_ok=True)

            # Initialize should still work
            app = Application.initialize(
                name=app_name,
                destination=temp_dir,
            )

            # Verify the application was created successfully
            self.assertIsNotNone(app.id)
            self.assertIsNone(app.description)  # description should be None when not provided
            self.assertEqual(app.src, app_dir)
            self.assertTrue(os.path.exists(app_dir))
            self.assertTrue(os.path.exists(os.path.join(app_dir, "app.yaml")))

    def test_poll_stop_callback(self):
        counter = 0

        # The polling func would stop after 9 calls.
        def polling_func() -> tuple[Any, bool]:
            nonlocal counter
            counter += 1

            if counter < 10:
                return "result", False

            return "result", True

        # The stop callback makes sure that the polling stops sooner, after 3
        # calls.
        def stop() -> bool:
            if counter == 3:
                return True

        polling_options = PollingOptions(stop=stop)

        result = poll(polling_options, polling_func, no_sleep)

        self.assertIsNone(result)

    def test_poll_long(self):
        counter = 0
        max_tries = 1000000

        def polling_func() -> tuple[Any, bool]:
            nonlocal counter
            counter += 1

            if counter < max_tries:
                return "result", False

            return "result", True

        polling_options = PollingOptions(
            max_tries=max_tries + 1,
        )

        result = poll(polling_options, polling_func, no_sleep)

        self.assertEqual(result, "result")


class TestApplicationNewLocalRun(unittest.TestCase):
    """Test cases for the Application.new_local_run method."""

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
            import yaml

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
        self.app = Application(id="test-app", client=Mock(spec=Client), src=self.app_src)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch("nextmv.cloud.application.run")
    def test_new_local_run_basic(self, mock_run):
        """Test basic new_local_run functionality."""
        mock_run.return_value = "test-run-id"

        result = self.app.new_local_run(input={"test": "input"}, options={"duration": "10s"})

        self.assertEqual(result, "test-run-id")
        mock_run.assert_called_once()

        # Verify the call arguments
        call_args = mock_run.call_args
        self.assertEqual(call_args[1]["src"], self.app_src)
        self.assertIn("manifest", call_args[1])
        self.assertIn("run_config", call_args[1])
        self.assertEqual(call_args[1]["input_data"], {"test": "input"})
        self.assertEqual(call_args[1]["options"], {"duration": "10s"})

    @patch("nextmv.cloud.application.run")
    def test_new_local_run_with_inputs_dir_path(self, mock_run):
        """Test new_local_run with inputs directory path."""
        mock_run.return_value = "test-run-id-2"

        # Create test inputs directory
        inputs_dir = os.path.join(self.test_dir, "inputs")
        os.makedirs(inputs_dir)
        with open(os.path.join(inputs_dir, "data.csv"), "w") as f:
            f.write("col1,col2\nval1,val2\n")

        result = self.app.new_local_run(
            inputs_dir_path=inputs_dir,
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

    @patch("nextmv.cloud.application.run")
    def test_new_local_run_with_dict_input(self, mock_run):
        """Test new_local_run with dictionary input."""
        mock_run.return_value = "test-run-id-3"

        input_data = {"vehicles": [{"id": 1, "capacity": 100}]}

        result = self.app.new_local_run(input=input_data)

        self.assertEqual(result, "test-run-id-3")

        # Verify input_data was extracted correctly
        call_args = mock_run.call_args
        self.assertEqual(call_args[1]["input_data"], input_data)

    @patch("nextmv.cloud.application.run")
    def test_new_local_run_with_string_input(self, mock_run):
        """Test new_local_run with string input."""
        mock_run.return_value = "test-run-id-4"

        input_data = "raw text input"

        result = self.app.new_local_run(input=input_data)

        self.assertEqual(result, "test-run-id-4")

        # Verify input_data was passed as string
        call_args = mock_run.call_args
        self.assertEqual(call_args[1]["input_data"], input_data)

    def test_new_local_run_no_src_error(self):
        """Test new_local_run raises error when src is not set."""
        app = Application(id="test-app", client=Mock(spec=Client))

        with self.assertRaises(ValueError) as context:
            app.new_local_run(input={"test": "data"})

        self.assertIn("`src` property for the `Application` must be specified", str(context.exception))

    def test_new_local_run_no_input_error(self):
        """Test new_local_run raises error when neither input nor inputs_dir_path is provided."""
        with self.assertRaises(ValueError) as context:
            self.app.new_local_run()

        self.assertIn("Either `input` or `input_directory` must be specified", str(context.exception))

    def test_new_local_run_manifest_not_found_error(self):
        """Test new_local_run raises error when manifest.yaml is not found."""
        # Remove the manifest file
        os.remove(os.path.join(self.app_src, "app.yaml"))

        with self.assertRaises(FileNotFoundError) as context:
            self.app.new_local_run(input={"test": "data"})

        self.assertIn("Could not find manifest.yaml", str(context.exception))

    @patch("nextmv.cloud.application.run")
    def test_new_local_run_with_nextmv_input_object(self, mock_run):
        """Test new_local_run with nextmv.Input object."""
        mock_run.return_value = "test-run-id-5"

        from nextmv import Input

        input_obj = Input(data={"test": "input_object"})

        result = self.app.new_local_run(input=input_obj)

        self.assertEqual(result, "test-run-id-5")

        # Verify input data was extracted from Input object
        call_args = mock_run.call_args
        self.assertEqual(call_args[1]["input_data"], {"test": "input_object"})

    @patch("nextmv.cloud.application.run")
    def test_new_local_run_with_options_object(self, mock_run):
        """Test new_local_run with nextmv.Options object."""
        mock_run.return_value = "test-run-id-6"

        from nextmv import Options

        options_obj = Options()
        options_obj.duration = "30s"
        options_obj.iterations = 500

        result = self.app.new_local_run(input={"test": "data"}, options=options_obj)

        self.assertEqual(result, "test-run-id-6")

        # Verify options were extracted correctly
        call_args = mock_run.call_args
        expected_options = {"duration": "30s", "iterations": "500"}
        self.assertEqual(call_args[1]["options"], expected_options)

    @patch("nextmv.cloud.application.run")
    def test_new_local_run_with_configuration_object(self, mock_run):
        """Test new_local_run with RunConfiguration object."""
        mock_run.return_value = "test-run-id-7"

        from nextmv.cloud.run import Format, FormatInput, FormatOutput, RunConfiguration
        from nextmv.input import InputFormat
        from nextmv.output import OutputFormat

        config = RunConfiguration(
            format=Format(
                format_input=FormatInput(input_type=InputFormat.JSON),
                format_output=FormatOutput(output_type=OutputFormat.JSON),
            )
        )

        result = self.app.new_local_run(input={"test": "data"}, configuration=config)

        self.assertEqual(result, "test-run-id-7")

        # Verify configuration was extracted correctly
        call_args = mock_run.call_args
        self.assertIn("run_config", call_args[1])
        run_config = call_args[1]["run_config"]
        self.assertEqual(run_config["format"]["input"]["type"], "json")

    @patch("nextmv.cloud.application.run")
    def test_new_local_run_inputs_dir_path_takes_precedence(self, mock_run):
        """Test that inputs_dir_path takes precedence over input."""
        mock_run.return_value = "test-run-id-8"

        # Create test inputs directory
        inputs_dir = os.path.join(self.test_dir, "inputs")
        os.makedirs(inputs_dir)
        with open(os.path.join(inputs_dir, "test.txt"), "w") as f:
            f.write("file content")

        result = self.app.new_local_run(
            input={"should": "be ignored"},
            inputs_dir_path=inputs_dir,
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

    @patch("nextmv.cloud.application.run")
    def test_new_local_run_json_configurations(self, mock_run):
        """Test new_local_run with json_configurations parameter."""
        mock_run.return_value = "test-run-id-9"

        json_configs = {"ensure_ascii": False, "indent": 2}

        result = self.app.new_local_run(input={"test": "data"}, json_configurations=json_configs)

        self.assertEqual(result, "test-run-id-9")
        mock_run.assert_called_once()

    def test_new_local_run_validate_dir_path_and_configuration(self):
        """Test validation of inputs_dir_path and configuration parameters."""
        # Create test inputs directory
        inputs_dir = os.path.join(self.test_dir, "inputs")
        os.makedirs(inputs_dir)

        # Should raise error when inputs_dir_path is provided without configuration
        with self.assertRaises(ValueError):
            self.app.new_local_run(inputs_dir_path=inputs_dir)

        # Should work when both are provided
        with patch("nextmv.cloud.application.run") as mock_run:
            mock_run.return_value = "test-run-id"

            result = self.app.new_local_run(
                inputs_dir_path=inputs_dir,
                configuration=RunConfiguration(
                    format=Format(
                        format_input=FormatInput(input_type=InputFormat.MULTI_FILE),
                        format_output=FormatOutput(output_type=OutputFormat.MULTI_FILE),
                    )
                ),
            )

            self.assertEqual(result, "test-run-id")
