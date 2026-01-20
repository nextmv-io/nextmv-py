"""
Unit tests for the nextmv cloud input-set CLI commands.
"""

import json
import tempfile
import unittest
from unittest.mock import Mock, patch

from nextmv.cli.cloud import app as cloud_app
from nextmv.cli.cloud.input_set import app as input_set_app
from nextmv.cli.cloud.input_set.create import app as create_app
from nextmv.cli.cloud.input_set.get import app as get_app
from nextmv.cli.cloud.input_set.list import app as list_app
from nextmv.cli.cloud.input_set.update import app as update_app
from typer.testing import CliRunner


class TestInputSetCreateCommand(unittest.TestCase):
    """Tests for the input-set create command."""

    def setUp(self):
        self.runner = CliRunner()
        self.app = create_app
        self.sample_response = {
            "id": "input-set-123",
            "name": "My Input Set",
            "description": "Test description",
            "input_ids": ["input-1", "input-2"],
            "created_at": "2024-01-15T00:00:00Z",
            "updated_at": "2024-01-15T00:00:00Z",
            "inputs": [],
        }

    @patch("nextmv.cli.cloud.input_set.create.build_client")
    def test_create_minimal(self, mock_build_client):
        """Test creating an input set with minimal options."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = self.sample_response
        mock_client.request.return_value = mock_response
        mock_build_client.return_value = mock_client

        result = self.runner.invoke(self.app, ["--app-id", "my-app", "--name", "My Input Set"])

        self.assertEqual(result.exit_code, 0)
        mock_build_client.assert_called_once_with(None)
        mock_client.request.assert_called_once_with(
            method="POST",
            endpoint="/v1/applications/my-app/experiments/inputsets",
            payload={"name": "My Input Set"},
        )

    @patch("nextmv.cli.cloud.input_set.create.build_client")
    def test_create_with_all_options(self, mock_build_client):
        """Test creating an input set with all options."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = self.sample_response
        mock_client.request.return_value = mock_response
        mock_build_client.return_value = mock_client

        result = self.runner.invoke(
            self.app,
            [
                "--app-id",
                "my-app",
                "--name",
                "My Input Set",
                "--input-set-id",
                "custom-id",
                "--description",
                "Test description",
                "--instance-id",
                "my-instance",
                "--run-ids",
                "run-1,run-2,run-3",
                "--start-time",
                "2024-01-01T00:00:00Z",
                "--end-time",
                "2024-01-31T23:59:59Z",
                "--limit",
                "10",
            ],
        )

        self.assertEqual(result.exit_code, 0)
        expected_payload = {
            "name": "My Input Set",
            "id": "custom-id",
            "description": "Test description",
            "instance_id": "my-instance",
            "run_ids": ["run-1", "run-2", "run-3"],
            "start_time": "2024-01-01T00:00:00Z",
            "end_time": "2024-01-31T23:59:59Z",
            "maximum_runs": 10,
        }
        mock_client.request.assert_called_once_with(
            method="POST",
            endpoint="/v1/applications/my-app/experiments/inputsets",
            payload=expected_payload,
        )

    @patch("nextmv.cli.cloud.input_set.create.build_client")
    def test_create_with_output_file(self, mock_build_client):
        """Test creating an input set and saving to a file."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = self.sample_response
        mock_client.request.return_value = mock_response
        mock_build_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_path = f.name

        result = self.runner.invoke(
            self.app,
            ["--app-id", "my-app", "--name", "My Input Set", "--output", output_path],
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("saved to", result.output)

        with open(output_path) as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, self.sample_response)

    @patch("nextmv.cli.cloud.input_set.create.build_client")
    def test_create_with_profile(self, mock_build_client):
        """Test creating an input set with a profile."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = self.sample_response
        mock_client.request.return_value = mock_response
        mock_build_client.return_value = mock_client

        result = self.runner.invoke(
            self.app,
            ["--app-id", "my-app", "--name", "My Input Set", "--profile", "test-profile"],
        )

        self.assertEqual(result.exit_code, 0)
        mock_build_client.assert_called_once_with("test-profile")

    def test_create_requires_app_id(self):
        """Test that create command requires app_id."""
        result = self.runner.invoke(self.app, ["--name", "My Input Set"])

        self.assertNotEqual(result.exit_code, 0)

    def test_create_requires_name(self):
        """Test that create command requires name."""
        result = self.runner.invoke(self.app, ["--app-id", "my-app"])

        self.assertNotEqual(result.exit_code, 0)


