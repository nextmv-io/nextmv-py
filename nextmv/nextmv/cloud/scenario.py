"""This module contains definitions for scenario tests.

Classes
-------
ScenarioConfiguration
    Configuration for a scenario with multiple option values.
ScenarioInputType
    Enumeration of input types for a scenario.
ScenarioInput
    Input to be processed in a scenario.
Scenario
    A test case for comparing a decision model with inputs and configurations.
"""

import itertools
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Union


@dataclass
class ScenarioConfiguration:
    """
    Configuration for a scenario.

    You can import the `ScenarioConfiguration` class directly from `cloud`:

    ```python
    from nextmv.cloud import ScenarioConfiguration
    ```

    You can define multiple values for a single option, which will result in
    multiple runs being created. For example, if you have a configuration
    option "x" with values [1, 2], and a configuration option "y" with values
    [3, 4], then the following runs will be created:
    - x=1, y=3
    - x=1, y=4
    - x=2, y=3
    - x=2, y=4

    Parameters
    ----------
    name : str
        Name of the configuration option.
    values : list[str]
        List of values for the configuration option.

    Examples
    --------
    >>> from nextmv.cloud import ScenarioConfiguration
    >>> config = ScenarioConfiguration(name="solver", values=["simplex", "interior-point"])
    """

    name: str
    """Name of the configuration option."""
    values: list[str]
    """List of values for the configuration option."""

    def __post_init__(self):
        """
        Post-initialization method to ensure that the values are unique.

        Raises
        ------
        ValueError
            If the configuration values list is empty.
        """
        if len(self.values) <= 0:
            raise ValueError("Configuration values must be non-empty.")


class ScenarioInputType(str, Enum):
    """
    Type of input for a scenario. This is used to determine how the input
    should be processed.

    You can import the `ScenarioInputType` class directly from `cloud`:

    ```python
    from nextmv.cloud import ScenarioInputType
    ```

    Parameters
    ----------
    INPUT_SET : str
        The data in the scenario is an input set.
    INPUT : str
        The data in the scenario is an input.
    NEW : str
        The data in the scenario is new data.

    Examples
    --------
    >>> from nextmv.cloud import ScenarioInputType
    >>> input_type = ScenarioInputType.INPUT_SET
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
    Input to be processed in a scenario.

    You can import the `ScenarioInput` class directly from `cloud`:

    ```python
    from nextmv.cloud import ScenarioInput
    ```

    The type of input is determined by the `scenario_input_type` attribute.
    The input can be a single input set ID, a list of input IDs, or raw data.
    The data itself of the scenario input is tracked by the `scenario_input_data`
    attribute.

    Parameters
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

    Examples
    --------
    >>> from nextmv.cloud import ScenarioInput, ScenarioInputType
    >>> # Using an existing input set
    >>> input_set = ScenarioInput(
    ...     scenario_input_type=ScenarioInputType.INPUT_SET,
    ...     scenario_input_data="input-set-id-123"
    ... )
    >>> # Using a list of inputs
    >>> inputs = ScenarioInput(
    ...     scenario_input_type=ScenarioInputType.INPUT,
    ...     scenario_input_data=["input-id-1", "input-id-2"]
    ... )
    >>> # Using raw data
    >>> raw_data = ScenarioInput(
    ...     scenario_input_type=ScenarioInputType.NEW,
    ...     scenario_input_data=[{"id": 1, "value": "data1"}, {"id": 2, "value": "data2"}]
    ... )
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

        Raises
        ------
        ValueError
            If the scenario input type and data type don't match:
            - When using INPUT_SET, scenario_input_data must be a string
            - When using INPUT or NEW, scenario_input_data must be a list
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

    You can import the `Scenario` class directly from `cloud`:

    ```python
    from nextmv.cloud import Scenario
    ```

    A scenario encapsulates all the necessary information to run a test case
    against a decision model. Each scenario includes input data, an instance ID,
    and can optionally include configuration options that define different
    variations of the run.

    Parameters
    ----------
    scenario_input : ScenarioInput
        Input for the scenario. The input is composed of a type and data. Make
        sure you use the `ScenarioInput` class to create the input.
    instance_id : str
        ID of the instance to be used for the scenario.
    scenario_id : Optional[str]
        Optional ID of the scenario. The default value will be set as
        `scenario-<index>` if not set.
    configuration : Optional[list[ScenarioConfiguration]]
        Optional configuration for the scenario. Use this attribute to
        configure variation of options for the scenario.

    Examples
    --------
    >>> from nextmv.cloud import Scenario, ScenarioInput, ScenarioInputType, ScenarioConfiguration
    >>> # Creating a simple scenario with an input set
    >>> input_data = ScenarioInput(
    ...     scenario_input_type=ScenarioInputType.INPUT_SET,
    ...     scenario_input_data="input-set-id-123"
    ... )
    >>> scenario = Scenario(
    ...     scenario_input=input_data,
    ...     instance_id="instance-id-456",
    ...     scenario_id="my-test-scenario"
    ... )
    >>>
    >>> # Creating a scenario with configuration options
    >>> config_options = [
    ...     ScenarioConfiguration(name="solver", values=["simplex", "interior-point"]),
    ...     ScenarioConfiguration(name="timeout", values=["10", "30", "60"])
    ... ]
    >>> scenario_with_config = Scenario(
    ...     scenario_input=input_data,
    ...     instance_id="instance-id-456",
    ...     configuration=config_options
    ... )
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
        `configuration` property.

        This method calculates the cross-product of all configuration
        options to generate all possible combinations. If no configuration
        is provided, it returns a list with an empty dictionary.

        Returns
        -------
        list[dict[str, str]]
            A list of dictionaries where each dictionary represents a set of
            options derived from the configuration.

        Examples
        --------
        >>> from nextmv.cloud import Scenario, ScenarioInput, ScenarioInputType, ScenarioConfiguration
        >>> input_data = ScenarioInput(
        ...     scenario_input_type=ScenarioInputType.INPUT_SET,
        ...     scenario_input_data="input-set-id"
        ... )
        >>> config = [
        ...     ScenarioConfiguration(name="x", values=["1", "2"]),
        ...     ScenarioConfiguration(name="y", values=["3", "4"])
        ... ]
        >>> scenario = Scenario(
        ...     scenario_input=input_data,
        ...     instance_id="instance-id",
        ...     configuration=config
        ... )
        >>> scenario.option_combinations()
        [{'x': '1', 'y': '3'}, {'x': '1', 'y': '4'}, {'x': '2', 'y': '3'}, {'x': '2', 'y': '4'}]
        """

        if self.configuration is None or len(self.configuration) == 0:
            return [{}]

        keys, value_lists = zip(*((config.name, config.values) for config in self.configuration))
        combinations = [dict(zip(keys, values)) for values in itertools.product(*value_lists)]

        return combinations


