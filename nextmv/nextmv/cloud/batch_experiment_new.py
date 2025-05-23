"""This module contains definitions for batch experiments.

Classes
-------
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
from typing import Any, Optional

from nextmv.base_model import BaseModel


class BatchExperimentInformation(BaseModel):
    """Information about a batch experiment. This serves as a base for all the
    other batch experiment models.

    You can import the `BatchExperimentInformation` class directly from `cloud`:

    ```python
    from nextmv.cloud import BatchExperimentInformation
    ```

    This class contains common attributes shared by different types of batch
    experiments.

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
    status : Optional[str], default=None
        Status of the batch experiment.
    description : Optional[str], default=None
        Description of the batch experiment.
    number_of_requested_runs : Optional[int], default=None
        Number of runs requested for the batch experiment.
    number_of_runs : Optional[int], default=None
        Number of runs in the batch experiment.
    number_of_completed_runs : Optional[int], default=None
        Number of completed runs in the batch experiment.
    type : Optional[str], default=None
        Type of the batch experiment.
    option_sets : Optional[dict[str, dict[str, str]]], default=None
        Option sets used for the experiment.

    Examples
    --------
    >>> info = BatchExperimentInformation(
    ...     id="bexp-123",
    ...     name="Test Experiment",
    ...     created_at=datetime.now(),
    ...     updated_at=datetime.now()
    ... )
    >>> print(info.id)
    bexp-123
    """

    id: str
    """ID of the batch experiment."""
    name: str
    """Name of the batch experiment."""
    created_at: datetime
    """Creation date of the batch experiment."""
    updated_at: datetime
    """Last update date of the batch experiment."""

    status: Optional[str] = None
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

    This class inherits from `BatchExperimentInformation` and adds additional
    attributes specific to batch experiments.

    Parameters
    ----------
    input_set_id : str
        ID of the input set used for the experiment.
    instance_ids : list[str]
        List of instance IDs used for the experiment.
    grouped_distributional_summaries : Optional[list[dict[str, Any]]], default=None
        Grouped distributional summaries of the batch experiment.

    Examples
    --------
    >>> experiment = BatchExperiment(
    ...     id="bexp-123",
    ...     name="My Experiment",
    ...     created_at=datetime.now(),
    ...     updated_at=datetime.now(),
    ...     input_set_id="inset-456",
    ...     instance_ids=["inst-789", "inst-abc"]
    ... )
    >>> print(len(experiment.instance_ids))
    2
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

    This class contains information about the experiment, the input used, and the
    configuration used for the run. Either instance_id or version_id must be set.

    Parameters
    ----------
    option_set : str
        Option set used for the experiment.
    input_id : str
        ID of the input used for the experiment.
    instance_id : Optional[str], default=None
        ID of the instance used for the experiment.
    version_id : Optional[str], default=None
        ID of the version used for the experiment.
    input_set_id : Optional[str], default=None
        ID of the input set used for the experiment.
    scenario_id : Optional[str], default=None
        If the batch experiment is a scenario test, this is the ID of that test.
    repetition : Optional[int], default=None
        Repetition number of the experiment.
    run_number : Optional[str], default=None
        Run number of the experiment.

    Examples
    --------
    >>> run = BatchExperimentRun(
    ...     option_set="default",
    ...     input_id="inp-123",
    ...     instance_id="inst-456"
    ... )
    >>> print(run.option_set)
    default

    Raises
    ------
    ValueError
        If neither instance_id nor version_id are set.
    """

    option_set: str
    """Option set used for the experiment."""
    input_id: str
    """ID of the input used for the experiment."""

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
    run_number: Optional[str] = None
    """Run number of the experiment."""

    def __post_init_post_parse__(self):
        """Logic to run after the class is initialized.

        Raises
        ------
        ValueError
            If neither instance_id nor version_id are set.
        """

        if self.instance_id is None and self.version_id is None:
            raise ValueError("either instance_id or version_id must be set")


class BatchExperimentMetadata(BatchExperimentInformation):
    """Metadata of a batch experiment.

    You can import the `BatchExperimentMetadata` class directly from `cloud`:

    ```python
    from nextmv.cloud import BatchExperimentMetadata
    ```

    This class inherits from `BatchExperimentInformation` and adds additional
    metadata information about the batch experiment.

    Parameters
    ----------
    app_id : Optional[str], default=None
        ID of the application used for the batch experiment.

    Examples
    --------
    >>> metadata = BatchExperimentMetadata(
    ...     id="bexp-123",
    ...     name="Test Experiment",
    ...     created_at=datetime.now(),
    ...     updated_at=datetime.now(),
    ...     app_id="app-456"
    ... )
    >>> print(metadata.app_id)
    app-456
    """

    app_id: Optional[str] = None
    """ID of the application used for the batch experiment."""
