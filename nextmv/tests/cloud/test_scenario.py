import unittest

from nextmv.cloud.scenario import Scenario, ScenarioConfiguration, _option_sets, _scenarios_by_id


class TestScenarioTest(unittest.TestCase):
    def test_option_sets(self):
        all_option_sets = _option_sets(
            scenarios=[
                Scenario(
                    scenario_input="",
                    instance_id="",
                    configuration=[
                        ScenarioConfiguration(
                            name="solve.duration",
                            values=["1s", "2s"],
                        ),
                        ScenarioConfiguration(
                            name="solve.iterations",
                            values=["1", "2"],
                        ),
                        ScenarioConfiguration(
                            name="solve.limit",
                            values=["10", "20"],
                        ),
                    ],
                ),
                Scenario(
                    scenario_input="",
                    instance_id="",
                    configuration=[
                        ScenarioConfiguration(
                            name="solve.duration",
                            values=["10s", "20s"],
                        ),
                        ScenarioConfiguration(
                            name="solve.iterations",
                            values=["10", "20"],
                        ),
                        ScenarioConfiguration(
                            name="solve.limit",
                            values=["100", "200"],
                        ),
                    ],
                ),
            ],
        )

        self.assertDictEqual(
            all_option_sets,
            {
                "scenario-1": {
                    "scenario-1_0": {"solve.duration": "1s", "solve.iterations": "1", "solve.limit": "10"},
                    "scenario-1_1": {"solve.duration": "1s", "solve.iterations": "1", "solve.limit": "20"},
                    "scenario-1_2": {"solve.duration": "1s", "solve.iterations": "2", "solve.limit": "10"},
                    "scenario-1_3": {"solve.duration": "1s", "solve.iterations": "2", "solve.limit": "20"},
                    "scenario-1_4": {"solve.duration": "2s", "solve.iterations": "1", "solve.limit": "10"},
                    "scenario-1_5": {"solve.duration": "2s", "solve.iterations": "1", "solve.limit": "20"},
                    "scenario-1_6": {"solve.duration": "2s", "solve.iterations": "2", "solve.limit": "10"},
                    "scenario-1_7": {"solve.duration": "2s", "solve.iterations": "2", "solve.limit": "20"},
                },
                "scenario-2": {
                    "scenario-2_0": {"solve.duration": "10s", "solve.iterations": "10", "solve.limit": "100"},
                    "scenario-2_1": {"solve.duration": "10s", "solve.iterations": "10", "solve.limit": "200"},
                    "scenario-2_2": {"solve.duration": "10s", "solve.iterations": "20", "solve.limit": "100"},
                    "scenario-2_3": {"solve.duration": "10s", "solve.iterations": "20", "solve.limit": "200"},
                    "scenario-2_4": {"solve.duration": "20s", "solve.iterations": "10", "solve.limit": "100"},
                    "scenario-2_5": {"solve.duration": "20s", "solve.iterations": "10", "solve.limit": "200"},
                    "scenario-2_6": {"solve.duration": "20s", "solve.iterations": "20", "solve.limit": "100"},
                    "scenario-2_7": {"solve.duration": "20s", "solve.iterations": "20", "solve.limit": "200"},
                },
            },
        )

    def test_scenarios_by_id(self):
        scenarios = [
            Scenario(
                scenario_input=None,
                instance_id="foo",
            ),
            Scenario(
                scenario_input=None,
                instance_id="bar",
            ),
        ]

        scenarios_by_id = _scenarios_by_id(scenarios)
        self.assertEqual(len(scenarios_by_id), 2)

        # Scenarios cannot have duplicate IDs.
        scenarios.append(
            Scenario(
                scenario_id="scenario-1",
                scenario_input=None,
                instance_id="foo",
            ),
        )
        with self.assertRaises(ValueError):
            scenarios_by_id = _scenarios_by_id(scenarios)


class TestScenario(unittest.TestCase):
    def test_option_combinations(self):
        scenario = Scenario(
            scenario_input="",
            instance_id="",
            configuration=[
                ScenarioConfiguration(
                    name="solve.duration",
                    values=["1s", "2s"],
                ),
                ScenarioConfiguration(
                    name="solve.iterations",
                    values=["1", "2"],
                ),
                ScenarioConfiguration(
                    name="solve.limit",
                    values=["10", "20"],
                ),
            ],
        )
        combinations = scenario.option_combinations()

        self.assertListEqual(
            combinations,
            [
                {"solve.duration": "1s", "solve.iterations": "1", "solve.limit": "10"},
                {"solve.duration": "1s", "solve.iterations": "1", "solve.limit": "20"},
                {"solve.duration": "1s", "solve.iterations": "2", "solve.limit": "10"},
                {"solve.duration": "1s", "solve.iterations": "2", "solve.limit": "20"},
                {"solve.duration": "2s", "solve.iterations": "1", "solve.limit": "10"},
                {"solve.duration": "2s", "solve.iterations": "1", "solve.limit": "20"},
                {"solve.duration": "2s", "solve.iterations": "2", "solve.limit": "10"},
                {"solve.duration": "2s", "solve.iterations": "2", "solve.limit": "20"},
            ],
        )
