"""Tests for nextmv.cli.actions.version."""

import unittest
from unittest.mock import MagicMock, patch


class TestListVersions(unittest.TestCase):
    @patch("nextmv.cli.actions.version.Application")
    def test_returns_list_of_dicts(self, mock_application_class):
        mock_v1 = MagicMock()
        mock_v1.to_dict.return_value = {"id": "v1", "name": "Version 1"}
        mock_v2 = MagicMock()
        mock_v2.to_dict.return_value = {"id": "v2", "name": "Version 2"}
        mock_app = MagicMock()
        mock_app.list_versions.return_value = [mock_v1, mock_v2]
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.version import list_versions

        result = list_versions(client, app_id="my-app")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.list_versions.assert_called_once()
        self.assertEqual(result, [{"id": "v1", "name": "Version 1"}, {"id": "v2", "name": "Version 2"}])

    @patch("nextmv.cli.actions.version.Application")
    def test_empty_list(self, mock_application_class):
        mock_app = MagicMock()
        mock_app.list_versions.return_value = []
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.version import list_versions

        result = list_versions(client, app_id="my-app")

        self.assertEqual(result, [])


class TestGetVersion(unittest.TestCase):
    @patch("nextmv.cli.actions.version.Application")
    def test_returns_version_dict(self, mock_application_class):
        mock_version = MagicMock()
        mock_version.to_dict.return_value = {"id": "v1", "name": "Version 1"}
        mock_app = MagicMock()
        mock_app.version.return_value = mock_version
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.version import get_version

        result = get_version(client, app_id="my-app", version_id="v1")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.version.assert_called_once_with(version_id="v1")
        self.assertEqual(result, {"id": "v1", "name": "Version 1"})


class TestCreateVersion(unittest.TestCase):
    @patch("nextmv.cli.actions.version.Application")
    def test_creates_version_with_all_params(self, mock_application_class):
        mock_version = MagicMock()
        mock_version.to_dict.return_value = {"id": "v1", "name": "My Version"}
        mock_app = MagicMock()
        mock_app.new_version.return_value = mock_version
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.version import create_version

        result = create_version(
            client,
            app_id="my-app",
            version_id="v1",
            name="My Version",
            description="A test version",
            exist_ok=True,
        )

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.new_version.assert_called_once_with(
            id="v1",
            name="My Version",
            description="A test version",
            exist_ok=True,
        )
        self.assertEqual(result, {"id": "v1", "name": "My Version"})

    @patch("nextmv.cli.actions.version.Application")
    def test_creates_version_with_defaults(self, mock_application_class):
        mock_version = MagicMock()
        mock_version.to_dict.return_value = {"id": "auto-id", "name": ""}
        mock_app = MagicMock()
        mock_app.new_version.return_value = mock_version
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.version import create_version

        result = create_version(client, app_id="my-app")

        mock_app.new_version.assert_called_once_with(
            id=None,
            name=None,
            description=None,
            exist_ok=False,
        )
        self.assertEqual(result, {"id": "auto-id", "name": ""})


class TestUpdateVersion(unittest.TestCase):
    @patch("nextmv.cli.actions.version.Application")
    def test_updates_version_with_all_params(self, mock_application_class):
        mock_updated = MagicMock()
        mock_updated.to_dict.return_value = {"id": "v1", "name": "New Name"}
        mock_app = MagicMock()
        mock_app.update_version.return_value = mock_updated
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.version import update_version

        result = update_version(
            client,
            app_id="my-app",
            version_id="v1",
            name="New Name",
            description="New desc",
        )

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.update_version.assert_called_once_with(
            version_id="v1",
            name="New Name",
            description="New desc",
        )
        self.assertEqual(result, {"id": "v1", "name": "New Name"})

    @patch("nextmv.cli.actions.version.Application")
    def test_updates_version_with_defaults(self, mock_application_class):
        mock_updated = MagicMock()
        mock_updated.to_dict.return_value = {"id": "v1", "name": "Unchanged"}
        mock_app = MagicMock()
        mock_app.update_version.return_value = mock_updated
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.version import update_version

        result = update_version(client, app_id="my-app", version_id="v1")

        mock_app.update_version.assert_called_once_with(
            version_id="v1",
            name=None,
            description=None,
        )
        self.assertEqual(result, {"id": "v1", "name": "Unchanged"})


class TestDeleteVersion(unittest.TestCase):
    @patch("nextmv.cli.actions.version.Application")
    def test_deletes_version(self, mock_application_class):
        mock_app = MagicMock()
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.version import delete_version

        result = delete_version(client, app_id="my-app", version_id="v1")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.delete_version.assert_called_once_with(version_id="v1")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
