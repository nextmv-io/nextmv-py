"""Tests for nextmv.cli.actions.shadow."""

import unittest
from unittest.mock import MagicMock, patch


class TestListShadowTests(unittest.TestCase):
    @patch("nextmv.cli.actions.shadow.Application")
    def test_returns_list_of_dicts(self, mock_app_class):
        mock_t = MagicMock()
        mock_t.to_dict.return_value = {"id": "shadow-1"}
        mock_app = MagicMock()
        mock_app.list_shadow_tests.return_value = [mock_t]
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.shadow import list_shadow_tests

        result = list_shadow_tests(client, "my-app")

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        self.assertEqual(result, [{"id": "shadow-1"}])

    @patch("nextmv.cli.actions.shadow.Application")
    def test_empty_list(self, mock_app_class):
        mock_app = MagicMock()
        mock_app.list_shadow_tests.return_value = []
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.shadow import list_shadow_tests

        result = list_shadow_tests(client, "my-app")

        self.assertEqual(result, [])


class TestGetShadowTest(unittest.TestCase):
    @patch("nextmv.cli.actions.shadow.Application")
    def test_returns_dict(self, mock_app_class):
        mock_test = MagicMock()
        mock_test.to_dict.return_value = {"id": "shadow-1", "status": "running"}
        mock_app = MagicMock()
        mock_app.shadow_test.return_value = mock_test
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.shadow import get_shadow_test

        result = get_shadow_test(client, "my-app", "shadow-1")

        mock_app.shadow_test.assert_called_once_with(shadow_test_id="shadow-1")
        self.assertEqual(result, {"id": "shadow-1", "status": "running"})


class TestCreateShadowTest(unittest.TestCase):
    @patch("nextmv.cli.actions.shadow.Application")
    def test_creates_with_all_params(self, mock_app_class):
        mock_test = MagicMock()
        mock_test.to_dict.return_value = {"id": "new-shadow"}
        mock_app = MagicMock()
        mock_app.new_shadow_test.return_value = mock_test
        mock_app_class.return_value = mock_app

        client = MagicMock()
        comparisons = {"baseline": ["candidate-1"]}
        termination = {"maximum_runs": 1000}
        start = {"time": "2024-01-01T00:00:00Z"}

        from nextmv.cli.actions.shadow import create_shadow_test

        result = create_shadow_test(
            client,
            "my-app",
            comparisons=comparisons,
            termination_events=termination,
            shadow_test_id="shadow-id",
            name="My Shadow",
            description="desc",
            start_events=start,
        )

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        mock_app.new_shadow_test.assert_called_once_with(
            comparisons=comparisons,
            termination_events=termination,
            shadow_test_id="shadow-id",
            name="My Shadow",
            description="desc",
            start_events=start,
        )
        self.assertEqual(result, {"id": "new-shadow"})

    @patch("nextmv.cli.actions.shadow.Application")
    def test_creates_with_defaults(self, mock_app_class):
        mock_test = MagicMock()
        mock_test.to_dict.return_value = {"id": "auto-shadow"}
        mock_app = MagicMock()
        mock_app.new_shadow_test.return_value = mock_test
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.shadow import create_shadow_test

        result = create_shadow_test(
            client,
            "my-app",
            comparisons={},
            termination_events={},
        )

        mock_app.new_shadow_test.assert_called_once_with(
            comparisons={},
            termination_events={},
            shadow_test_id=None,
            name=None,
            description=None,
            start_events=None,
        )
        self.assertEqual(result, {"id": "auto-shadow"})


class TestStartShadowTest(unittest.TestCase):
    @patch("nextmv.cli.actions.shadow.Application")
    def test_starts_test(self, mock_app_class):
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.shadow import start_shadow_test

        result = start_shadow_test(client, "my-app", "shadow-1")

        mock_app.start_shadow_test.assert_called_once_with(shadow_test_id="shadow-1")
        self.assertIsNone(result)


class TestStopShadowTest(unittest.TestCase):
    @patch("nextmv.cli.actions.shadow.StopIntent")
    @patch("nextmv.cli.actions.shadow.Application")
    def test_stops_with_cancel_intent(self, mock_app_class, mock_stop_intent):
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_intent = MagicMock()
        mock_stop_intent.return_value = mock_intent

        client = MagicMock()

        from nextmv.cli.actions.shadow import stop_shadow_test

        result = stop_shadow_test(client, "my-app", "shadow-1", intent="cancel")

        mock_stop_intent.assert_called_once_with("cancel")
        mock_app.stop_shadow_test.assert_called_once_with(
            shadow_test_id="shadow-1",
            intent=mock_intent,
        )
        self.assertIsNone(result)

    @patch("nextmv.cli.actions.shadow.StopIntent")
    @patch("nextmv.cli.actions.shadow.Application")
    def test_stops_with_promote_intent(self, mock_app_class, mock_stop_intent):
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_intent = MagicMock()
        mock_stop_intent.return_value = mock_intent

        client = MagicMock()

        from nextmv.cli.actions.shadow import stop_shadow_test

        stop_shadow_test(client, "my-app", "shadow-1", intent="promote")

        mock_stop_intent.assert_called_once_with("promote")


class TestDeleteShadowTest(unittest.TestCase):
    @patch("nextmv.cli.actions.shadow.Application")
    def test_deletes_test(self, mock_app_class):
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.shadow import delete_shadow_test

        result = delete_shadow_test(client, "my-app", "shadow-1")

        mock_app.delete_shadow_test.assert_called_once_with(shadow_test_id="shadow-1")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