def _option_sets(scenarios: list[Scenario]) -> dict[str, dict[str, dict[str, str]]]:
    """
    Creates options sets that are derived from `scenarios`.

    The options sets are grouped by scenario ID. The cross-product of the
    configuration options is created to generate all possible combinations
    of options. Each combination is given a unique key based on the scenario ID
    and a combination index.

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

    Examples
    --------
    >>> from nextmv.cloud import Scenario, ScenarioInput, ScenarioInputType, ScenarioConfiguration
    >>> input_data = ScenarioInput(
    ...     scenario_input_type=ScenarioInputType.INPUT_SET,
    ...     scenario_input_data="input-set-id"
    ... )
    >>> config = [ScenarioConfiguration(name="x", values=["1", "2"])]
    >>> scenario = Scenario(
    ...     scenario_input=input_data,
    ...     instance_id="instance-id",
    ...     scenario_id="test-scenario",
    ...     configuration=config
    ... )
    >>> _option_sets([scenario])
    {'test-scenario': {'test-scenario_0': {'x': '1'}, 'test-scenario_1': {'x': '2'}}}
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
    Maps scenarios to their IDs.

    This function builds a dictionary that maps each scenario to its ID.
    If a scenario doesn't have an ID defined, one is created using the format
    "scenario-{index}". The function also checks that there are no duplicate
    scenario IDs in the provided list.

    Parameters
    ----------
    scenarios : list[Scenario]
        List of scenarios to be mapped.

    Returns
    -------
    dict[str, Scenario]
        A dictionary where keys are scenario IDs and values are the corresponding
        Scenario objects.

    Raises
    ------
    ValueError
        If duplicate scenario IDs are found in the list.

    Examples
    --------
    >>> from nextmv.cloud import Scenario, ScenarioInput, ScenarioInputType
    >>> input_data = ScenarioInput(
    ...     scenario_input_type=ScenarioInputType.INPUT_SET,
    ...     scenario_input_data="input-set-id"
    ... )
    >>> scenarios = [
    ...     Scenario(scenario_input=input_data, instance_id="instance-1", scenario_id="test-1"),
    ...     Scenario(scenario_input=input_data, instance_id="instance-2")
    ... ]
    >>> result = _scenarios_by_id(scenarios)
    >>> sorted(list(result.keys()))
    ['scenario-2', 'test-1']
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
