"""
Unit tests for the nextmv community CLI commands.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, mock_open, patch

from nextmv.cli.community import app as community_app
from nextmv.cli.community.clone import app as clone_app
from nextmv.cli.community.clone import app_has_version, download_object, get_valid_path
from nextmv.cli.community.list import app as list_app
from nextmv.cli.community.list import (
    apps_list,
    apps_table,
    download_file,
    download_manifest,
    find_app,
    versions_list,
    versions_table,
)
from typer.testing import CliRunner


class TestCommunityListCommand(unittest.TestCase):
    """Tests for the community list command."""

    def setUp(self):
        self.runner = CliRunner()
        self.app = list_app
        self.sample_manifest = {
            "apps": [
                {
                    "name": "go-nextroute",
                    "type": "go",
                    "latest_app_version": "v1.2.0",
                    "description": "A routing app",
                    "app_versions": ["v1.2.0", "v1.1.0", "v1.0.0"],
                },
                {
                    "name": "python-knapsack",
                    "type": "python",
                    "latest_app_version": "v2.0.0",
                    "description": "A knapsack solver",
                    "app_versions": ["v2.0.0", "v1.5.0"],
                },
            ]
        }

    @patch("nextmv.cli.community.list.download_manifest")
    @patch("nextmv.cli.community.list.apps_table")
    def test_list_default_shows_apps_table(self, mock_apps_table, mock_download_manifest):
        """Test that list without flags shows apps table."""
        mock_download_manifest.return_value = self.sample_manifest

        result = self.runner.invoke(self.app, [])

        self.assertEqual(result.exit_code, 0)
        mock_download_manifest.assert_called_once_with(profile=None)
        mock_apps_table.assert_called_once_with(self.sample_manifest)

    @patch("nextmv.cli.community.list.download_manifest")
    @patch("nextmv.cli.community.list.apps_list")
    def test_list_flat_shows_apps_list(self, mock_apps_list, mock_download_manifest):
        """Test that list with --flat flag shows apps list."""
        mock_download_manifest.return_value = self.sample_manifest

        result = self.runner.invoke(self.app, ["--flat"])

        self.assertEqual(result.exit_code, 0)
        mock_download_manifest.assert_called_once_with(profile=None)
        mock_apps_list.assert_called_once_with(self.sample_manifest)

    @patch("nextmv.cli.community.list.download_manifest")
    @patch("nextmv.cli.community.list.versions_table")
    def test_list_with_app_shows_versions_table(self, mock_versions_table, mock_download_manifest):
        """Test that list with --app flag shows versions table."""
        mock_download_manifest.return_value = self.sample_manifest

        result = self.runner.invoke(self.app, ["--app", "go-nextroute"])

        self.assertEqual(result.exit_code, 0)
        mock_download_manifest.assert_called_once_with(profile=None)
        mock_versions_table.assert_called_once_with(self.sample_manifest, "go-nextroute")

    @patch("nextmv.cli.community.list.download_manifest")
    @patch("nextmv.cli.community.list.versions_list")
    def test_list_with_app_and_flat_shows_versions_list(self, mock_versions_list, mock_download_manifest):
        """Test that list with --app and --flat flags shows versions list."""
        mock_download_manifest.return_value = self.sample_manifest

        result = self.runner.invoke(self.app, ["--app", "go-nextroute", "--flat"])

        self.assertEqual(result.exit_code, 0)
        mock_download_manifest.assert_called_once_with(profile=None)
        mock_versions_list.assert_called_once_with(self.sample_manifest, "go-nextroute")

    @patch("nextmv.cli.community.list.download_manifest")
    def test_list_with_empty_app_string_errors(self, mock_download_manifest):
        """Test that list with empty --app string returns error."""
        mock_download_manifest.return_value = self.sample_manifest

        result = self.runner.invoke(self.app, ["--app", ""])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("cannot be an empty string", result.output)

    @patch("nextmv.cli.community.list.download_manifest")
    @patch("nextmv.cli.community.list.apps_table")
    def test_list_with_profile(self, mock_apps_table, mock_download_manifest):
        """Test that list with --profile flag passes profile to download_manifest."""
        mock_download_manifest.return_value = self.sample_manifest

        result = self.runner.invoke(self.app, ["--profile", "test-profile"])

        self.assertEqual(result.exit_code, 0)
        mock_download_manifest.assert_called_once_with(profile="test-profile")


class TestDownloadManifest(unittest.TestCase):
    """Tests for the download_manifest function."""

    @patch("nextmv.cli.community.list.download_file")
    @patch("nextmv.cli.community.list.yaml.safe_load")
    def test_download_manifest_success(self, mock_yaml_load, mock_download_file):
        """Test successful manifest download."""
        mock_response = Mock()
        mock_response.text = "apps: []"
        mock_download_file.return_value = mock_response
        mock_yaml_load.return_value = {"apps": []}

        result = download_manifest()

        mock_download_file.assert_called_once_with(directory="community-apps", file="manifest.yml", profile=None)
        mock_yaml_load.assert_called_once_with("apps: []")
        self.assertEqual(result, {"apps": []})

    @patch("nextmv.cli.community.list.download_file")
    @patch("nextmv.cli.community.list.yaml.safe_load")
    def test_download_manifest_with_profile(self, mock_yaml_load, mock_download_file):
        """Test manifest download with custom profile."""
        mock_response = Mock()
        mock_response.text = "apps: []"
        mock_download_file.return_value = mock_response
        mock_yaml_load.return_value = {"apps": []}

        _ = download_manifest(profile="custom-profile")

        mock_download_file.assert_called_once_with(
            directory="community-apps", file="manifest.yml", profile="custom-profile"
        )


class TestAppsTable(unittest.TestCase):
    """Tests for the apps_table function."""

    @patch("nextmv.cli.community.list.console")
    def test_apps_table_prints_table(self, mock_console):
        """Test that apps_table prints a table with correct data."""
        manifest = {
            "apps": [
                {
                    "name": "test-app",
                    "type": "go",
                    "latest_app_version": "v1.0.0",
                    "description": "Test description",
                }
            ]
        }

        apps_table(manifest)

        # Verify console.print was called
        self.assertEqual(mock_console.print.call_count, 1)
        # Get the table that was printed
        table = mock_console.print.call_args[0][0]
        self.assertEqual(table.columns[0].header, "Name")
        self.assertEqual(table.columns[1].header, "Type")

    @patch("nextmv.cli.community.list.console")
    def test_apps_table_handles_empty_manifest(self, mock_console):
        """Test that apps_table handles empty manifest."""
        manifest = {"apps": []}

        apps_table(manifest)

        self.assertEqual(mock_console.print.call_count, 1)


class TestAppsList(unittest.TestCase):
    """Tests for the apps_list function."""

    @patch("builtins.print")
    def test_apps_list_prints_names(self, mock_print):
        """Test that apps_list prints app names."""
        manifest = {
            "apps": [
                {"name": "app1"},
                {"name": "app2"},
                {"name": "app3"},
            ]
        }

        apps_list(manifest)

        mock_print.assert_called_once_with("app1\napp2\napp3")

    @patch("builtins.print")
    def test_apps_list_handles_empty_manifest(self, mock_print):
        """Test that apps_list handles empty manifest."""
        manifest = {"apps": []}

        apps_list(manifest)

        mock_print.assert_called_once_with("")


class TestVersionsTable(unittest.TestCase):
    """Tests for the versions_table function."""

    @patch("nextmv.cli.community.list.console")
    def test_versions_table_shows_latest_first(self, mock_console):
        """Test that versions_table shows latest version first with indicator."""
        manifest = {
            "apps": [
                {
                    "name": "test-app",
                    "latest_app_version": "v2.0.0",
                    "app_versions": ["v2.0.0", "v1.0.0"],
                }
            ]
        }

        versions_table(manifest, "test-app")

        self.assertEqual(mock_console.print.call_count, 1)
        table = mock_console.print.call_args[0][0]
        self.assertEqual(table.columns[0].header, "Version")
        self.assertEqual(table.columns[1].header, "Latest?")

    @patch("nextmv.cli.community.list.console")
    @patch("nextmv.cli.community.list.find_app")
    def test_versions_table_calls_find_app(self, mock_find_app, mock_console):
        """Test that versions_table calls find_app."""
        mock_find_app.return_value = {
            "latest_app_version": "v1.0.0",
            "app_versions": ["v1.0.0"],
        }

        versions_table({}, "test-app")

        mock_find_app.assert_called_once_with({}, "test-app")


class TestVersionsList(unittest.TestCase):
    """Tests for the versions_list function."""

    @patch("builtins.print")
    def test_versions_list_prints_versions(self, mock_print):
        """Test that versions_list prints all versions."""
        manifest = {
            "apps": [
                {
                    "name": "test-app",
                    "app_versions": ["v2.0.0", "v1.5.0", "v1.0.0"],
                }
            ]
        }

        versions_list(manifest, "test-app")

        mock_print.assert_called_once_with("v2.0.0\nv1.5.0\nv1.0.0")

    @patch("builtins.print")
    @patch("nextmv.cli.community.list.find_app")
    def test_versions_list_calls_find_app(self, mock_find_app, mock_print):
        """Test that versions_list calls find_app."""
        mock_find_app.return_value = {"app_versions": ["v1.0.0"]}

        versions_list({}, "test-app")

        mock_find_app.assert_called_once_with({}, "test-app")


class TestDownloadFile(unittest.TestCase):
    """Tests for the download_file function."""

    @patch("nextmv.cli.community.list.build_client")
    def test_download_file_makes_correct_requests(self, mock_build_client):
        """Test that download_file makes correct API requests."""
        mock_client = Mock()
        mock_client.headers = {"Authorization": "Bearer token"}
        mock_build_client.return_value = mock_client

        # Mock first request response
        mock_first_response = Mock()
        mock_first_response.json.return_value = {"url": "https://example.com/file"}

        # Mock second request response
        mock_second_response = Mock()
        mock_second_response.content = b"file content"

        # Set up client.request to return different responses
        mock_client.request.side_effect = [mock_first_response, mock_second_response]

        result = download_file(directory="test-dir", file="test-file.txt", profile="test-profile")

        # Verify build_client was called with profile
        mock_build_client.assert_called_once_with("test-profile")

        # Verify first request
        first_call = mock_client.request.call_args_list[0]
        self.assertEqual(first_call[1]["method"], "GET")
        self.assertEqual(first_call[1]["endpoint"], "v0/internal/tools")
        self.assertIn("Authorization", first_call[1]["headers"])
        self.assertEqual(first_call[1]["query_params"], {"file": "test-dir/test-file.txt"})

        # Verify second request
        second_call = mock_client.request.call_args_list[1]
        self.assertEqual(second_call[1]["method"], "GET")
        self.assertEqual(second_call[1]["endpoint"], "https://example.com/file")

        self.assertEqual(result, mock_second_response)


class TestFindApp(unittest.TestCase):
    """Tests for the find_app function."""

    def setUp(self):
        self.manifest = {
            "apps": [
                {"name": "app1", "description": "First app"},
                {"name": "app2", "description": "Second app"},
                {"name": "app3", "description": "Third app"},
            ]
        }

    def test_find_app_returns_correct_app(self):
        """Test that find_app returns the correct app."""
        result = find_app(self.manifest, "app2")

        self.assertEqual(result["name"], "app2")
        self.assertEqual(result["description"], "Second app")

    @patch("nextmv.cli.community.list.apps_table")
    @patch("nextmv.cli.community.list.rich.print")
    def test_find_app_raises_exit_when_not_found(self, mock_rich_print, mock_apps_table):
        """Test that find_app raises typer.Exit when app not found."""
        from typer import Exit

        with self.assertRaises(Exit) as context:
            find_app(self.manifest, "nonexistent-app")

        self.assertEqual(context.exception.exit_code, 1)
        mock_rich_print.assert_called_once()
        mock_apps_table.assert_called_once_with(self.manifest)


class TestCommunityCloneCommand(unittest.TestCase):
    """Tests for the community clone command."""

    def setUp(self):
        self.runner = CliRunner()
        self.app = clone_app
        self.sample_manifest = {
            "apps": [
                {
                    "name": "go-nextroute",
                    "type": "go",
                    "latest_app_version": "v1.2.0",
                    "description": "A routing app",
                    "app_versions": ["v1.2.0", "v1.1.0", "v1.0.0"],
                },
            ]
        }

    @patch("nextmv.cli.community.clone.os.remove")
    @patch("nextmv.cli.community.clone.shutil.move")
    @patch("nextmv.cli.community.clone.tarfile.open")
    @patch("nextmv.cli.community.clone.download_object")
    @patch("nextmv.cli.community.clone.get_valid_path")
    @patch("nextmv.cli.community.clone.os.makedirs")
    @patch("nextmv.cli.community.clone.app_has_version")
    @patch("nextmv.cli.community.clone.find_app")
    @patch("nextmv.cli.community.clone.download_manifest")
    def test_clone_with_latest_version(
        self,
        mock_download_manifest,
        mock_find_app,
        mock_app_has_version,
        mock_makedirs,
        mock_get_valid_path,
        mock_download_object,
        mock_tarfile_open,
        mock_shutil_move,
        mock_os_remove,
    ):
        """Test cloning an app with latest version."""
        mock_download_manifest.return_value = self.sample_manifest
        mock_find_app.return_value = self.sample_manifest["apps"][0]
        mock_app_has_version.return_value = True
        mock_get_valid_path.return_value = "/test/path/go-nextroute"
        mock_download_object.return_value = "/test/path/go-nextroute/tarball.tar.gz"

        # Mock tarfile extraction
        mock_tar = MagicMock()
        mock_tarfile_open.return_value.__enter__.return_value = mock_tar

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock extracted directory
            extracted_dir = os.path.join(temp_dir, "go-nextroute")
            os.makedirs(extracted_dir)

            with patch("nextmv.cli.community.clone.tempfile.TemporaryDirectory") as mock_tempdir:
                mock_tempdir.return_value.__enter__.return_value = temp_dir
                with patch("nextmv.cli.community.clone.os.listdir") as mock_listdir:
                    mock_listdir.side_effect = [["go-nextroute"], ["file1.py", "file2.py"]]
                    with patch("nextmv.cli.community.clone.os.path.isdir") as mock_isdir:
                        mock_isdir.return_value = True

                        result = self.runner.invoke(self.app, ["--app", "go-nextroute"])

                        self.assertEqual(result.exit_code, 0)
                        mock_download_manifest.assert_called_once_with(profile=None)
                        mock_find_app.assert_called_once_with(self.sample_manifest, "go-nextroute")

    @patch("nextmv.cli.community.clone.download_manifest")
    @patch("nextmv.cli.community.clone.find_app")
    def test_clone_with_empty_version_errors(self, mock_find_app, mock_download_manifest):
        """Test that clone with empty --version string returns error."""
        mock_download_manifest.return_value = self.sample_manifest
        mock_find_app.return_value = self.sample_manifest["apps"][0]

        result = self.runner.invoke(self.app, ["--app", "go-nextroute", "--version", ""])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("cannot be an empty string", result.output)

    @patch("nextmv.cli.community.clone.versions_table")
    @patch("nextmv.cli.community.clone.app_has_version")
    @patch("nextmv.cli.community.clone.find_app")
    @patch("nextmv.cli.community.clone.download_manifest")
    def test_clone_with_invalid_version_shows_available(
        self, mock_download_manifest, mock_find_app, mock_app_has_version, mock_versions_table
    ):
        """Test that clone with invalid version shows available versions."""
        mock_download_manifest.return_value = self.sample_manifest
        mock_find_app.return_value = self.sample_manifest["apps"][0]
        mock_app_has_version.return_value = False

        result = self.runner.invoke(self.app, ["--app", "go-nextroute", "--version", "v99.0.0"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Version", result.output)
        self.assertIn("not found", result.output)
        mock_versions_table.assert_called_once_with(self.sample_manifest, "go-nextroute")

    @patch("nextmv.cli.community.clone.os.remove")
    @patch("nextmv.cli.community.clone.shutil.move")
    @patch("nextmv.cli.community.clone.tarfile.open")
    @patch("nextmv.cli.community.clone.download_object")
    @patch("nextmv.cli.community.clone.get_valid_path")
    @patch("nextmv.cli.community.clone.os.makedirs")
    @patch("nextmv.cli.community.clone.app_has_version")
    @patch("nextmv.cli.community.clone.find_app")
    @patch("nextmv.cli.community.clone.download_manifest")
    def test_clone_with_custom_directory(
        self,
        mock_download_manifest,
        mock_find_app,
        mock_app_has_version,
        mock_makedirs,
        mock_get_valid_path,
        mock_download_object,
        mock_tarfile_open,
        mock_shutil_move,
        mock_os_remove,
    ):
        """Test cloning an app to a custom directory."""
        mock_download_manifest.return_value = self.sample_manifest
        mock_find_app.return_value = self.sample_manifest["apps"][0]
        mock_app_has_version.return_value = True
        mock_get_valid_path.return_value = "/custom/path"
        mock_download_object.return_value = "/custom/path/tarball.tar.gz"

        mock_tar = MagicMock()
        mock_tarfile_open.return_value.__enter__.return_value = mock_tar

        with tempfile.TemporaryDirectory() as temp_dir:
            extracted_dir = os.path.join(temp_dir, "go-nextroute")
            os.makedirs(extracted_dir)

            with patch("nextmv.cli.community.clone.tempfile.TemporaryDirectory") as mock_tempdir:
                mock_tempdir.return_value.__enter__.return_value = temp_dir
                with patch("nextmv.cli.community.clone.os.listdir") as mock_listdir:
                    mock_listdir.side_effect = [["go-nextroute"], ["file1.py"]]
                    with patch("nextmv.cli.community.clone.os.path.isdir") as mock_isdir:
                        mock_isdir.return_value = True

                        result = self.runner.invoke(self.app, ["--app", "go-nextroute", "--directory", "/custom/path"])

                        self.assertEqual(result.exit_code, 0)
                        expected_path = os.path.join(os.sep, "custom", "path")
                        mock_get_valid_path.assert_called_once_with(expected_path, os.stat)


class TestAppHasVersion(unittest.TestCase):
    """Tests for the app_has_version function."""

    def test_app_has_version_returns_true_for_existing_version(self):
        """Test that app_has_version returns True for existing version."""
        app_obj = {
            "latest_app_version": "v2.0.0",
            "app_versions": ["v2.0.0", "v1.5.0", "v1.0.0"],
        }

        result = app_has_version(app_obj, "v1.5.0")

        self.assertTrue(result)

    def test_app_has_version_returns_false_for_nonexistent_version(self):
        """Test that app_has_version returns False for nonexistent version."""
        app_obj = {
            "latest_app_version": "v2.0.0",
            "app_versions": ["v2.0.0", "v1.5.0", "v1.0.0"],
        }

        result = app_has_version(app_obj, "v99.0.0")

        self.assertFalse(result)

    def test_app_has_version_handles_latest_keyword(self):
        """Test that app_has_version handles 'latest' keyword."""
        app_obj = {
            "latest_app_version": "v2.0.0",
            "app_versions": ["v2.0.0", "v1.5.0", "v1.0.0"],
        }

        result = app_has_version(app_obj, "latest")

        self.assertTrue(result)


class TestGetValidPath(unittest.TestCase):
    """Tests for the get_valid_path function."""

    def test_get_valid_path_returns_path_when_not_exists(self):
        """Test that get_valid_path returns path when it doesn't exist."""

        def mock_stat(path):
            raise FileNotFoundError()

        result = get_valid_path("/test/path", mock_stat)

        self.assertEqual(result, "/test/path")

    def test_get_valid_path_appends_number_when_exists(self):
        """Test that get_valid_path appends number when path exists."""
        call_count = [0]

        def mock_stat(path):
            call_count[0] += 1
            if call_count[0] <= 2:
                # First two calls: path exists
                return os.stat_result((0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
            else:
                # Third call: path doesn't exist
                raise FileNotFoundError()

        result = get_valid_path("/test/myapp", mock_stat)

        self.assertEqual(result, "/test/myapp-2")

    def test_get_valid_path_handles_file_extension(self):
        """Test that get_valid_path handles file extensions correctly."""
        call_count = [0]

        def mock_stat(path):
            call_count[0] += 1
            if call_count[0] == 1:
                return os.stat_result((0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
            else:
                raise FileNotFoundError()

        result = get_valid_path("/test/file.json", mock_stat, ending=".json")

        self.assertEqual(result, "/test/file-1.json")

    def test_get_valid_path_increments_existing_number(self):
        """Test that get_valid_path increments existing number."""
        existing_paths = {"/test/myapp-3", "/test/myapp-3-4"}

        def mock_stat(path):
            if path in existing_paths:
                return os.stat_result((0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
            raise FileNotFoundError()

        result = get_valid_path("/test/myapp-3", mock_stat)

        # When path ends with a number, it appends incrementing numbers to the base name
        self.assertEqual(result, "/test/myapp-3-5")


class TestDownloadObject(unittest.TestCase):
    """Tests for the download_object function."""

    @patch("builtins.open", new_callable=mock_open)
    @patch("nextmv.cli.community.clone.os.path.join")
    @patch("nextmv.cli.community.clone.download_file")
    def test_download_object_saves_file(self, mock_download_file, mock_path_join, mock_file):
        """Test that download_object downloads and saves file."""
        mock_response = Mock()
        mock_response.content = b"file content"
        mock_download_file.return_value = mock_response
        mock_path_join.return_value = "/output/file.tar.gz"

        result = download_object(
            file="test-file.tar.gz", path="test-path", output_dir="/output", output_file="file.tar.gz", profile="test"
        )

        mock_download_file.assert_called_once_with(directory="test-path", file="test-file.tar.gz", profile="test")
        mock_file.assert_called_once_with("/output/file.tar.gz", "wb")
        mock_file().write.assert_called_once_with(b"file content")
        self.assertEqual(result, "/output/file.tar.gz")


class TestCommunityCommunityCommand(unittest.TestCase):
    """Tests for the main community command."""

    def setUp(self):
        self.runner = CliRunner()
        self.app = community_app

    def test_community_help_shows_description(self):
        """Test that community command shows help description."""
        result = self.runner.invoke(self.app, ["--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("community apps", result.output.lower())

    @patch("nextmv.cli.community.list.download_manifest")
    @patch("nextmv.cli.community.list.apps_table")
    def test_community_list_subcommand_works(self, mock_apps_table, mock_download_manifest):
        """Test that community list subcommand is registered."""
        mock_download_manifest.return_value = {"apps": []}

        result = self.runner.invoke(self.app, ["list"])

        self.assertEqual(result.exit_code, 0)

    @patch("nextmv.cli.community.clone.download_manifest")
    @patch("nextmv.cli.community.clone.find_app")
    def test_community_clone_subcommand_works(self, mock_find_app, mock_download_manifest):
        """Test that community clone subcommand is registered."""
        mock_download_manifest.return_value = {"apps": []}

        # This should fail because --app is required, but it proves the subcommand is registered
        result = self.runner.invoke(self.app, ["clone"])

        # Missing required option should give exit code 2
        self.assertNotEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
