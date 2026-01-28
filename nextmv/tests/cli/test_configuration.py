"""
Unit tests for the nextmv configuration command.
"""

import os
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

from nextmv.cli.configuration.config import (
    API_KEY_KEY,
    CONFIG_DIR,
    CONFIG_FILE,
    DEFAULT_ENDPOINT,
    ENDPOINT_KEY,
    GO_CLI_PATH,
    load_config,
    obscure_api_key,
    save_config,
)
from nextmv.cli.main import app, go_cli_exists, remove_go_cli
from typer.testing import CliRunner


class TestConfigureCommand(unittest.TestCase):
    """Tests for the configure CLI command."""

    def setUp(self):
        self.runner = CliRunner()
        self.app = app
        self.test_api_key = "test_api_key_12345"
        self.test_profile = "test_profile"

        # Backup and clear NEXTMV_API_KEY env var if set, this is needed for
        # tests that check its absence.
        env_api_key = os.getenv("NEXTMV_API_KEY")
        self.env_api_key = env_api_key
        if env_api_key is not None:
            del os.environ["NEXTMV_API_KEY"]

    def tearDown(self):
        # Restore NEXTMV_API_KEY env var if it was set.
        if self.env_api_key is not None:
            os.environ["NEXTMV_API_KEY"] = self.env_api_key

    def test_configure_no_args_shows_error(self):
        """Test that running configuration create without arguments shows an error."""
        result = self.runner.invoke(self.app, ["configuration", "create"])
        self.assertEqual(result.exit_code, 2)

    @patch("nextmv.cli.configuration.create.save_config")
    @patch("nextmv.cli.configuration.create.load_config")
    def test_configure_default_profile(self, mock_load, mock_save):
        """Test configuring the default profile with an API key."""
        mock_load.return_value = {}

        result = self.runner.invoke(self.app, ["configuration", "create", "--api-key", self.test_api_key])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Configuration saved successfully", result.output)
        self.assertIn("Default", result.output)

        # Verify save was called with the correct config
        mock_save.assert_called_once()
        saved_config = mock_save.call_args[0][0]
        self.assertEqual(saved_config[API_KEY_KEY], self.test_api_key)
        self.assertEqual(saved_config[ENDPOINT_KEY], DEFAULT_ENDPOINT)

    @patch("nextmv.cli.configuration.create.save_config")
    @patch("nextmv.cli.configuration.create.load_config")
    def test_configure_named_profile(self, mock_load, mock_save):
        """Test configuring a named profile."""
        mock_load.return_value = {}

        result = self.runner.invoke(
            self.app, ["configuration", "create", "--api-key", self.test_api_key, "--profile", self.test_profile]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Configuration saved successfully", result.output)
        self.assertIn(self.test_profile, result.output)

        # Verify save was called with the correct config
        mock_save.assert_called_once()
        saved_config = mock_save.call_args[0][0]
        self.assertIn(self.test_profile, saved_config)
        self.assertEqual(saved_config[self.test_profile][API_KEY_KEY], self.test_api_key)

    @patch("nextmv.cli.configuration.create.save_config")
    @patch("nextmv.cli.configuration.create.load_config")
    def test_configure_reserved_profile_name_default(self, mock_load, mock_save):
        """Test that 'default' profile name is rejected."""
        mock_load.return_value = {}

        result = self.runner.invoke(
            self.app, ["configuration", "create", "--api-key", self.test_api_key, "--profile", "default"]
        )

        self.assertEqual(result.exit_code, 1)
        self.assertIn("reserved", result.output.lower())
        mock_save.assert_not_called()

    @patch("nextmv.cli.configuration.list.load_config")
    def test_profiles_empty(self, mock_load):
        """Test showing profiles when no configuration exists."""
        mock_load.return_value = {}

        result = self.runner.invoke(self.app, ["configuration", "list"])

        self.assertEqual(result.exit_code, 1)

    @patch("nextmv.cli.configuration.list.load_config")
    def test_show_profiles_with_config(self, mock_load):
        """Test showing profiles when configuration exists."""
        mock_load.return_value = {
            API_KEY_KEY: "default_key_123",
            ENDPOINT_KEY: DEFAULT_ENDPOINT,
            "custom_profile": {
                API_KEY_KEY: "custom_key_456",
                ENDPOINT_KEY: "custom.endpoint.com",
            },
        }

        result = self.runner.invoke(self.app, ["configuration", "list"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Default", result.output)
        self.assertIn("custom_profile", result.output)

    @patch("nextmv.cli.configuration.delete.save_config")
    @patch("nextmv.cli.configuration.delete.load_config")
    @patch("nextmv.cli.configuration.delete.get_confirmation", return_value=True)
    @patch("sys.stdin.isatty", return_value=True)
    def test_delete_profile(self, mock_isatty, mock_confirm, mock_load, mock_save):
        """Test deleting a profile."""
        mock_load.return_value = {
            API_KEY_KEY: "default_key",
            ENDPOINT_KEY: DEFAULT_ENDPOINT,
            self.test_profile: {
                API_KEY_KEY: "profile_key",
                ENDPOINT_KEY: DEFAULT_ENDPOINT,
            },
        }

        result = self.runner.invoke(self.app, ["configuration", "delete", "--profile", self.test_profile])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("deleted successfully", result.output)

        # Verify save was called with the profile removed
        mock_save.assert_called_once()
        saved_config = mock_save.call_args[0][0]
        self.assertNotIn(self.test_profile, saved_config)

    @patch("nextmv.cli.configuration.delete.load_config")
    def test_delete_nonexistent_profile(self, mock_load):
        """Test deleting a profile that doesn't exist."""
        mock_load.return_value = {
            API_KEY_KEY: "default_key",
            ENDPOINT_KEY: DEFAULT_ENDPOINT,
        }

        result = self.runner.invoke(self.app, ["configuration", "delete", "--profile", "nonexistent"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("does not exist", result.output)

    def test_delete_without_profile_shows_error(self):
        """Test that delete subcommand without --profile shows an error."""
        result = self.runner.invoke(self.app, ["configuration", "delete"])

        self.assertEqual(result.exit_code, 2)

    @patch("nextmv.cli.configuration.create.save_config")
    @patch("nextmv.cli.configuration.create.load_config")
    def test_configure_strips_https_from_endpoint(self, mock_load, mock_save):
        """Test that https:// is stripped from the endpoint."""
        mock_load.return_value = {}

        result = self.runner.invoke(
            self.app,
            ["configuration", "create", "--api-key", self.test_api_key, "--endpoint", "https://custom.api.com"],
        )

        self.assertEqual(result.exit_code, 0)

        # Verify the endpoint was saved without https://
        mock_save.assert_called_once()
        saved_config = mock_save.call_args[0][0]
        self.assertEqual(saved_config[ENDPOINT_KEY], "custom.api.com")


class TestObscureApiKey(unittest.TestCase):
    """Tests for the obscure_api_key helper function."""

    def test_obscure_short_key(self):
        """Test obscuring a short API key (4 chars or less)."""
        self.assertEqual(obscure_api_key("ab"), "**")
        self.assertEqual(obscure_api_key("abc"), "***")
        self.assertEqual(obscure_api_key("abcd"), "****")

    def test_obscure_normal_key(self):
        """Test obscuring a normal length API key."""
        result = obscure_api_key("abcdefghij")
        self.assertEqual(result, "ab****ij")
        self.assertEqual(len(result), 8)


class TestLoadConfig(unittest.TestCase):
    """Tests for the load_config helper function."""

    @patch.object(Path, "exists")
    def test_load_config_no_file(self, mock_exists):
        """Test loading config when file doesn't exist."""
        mock_exists.return_value = False

        result = load_config()
        self.assertEqual(result, {})

    @patch.object(Path, "open", mock_open(read_data="apikey: test_key\nendpoint: api.test.com\n"))
    @patch.object(Path, "exists")
    def test_load_config_with_file(self, mock_exists):
        """Test loading config from existing file."""
        mock_exists.return_value = True

        result = load_config()
        self.assertEqual(result[API_KEY_KEY], "test_key")
        self.assertEqual(result[ENDPOINT_KEY], "api.test.com")


class TestSaveConfig(unittest.TestCase):
    """Tests for the save_config helper function."""

    @patch.object(Path, "open", mock_open())
    @patch.object(Path, "mkdir")
    def test_save_config_creates_directory(self, mock_mkdir):
        """Test that save_config creates the config directory."""
        config = {API_KEY_KEY: "test_key", ENDPOINT_KEY: "api.test.com"}
        save_config(config)

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestConfigConstants(unittest.TestCase):
    """Tests for configuration constants."""

    def test_config_dir_is_in_home(self):
        """Test that CONFIG_DIR is in the home directory."""
        self.assertEqual(CONFIG_DIR.parent, Path.home())
        self.assertEqual(CONFIG_DIR.name, ".nextmv")

    def test_config_file_is_yaml(self):
        """Test that CONFIG_FILE is a yaml file."""
        self.assertEqual(CONFIG_FILE.suffix, ".yaml")
        self.assertEqual(CONFIG_FILE.name, "config.yaml")

    def test_default_endpoint(self):
        """Test the default endpoint value."""
        self.assertEqual(DEFAULT_ENDPOINT, "api.cloud.nextmv.io")


class TestGoCliExists(unittest.TestCase):
    """Tests for the go_cli_exists function."""

    @patch("nextmv.cli.main.warning")
    @patch.object(Path, "exists")
    def test_go_cli_exists_returns_true_when_file_exists(self, mock_exists, mock_warning):
        """Test that go_cli_exists returns True when the Go CLI file exists."""
        mock_exists.return_value = True

        result = go_cli_exists()

        self.assertTrue(result)

    @patch.object(Path, "exists")
    def test_go_cli_exists_returns_false_when_file_not_exists(self, mock_exists):
        """Test that go_cli_exists returns False when the Go CLI file does not exist."""
        mock_exists.return_value = False

        result = go_cli_exists()

        self.assertFalse(result)


class TestRemoveGoCli(unittest.TestCase):
    """Tests for the remove_go_cli function."""

    @patch("nextmv.cli.main.success")
    @patch.object(Path, "unlink")
    @patch.object(Path, "exists")
    def test_remove_go_cli_deletes_file_when_exists(self, mock_exists, mock_unlink, mock_success):
        """Test that remove_go_cli deletes the file when it exists."""
        mock_exists.return_value = True

        remove_go_cli()

        mock_unlink.assert_called_once()

    @patch.object(Path, "unlink")
    @patch.object(Path, "exists")
    def test_remove_go_cli_does_not_delete_when_not_exists(self, mock_exists, mock_unlink):
        """Test that remove_go_cli does not attempt to delete when file does not exist."""
        mock_exists.return_value = False

        remove_go_cli()

        mock_unlink.assert_not_called()


class TestGoCliPath(unittest.TestCase):
    """Tests for the GO_CLI_PATH constant."""

    def test_go_cli_path_is_in_config_dir(self):
        """Test that GO_CLI_PATH is inside CONFIG_DIR."""
        self.assertEqual(GO_CLI_PATH.parent, CONFIG_DIR)
        self.assertEqual(GO_CLI_PATH.name, "nextmv")


if __name__ == "__main__":
    unittest.main()
