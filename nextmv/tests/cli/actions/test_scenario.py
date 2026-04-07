"""Tests for nextmv.cli.actions.scenario."""

import unittest
from unittest.mock import MagicMock, patch


class TestBuildScenario(unittest.TestCase):
    def test_builds_from_input_set_id(self):
        from nextmv.cli.actions.scenario import build_scenario

        s = {
            "instance_id": "inst-1",
            "scenario_input": {"input_set_id": "set-1"},
        }
        scenario = build_scenario(s)
        self.assertEqual(scenario.instance_id, "inst-1")
        self.assertEqual(scenario.scenario_input.scenario_input_data, "set-1")

    def test_builds_from_explicit_type(self):
        from nextmv.cli.actions.scenario import build_scenario

        s = {
            "instance_id": "inst-1",
            "scenario_input": {
                "scenario_input_type": "input_set",
                "scenario_input_data": "set-2",
            },
        }
        scenario = build_scenario(s)
        self.assertEqual(scenario.scenario_input.scenario_input_data, "set-2")

    def test_raises_on_missing_instance_id(self):
        from nextmv.cli.actions.scenario import build_scenario

        with self.assertRaises(ValueError):
            build_scenario({"scenario_input": {"input_set_id": "x"}})

    def test_raises_on_missing_scenario_input(self):
        from nextmv.cli.actions.scenario import build_scenario

        with self.assertRaises(ValueError):
            build_scenario({"instance_id": "inst-1"})

    def test_raises_on_invalid_scenario_input(self):
        from nextmv.cli.actions.scenario import build_scenario

        with self.assertRaises(ValueError):
            build_scenario({"instance_id": "inst-1", "scenario_input": {}})

    def test_builds_with_list_configuration(self):
        from nextmv.cli.actions.scenario import build_scenario

        s = {
            "instance_id": "inst-1",
            "scenario_input": {"input_set_id": "set-1"},
            "configuration": [{"name": "opt1", "values": ["v1", "v2"]}],
        }
        scenario = build_scenario(s)
        self.assertEqual(len(scenario.configuration), 1)
        self.assertEqual(scenario.configuration[0].name, "opt1")

    def test_builds_with_dict_configuration(self):
        from nextmv.cli.actions.scenario import build_scenario

        s = {
            "instance_id": "inst-1",
            "scenario_input": {"input_set_id": "set-1"},
            "configuration": {"solve.duration": "5s"},
        }
        scenario = build_scenario(s)
        self.assertEqual(len(scenario.configuration), 1)


class TestListScenarioTests(unittest.TestCase):
    @patch("nextmv.cli.actions.scenario.Application")
    def test_returns_list_of_dicts(self, mock_app_class):
        mock_t1 = MagicMock()
        mock_t1.to_dict.return_value = {"id": "test-1"}
        mock_app = MagicMock()
        mock_app.list_scenario_tests.return_value = [mock_t1]
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.scenario import list_scenario_tests

        result = list_scenario_tests(client, "my-app")

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        self.assertEqual(result, [{"id": "test-1"}])

    @patch("nextmv.cli.actions.scenario.Application")
    def test_empty_list(self, mock_app_class):
        mock_app = MagicMock()
        mock_app.list_scenario_tests.return_value = []
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.scenario import list_scenario_tests

        result = list_scenario_tests(client, "my-app")

        self.assertEqual(result, [])


class TestGetScenarioTest(unittest.TestCase):
    @patch("nextmv.cli.actions.scenario.Application")
    def test_returns_dict(self, mock_app_class):
        mock_test = MagicMock()
        mock_test.to_dict.return_value = {"id": "test-1"}
        mock_app = MagicMock()
        mock_app.scenario_test.return_value = mock_test
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.scenario import get_scenario_test

        result = get_scenario_test(client, "my-app", "test-1")

        mock_app.scenario_test.assert_called_once_with(scenario_test_id="test-1")
        self.assertEqual(result, {"id": "test-1"})


class TestCreateScenarioTest(unittest.TestCase):
    @patch("nextmv.cli.actions.scenario.build_scenario")
    @patch("nextmv.cli.actions.scenario.Application")
    def test_creates_with_all_params(self, mock_app_class, mock_build):
        mock_scenario = MagicMock()
        mock_build.return_value = mock_scenario
        mock_app = MagicMock()
        mock_app.new_scenario_test.return_value = "new-test-id"
        mock_app_class.return_value = mock_app

        client = MagicMock()
        scenarios = [{"instance_id": "inst-1", "scenario_input": {"input_set_id": "s"}}]

        from nextmv.cli.actions.scenario import create_scenario_test

        result = create_scenario_test(
            client,
            "my-app",
            scenarios=scenarios,
            scenario_test_id="tid",
            name="My Test",
            description="desc",
            repetitions=2,
            content_type="json",
        )

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        mock_build.assert_called_once_with(scenarios[0])
        mock_app.new_scenario_test.assert_called_once_with(
            scenarios=[mock_scenario],
            id="tid",
            name="My Test",
            description="desc",
            repetitions=2,
            content_type="json",
        )
        self.assertEqual(result, "new-test-id")

    @patch("nextmv.cli.actions.scenario.build_scenario")
    @patch("nextmv.cli.actions.scenario.Application")
    def test_creates_with_defaults(self, mock_app_class, mock_build):
        mock_scenario = MagicMock()
        mock_build.return_value = mock_scenario
        mock_app = MagicMock()
        mock_app.new_scenario_test.return_value = "auto-id"
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.scenario import create_scenario_test

        result = create_scenario_test(client, "my-app", scenarios=[{}])

        mock_app.new_scenario_test.assert_called_once_with(
            scenarios=[mock_scenario],
            id=None,
            name=None,
            description=None,
            repetitions=0,
            content_type=None,
        )
        self.assertEqual(result, "auto-id")


class TestDeleteScenarioTest(unittest.TestCase):
    @patch("nextmv.cli.actions.scenario.Application")
    def test_deletes_test(self, mock_app_class):
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.scenario import delete_scenario_test

        result = delete_scenario_test(client, "my-app", "test-1")

        mock_app.delete_scenario_test.assert_called_once_with(scenario_test_id="test-1")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
