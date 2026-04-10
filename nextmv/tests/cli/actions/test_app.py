"""Tests for nextmv.cli.actions.app."""

import unittest
from unittest.mock import MagicMock, patch


class TestListApps(unittest.TestCase):
    @patch("nextmv.cli.actions.app.list_applications")
    def test_returns_list_of_dicts(self, mock_list_applications):
        mock_app1 = MagicMock()
        mock_app1.to_dict.return_value = {"id": "app-1", "name": "App One"}
        mock_app2 = MagicMock()
        mock_app2.to_dict.return_value = {"id": "app-2", "name": "App Two"}
        mock_list_applications.return_value = [mock_app1, mock_app2]

        client = MagicMock()

        from nextmv.cli.actions.app import list_apps

        result = list_apps(client)

        mock_list_applications.assert_called_once_with(client)
        self.assertEqual(result, [{"id": "app-1", "name": "App One"}, {"id": "app-2", "name": "App Two"}])

    @patch("nextmv.cli.actions.app.list_applications")
    def test_empty_list(self, mock_list_applications):
        mock_list_applications.return_value = []
        client = MagicMock()

        from nextmv.cli.actions.app import list_apps

        result = list_apps(client)

        self.assertEqual(result, [])


class TestCreateApp(unittest.TestCase):
    @patch("nextmv.cli.actions.app.Application")
    def test_creates_app_with_all_params(self, mock_application_class):
        mock_app = MagicMock()
        mock_app.to_dict.return_value = {"id": "my-app", "name": "My App"}
        mock_application_class.new.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.app import create_app

        result = create_app(
            client,
            name="My App",
            app_id="my-app",
            description="A test app",
            is_workflow=True,
            exist_ok=True,
            default_instance_id="inst-1",
            default_experiment_instance="exp-1",
        )

        mock_application_class.new.assert_called_once_with(
            client=client,
            name="My App",
            id="my-app",
            description="A test app",
            is_workflow=True,
            exist_ok=True,
            default_instance_id="inst-1",
            default_experiment_instance="exp-1",
        )
        self.assertEqual(result, {"id": "my-app", "name": "My App"})

    @patch("nextmv.cli.actions.app.Application")
    def test_creates_app_with_defaults(self, mock_application_class):
        mock_app = MagicMock()
        mock_app.to_dict.return_value = {"id": "auto-id", "name": "My App"}
        mock_application_class.new.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.app import create_app

        result = create_app(client, name="My App")

        mock_application_class.new.assert_called_once_with(
            client=client,
            name="My App",
            id=None,
            description=None,
            is_workflow=False,
            exist_ok=False,
            default_instance_id=None,
            default_experiment_instance=None,
        )
        self.assertEqual(result, {"id": "auto-id", "name": "My App"})


class TestGetApp(unittest.TestCase):
    @patch("nextmv.cli.actions.app.Application")
    def test_returns_app_dict(self, mock_application_class):
        mock_app = MagicMock()
        mock_app.to_dict.return_value = {"id": "my-app", "name": "My App"}
        mock_application_class.get.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.app import get_app

        result = get_app(client, app_id="my-app")

        mock_application_class.get.assert_called_once_with(client=client, id="my-app")
        self.assertEqual(result, {"id": "my-app", "name": "My App"})


class TestDeleteApp(unittest.TestCase):
    @patch("nextmv.cli.actions.app.Application")
    def test_deletes_app(self, mock_application_class):
        mock_app = MagicMock()
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.app import delete_app

        result = delete_app(client, app_id="my-app")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.delete.assert_called_once()
        self.assertIsNone(result)


class TestAppExists(unittest.TestCase):
    @patch("nextmv.cli.actions.app.Application")
    def test_returns_true_when_exists(self, mock_application_class):
        mock_application_class.exists.return_value = True

        client = MagicMock()

        from nextmv.cli.actions.app import app_exists

        result = app_exists(client, app_id="my-app")

        mock_application_class.exists.assert_called_once_with(client=client, id="my-app")
        self.assertTrue(result)

    @patch("nextmv.cli.actions.app.Application")
    def test_returns_false_when_not_exists(self, mock_application_class):
        mock_application_class.exists.return_value = False

        client = MagicMock()

        from nextmv.cli.actions.app import app_exists

        result = app_exists(client, app_id="missing-app")

        self.assertFalse(result)


class TestUpdateApp(unittest.TestCase):
    @patch("nextmv.cli.actions.app.Application")
    def test_updates_app_with_all_params(self, mock_application_class):
        mock_updated = MagicMock()
        mock_updated.to_dict.return_value = {"id": "my-app", "name": "New Name"}
        mock_app = MagicMock()
        mock_app.update.return_value = mock_updated
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.app import update_app

        result = update_app(
            client,
            app_id="my-app",
            name="New Name",
            description="New desc",
            default_instance_id="inst-2",
            default_experiment_instance="exp-2",
        )

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.update.assert_called_once_with(
            name="New Name",
            description="New desc",
            default_instance_id="inst-2",
            default_experiment_instance="exp-2",
        )
        self.assertEqual(result, {"id": "my-app", "name": "New Name"})

    @patch("nextmv.cli.actions.app.Application")
    def test_updates_app_with_defaults(self, mock_application_class):
        mock_updated = MagicMock()
        mock_updated.to_dict.return_value = {"id": "my-app", "name": "Unchanged"}
        mock_app = MagicMock()
        mock_app.update.return_value = mock_updated
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.app import update_app

        result = update_app(client, app_id="my-app")

        mock_app.update.assert_called_once_with(
            name=None,
            description=None,
            default_instance_id=None,
            default_experiment_instance=None,
        )
        self.assertEqual(result, {"id": "my-app", "name": "Unchanged"})


class TestPushApp(unittest.TestCase):
    @patch("nextmv.cli.actions.app.Application")
    def test_pushes_app(self, mock_application_class):
        mock_app = MagicMock()
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.app import push_app

        result = push_app(client, app_id="my-app", app_dir="/path/to/app")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.push.assert_called_once_with(app_dir="/path/to/app")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
