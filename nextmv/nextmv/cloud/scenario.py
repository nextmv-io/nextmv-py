"""This module contains definitions for scenario tests."""

import itertools
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Union


@dataclass
class ScenarioConfiguration:
    """
    Configuration for a scenario.

    You can define multiple values for a single option, which will result in
    multiple runs being created. For example, if you have a configuration
    option "x" with values [1, 2], and a configuration option "y" with values
    [3, 4], then the following runs will be created:
    - x=1, y=3
    - x=1, y=4
    - x=2, y=3
    - x=2, y=4

    Attributes
    ----------
    name : str
        Name of the configuration option.
    values : list[str]
        List of values for the configuration option.
    """

    name: str
    """Name of the configuration option."""
    values: list[str]
    """List of values for the configuration option."""

    def __post_init__(self):
        """
        Post-initialization method to ensure that the values are unique.
        """
        if len(self.values) <= 0:
            raise ValueError("Configuration values must be non-empty.")


class ScenarioInputType(str, Enum):
    """
    Type of input for a scenario. This is used to determine how the input
    should be processed.

    Attributes
    ----------
    INPUT_SET : str
        The data in the scenario is an input set.
    INPUT : str
        The data in the scenario is an input.
    NEW : str
        The data in the scenario is new data.
    """

    INPUT_SET = "input_set"
    """The data in the scenario is an input set."""
    INPUT = "input"
    """The data in the scenario is an input."""
    NEW = "new"
    """The data in the scenario is new data."""


@dataclass
class ScenarioInput:
    """
    Input to be processed in a scenario. The type of input is determined by
    the `scenario_input_type` attribute. The input can be a single input set
    ID, a list of input IDs, or raw data. The data itself of the scenario input
    is tracked by the `scenario_input_data` attribute.

    Attributes
    ----------
    scenario_input_type : ScenarioInputType
        Type of input for the scenario. This is used to determine how the input
        should be processed.
    scenario_input_data : Union[str, list[str], list[dict[str, Any]]]
        Input data for the scenario. This can be a single input set ID
        (`str`), a list of input IDs (`list[str]`), or raw data
        (`list[dict[str, Any]]`). If you provide a `list[str]` (list of
        inputs), a new input set will be created using these inputs. A similar
        behavior occurs when providing raw data (`list[dict[str, Any]]`). All
        the entries in the list of raw dicts will be collected to create a new
        input set.
    """

    scenario_input_type: ScenarioInputType
    """
    Type of input for the scenario. This is used to determine how the input
    should be processed.
    """
    scenario_input_data: Union[
        str,  # Input set ID
        list[str],  # List of Input IDs
        list[dict[str, Any]],  # Raw data
    ]
    """
    Input data for the scenario. This can be a single input set ID (`str`), a
    list of input IDs (`list[str]`), or raw data (`list[dict[str, Any]]`).
    """

    def __post_init__(self):
        """
        Post-initialization method to ensure that the input data is valid.
        """
        if self.scenario_input_type == ScenarioInputType.INPUT_SET and not isinstance(self.scenario_input_data, str):
            raise ValueError("Scenario input type must be a string when using an input set.")
        elif self.scenario_input_type == ScenarioInputType.INPUT and not isinstance(self.scenario_input_data, list):
            raise ValueError("Scenario input type must be a list when using an input.")
        elif self.scenario_input_type == ScenarioInputType.NEW and not isinstance(self.scenario_input_data, list):
            raise ValueError("Scenario input type must be a list when using new data.")


@dataclass
class Scenario:
    """
    A scenario is a test case that is used to compare a decision model being
    executed with a set of inputs and configurations.

    Attributes
    ----------
    scenario_input : ScenarioInput
        Input for the scenario. The input is composed of a type and data. Make
        sure you use the `ScenarioInput` class to create the input.
    scenario_id : Optional[str]
        Optional ID of the scenario. The default value will be set as
        `scenario-<index>` if not set.
    instance_id : str
        ID of the instance to be used for the scenario.
    configuration : Optional[ScenarioConfiguration]
        Optional configuration for the scenario. Use this attribute to
        configure variation of options for the scenario.
    """

    scenario_input: ScenarioInput
    """
    Input for the scenario. The input is composed of a type and data. Make sure
    you use the `ScenarioInput` class to create the input.
    """
    instance_id: str
    """ID of the instance to be used for the scenario."""

    scenario_id: Optional[str] = None
    """
    Optional ID of the scenario. The default value will be set as
    `scenario-<index>` if not set.
    """
    configuration: Optional[list[ScenarioConfiguration]] = None
    """Optional configuration for the scenario. Use this attribute to configure
    variation of options for the scenario.
    """

    def option_combinations(self) -> list[dict[str, str]]:
        """
        Creates the combination of options that are derived from the
        `configuration` property. The cross-product of the configuration
        options is created to generate all possible combinations of options.

        Returns
        -------
        list[dict[str, str]]
            A list of dictionaries where each dictionary represents a set of
            options derived from the configuration.
        """

        if self.configuration is None or len(self.configuration) == 0:
            return [{}]

        keys, value_lists = zip(*((config.name, config.values) for config in self.configuration))
        combinations = [dict(zip(keys, values)) for values in itertools.product(*value_lists)]

        return combinations


def _option_sets(scenarios: list[Scenario]) -> dict[str, dict[str, dict[str, str]]]:
    """
    Creates options sets that are derived from `scenarios`. The options sets
    are grouped by scenario ID. The cross-product of the configuration
    options is created to generate all possible combinations of options.

    Parameters
    ----------
    scenarios : list[Scenario]
        List of scenarios to be tested.

    Returns
    -------
    dict[str, dict[str, dict[str, str]]]
        A dictionary where the keys are scenario IDs and the values are
        dictionaries of option sets. Each option set is a dictionary where the
        keys are option names and the values are the corresponding option
        values.
    """

    sets_by_scenario = {}
    scenarios_by_id = _scenarios_by_id(scenarios)
    for scenario_id, scenario in scenarios_by_id.items():
        combinations = scenario.option_combinations()
        option_sets = {}
        for comb_ix, combination in enumerate(combinations):
            option_sets[f"{scenario_id}_{comb_ix}"] = combination

        sets_by_scenario[scenario_id] = option_sets

    return sets_by_scenario


def _scenarios_by_id(scenarios: list[Scenario]) -> dict[str, Scenario]:
    """
    This function maps a scenario to its ID. A scenario ID is created if it
    wasn’t defined. This function also checks that there are no duplicate
    scenario IDs.
    """

    scenario_by_id = {}
    ids_used = {}
    for scenario_ix, scenario in enumerate(scenarios, start=1):
        scenario_id = f"scenario-{scenario_ix}" if scenario.scenario_id is None else scenario.scenario_id
        used = ids_used.get(scenario_id) is not None
        if used:
            raise ValueError(f"Duplicate scenario ID found: {scenario_id}")

        ids_used[scenario_id] = True
        scenario_by_id[scenario_id] = scenario

    return scenario_by_id
