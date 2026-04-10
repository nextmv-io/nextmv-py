"""Tests for nextmv.cli.actions.managed_input."""

import unittest
from unittest.mock import MagicMock, patch


class TestListManagedInputs(unittest.TestCase):
    @patch("nextmv.cli.actions.managed_input.Application")
    def test_returns_list_of_dicts(self, mock_application_class):
        mock_i1 = MagicMock()
        mock_i1.to_dict.return_value = {"id": "mi-1", "name": "Input One"}
        mock_i2 = MagicMock()
        mock_i2.to_dict.return_value = {"id": "mi-2", "name": "Input Two"}
        mock_app = MagicMock()
        mock_app.list_managed_inputs.return_value = [mock_i1, mock_i2]
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.managed_input import list_managed_inputs

        result = list_managed_inputs(client, app_id="my-app")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.list_managed_inputs.assert_called_once()
        self.assertEqual(result, [{"id": "mi-1", "name": "Input One"}, {"id": "mi-2", "name": "Input Two"}])

    @patch("nextmv.cli.actions.managed_input.Application")
    def test_empty_list(self, mock_application_class):
        mock_app = MagicMock()
        mock_app.list_managed_inputs.return_value = []
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.managed_input import list_managed_inputs

        result = list_managed_inputs(client, app_id="my-app")

        self.assertEqual(result, [])


class TestGetManagedInput(unittest.TestCase):
    @patch("nextmv.cli.actions.managed_input.Application")
    def test_returns_managed_input_dict(self, mock_application_class):
        mock_mi = MagicMock()
        mock_mi.to_dict.return_value = {"id": "mi-1", "name": "Input One"}
        mock_app = MagicMock()
        mock_app.managed_input.return_value = mock_mi
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.managed_input import get_managed_input

        result = get_managed_input(client, app_id="my-app", managed_input_id="mi-1")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.managed_input.assert_called_once_with(managed_input_id="mi-1")
        self.assertEqual(result, {"id": "mi-1", "name": "Input One"})


class TestCreateManagedInput(unittest.TestCase):
    @patch("nextmv.cli.actions.managed_input.Application")
    def test_creates_with_run_id(self, mock_application_class):
        mock_mi = MagicMock()
        mock_mi.to_dict.return_value = {"id": "mi-1"}
        mock_app = MagicMock()
        mock_app.new_managed_input.return_value = mock_mi
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.managed_input import create_managed_input

        result = create_managed_input(
            client,
            app_id="my-app",
            managed_input_id="mi-1",
            name="Input One",
            description="A test input",
            run_id="run-1",
        )

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.upload_url.assert_not_called()
        mock_app.new_managed_input.assert_called_once_with(
            id="mi-1",
            name="Input One",
            description="A test input",
            upload_id=None,
            run_id="run-1",
        )
        self.assertEqual(result, {"id": "mi-1"})

    @patch("nextmv.cli.actions.managed_input.Application")
    def test_creates_with_upload_id(self, mock_application_class):
        mock_mi = MagicMock()
        mock_mi.to_dict.return_value = {"id": "mi-2"}
        mock_app = MagicMock()
        mock_app.new_managed_input.return_value = mock_mi
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.managed_input import create_managed_input

        result = create_managed_input(
            client,
            app_id="my-app",
            upload_id="upl_123",
        )

        mock_app.upload_url.assert_not_called()
        mock_app.new_managed_input.assert_called_once_with(
            id=None,
            name=None,
            description=None,
            upload_id="upl_123",
            run_id=None,
        )
        self.assertEqual(result, {"id": "mi-2"})

    @patch("nextmv.cli.actions.managed_input.Application")
    def test_creates_with_raw_data(self, mock_application_class):
        mock_mi = MagicMock()
        mock_mi.to_dict.return_value = {"id": "mi-3"}
        mock_upload_url = MagicMock()
        mock_upload_url.upload_id = "upl_456"
        mock_app = MagicMock()
        mock_app.upload_url.return_value = mock_upload_url
        mock_app.new_managed_input.return_value = mock_mi
        mock_application_class.return_value = mock_app

        client = MagicMock()
        data = {"key": "value"}

        from nextmv.cli.actions.managed_input import create_managed_input

        result = create_managed_input(
            client,
            app_id="my-app",
            data=data,
            name="Raw Input",
        )

        mock_app.upload_url.assert_called_once()
        mock_app.upload_data.assert_called_once_with(upload_url=mock_upload_url, data=data)
        mock_app.new_managed_input.assert_called_once_with(
            id=None,
            name="Raw Input",
            description=None,
            upload_id="upl_456",
            run_id=None,
        )
        self.assertEqual(result, {"id": "mi-3"})


class TestDeleteManagedInput(unittest.TestCase):
    @patch("nextmv.cli.actions.managed_input.Application")
    def test_deletes_managed_input(self, mock_application_class):
        mock_app = MagicMock()
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.managed_input import delete_managed_input

        result = delete_managed_input(client, app_id="my-app", managed_input_id="mi-1")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.delete_managed_input.assert_called_once_with(managed_input_id="mi-1")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
