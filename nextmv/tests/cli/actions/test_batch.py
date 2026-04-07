"""Tests for nextmv.cli.actions.batch."""

import unittest
from unittest.mock import MagicMock, patch


class TestListBatches(unittest.TestCase):
    @patch("nextmv.cli.actions.batch.Application")
    def test_returns_list_of_dicts(self, mock_app_class):
        mock_b1 = MagicMock()
        mock_b1.to_dict.return_value = {"id": "batch-1"}
        mock_b2 = MagicMock()
        mock_b2.to_dict.return_value = {"id": "batch-2"}
        mock_app = MagicMock()
        mock_app.list_batch_experiments.return_value = [mock_b1, mock_b2]
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.batch import list_batches

        result = list_batches(client, "my-app")

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        mock_app.list_batch_experiments.assert_called_once()
        self.assertEqual(result, [{"id": "batch-1"}, {"id": "batch-2"}])

    @patch("nextmv.cli.actions.batch.Application")
    def test_empty_list(self, mock_app_class):
        mock_app = MagicMock()
        mock_app.list_batch_experiments.return_value = []
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.batch import list_batches

        result = list_batches(client, "my-app")

        self.assertEqual(result, [])


class TestGetBatch(unittest.TestCase):
    @patch("nextmv.cli.actions.batch.Application")
    def test_returns_dict(self, mock_app_class):
        mock_batch = MagicMock()
        mock_batch.to_dict.return_value = {"id": "batch-1", "status": "completed"}
        mock_app = MagicMock()
        mock_app.batch_experiment.return_value = mock_batch
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.batch import get_batch

        result = get_batch(client, "my-app", "batch-1")

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        mock_app.batch_experiment.assert_called_once_with(batch_id="batch-1")
        self.assertEqual(result, {"id": "batch-1", "status": "completed"})


class TestBatchMetadata(unittest.TestCase):
    @patch("nextmv.cli.actions.batch.Application")
    def test_returns_metadata_dict(self, mock_app_class):
        mock_meta = MagicMock()
        mock_meta.to_dict.return_value = {"id": "batch-1", "run_count": 5}
        mock_app = MagicMock()
        mock_app.batch_experiment_metadata.return_value = mock_meta
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.batch import batch_metadata

        result = batch_metadata(client, "my-app", "batch-1")

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        mock_app.batch_experiment_metadata.assert_called_once_with(batch_id="batch-1")
        self.assertEqual(result, {"id": "batch-1", "run_count": 5})


class TestCreateBatch(unittest.TestCase):
    @patch("nextmv.cli.actions.batch.Application")
    def test_creates_batch_with_all_params(self, mock_app_class):
        mock_app = MagicMock()
        mock_app.new_batch_experiment.return_value = "new-batch-id"
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.batch import create_batch

        result = create_batch(
            client,
            "my-app",
            input_set_id="input-set-1",
            name="My Batch",
            description="A test batch",
            option_sets={"fast": {"solve.duration": "5s"}},
        )

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        mock_app.new_batch_experiment.assert_called_once_with(
            input_set_id="input-set-1",
            name="My Batch",
            description="A test batch",
            option_sets={"fast": {"solve.duration": "5s"}},
        )
        self.assertEqual(result, "new-batch-id")

    @patch("nextmv.cli.actions.batch.Application")
    def test_creates_batch_with_defaults(self, mock_app_class):
        mock_app = MagicMock()
        mock_app.new_batch_experiment.return_value = "auto-batch-id"
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.batch import create_batch

        result = create_batch(client, "my-app", input_set_id="input-set-1")

        mock_app.new_batch_experiment.assert_called_once_with(
            input_set_id="input-set-1",
            name=None,
            description=None,
            option_sets=None,
        )
        self.assertEqual(result, "auto-batch-id")


class TestDeleteBatch(unittest.TestCase):
    @patch("nextmv.cli.actions.batch.Application")
    def test_deletes_batch(self, mock_app_class):
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.batch import delete_batch

        result = delete_batch(client, "my-app", "batch-1")

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        mock_app.delete_batch_experiment.assert_called_once_with(batch_id="batch-1")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
