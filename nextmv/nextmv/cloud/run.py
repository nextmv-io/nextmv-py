"""This module contains definitions for an app run."""

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from pydantic import AliasChoices, Field

from nextmv.base_model import BaseModel
from nextmv.cloud.status import Status, StatusV2
from nextmv.input import Input, InputFormat
from nextmv.output import Output, OutputFormat


def run_duration(
    start: Union[datetime, float],
    end: Union[datetime, float],
) -> int:
    """
    Calculate the duration of a run in milliseconds.

    Parameters
    ----------
    start : Union[datetime, float]
        The start time of the run. Can be a datetime object or a float
        representing the start time in seconds since the epoch.
    end : Union[datetime, float]
        The end time of the run. Can be a datetime object or a float
        representing the end time in seconds since the epoch.

    Returns
    -------
    int
        The duration of the run in milliseconds.
    """
    if isinstance(start, float) and isinstance(end, float):
        if start > end:
            raise ValueError("Start time must be before end time.")
        return int(round((end - start) * 1000))
    if isinstance(start, datetime) and isinstance(end, datetime):
        if start > end:
            raise ValueError("Start time must be before end time.")
        return int(round((end - start).total_seconds() * 1000))
    raise TypeError("Start and end must be either datetime or float.")


class Metadata(BaseModel):
    """Metadata of a run, whether it was successful or not."""

    application_id: str
    """ID of the application where the run was submitted to."""
    application_instance_id: str
    """ID of the instance where the run was submitted to."""
    application_version_id: str
    """ID of the version of the application where the run was submitted to."""
    created_at: datetime
    """Date and time when the run was created."""
    duration: float
    """Duration of the run in milliseconds."""
    error: str
    """Error message if the run failed."""
    input_size: float
    """Size of the input in bytes."""
    output_size: float
    """Size of the output in bytes."""
    status: Status
    """Deprecated: use status_v2."""
    status_v2: StatusV2
    """Status of the run."""


class RunInformation(BaseModel):
    """Information of a run."""

    description: str
    """Description of the run."""
    id: str
    """ID of the run."""
    metadata: Metadata
    """Metadata of the run."""
    name: str
    """Name of the run."""
    user_email: str
    """Email of the user who submitted the run."""
    console_url: str = Field(default="")


class ErrorLog(BaseModel):
    """Error log of a run, when it was not successful."""

    error: Optional[str] = None
    """Error message."""
    stdout: Optional[str] = None
    """Standard output."""
    stderr: Optional[str] = None
    """Standard error."""


class RunResult(RunInformation):
    """Result of a run, whether it was successful or not."""

    error_log: Optional[ErrorLog] = None
    """Error log of the run. Only available if the run failed."""
    output: Optional[dict[str, Any]] = None
    """Output of the run. Only available if the run succeeded."""


class RunLog(BaseModel):
    """Log of a run."""

    log: str
    """Log of the run."""


class FormatInput(BaseModel):
    """Input format for a run configuration."""

    input_type: InputFormat = Field(
        serialization_alias="type",
        validation_alias=AliasChoices("type", "input_type"),
        default=InputFormat.JSON,
    )
    """Type of the input format."""


class Format(BaseModel):
    """Format for a run configuration."""

    format_input: FormatInput = Field(
        serialization_alias="input",
        validation_alias=AliasChoices("input", "format_input"),
    )
    """Input format for the run configuration."""


class RunType(str, Enum):
    """The actual type of the run."""

    STANDARD = "standard"
    """Standard run type."""
    EXTERNAL = "external"
    """External run type."""
    ENSEMBLE = "ensemble"
    """Ensemble run type."""


class RunTypeConfiguration(BaseModel):
    """Defines the configuration for the type of the run that is being executed
    on an application."""

    run_type: RunType = Field(
        serialization_alias="type",
        validation_alias=AliasChoices("type", "run_type"),
    )
    """Type of the run."""
    definition_id: Optional[str] = None
    """ID of the definition for the run type."""
    reference_id: Optional[str] = None
    """ID of the reference for the run type."""


class RunQueuing(BaseModel):
    """RunQueuing configuration for a run."""

    priority: Optional[int] = None
    """
    Priority of the run in the queue. 1 is the highest priority, 9 is the
    lowest priority.
    """
    disabled: Optional[bool] = None
    """
    Whether the run should be queued, or not. If True, the run will not be
    queued. If False, the run will be queued.
    """

    def __post_init_post_parse__(self):
        """Validations done after parsing the model."""

        if self.priority is not None and (self.priority < 1 or self.priority > 9):
            raise ValueError("Priority must be between 1 and 9.")

        if self.disabled is not None and self.disabled not in {True, False}:
            raise ValueError("Disabled must be a boolean value.")


