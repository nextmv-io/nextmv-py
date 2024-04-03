"""This module contains definitions for batch experiments."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from nextmv.base_model import BaseModel


class BatchExperimentInformation(BaseModel):
    """Information about a batch experiment. This serves as a base for all the
    other batch experiment models."""

    name: str
    """Name of the batch experiment."""
    input_set_id: str
    """ID of the input set used for the experiment."""
    instance_ids: List[str]
    """List of instance IDs used for the experiment."""

    description: Optional[str] = None
    """Description of the batch experiment."""
    id: Optional[str] = None
    """ID of the batch experiment."""


class BatchExperiment(BatchExperimentInformation):
    """A batch experiment compares two or more instances by executing all the
    inputs contained in the input set."""

    created_at: datetime
    """Creation date of the batch experiment."""
    status: str
    """Status of the batch experiment."""

    grouped_distributional_summaries: Optional[List[Dict[str, Any]]] = None
    """Grouped distributional summaries of the batch experiment."""
    option_sets: Optional[Dict[str, Dict[str, str]]] = None
    """Option sets used for the experiment."""


class BatchExperimentRun(BaseModel):
    """A batch experiment run is a single execution of a batch experiment."""

    option_set: str
    """Option set used for the experiment."""
    input_id: str
    """ID of the input used for the experiment."""

    instance_id: Optional[str] = None
    """ID of the instance used for the experiment."""
    version_id: Optional[str] = None
    """ID of the version used for the experiment."""

    def __post_init__(self):
        """Logic to run after the class is initialized."""

        if self.instance_id is None and self.version_id is None:
            raise ValueError("either instance_id or version_id must be set")


class BatchExperimentMetadata(BatchExperimentInformation):
    """Metadata of a batch experiment."""

    status: str
    """Status of the batch experiment."""
    created_at: datetime
    """Creation date of the batch experiment."""
    number_of_runs: int
    """Number of runs in the batch experiment."""
