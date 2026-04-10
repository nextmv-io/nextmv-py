"""Tests for nextmv.cli.actions.acceptance."""

import unittest
from unittest.mock import MagicMock, patch


class TestListAcceptanceTests(unittest.TestCase):
    @patch("nextmv.cli.actions.acceptance.Application")
    def test_returns_list_of_dicts(self, mock_app_class):
        mock_t1 = MagicMock()
        mock_t1.to_dict.return_value = {"id": "test-1"}
        mock_t2 = MagicMock()
        mock_t2.to_dict.return_value = {"id": "test-2"}
        mock_app = MagicMock()
        mock_app.list_acceptance_tests.return_value = [mock_t1, mock_t2]
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.acceptance import list_acceptance_tests

        result = list_acceptance_tests(client, "my-app")

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        self.assertEqual(result, [{"id": "test-1"}, {"id": "test-2"}])

    @patch("nextmv.cli.actions.acceptance.Application")
    def test_empty_list(self, mock_app_class):
        mock_app = MagicMock()
        mock_app.list_acceptance_tests.return_value = []
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.acceptance import list_acceptance_tests

        result = list_acceptance_tests(client, "my-app")

        self.assertEqual(result, [])


class TestGetAcceptanceTest(unittest.TestCase):
    @patch("nextmv.cli.actions.acceptance.Application")
    def test_returns_dict(self, mock_app_class):
        mock_test = MagicMock()
        mock_test.to_dict.return_value = {"id": "test-1", "status": "completed"}
        mock_app = MagicMock()
        mock_app.acceptance_test.return_value = mock_test
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.acceptance import get_acceptance_test

        result = get_acceptance_test(client, "my-app", "test-1")

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        mock_app.acceptance_test.assert_called_once_with(acceptance_test_id="test-1")
        self.assertEqual(result, {"id": "test-1", "status": "completed"})


class TestCreateAcceptanceTest(unittest.TestCase):
    @patch("nextmv.cli.actions.acceptance.Application")
    def test_creates_with_all_params(self, mock_app_class):
        mock_test = MagicMock()
        mock_test.to_dict.return_value = {"id": "new-test"}
        mock_app = MagicMock()
        mock_app.new_acceptance_test.return_value = mock_test
        mock_app_class.return_value = mock_app

        client = MagicMock()
        metrics = [{"field": "value", "metric_type": "direct-comparison"}]

        from nextmv.cli.actions.acceptance import create_acceptance_test

        result = create_acceptance_test(
            client,
            "my-app",
            candidate_instance_id="candidate-1",
            baseline_instance_id="baseline-1",
            metrics=metrics,
            acceptance_test_id="test-id",
            name="My Test",
            input_set_id="input-set-1",
            description="A test",
        )

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        mock_app.new_acceptance_test.assert_called_once_with(
            candidate_instance_id="candidate-1",
            baseline_instance_id="baseline-1",
            metrics=metrics,
            id="test-id",
            name="My Test",
            input_set_id="input-set-1",
            description="A test",
        )
        self.assertEqual(result, {"id": "new-test"})

    @patch("nextmv.cli.actions.acceptance.Application")
    def test_creates_with_defaults(self, mock_app_class):
        mock_test = MagicMock()
        mock_test.to_dict.return_value = {"id": "auto-test"}
        mock_app = MagicMock()
        mock_app.new_acceptance_test.return_value = mock_test
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.acceptance import create_acceptance_test

        result = create_acceptance_test(
            client,
            "my-app",
            candidate_instance_id="cand",
            baseline_instance_id="base",
            metrics=[],
        )

        mock_app.new_acceptance_test.assert_called_once_with(
            candidate_instance_id="cand",
            baseline_instance_id="base",
            metrics=[],
            id=None,
            name=None,
            input_set_id=None,
            description=None,
        )
        self.assertEqual(result, {"id": "auto-test"})


class TestDeleteAcceptanceTest(unittest.TestCase):
    @patch("nextmv.cli.actions.acceptance.Application")
    def test_deletes_test(self, mock_app_class):
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.acceptance import delete_acceptance_test

        result = delete_acceptance_test(client, "my-app", "test-1")

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        mock_app.delete_acceptance_test.assert_called_once_with(acceptance_test_id="test-1")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
