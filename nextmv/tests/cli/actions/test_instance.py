"""Tests for nextmv.cli.actions.instance."""

import unittest
from unittest.mock import MagicMock, patch


class TestListInstances(unittest.TestCase):
    @patch("nextmv.cli.actions.instance.Application")
    def test_returns_list_of_dicts(self, mock_application_class):
        mock_i1 = MagicMock()
        mock_i1.to_dict.return_value = {"id": "prod", "name": "Production"}
        mock_i2 = MagicMock()
        mock_i2.to_dict.return_value = {"id": "staging", "name": "Staging"}
        mock_app = MagicMock()
        mock_app.list_instances.return_value = [mock_i1, mock_i2]
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.instance import list_instances

        result = list_instances(client, app_id="my-app")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.list_instances.assert_called_once()
        self.assertEqual(
            result,
            [{"id": "prod", "name": "Production"}, {"id": "staging", "name": "Staging"}],
        )

    @patch("nextmv.cli.actions.instance.Application")
    def test_empty_list(self, mock_application_class):
        mock_app = MagicMock()
        mock_app.list_instances.return_value = []
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.instance import list_instances

        result = list_instances(client, app_id="my-app")

        self.assertEqual(result, [])


class TestGetInstance(unittest.TestCase):
    @patch("nextmv.cli.actions.instance.Application")
    def test_returns_instance_dict(self, mock_application_class):
        mock_instance = MagicMock()
        mock_instance.to_dict.return_value = {"id": "prod", "name": "Production"}
        mock_app = MagicMock()
        mock_app.instance.return_value = mock_instance
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.instance import get_instance

        result = get_instance(client, app_id="my-app", instance_id="prod")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.instance.assert_called_once_with(instance_id="prod")
        self.assertEqual(result, {"id": "prod", "name": "Production"})


class TestCreateInstance(unittest.TestCase):
    @patch("nextmv.cli.actions.instance.InstanceConfiguration")
    @patch("nextmv.cli.actions.instance.Application")
    def test_creates_instance_with_all_params(self, mock_application_class, mock_instance_config_class):
        mock_instance = MagicMock()
        mock_instance.to_dict.return_value = {"id": "prod", "name": "My Instance"}
        mock_app = MagicMock()
        mock_app.new_instance.return_value = mock_instance
        mock_application_class.return_value = mock_app

        mock_config = MagicMock()
        mock_instance_config_class.return_value = mock_config

        client = MagicMock()
        configuration = {"execution_class": "6c9500mb870s"}

        from nextmv.cli.actions.instance import create_instance

        result = create_instance(
            client,
            app_id="my-app",
            version_id="v1",
            instance_id="prod",
            name="My Instance",
            description="A test instance",
            configuration=configuration,
        )

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_instance_config_class.assert_called_once_with(**configuration)
        mock_app.new_instance.assert_called_once_with(
            version_id="v1",
            id="prod",
            name="My Instance",
            description="A test instance",
            configuration=mock_config,
        )
        self.assertEqual(result, {"id": "prod", "name": "My Instance"})

    @patch("nextmv.cli.actions.instance.Application")
    def test_creates_instance_without_configuration(self, mock_application_class):
        mock_instance = MagicMock()
        mock_instance.to_dict.return_value = {"id": "auto-id", "name": ""}
        mock_app = MagicMock()
        mock_app.new_instance.return_value = mock_instance
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.instance import create_instance

        result = create_instance(client, app_id="my-app", version_id="v1")

        mock_app.new_instance.assert_called_once_with(
            version_id="v1",
            id=None,
            name=None,
            description=None,
            configuration=None,
        )
        self.assertEqual(result, {"id": "auto-id", "name": ""})


class TestUpdateInstance(unittest.TestCase):
    @patch("nextmv.cli.actions.instance.Application")
    def test_updates_instance_with_all_params(self, mock_application_class):
        mock_updated = MagicMock()
        mock_updated.to_dict.return_value = {"id": "prod", "name": "New Name"}
        mock_app = MagicMock()
        mock_app.update_instance.return_value = mock_updated
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.instance import update_instance

        result = update_instance(
            client,
            app_id="my-app",
            instance_id="prod",
            name="New Name",
            version_id="v2",
            description="New desc",
            configuration={"execution_class": "high"},
        )

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.update_instance.assert_called_once_with(
            id="prod",
            name="New Name",
            version_id="v2",
            description="New desc",
            configuration={"execution_class": "high"},
        )
        self.assertEqual(result, {"id": "prod", "name": "New Name"})

    @patch("nextmv.cli.actions.instance.Application")
    def test_updates_instance_with_defaults(self, mock_application_class):
        mock_updated = MagicMock()
        mock_updated.to_dict.return_value = {"id": "prod", "name": "Unchanged"}
        mock_app = MagicMock()
        mock_app.update_instance.return_value = mock_updated
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.instance import update_instance

        result = update_instance(client, app_id="my-app", instance_id="prod")

        mock_app.update_instance.assert_called_once_with(
            id="prod",
            name=None,
            version_id=None,
            description=None,
            configuration=None,
        )
        self.assertEqual(result, {"id": "prod", "name": "Unchanged"})


class TestDeleteInstance(unittest.TestCase):
    @patch("nextmv.cli.actions.instance.Application")
    def test_deletes_instance(self, mock_application_class):
        mock_app = MagicMock()
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.instance import delete_instance

        result = delete_instance(client, app_id="my-app", instance_id="prod")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.delete_instance.assert_called_once_with(instance_id="prod")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