class TestInputSetGetCommand(unittest.TestCase):
    """Tests for the input-set get command."""

    def setUp(self):
        self.runner = CliRunner()
        self.app = get_app
        self.sample_response = {
            "id": "input-set-123",
            "name": "My Input Set",
            "description": "Test description",
            "input_ids": ["input-1", "input-2"],
            "created_at": "2024-01-15T00:00:00Z",
            "updated_at": "2024-01-15T00:00:00Z",
            "inputs": [
                {"id": "input-1", "name": "Input 1"},
                {"id": "input-2", "name": "Input 2"},
            ],
        }

    @patch("nextmv.cli.cloud.input_set.get.build_client")
    def test_get_input_set(self, mock_build_client):
        """Test getting an input set."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = self.sample_response
        mock_client.request.return_value = mock_response
        mock_build_client.return_value = mock_client

        result = self.runner.invoke(
            self.app,
            ["--app-id", "my-app", "--input-set-id", "input-set-123"],
        )

        self.assertEqual(result.exit_code, 0)
        mock_client.request.assert_called_once_with(
            method="GET",
            endpoint="/v1/applications/my-app/experiments/inputsets/input-set-123",
        )

    @patch("nextmv.cli.cloud.input_set.get.build_client")
    def test_get_with_output_file(self, mock_build_client):
        """Test getting an input set and saving to a file."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = self.sample_response
        mock_client.request.return_value = mock_response
        mock_build_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_path = f.name

        result = self.runner.invoke(
            self.app,
            ["--app-id", "my-app", "--input-set-id", "input-set-123", "--output", output_path],
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("saved to", result.output)

        with open(output_path) as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, self.sample_response)

    @patch("nextmv.cli.cloud.input_set.get.build_client")
    def test_get_with_profile(self, mock_build_client):
        """Test getting an input set with a profile."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = self.sample_response
        mock_client.request.return_value = mock_response
        mock_build_client.return_value = mock_client

        result = self.runner.invoke(
            self.app,
            ["--app-id", "my-app", "--input-set-id", "input-set-123", "--profile", "test-profile"],
        )

        self.assertEqual(result.exit_code, 0)
        mock_build_client.assert_called_once_with("test-profile")

    def test_get_requires_app_id(self):
        """Test that get command requires app_id."""
        result = self.runner.invoke(self.app, ["--input-set-id", "input-set-123"])

        self.assertNotEqual(result.exit_code, 0)

    def test_get_requires_input_set_id(self):
        """Test that get command requires input_set_id."""
        result = self.runner.invoke(self.app, ["--app-id", "my-app"])

        self.assertNotEqual(result.exit_code, 0)


class TestInputSetListCommand(unittest.TestCase):
    """Tests for the input-set list command."""

    def setUp(self):
        self.runner = CliRunner()
        self.app = list_app
        self.sample_response = {
            "input": [
                {
                    "id": "input-set-1",
                    "name": "Input Set 1",
                    "description": "First input set",
                    "input_ids": ["input-1"],
                    "created_at": "2024-01-15T00:00:00Z",
                    "updated_at": "2024-01-15T00:00:00Z",
                },
                {
                    "id": "input-set-2",
                    "name": "Input Set 2",
                    "description": "Second input set",
                    "input_ids": ["input-2", "input-3"],
                    "created_at": "2024-01-16T00:00:00Z",
                    "updated_at": "2024-01-16T00:00:00Z",
                },
            ]
        }

    @patch("nextmv.cli.cloud.input_set.list.build_client")
    def test_list_input_sets(self, mock_build_client):
        """Test listing input sets."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = self.sample_response
        mock_client.request.return_value = mock_response
        mock_build_client.return_value = mock_client

        result = self.runner.invoke(self.app, ["--app-id", "my-app"])

        self.assertEqual(result.exit_code, 0)
        mock_client.request.assert_called_once_with(
            method="GET",
            endpoint="/v1/applications/my-app/experiments/inputsets",
        )

    @patch("nextmv.cli.cloud.input_set.list.build_client")
    def test_list_with_output_file(self, mock_build_client):
        """Test listing input sets and saving to a file."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = self.sample_response
        mock_client.request.return_value = mock_response
        mock_build_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_path = f.name

        result = self.runner.invoke(self.app, ["--app-id", "my-app", "--output", output_path])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("saved to", result.output)

        with open(output_path) as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, self.sample_response)

    @patch("nextmv.cli.cloud.input_set.list.build_client")
    def test_list_with_profile(self, mock_build_client):
        """Test listing input sets with a profile."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = self.sample_response
        mock_client.request.return_value = mock_response
        mock_build_client.return_value = mock_client

        result = self.runner.invoke(self.app, ["--app-id", "my-app", "--profile", "test-profile"])

        self.assertEqual(result.exit_code, 0)
        mock_build_client.assert_called_once_with("test-profile")

    def test_list_requires_app_id(self):
        """Test that list command requires app_id."""
        result = self.runner.invoke(self.app, [])

        self.assertNotEqual(result.exit_code, 0)


