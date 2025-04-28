"""This module contains definitions for scenario tests."""

from typing import Optional

from pydantic import AliasChoices, Field

from nextmv.base_model import BaseModel


class ScenarioConfiguration(BaseModel):
    """
    Configuration for a scenario.
    """


class Scenario(BaseModel):
    """
    A scenario is a test case that is used to compare a decision model being
    executed with a set of inputs and configurations.
    """

    instance_id: str
    """ID of the instance to be used for the scenario."""


class ScenarioTest(BaseModel):
    """
    A scenario test allows you to test and compare different scenarios in
    one test.

    A scenario test is a collection of scenarios that are executed
    against a decision model. Each scenario is a test case that
    is used to compare a decision model being executed with a set
    of inputs and configurations.

    Attributes
    ----------
    name : str
        Name of the scenario test.
    scenario_test_id : str
        ID of the scenario test.
    scenarios : list[Scenario]
        List of scenarios to be tested.
    description : Optional[str]
        Optional description of the scenario test.
    repetitions : Optional[int]
        Number of times to repeat the scenario test. Default is 0.
    """

    name: str
    """Name of the scenario test."""
    scenario_test_id: str = Field(
        serialization_alias="id",
        validation_alias=AliasChoices("id", "scenario_test_id"),
    )
    """ID of the scenario test."""
    scenarios: list[Scenario]
    """List of scenarios to be tested."""

    description: Optional[str] = None
    """Optional description of the scenario test."""
    repetitions: Optional[int] = 0
    """Number of times to repeat the scenario test."""
