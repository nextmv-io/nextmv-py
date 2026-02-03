"""
Classes for working with Nextmv Cloud shadow tests.

This module provides classes for interacting with shadow tests in Nextmv Cloud.
It details the core data structures for these types of experiments.

Classes
-------
TestComparison
    A structure to define comparison parameters for tests.
StartEvents
    A structure to define start events for tests.
TerminationEvents
    A structure to define termination events for tests.
ShadowTestMetadata
    Metadata for a Nextmv Cloud shadow test.
ShadowTest
    A Nextmv Cloud shadow test definition.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import AliasChoices, Field

from nextmv.base_model import BaseModel
from nextmv.cloud.batch_experiment import ExperimentStatus
from nextmv.run import Run


class TestComparison(BaseModel):
    """
    A structure to define comparison parameters for tests.

    You can import the `TestComparison` class directly from `cloud`:

    ```python
    from nextmv.cloud import TestComparison
    ```

    Parameters
    ----------
    baseline_instance_id : str
        ID of the baseline instance for comparison.
    candidate_instance_ids : list[str]
        List of candidate instance IDs to compare against the baseline.
    """

    baseline_instance_id: str
    """ID of the baseline instance for comparison."""
    candidate_instance_ids: list[str]
    """List of candidate instance IDs to compare against the baseline."""


class StartEvents(BaseModel):
    """
    A structure to define start events for tests.

    You can import the `StartEvents` class directly from `cloud`:

    ```python
    from nextmv.cloud import StartEvents
    ```

    Parameters
    ----------
    time : datetime, optional
        Scheduled time for the test to start.
    """

    time: datetime | None = None
    """Scheduled time for the test to start."""


class TerminationEvents(BaseModel):
    """
    A structure to define termination events for tests.

    You can import the `TerminationEvents` class directly from `cloud`:

    ```python
    from nextmv.cloud import TerminationEvents
    ```

    Parameters
    ----------
    time : datetime, optional
        Scheduled time for the test to terminate.
    """

    maximum_runs: int
    """
    Maximum number of runs for the test. Value must be between 1 and 300.
    """
    time: datetime | None = None
    """
    Scheduled time for the test to terminate. A zero value means no
    limit.
    """

    def model_post_init(self, __context):
        if self.maximum_runs < 1 or self.maximum_runs > 300:
            raise ValueError("maximum_runs must be between 1 and 300")


class ShadowTestMetadata(BaseModel):
    """
    Metadata for a Nextmv Cloud shadow test.

    You can import the `ShadowTestMetadata` class directly from `cloud`:

    ```python
    from nextmv.cloud import ShadowTestMetadata
    ```

    Parameters
    ----------
    shadow_test_id : str, optional
        The unique identifier of the shadow test.
    name : str, optional
        Name of the shadow test.
    description : str, optional
        Description of the shadow test.
    app_id : str, optional
        ID of the application to which the shadow test belongs.
    created_at : datetime, optional
        Creation date of the shadow test.
    updated_at : datetime, optional
        Last update date of the shadow test.
    status : ExperimentStatus, optional
        The current status of the shadow test.
    """

    shadow_test_id: str | None = Field(
        serialization_alias="id",
        validation_alias=AliasChoices("id", "shadow_test_id"),
        default=None,
    )
    """The unique identifier of the shadow test."""
    name: str | None = None
    """Name of the shadow test."""
    description: str | None = None
    """Description of the shadow test."""
    app_id: str | None = None
    """ID of the application to which the shadow test belongs."""
    created_at: datetime | None = None
    """Creation date of the shadow test."""
    updated_at: datetime | None = None
    """Last update date of the shadow test."""
    status: ExperimentStatus | None = None
    """The current status of the shadow test."""


# This class uses some fields defined in ShadowTestMetadata. We are not
# using inheritance to help the user understand the full structure when using
# tools like intellisense.
class ShadowTest(BaseModel):
    """
    A Nextmv Cloud shadow test definition.

    A shadow test is a type of experiment where runs are executed in parallel
    to compare different instances.

    You can import the `ShadowTest` class directly from `cloud`:

    ```python
    from nextmv.cloud import ShadowTest
    ```

    Parameters
    ----------
    shadow_test_id : str, optional
        The unique identifier of the shadow test.
    name : str, optional
        Name of the shadow test.
    description : str, optional
        Description of the shadow test.
    app_id : str, optional
        ID of the application to which the shadow test belongs.
    created_at : datetime, optional
        Creation date of the shadow test.
    updated_at : datetime, optional
        Last update date of the shadow test.
    status : ExperimentStatus, optional
        The current status of the shadow test.
    completed_at : datetime, optional
        Completion date of the shadow test, if applicable.
    comparisons : list[TestComparison], optional
        List of test comparisons defined in the shadow test.
    start_events : StartEvents, optional
        Start events for the shadow test.
    termination_events : TerminationEvents, optional
        Termination events for the shadow test.
    grouped_distributional_summaries : list[dict[str, Any]], optional
        Grouped distributional summaries of the shadow test.
    runs : list[Run], optional
        List of runs in the shadow test.
    """

    shadow_test_id: str | None = Field(
        serialization_alias="id",
        validation_alias=AliasChoices("id", "shadow_test_id"),
        default=None,
    )
    """The unique identifier of the shadow test."""
    name: str | None = None
    """Name of the shadow test."""
    description: str | None = None
    """Description of the shadow test."""
    app_id: str | None = None
    """ID of the application to which the shadow test belongs."""
    created_at: datetime | None = None
    """Creation date of the shadow test."""
    updated_at: datetime | None = None
    """Last update date of the shadow test."""
    status: ExperimentStatus | None = None
    """The current status of the shadow test."""
    completed_at: datetime | None = None
    """Completion date of the shadow test, if applicable."""
    comparisons: list[TestComparison] | None = None
    """List of test comparisons defined in the shadow test."""
    start_events: StartEvents | None = None
    """Start events for the shadow test."""
    termination_events: TerminationEvents | None = None
    """Termination events for the shadow test."""
    grouped_distributional_summaries: list[dict[str, Any]] | None = None
    """Grouped distributional summaries of the shadow test."""
    runs: list[Run] | None = None
    """List of runs in the shadow test."""


class StopIntent(str, Enum):
    """
    Intent for stopping a shadow test.

    You can import the `StopIntent` class directly from `cloud`:

    ```python
    from nextmv.cloud import StopIntent
    ```

    Attributes
    ----------
    complete : str
        The test is marked as complete.
    cancel : str
        The test is canceled.
    """

    complete = "complete"
    """The test is marked as complete."""
    cancel = "cancel"
    """The test is canceled."""
