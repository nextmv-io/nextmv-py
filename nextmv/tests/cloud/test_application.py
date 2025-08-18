import os
import tempfile
import unittest
from typing import Any
from unittest.mock import Mock

from nextmv.cloud.application import Application, PollingOptions, poll
from nextmv.cloud.client import Client


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
