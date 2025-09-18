"""
This module contains definitions for batch experiments.

Classes
-------
ExperimentStatus
    Enum representing the status of an experiment.
BatchExperimentInformation
    Base class for all batch experiment models containing common information.
BatchExperiment
    Class representing a batch experiment that compares two or more instances.
BatchExperimentRun
    Class representing a single execution of a batch experiment.
BatchExperimentMetadata
    Class containing metadata of a batch experiment.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from nextmv.base_model import BaseModel
from nextmv.cloud.input_set import InputSet


class ExperimentStatus(str, Enum):
    """
    Status of an experiment.

    You can import the `ExperimentStatus` class directly from `cloud`:

    ```python from nextmv.cloud import ExperimentStatus ```

    This enum represents the comprehensive set of possible states for an
    experiment in Nextmv Cloud.

    Attributes
    ----------
    STARTED : str
        Experiment started.
    COMPLETED : str
        Experiment completed.
    FAILED : str
        Experiment failed.
    DRAFT : str
        Experiment is a draft.
    CANCELED : str
        Experiment was canceled.
    STOPPING : str
        Experiment is stopping.
    DELETING : str
        Experiment is being deleted.
    DELETE_FAILED : str
        Experiment deletion failed.
    UNKNOWN : str
        Experiment status is unknown.

    Examples
    --------
    >>> from nextmv.cloud import ExperimentStatus
    >>> status = ExperimentStatus.STARTED
    >>> print(f"The status is: {status.value}")
    The status is: started

    >>> if status == ExperimentStatus.COMPLETED:
    ...     print("Processing complete.")
    ... elif status in [ExperimentStatus.STARTED, ExperimentStatus.STOPPING]:
    ...     print("Processing in progress.")
    ... else:
    ...     print("Processing has not started or has ended with issues.")
    Processing in progress.

    """

    STARTED = "started"
    """Experiment started."""
    COMPLETED = "completed"
    """Experiment completed."""
    FAILED = "failed"
    """Experiment failed."""
    DRAFT = "draft"
    """Experiment is a draft."""
    CANCELED = "canceled"
    """Experiment was canceled."""
    STOPPING = "stopping"
    """Experiment is stopping."""
    DELETING = "deleting"
    """Experiment is being deleted."""
    DELETE_FAILED = "delete-failed"
    """Experiment deletion failed."""
    UNKNOWN = "unknown"
    """Experiment status is unknown."""


class BatchExperimentInformation(BaseModel):
    """Information about a batch experiment.

    You can import the `BatchExperimentInformation` class directly from `cloud`:

    ```python
    from nextmv.cloud import BatchExperimentInformation
    ```

    This class serves as a base for all the other batch experiment models and
    contains common attributes shared by different types of batch experiments.

    Parameters
    ----------
    id : str
        ID of the batch experiment.
    name : str
        Name of the batch experiment.
    created_at : datetime
        Creation date of the batch experiment.
    updated_at : datetime
        Last update date of the batch experiment.
    status : str, optional
        Status of the batch experiment. Defaults to None.
    description : str, optional
        Description of the batch experiment. Defaults to None.
    number_of_requested_runs : int, optional
        Number of runs requested for the batch experiment. Defaults to None.
    number_of_runs : int, optional
        Number of runs in the batch experiment. Defaults to None.
    number_of_completed_runs : int, optional
        Number of completed runs in the batch experiment. Defaults to None.
    type : str, optional
        Type of the batch experiment. Defaults to None.
    option_sets : dict[str, dict[str, str]], optional
        Option sets used for the experiment. Defaults to None.

    Examples
    --------
    >>> from datetime import datetime
    >>> info = BatchExperimentInformation(
    ...     id="bexp-123",
    ...     name="Test Experiment",
    ...     created_at=datetime.now(),
    ...     updated_at=datetime.now(),
    ...     status="running",
    ...     description="A sample batch experiment."
    ... )
    >>> print(info.id)
    bexp-123
    >>> print(info.name)
    Test Experiment
    """

    id: str
    """ID of the batch experiment."""
    name: str
    """Name of the batch experiment."""
    created_at: datetime
    """Creation date of the batch experiment."""
    updated_at: datetime
    """Last update date of the batch experiment."""

    status: Optional[ExperimentStatus] = None
    """Status of the batch experiment."""
    description: Optional[str] = None
    """Description of the batch experiment."""
    number_of_requested_runs: Optional[int] = None
    """Number of runs requested for the batch experiment."""
    number_of_runs: Optional[int] = None
    """Number of runs in the batch experiment."""
    number_of_completed_runs: Optional[int] = None
    """Number of completed runs in the batch experiment."""
    type: Optional[str] = None
    """Type of the batch experiment."""
    option_sets: Optional[dict[str, dict[str, str]]] = None
    """Option sets used for the experiment."""


class BatchExperiment(BatchExperimentInformation):
    """A batch experiment compares two or more instances by executing all the
    inputs contained in the input set.

    You can import the `BatchExperiment` class directly from `cloud`:

    ```python
    from nextmv.cloud import BatchExperiment
    ```

    This class extends `BatchExperimentInformation` with attributes specific
    to a full batch experiment.

    Parameters
    ----------
    input_set_id : str
        ID of the input set used for the experiment.
    instance_ids : list[str]
        List of instance IDs used for the experiment.
    grouped_distributional_summaries : list[dict[str, Any]], optional
        Grouped distributional summaries of the batch experiment. Defaults to None.
    """

    input_set_id: str
    """ID of the input set used for the experiment."""
    instance_ids: list[str]
    """List of instance IDs used for the experiment."""
    grouped_distributional_summaries: Optional[list[dict[str, Any]]] = None
    """Grouped distributional summaries of the batch experiment."""


class BatchExperimentRun(BaseModel):
    """A batch experiment run is a single execution of a batch experiment.

    You can import the `BatchExperimentRun` class directly from `cloud`:

    ```python
    from nextmv.cloud import BatchExperimentRun
    ```

    It contains information about the experiment, the input used, and the
    configuration used for the run.

    Parameters
    ----------
    input_id : str
        ID of the input used for the experiment.
    option_set : str
        Option set used for the experiment. Defaults to None.
    instance_id : str, optional
        ID of the instance used for the experiment. Defaults to None.
    version_id : str, optional
        ID of the version used for the experiment. Defaults to None.
    input_set_id : str, optional
        ID of the input set used for the experiment. Defaults to None.
    scenario_id : str, optional
        If the batch experiment is a scenario test, this is the ID of that test.
        Defaults to None.
    repetition : int, optional
        Repetition number of the experiment. Defaults to None.
    run_number : str, optional
        Run number of the experiment. Defaults to None.
    """

    input_id: str
    """ID of the input used for the experiment."""

    option_set: Optional[str] = None
    """Option set used for the experiment."""
    instance_id: Optional[str] = None
    """ID of the instance used for the experiment."""
    version_id: Optional[str] = None
    """ID of the version used for the experiment."""
    input_set_id: Optional[str] = None
    """ID of the input set used for the experiment."""
    scenario_id: Optional[str] = None
    """If the batch experiment is a scenario test, this is the ID of that test."""
    repetition: Optional[int] = None
    """Repetition number of the experiment."""

    def __post_init_post_parse__(self):
        """
        Logic to run after the class is initialized.

        Ensures that either `instance_id` or `version_id` is set.

        Raises
        ------
        ValueError
            If both `instance_id` and `version_id` are None.
        """
        if self.instance_id is None and self.version_id is None:
            raise ValueError("either instance_id or version_id must be set")


class BatchExperimentMetadata(BatchExperimentInformation):
    """Metadata of a batch experiment.

    You can import the `BatchExperimentMetadata` class directly from `cloud`:

    ```python
    from nextmv.cloud import BatchExperimentMetadata
    ```

    This class extends `BatchExperimentInformation` with application-specific
    metadata.

    Parameters
    ----------
    app_id : str, optional
        ID of the application used for the batch experiment. Defaults to None.
    """

    app_id: Optional[str] = None
    """ID of the application used for the batch experiment."""


def to_runs(instance_ids: list[str], input_set: InputSet) -> list[BatchExperimentRun]:
    """
    Translate a legacy batch experiment list of instance ids to runs.

    Parameters
    ----------
    instance_ids : list[str]
        List of instance IDs to be converted into runs.
    input_set : InputSet
        Input set associated with the runs.

    Returns
    -------
    list[BatchExperimentRun]
        A list of `BatchExperimentRun` objects created from the instance IDs.
    """

    input_ids = input_set.input_ids
    if len(input_set.input_ids) == 0:
        input_ids = [i.id for i in input_set.inputs]

    runs = []
    for instance_id in instance_ids:
        for input_id in input_ids:
            run = BatchExperimentRun(
                input_id=input_id,
                instance_id=instance_id,
                input_set_id=input_set.id,
            )
            runs.append(run)

    return runs
