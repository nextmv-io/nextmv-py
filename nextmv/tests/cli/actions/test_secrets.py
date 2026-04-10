"""Tests for nextmv.cli.actions.secrets."""

import unittest
from unittest.mock import MagicMock, patch


class TestListSecretsCollections(unittest.TestCase):
    @patch("nextmv.cli.actions.secrets.Application")
    def test_returns_list_of_dicts(self, mock_application_class):
        mock_c1 = MagicMock()
        mock_c1.to_dict.return_value = {"id": "coll-1", "name": "Collection One"}
        mock_c2 = MagicMock()
        mock_c2.to_dict.return_value = {"id": "coll-2", "name": "Collection Two"}
        mock_app = MagicMock()
        mock_app.list_secrets_collections.return_value = [mock_c1, mock_c2]
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.secrets import list_secrets_collections

        result = list_secrets_collections(client, app_id="my-app")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.list_secrets_collections.assert_called_once()
        self.assertEqual(
            result,
            [{"id": "coll-1", "name": "Collection One"}, {"id": "coll-2", "name": "Collection Two"}],
        )

    @patch("nextmv.cli.actions.secrets.Application")
    def test_empty_list(self, mock_application_class):
        mock_app = MagicMock()
        mock_app.list_secrets_collections.return_value = []
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.secrets import list_secrets_collections

        result = list_secrets_collections(client, app_id="my-app")

        self.assertEqual(result, [])


class TestGetSecretsCollection(unittest.TestCase):
    @patch("nextmv.cli.actions.secrets.Application")
    def test_returns_collection_dict(self, mock_application_class):
        mock_collection = MagicMock()
        mock_collection.to_dict.return_value = {"id": "coll-1", "name": "Collection One"}
        mock_app = MagicMock()
        mock_app.secrets_collection.return_value = mock_collection
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.secrets import get_secrets_collection

        result = get_secrets_collection(client, app_id="my-app", secrets_collection_id="coll-1")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.secrets_collection.assert_called_once_with(secrets_collection_id="coll-1")
        self.assertEqual(result, {"id": "coll-1", "name": "Collection One"})


class TestCreateSecretsCollection(unittest.TestCase):
    @patch("nextmv.cli.actions.secrets.Application")
    def test_creates_with_all_params(self, mock_application_class):
        mock_collection = MagicMock()
        mock_collection.to_dict.return_value = {"id": "coll-1"}
        mock_app = MagicMock()
        mock_app.new_secrets_collection.return_value = mock_collection
        mock_application_class.return_value = mock_app

        client = MagicMock()
        secrets = [{"type": "env", "location": "API_KEY", "value": "secret"}]

        from nextmv.cli.actions.secrets import create_secrets_collection

        result = create_secrets_collection(
            client,
            app_id="my-app",
            secrets=secrets,
            secrets_collection_id="coll-1",
            name="My Collection",
            description="A test collection",
        )

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.new_secrets_collection.assert_called_once_with(
            secrets=secrets,
            id="coll-1",
            name="My Collection",
            description="A test collection",
        )
        self.assertEqual(result, {"id": "coll-1"})

    @patch("nextmv.cli.actions.secrets.Application")
    def test_creates_with_defaults(self, mock_application_class):
        mock_collection = MagicMock()
        mock_collection.to_dict.return_value = {"id": "auto-id"}
        mock_app = MagicMock()
        mock_app.new_secrets_collection.return_value = mock_collection
        mock_application_class.return_value = mock_app

        client = MagicMock()
        secrets = [{"type": "env", "location": "KEY", "value": "val"}]

        from nextmv.cli.actions.secrets import create_secrets_collection

        result = create_secrets_collection(client, app_id="my-app", secrets=secrets)

        mock_app.new_secrets_collection.assert_called_once_with(
            secrets=secrets,
            id=None,
            name=None,
            description=None,
        )
        self.assertEqual(result, {"id": "auto-id"})


class TestDeleteSecretsCollection(unittest.TestCase):
    @patch("nextmv.cli.actions.secrets.Application")
    def test_deletes_collection(self, mock_application_class):
        mock_app = MagicMock()
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.secrets import delete_secrets_collection

        result = delete_secrets_collection(client, app_id="my-app", secrets_collection_id="coll-1")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.delete_secrets_collection.assert_called_once_with(secrets_collection_id="coll-1")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
