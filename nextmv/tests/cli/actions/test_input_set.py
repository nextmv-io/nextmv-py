"""Tests for nextmv.cli.actions.input_set."""

import unittest
from unittest.mock import MagicMock, patch


class TestListInputSets(unittest.TestCase):
    @patch("nextmv.cli.actions.input_set.Application")
    def test_returns_list_of_dicts(self, mock_application_class):
        mock_s1 = MagicMock()
        mock_s1.to_dict.return_value = {"id": "set-1", "name": "Set One"}
        mock_s2 = MagicMock()
        mock_s2.to_dict.return_value = {"id": "set-2", "name": "Set Two"}
        mock_app = MagicMock()
        mock_app.list_input_sets.return_value = [mock_s1, mock_s2]
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.input_set import list_input_sets

        result = list_input_sets(client, app_id="my-app")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.list_input_sets.assert_called_once()
        self.assertEqual(result, [{"id": "set-1", "name": "Set One"}, {"id": "set-2", "name": "Set Two"}])

    @patch("nextmv.cli.actions.input_set.Application")
    def test_empty_list(self, mock_application_class):
        mock_app = MagicMock()
        mock_app.list_input_sets.return_value = []
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.input_set import list_input_sets

        result = list_input_sets(client, app_id="my-app")

        self.assertEqual(result, [])


class TestGetInputSet(unittest.TestCase):
    @patch("nextmv.cli.actions.input_set.Application")
    def test_returns_input_set_dict(self, mock_application_class):
        mock_input_set = MagicMock()
        mock_input_set.to_dict.return_value = {"id": "set-1", "name": "Set One"}
        mock_app = MagicMock()
        mock_app.input_set.return_value = mock_input_set
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.input_set import get_input_set

        result = get_input_set(client, app_id="my-app", input_set_id="set-1")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.input_set.assert_called_once_with(input_set_id="set-1")
        self.assertEqual(result, {"id": "set-1", "name": "Set One"})


class TestCreateInputSet(unittest.TestCase):
    @patch("nextmv.cli.actions.input_set.Application")
    def test_creates_with_run_ids(self, mock_application_class):
        mock_input_set = MagicMock()
        mock_input_set.to_dict.return_value = {"id": "set-1", "name": "Set One"}
        mock_app = MagicMock()
        mock_app.new_input_set.return_value = mock_input_set
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.input_set import create_input_set

        result = create_input_set(
            client,
            app_id="my-app",
            input_set_id="set-1",
            name="Set One",
            description="A test set",
            run_ids=["run-1", "run-2"],
        )

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.new_input_set.assert_called_once_with(
            id="set-1",
            name="Set One",
            description="A test set",
            instance_id=None,
            maximum_runs=None,
            run_ids=["run-1", "run-2"],
            start_time=None,
            end_time=None,
            inputs=None,
        )
        self.assertEqual(result, {"id": "set-1", "name": "Set One"})

    @patch("nextmv.cli.actions.input_set.Application")
    def test_creates_with_instance_id(self, mock_application_class):
        mock_input_set = MagicMock()
        mock_input_set.to_dict.return_value = {"id": "set-2"}
        mock_app = MagicMock()
        mock_app.new_input_set.return_value = mock_input_set
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.input_set import create_input_set

        result = create_input_set(
            client,
            app_id="my-app",
            instance_id="prod",
            maximum_runs=10,
        )

        mock_app.new_input_set.assert_called_once_with(
            id=None,
            name=None,
            description=None,
            instance_id="prod",
            maximum_runs=10,
            run_ids=None,
            start_time=None,
            end_time=None,
            inputs=None,
        )
        self.assertEqual(result, {"id": "set-2"})

    @patch("nextmv.cli.actions.input_set.Application")
    def test_creates_with_managed_input_ids(self, mock_application_class):
        mock_input_set = MagicMock()
        mock_input_set.to_dict.return_value = {"id": "set-3"}
        mock_app = MagicMock()
        mock_app.new_input_set.return_value = mock_input_set
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.input_set import create_input_set

        result = create_input_set(
            client,
            app_id="my-app",
            managed_input_ids=["mi-1", "mi-2"],
        )

        call_kwargs = mock_app.new_input_set.call_args[1]
        inputs = call_kwargs["inputs"]
        self.assertEqual(len(inputs), 2)
        self.assertEqual(inputs[0].id, "mi-1")
        self.assertEqual(inputs[1].id, "mi-2")
        self.assertEqual(result, {"id": "set-3"})


class TestUpdateInputSet(unittest.TestCase):
    @patch("nextmv.cli.actions.input_set.Application")
    def test_updates_with_name_and_description(self, mock_application_class):
        mock_updated = MagicMock()
        mock_updated.to_dict.return_value = {"id": "set-1", "name": "New Name"}
        mock_app = MagicMock()
        mock_app.update_input_set.return_value = mock_updated
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.input_set import update_input_set

        result = update_input_set(
            client,
            app_id="my-app",
            input_set_id="set-1",
            name="New Name",
            description="New desc",
        )

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.update_input_set.assert_called_once_with(
            id="set-1",
            name="New Name",
            description="New desc",
            inputs=None,
        )
        self.assertEqual(result, {"id": "set-1", "name": "New Name"})

    @patch("nextmv.cli.actions.input_set.Application")
    def test_updates_with_defaults(self, mock_application_class):
        mock_updated = MagicMock()
        mock_updated.to_dict.return_value = {"id": "set-1"}
        mock_app = MagicMock()
        mock_app.update_input_set.return_value = mock_updated
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.input_set import update_input_set

        result = update_input_set(client, app_id="my-app", input_set_id="set-1")

        mock_app.update_input_set.assert_called_once_with(
            id="set-1",
            name=None,
            description=None,
            inputs=None,
        )
        self.assertEqual(result, {"id": "set-1"})


class TestDeleteInputSet(unittest.TestCase):
    @patch("nextmv.cli.actions.input_set.Application")
    def test_deletes_input_set(self, mock_application_class):
        mock_app = MagicMock()
        mock_application_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.input_set import delete_input_set

        result = delete_input_set(client, app_id="my-app", input_set_id="set-1")

        mock_application_class.assert_called_once_with(client=client, id="my-app")
        mock_app.delete_input_set.assert_called_once_with(input_set_id="set-1")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