class TestInputSetUpdateCommand(unittest.TestCase):
    """Tests for the input-set update command."""

    def setUp(self):
        self.runner = CliRunner()
        self.app = update_app
        self.sample_response = {
            "id": "input-set-123",
            "name": "Updated Name",
            "description": "Updated description",
            "input_ids": ["input-1", "input-2"],
            "created_at": "2024-01-15T00:00:00Z",
            "updated_at": "2024-01-16T00:00:00Z",
            "inputs": [],
        }

    @patch("nextmv.cli.cloud.input_set.update.build_client")
    def test_update_name(self, mock_build_client):
        """Test updating an input set's name."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = self.sample_response
        mock_client.request.return_value = mock_response
        mock_build_client.return_value = mock_client

        result = self.runner.invoke(
            self.app,
            ["--app-id", "my-app", "--input-set-id", "input-set-123", "--name", "Updated Name"],
        )

        self.assertEqual(result.exit_code, 0)
        mock_client.request.assert_called_once_with(
            method="PUT",
            endpoint="/v1/applications/my-app/experiments/inputsets/input-set-123",
            payload={"name": "Updated Name"},
        )

    @patch("nextmv.cli.cloud.input_set.update.build_client")
    def test_update_description(self, mock_build_client):
        """Test updating an input set's description."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = self.sample_response
        mock_client.request.return_value = mock_response
        mock_build_client.return_value = mock_client

        result = self.runner.invoke(
            self.app,
            [
                "--app-id",
                "my-app",
                "--input-set-id",
                "input-set-123",
                "--description",
                "Updated description",
            ],
        )

        self.assertEqual(result.exit_code, 0)
        mock_client.request.assert_called_once_with(
            method="PUT",
            endpoint="/v1/applications/my-app/experiments/inputsets/input-set-123",
            payload={"description": "Updated description"},
        )

    @patch("nextmv.cli.cloud.input_set.update.build_client")
    def test_update_both(self, mock_build_client):
        """Test updating both name and description."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = self.sample_response
        mock_client.request.return_value = mock_response
        mock_build_client.return_value = mock_client

        result = self.runner.invoke(
            self.app,
            [
                "--app-id",
                "my-app",
                "--input-set-id",
                "input-set-123",
                "--name",
                "Updated Name",
                "--description",
                "Updated description",
            ],
        )

        self.assertEqual(result.exit_code, 0)
        mock_client.request.assert_called_once_with(
            method="PUT",
            endpoint="/v1/applications/my-app/experiments/inputsets/input-set-123",
            payload={"name": "Updated Name", "description": "Updated description"},
        )

    @patch("nextmv.cli.cloud.input_set.update.build_client")
    def test_update_with_output_file(self, mock_build_client):
        """Test updating an input set and saving to a file."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = self.sample_response
        mock_client.request.return_value = mock_response
        mock_build_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_path = f.name

        result = self.runner.invoke(
            self.app,
            [
                "--app-id",
                "my-app",
                "--input-set-id",
                "input-set-123",
                "--name",
                "Updated Name",
                "--output",
                output_path,
            ],
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("saved to", result.output)

        with open(output_path) as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, self.sample_response)

    def test_update_requires_at_least_one_option(self):
        """Test that update command requires at least one option to update."""
        result = self.runner.invoke(
            self.app,
            ["--app-id", "my-app", "--input-set-id", "input-set-123"],
        )

        self.assertEqual(result.exit_code, 1)
        self.assertIn("--name", result.output)
        self.assertIn("--description", result.output)

    def test_update_requires_app_id(self):
        """Test that update command requires app_id."""
        result = self.runner.invoke(
            self.app,
            ["--input-set-id", "input-set-123", "--name", "Updated Name"],
        )

        self.assertNotEqual(result.exit_code, 0)

    def test_update_requires_input_set_id(self):
        """Test that update command requires input_set_id."""
        result = self.runner.invoke(
            self.app,
            ["--app-id", "my-app", "--name", "Updated Name"],
        )

        self.assertNotEqual(result.exit_code, 0)


class TestCloudCommand(unittest.TestCase):
    """Tests for the main cloud command."""

    def setUp(self):
        self.runner = CliRunner()
        self.app = cloud_app

    def test_cloud_help_shows_description(self):
        """Test that cloud command shows help description."""
        result = self.runner.invoke(self.app, ["--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("cloud", result.output.lower())

    def test_cloud_input_set_subcommand_registered(self):
        """Test that input-set subcommand is registered."""
        result = self.runner.invoke(self.app, ["--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("input-set", result.output)


class TestInputSetCommand(unittest.TestCase):
    """Tests for the input-set command."""

    def setUp(self):
        self.runner = CliRunner()
        self.app = input_set_app

    def test_input_set_help_shows_description(self):
        """Test that input-set command shows help description."""
        result = self.runner.invoke(self.app, ["--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("input set", result.output.lower())

    def test_input_set_subcommands_registered(self):
        """Test that all input-set subcommands are registered."""
        result = self.runner.invoke(self.app, ["--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("create", result.output)
        self.assertIn("get", result.output)
        self.assertIn("list", result.output)
        self.assertIn("update", result.output)


if __name__ == "__main__":
    unittest.main()
