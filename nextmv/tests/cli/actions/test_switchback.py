"""Tests for nextmv.cli.actions.switchback."""

import unittest
from unittest.mock import MagicMock, patch


class TestListSwitchbackTests(unittest.TestCase):
    @patch("nextmv.cli.actions.switchback.Application")
    def test_returns_list_of_dicts(self, mock_app_class):
        mock_t = MagicMock()
        mock_t.to_dict.return_value = {"id": "sb-1"}
        mock_app = MagicMock()
        mock_app.list_switchback_tests.return_value = [mock_t]
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.switchback import list_switchback_tests

        result = list_switchback_tests(client, "my-app")

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        self.assertEqual(result, [{"id": "sb-1"}])

    @patch("nextmv.cli.actions.switchback.Application")
    def test_empty_list(self, mock_app_class):
        mock_app = MagicMock()
        mock_app.list_switchback_tests.return_value = []
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.switchback import list_switchback_tests

        result = list_switchback_tests(client, "my-app")

        self.assertEqual(result, [])


class TestGetSwitchbackTest(unittest.TestCase):
    @patch("nextmv.cli.actions.switchback.Application")
    def test_returns_dict(self, mock_app_class):
        mock_test = MagicMock()
        mock_test.to_dict.return_value = {"id": "sb-1", "status": "running"}
        mock_app = MagicMock()
        mock_app.switchback_test.return_value = mock_test
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.switchback import get_switchback_test

        result = get_switchback_test(client, "my-app", "sb-1")

        mock_app.switchback_test.assert_called_once_with(switchback_test_id="sb-1")
        self.assertEqual(result, {"id": "sb-1", "status": "running"})


class TestCreateSwitchbackTest(unittest.TestCase):
    @patch("nextmv.cli.actions.switchback.TestComparisonSingle")
    @patch("nextmv.cli.actions.switchback.Application")
    def test_creates_with_all_params(self, mock_app_class, mock_comparison_class):
        mock_comparison = MagicMock()
        mock_comparison_class.return_value = mock_comparison
        mock_test = MagicMock()
        mock_test.to_dict.return_value = {"id": "new-sb"}
        mock_app = MagicMock()
        mock_app.new_switchback_test.return_value = mock_test
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.switchback import create_switchback_test

        result = create_switchback_test(
            client,
            "my-app",
            baseline_instance_id="baseline-1",
            candidate_instance_id="candidate-1",
            unit_duration_minutes=60.0,
            units=10,
            switchback_test_id="sb-id",
            name="My Switchback",
            description="desc",
        )

        mock_comparison_class.assert_called_once_with(
            baseline_instance_id="baseline-1",
            candidate_instance_id="candidate-1",
        )
        mock_app.new_switchback_test.assert_called_once_with(
            comparison=mock_comparison,
            unit_duration_minutes=60.0,
            units=10,
            switchback_test_id="sb-id",
            name="My Switchback",
            description="desc",
        )
        self.assertEqual(result, {"id": "new-sb"})

    @patch("nextmv.cli.actions.switchback.TestComparisonSingle")
    @patch("nextmv.cli.actions.switchback.Application")
    def test_creates_with_defaults(self, mock_app_class, mock_comparison_class):
        mock_comparison = MagicMock()
        mock_comparison_class.return_value = mock_comparison
        mock_test = MagicMock()
        mock_test.to_dict.return_value = {"id": "auto-sb"}
        mock_app = MagicMock()
        mock_app.new_switchback_test.return_value = mock_test
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.switchback import create_switchback_test

        result = create_switchback_test(
            client,
            "my-app",
            baseline_instance_id="base",
            candidate_instance_id="cand",
            unit_duration_minutes=30.0,
            units=5,
        )

        mock_app.new_switchback_test.assert_called_once_with(
            comparison=mock_comparison,
            unit_duration_minutes=30.0,
            units=5,
            switchback_test_id=None,
            name=None,
            description=None,
        )
        self.assertEqual(result, {"id": "auto-sb"})


class TestStartSwitchbackTest(unittest.TestCase):
    @patch("nextmv.cli.actions.switchback.Application")
    def test_starts_test(self, mock_app_class):
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.switchback import start_switchback_test

        result = start_switchback_test(client, "my-app", "sb-1")

        mock_app.start_switchback_test.assert_called_once_with(switchback_test_id="sb-1")
        self.assertIsNone(result)


class TestStopSwitchbackTest(unittest.TestCase):
    @patch("nextmv.cli.actions.switchback.StopIntent")
    @patch("nextmv.cli.actions.switchback.Application")
    def test_stops_with_cancel_intent(self, mock_app_class, mock_stop_intent):
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_intent = MagicMock()
        mock_stop_intent.return_value = mock_intent

        client = MagicMock()

        from nextmv.cli.actions.switchback import stop_switchback_test

        result = stop_switchback_test(client, "my-app", "sb-1", intent="cancel")

        mock_stop_intent.assert_called_once_with("cancel")
        mock_app.stop_switchback_test.assert_called_once_with(
            switchback_test_id="sb-1",
            intent=mock_intent,
        )
        self.assertIsNone(result)


class TestDeleteSwitchbackTest(unittest.TestCase):
    @patch("nextmv.cli.actions.switchback.Application")
    def test_deletes_test(self, mock_app_class):
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.switchback import delete_switchback_test

        result = delete_switchback_test(client, "my-app", "sb-1")

        mock_app.delete_switchback_test.assert_called_once_with(switchback_test_id="sb-1")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
