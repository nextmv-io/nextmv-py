"""This module contains definitions for batch experiments."""

from datetime import datetime
from typing import Any, Optional

from nextmv.base_model import BaseModel


class BatchExperimentInformation(BaseModel):
    """Information about a batch experiment. This serves as a base for all the
    other batch experiment models."""

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
    inputs contained in the input set."""

    input_set_id: str
    """ID of the input set used for the experiment."""
    instance_ids: list[str]
    """List of instance IDs used for the experiment."""
    grouped_distributional_summaries: Optional[list[dict[str, Any]]] = None
    """Grouped distributional summaries of the batch experiment."""


class BatchExperimentRun(BaseModel):
    """
    A batch experiment run is a single execution of a batch experiment. It
    contains information about the experiment, the input used, and the
    configuration used for the run.

    Attributes
    ----------
    option_set : str
        Option set used for the experiment.
    input_id : str
        ID of the input used for the experiment.
    instance_id : Optional[str]
        ID of the instance used for the experiment.
    version_id : Optional[str]
        ID of the version used for the experiment.
    input_set_id : Optional[str]
        ID of the input set used for the experiment.
    scenario_id : Optional[str]
        If the batch experiment is a scenario test, this is the ID of that test.
    repetition : Optional[int]
        Repetition number of the experiment.
    run_number : Optional[str]
        Run number of the experiment.
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
        """Logic to run after the class is initialized."""

        if self.instance_id is None and self.version_id is None:
            raise ValueError("either instance_id or version_id must be set")


class BatchExperimentMetadata(BatchExperimentInformation):
    """Metadata of a batch experiment."""

    app_id: Optional[str] = None
    """ID of the application used for the batch experiment."""