class RunConfiguration(BaseModel):
    """Configuration for an app run."""

    execution_class: Optional[str] = None
    """Execution class for the instance."""
    format: Optional[Format] = None
    """Format for the run configuration."""
    run_type: Optional[RunTypeConfiguration] = None
    """Run type configuration for the run."""
    secrets_collection_id: Optional[str] = None
    """ID of the secrets collection to use for the run."""
    queuing: Optional[RunQueuing] = None
    """Queuing configuration for the run."""


class ExternalRunResult(BaseModel):
    """Result of a run used to configure a new application run as an
    external one."""

    output_upload_id: Optional[str] = None
    """ID of the output upload."""
    error_upload_id: Optional[str] = None
    """ID of the error upload."""
    status: Optional[str] = None
    """Status of the run."""
    error_message: Optional[str] = None
    """Error message of the run."""
    execution_duration: Optional[int] = None
    """Duration of the run, in milliseconds."""

    def __post_init_post_parse__(self):
        """Validations done after parsing the model."""

        valid_statuses = {"succeeded", "failed"}
        if self.status is not None and self.status not in valid_statuses:
            raise ValueError("Invalid status value, must be one of: " + ", ".join(valid_statuses))


class TrackedRunStatus(str, Enum):
    """
    The status of a tracked run.

    Attributes
    ----------
    SUCCEEDED : str
        The run succeeded.
    FAILED : str
        The run failed.
    """

    SUCCEEDED = "succeeded"
    """The run succeeded."""
    FAILED = "failed"
    """The run failed."""


@dataclass
class TrackedRun:
    """
    An external run that is tracked in the Nextmv platform.

    Attributes
    ----------
    input : Union[Input, dict[str, any], str]
        The input of the run being tracked. Please note that if the input
        format is JSON, then the input data must be JSON serializable. This
        field is required.
    output : Union[Output, dict[str, any], str]
        The output of the run being tracked. Please note that if the output
        format is JSON, then the output data must be JSON serializable. This
        field is required.
    status : TrackedRunStatus
        The status of the run being tracked. This field is required.
    duration : Optional[int]
        The duration of the run being tracked, in seconds. This field is
        optional.
    error : Optional[str]
        An error message if the run failed. You should only specify this if the
        run failed (the `status` is `TrackedRunStatus.FAILED`), otherwise an
        exception will be raised. This field is optional.
    logs : Optional[list[str]]
        The logs of the run being tracked. Each element of the list is a line in
        the log. This field is optional.
    """

    input: Union[Input, dict[str, any], str]
    """The input of the run being tracked."""
    output: Union[Output, dict[str, any], str]
    """The output of the run being tracked. Only JSON output_format is supported."""
    status: TrackedRunStatus
    """The status of the run being tracked"""

    duration: Optional[int] = None
    """The duration of the run being tracked, in milliseconds."""
    error: Optional[str] = None
    """An error message if the run failed. You should only specify this if the
    run failed, otherwise an exception will be raised."""
    logs: Optional[list[str]] = None
    """The logs of the run being tracked. Each element of the list is a line in
    the log."""

    def __post_init__(self):  # noqa: C901
        """Validations done after parsing the model."""

        valid_statuses = {TrackedRunStatus.SUCCEEDED, TrackedRunStatus.FAILED}
        if self.status not in valid_statuses:
            raise ValueError("Invalid status value, must be one of: " + ", ".join(valid_statuses))

        if self.error is not None and self.error != "" and self.status != TrackedRunStatus.FAILED:
            raise ValueError("Error message must be empty if the run succeeded.")

        if isinstance(self.input, Input):
            if self.input.input_format != InputFormat.JSON:
                raise ValueError("Input.input_format must be JSON.")
        elif isinstance(self.input, dict):
            try:
                _ = json.dumps(self.input)
            except (TypeError, OverflowError) as e:
                raise ValueError("Input is dict[str, any] but it is not JSON serializable") from e

        if isinstance(self.output, Output):
            if self.output.output_format != OutputFormat.JSON:
                raise ValueError("Output.output_format must be JSON.")
        elif isinstance(self.output, dict):
            try:
                _ = json.dumps(self.output)
            except (TypeError, OverflowError) as e:
                raise ValueError("Output is dict[str, any] but it is not JSON serializable") from e

    def logs_text(self) -> str:
        """
        Returns the logs as a single string.

        Parameters
        ----------
        None

        Returns
        -------
        str
            The logs as a single string.
        """

        if self.logs is None:
            return ""

        return "\n".join(self.logs)
