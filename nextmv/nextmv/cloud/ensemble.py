"""
Classes for working with Nextmv Cloud Ensemble Runs.

This module provides classes for interacting with ensemble runs in Nextmv Cloud.
It details the core data structures for ensemble definitions.

Classes
-------
RunGroup
    A structure to group execution of child runs for an ensemble run.
RuleObjective
    An enum that specifies the supported evaluation rule objectives.
ToleranceType
    An enum that specifies the supported tolerance types for evaluation rules.
RuleTolerance
    A structure for defining tolerance thresholds for an evaluation rule
EvaluationRule
    A structure to evaluate run results for an ensemble run.
EnsembleDefinition
    Representation of a Nextmv Cloud Ensemble Definition for an application.
"""

from datetime import datetime
from enum import Enum

from nextmv.base_model import BaseModel


class RunGroup(BaseModel):
    """A structure to group child runs for an ensemble run.

    You can import the `RunGroup` class directly from `cloud`:

    ```python
    from nextmv.cloud import RunGroup
    ```

    This class represents a grouping of child runs that share a configuration
    for ensemble run executions.

    Parameters
    ----------
    id : str
        The unique identifier of the run group.
    instance_id : str
        ID of the app instance that this run group executes on.
    options : dict, optional
        Runtime options/parameters for the application.
    repetitions : int, optional
        The number of times the run is to be repeated on the instance and with
        the options defined in the run group
    """

    id: str
    """The unique identifier of the run group."""
    instance_id: str
    """ID of the app instance that this run group executes on."""
    options: dict | None = None
    """Runtime options/parameters for the application."""
    repetitions: int | None = None
    """The number of times the run is to be repeated on the instance and with
    the options defined in the run group"""


class RuleObjective(str, Enum):
    """The value of this data determines how a value of a run is optimized to
    determined which ensemble child run is the "best" for a given metric and
    rule, as well as which other ones are within tolerance of that run for the
    purposes of selecting a result for the ensemble run from among the child runs.

    You can import the `RuleObjective` class directly from `cloud`:

    ```python
    from nextmv.cloud import RuleObjective
    ```

    This enum specifies the supported evaluation rule objectives.

    Attributes
    ----------
    MAXIMIZE : str
        Maximize the value of the evaluated metric.
    MINIMIZE : str
        Minimize the value of the evaluated metric.
    """

    MAXIMIZE = "maximize"
    """Maximize the value of the evaluated metric."""
    MINIMIZE = "minimize"
    """Minimize the value of the evaluated metric."""


class RuleToleranceType(str, Enum):
    """The type of comparison used to determine if a run metric is within
    tolerance of a the "best" run for that rule and metric

    You can import the `RuleToleranceType` class directly from `cloud`:

    ```python
    from nextmv.cloud import RuleToleranceType
    ```

    This enum specifies the supported tolerance types.

    Attributes
    ----------
    ABSOLUTE : str
        Uses the absolute difference between the value of the "best" run and
        the run being evaluated for tolerance
    RELATIVE : str
        Uses the the percentage of the "best" run by which the run being
        evaluted for tolerance differs. A value of `1` is 100%.
    """

    ABSOLUTE = "absolute"
    """Uses the absolute difference between the value of the "best" run and
    the run being evaluated for tolerance"""
    RELATIVE = "relative"
    """Uses the the percentage of the "best" run by which the run being
    evaluted for tolerance differs. A value of `1` is 100%."""


class RuleTolerance(BaseModel):
    """A structure used to determine if a run is within tolerance of of the best
    run (as determined by the objective of the `EvaluationRule` it is defined on).

    You can import the `RuleTolerance` class directly from `cloud`:

    ```python
    from nextmv.cloud import RuleTolerance
    ```

    This class represents the tolerance on a particular evaluation rule by
    which a child run may be selected as the result of an ensemble run.

    value : float
        The value within which runs can deviate from the "best" run
        for that metric to be considered within tolerance of it.
    type : ToleranceType
        The method by which runs are determined to be within tolerance.
    """

    value: float
    """The value within which runs can deviate from the "best" run
    for that metric to be considered within tolerance of it."""
    type: RuleToleranceType
    """The method by which runs are determined to be within tolerance."""


class EvaluationRule(BaseModel):
    """A structure to evaluate run results for an ensemble run.

    You can import the `EvaluationRule` class directly from `cloud`:

    ```python
    from nextmv.cloud import EvaluationRule
    ```

    This class represents a rule by which the child runs for an ensemble run
    will be evaluated for the purpose of selecting an optimal result for the
    ensemble run.

    Parameters
    ----------
    id : str
        The unique identifier of the evaluation rule.
    statistics_path : str
        The path within the statistics of a run output (conforming to Nextmv
        statistics convention and flattened to a string starting with `$` and
        delimited by `.` e.g. `$.result.value`.)
    objective : RuleObjective
        The objective by which runs are optimized for this rule
    tolerance : RuleTolerance
        The tolerance by which runs can be accepted as a potential result
        for an evaluation rule
    index : int, optional
        The index (non-negative integer) of the evalutation rule. Lower indicies
        are evaluated first.
    """

    id: str
    """The unique identifier of the evaluation rule."""
    statistics_path: str
    """The path within the statistics of a run output (conforming to Nextmv
    statistics convention and flattened to a string starting with `$` and
    delimited by `.` e.g. `$.result.value`.)"""
    objective: RuleObjective
    """The objective by which runs are optimized for this rule"""
    tolerance: RuleTolerance
    """The tolerance by which runs can be accepted as a potential result
    for an evaluation rule"""
    index: int
    """The index (non-negative integer) of the evalutation rule. Lower indicies
    are evaluated first."""


class EnsembleDefinition(BaseModel):
    """An ensemble definition for an application.

    You can import the `EnsembleDefinition` class directly from `cloud`:

    ```python
    from nextmv.cloud import EnsembleDefinition
    ```

    A Nextmv Cloud ensemble definition represents a structure by which an
    application can coordinate and execute, and determine the optimal result of
    an ensemble run.

    Parameters
    ----------
    id : str
        The unique identifier of the ensemble definition.
    application_id : str
        ID of the application that this ensemble definition belongs to.
    name : str
        Human-readable name of the ensemble definition.
    description : str
        Detailed description of the ensemble definition.
    run_groups : list[RunGroup], optional
        The run groups that structure the execution of an ensemble run
    rules : list[EvaluationRule], optional
        The rules by which ensemble child runs are evaluated
        to find an optimal result.
    created_at : datetime
        Timestamp when the ensemble definition was created.
    updated_at : datetime
        Timestamp when the ensemble definition was last updated.
    """

    id: str
    """The unique identifier of the ensemble definition."""
    application_id: str
    """ID of the application that this ensemble definition belongs to."""
    name: str = ""
    """Human-readable name of the ensemble definition."""
    description: str = ""
    """Detailed description of the ensemble definition."""
    run_groups: list[RunGroup]
    """The run groups that structure the execution of an ensemble run"""
    rules: list[EvaluationRule]
    """The rules by which ensemble child runs are evaluated
    to find an optimal result."""
    created_at: datetime
    """Timestamp when the ensemble definition was created."""
    updated_at: datetime
    """Timestamp when the ensemble definition was last updated."""
