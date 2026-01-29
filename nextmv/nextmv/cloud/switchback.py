"""
Classes for working with Nextmv Cloud switchback tests.

This module provides classes for interacting with switchback tests in Nextmv Cloud.
It details the core data structures for these types of experiments.

Classes
-------
TestComparisonSingle
    A structure to define a single comparison for tests.
SwitchbackPlanUnit
    A structure to define a single unit in the switchback plan.
SwitchbackPlan
    A structure to define the switchback plan for tests.
SwitchbackTestMetadata
    Metadata for a Nextmv Cloud switchback test.
SwitchbackTest
    A Nextmv Cloud switchback test definition.
"""

from datetime import datetime

from pydantic import AliasChoices, Field

from nextmv.base_model import BaseModel
from nextmv.cloud.batch_experiment import ExperimentStatus
from nextmv.run import Run


class TestComparisonSingle(BaseModel):
    """
    A structure to define a single comparison for tests.

    You can import the `TestComparisonSingle` class directly from `cloud`:

    ```python
    from nextmv.cloud import TestComparisonSingle
    ```

    Parameters
    ----------
    baseline_instance_id : str
        ID of the baseline instance for comparison.
    candidate_instance_id : str
        ID of the candidate instance for comparison.
    """

    __test__ = False  # Prevents pytest from collecting this class as a test case

    baseline_instance_id: str
    """ID of the baseline instance for comparison."""
    candidate_instance_id: str
    """ID of the candidate instance for comparison."""


class SwitchbackPlanUnit(BaseModel):
    """
    A structure to define a single unit in the switchback plan.

    You can import the `SwitchbackPlanUnit` class directly from `cloud`:

    ```python
    from nextmv.cloud import SwitchbackPlanUnit
    ```

    Parameters
    ----------
    duration_minutes : float
        Duration of this interval in minutes.
    instance_id : str
        ID of the instance to run during this unit.
    index : int
        Index of this unit in the switchback plan.
    """

    duration_minutes: float
    """Duration of this interval in minutes."""
    instance_id: str
    """ID of the instance to run during this unit."""
    index: int
    """Index of this unit in the switchback plan."""


class SwitchbackPlan(BaseModel):
    """
    A structure to define the switchback plan for tests.

    You can import the `SwitchbackPlan` class directly from `cloud`:

    ```python
    from nextmv.cloud import SwitchbackPlan
    ```

    Parameters
    ----------
    start : datetime, optional
        Start time of the switchback test.
    units : list[SwitchbackPlanUnit], optional
        List of switchback plan units.
    """

    start: datetime | None = None
    """Start time of the switchback test."""
    units: list[SwitchbackPlanUnit] | None = None
    """List of switchback plan units."""


class SwitchbackTestMetadata(BaseModel):
    """
    Metadata for a Nextmv Cloud switchback test.

    You can import the `SwitchbackTestMetadata` class directly from `cloud`:

    ```python
    from nextmv.cloud import SwitchbackTestMetadata
    ```

    Parameters
    ----------
    switchback_test_id : str, optional
        The unique identifier of the switchback test.
    name : str, optional
        Name of the switchback test.
    description : str, optional
        Description of the switchback test.
    app_id : str, optional
        ID of the application to which the switchback test belongs.
    created_at : datetime, optional
        Creation date of the switchback test.
    updated_at : datetime, optional
        Last update date of the switchback test.
    status : ExperimentStatus, optional
        The current status of the switchback test.
    """

    switchback_test_id: str | None = Field(
        serialization_alias="id",
        validation_alias=AliasChoices("id", "switchback_test_id"),
        default=None,
    )
    """The unique identifier of the switchback test."""
    name: str | None = None
    """Name of the switchback test."""
    description: str | None = None
    """Description of the switchback test."""
    app_id: str | None = None
    """ID of the application to which the switchback test belongs."""
    created_at: datetime | None = None
    """Creation date of the switchback test."""
    updated_at: datetime | None = None
    """Last update date of the switchback test."""
    status: ExperimentStatus | None = None
    """The current status of the switchback test."""


# This class uses some fields defined in SwitchbackTestMetadata. We are not
# using inheritance to help the user understand the full structure when using
# tools like intellisense.
class SwitchbackTest(BaseModel):
    """
    A Nextmv Cloud switchback test definition.

    A switchback test is a type of experiment where runs are executed in
    sequential intervals, alternating between different instances to compare
    their performance.

    You can import the `SwitchbackTest` class directly from `cloud`:

    ```python
    from nextmv.cloud import SwitchbackTest
    ```

    Parameters
    ----------
    switchback_test_id : str, optional
        The unique identifier of the switchback test.
    name : str, optional
        Name of the switchback test.
    description : str, optional
        Description of the switchback test.
    app_id : str, optional
        ID of the application to which the switchback test belongs.
    created_at : datetime, optional
        Creation date of the switchback test.
    updated_at : datetime, optional
        Last update date of the switchback test.
    status : ExperimentStatus, optional
        The current status of the switchback test.
    started_at : datetime, optional
        Start date of the switchback test, if applicable.
    completed_at : datetime, optional
        Completion date of the switchback test, if applicable.
    comparison : TestComparisonSingle, optional
        Test comparison defined in the switchback test.
    plan : SwitchbackPlan, optional
        Switchback plan defining the intervals and instance switching.
    runs : list[Run], optional
        List of runs in the switchback test.
    """

    switchback_test_id: str | None = Field(
        serialization_alias="id",
        validation_alias=AliasChoices("id", "switchback_test_id"),
        default=None,
    )
    """The unique identifier of the switchback test."""
    name: str | None = None
    """Name of the switchback test."""
    description: str | None = None
    """Description of the switchback test."""
    app_id: str | None = None
    """ID of the application to which the switchback test belongs."""
    created_at: datetime | None = None
    """Creation date of the switchback test."""
    updated_at: datetime | None = None
    """Last update date of the switchback test."""
    status: ExperimentStatus | None = None
    """The current status of the switchback test."""
    started_at: datetime | None = None
    """Start date of the switchback test, if applicable."""
    completed_at: datetime | None = None
    """Completion date of the switchback test, if applicable."""
    comparison: TestComparisonSingle | None = None
    """Test comparison defined in the switchback test."""
    plan: SwitchbackPlan | None = None
    """Switchback plan defining the intervals and instance switching."""
    runs: list[Run] | None = None
    """List of runs in the switchback test."""
