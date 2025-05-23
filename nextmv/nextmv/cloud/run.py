"""This module contains definitions for an app run.

Classes
-------
Metadata
    Metadata of a run, whether it was successful or not.
RunInformation
    Information of a run.
ErrorLog
    Error log of a run, when it was not successful.
RunResult
    Result of a run, whether it was successful or not.
RunLog
    Log of a run.
FormatInput
    Input format for a run configuration.
Format
    Format for a run configuration.
RunType
    The actual type of the run.
RunTypeConfiguration
    Defines the configuration for the type of the run that is being executed
    on an application.
RunQueuing
    RunQueuing configuration for a run.
RunConfiguration
    Configuration for an app run.
ExternalRunResult
    Result of a run used to configure a new application run as an
    external one.
TrackedRunStatus
    The status of a tracked run.
TrackedRun
    An external run that is tracked in the Nextmv platform.

Functions
---------
run_duration(start, end)
    Calculate the duration of a run in milliseconds.
"""

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


def run_duration(start: Union[datetime, float], end: Union[datetime, float]) -> int:
    """
    Calculate the duration of a run in milliseconds.

    You can import the `run_duration` function directly from `cloud`:

    ```python
    from nextmv.cloud import run_duration
    ```

    Parameters
    ----------
    start : datetime or float
        The start time of the run. Can be a datetime object or a float
        representing the start time in seconds since the epoch.
    end : datetime or float
        The end time of the run. Can be a datetime object or a float
        representing the end time in seconds since the epoch.

    Returns
    -------
    int
        The duration of the run in milliseconds.

    Raises
    ------
    ValueError
        If the start time is after the end time.
    TypeError
        If start and end are not both datetime objects or both float numbers.

    Examples
    --------
    >>> from datetime import datetime, timedelta
    >>> start_dt = datetime(2023, 1, 1, 12, 0, 0)
    >>> end_dt = datetime(2023, 1, 1, 12, 0, 1)
    >>> run_duration(start_dt, end_dt)
    1000

    >>> start_float = 1672574400.0  # Corresponds to 2023-01-01 12:00:00
    >>> end_float = 1672574401.0    # Corresponds to 2023-01-01 12:00:01
    >>> run_duration(start_float, end_float)
    1000
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
    """
    Metadata of a run, whether it was successful or not.

    You can import the `Metadata` class directly from `cloud`:

    ```python
    from nextmv.cloud import Metadata
    ```

    Parameters
    ----------
    application_id : str
        ID of the application where the run was submitted to.
    application_instance_id : str
        ID of the instance where the run was submitted to.
    application_version_id : str
        ID of the version of the application where the run was submitted to.
    created_at : datetime
        Date and time when the run was created.
    duration : float
        Duration of the run in milliseconds.
    error : str
        Error message if the run failed.
    input_size : float
        Size of the input in bytes.
    output_size : float
        Size of the output in bytes.
    status : Status
        Deprecated: use status_v2.
    status_v2 : StatusV2
        Status of the run.
    """

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
    """
    Information of a run.

    You can import the `RunInformation` class directly from `cloud`:

    ```python
    from nextmv.cloud import RunInformation
    ```

    Parameters
    ----------
    description : str
        Description of the run.
    id : str
        ID of the run.
    metadata : Metadata
        Metadata of the run.
    name : str
        Name of the run.
    user_email : str
        Email of the user who submitted the run.
    console_url : str, optional
        URL to the run in the Nextmv console. Defaults to "".
    """

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
    """
    Error log of a run, when it was not successful.

    You can import the `ErrorLog` class directly from `cloud`:

    ```python
    from nextmv.cloud import ErrorLog
    ```

    Parameters
    ----------
    error : str, optional
        Error message. Defaults to None.
    stdout : str, optional
        Standard output. Defaults to None.
    stderr : str, optional
        Standard error. Defaults to None.
    """

    error: Optional[str] = None
    """Error message."""
    stdout: Optional[str] = None
    """Standard output."""
    stderr: Optional[str] = None
    """Standard error."""


class RunResult(RunInformation):
    """
    Result of a run, whether it was successful or not.

    You can import the `RunResult` class directly from `cloud`:

    ```python
    from nextmv.cloud import RunResult
    ```

    Parameters
    ----------
    error_log : ErrorLog, optional
        Error log of the run. Only available if the run failed. Defaults to
        None.
    output : dict[str, Any], optional
        Output of the run. Only available if the run succeeded. Defaults to
        None.
    """

    error_log: Optional[ErrorLog] = None
    """Error log of the run. Only available if the run failed."""
    output: Optional[dict[str, Any]] = None
    """Output of the run. Only available if the run succeeded."""


class RunLog(BaseModel):
    """
    Log of a run.

    You can import the `RunLog` class directly from `cloud`:

    ```python
    from nextmv.cloud import RunLog
    ```

    Parameters
    ----------
    log : str
        Log of the run.
    """

    log: str
    """Log of the run."""


class FormatInput(BaseModel):
    """
    Input format for a run configuration.

    You can import the `FormatInput` class directly from `cloud`:

    ```python
    from nextmv.cloud import FormatInput
    ```

    Parameters
    ----------
    input_type : InputFormat, optional
        Type of the input format. Defaults to `InputFormat.JSON`.
    """

    input_type: InputFormat = Field(
        serialization_alias="type",
        validation_alias=AliasChoices("type", "input_type"),
        default=InputFormat.JSON,
    )
    """Type of the input format."""


class Format(BaseModel):
    """
    Format for a run configuration.

    You can import the `Format` class directly from `cloud`:

    ```python
    from nextmv.cloud import Format
    ```

    Parameters
    ----------
    format_input : FormatInput
        Input format for the run configuration.
    """

    format_input: FormatInput = Field(
        serialization_alias="input",
        validation_alias=AliasChoices("input", "format_input"),
    )
    """Input format for the run configuration."""


class RunType(str, Enum):
    """
    The actual type of the run.

    You can import the `RunType` class directly from `cloud`:

    ```python
    from nextmv.cloud import RunType
    ```

    Parameters
    ----------
    STANDARD : str
        Standard run type.
    EXTERNAL : str
        External run type.
    ENSEMBLE : str
        Ensemble run type.
    """

    STANDARD = "standard"
    """Standard run type."""
    EXTERNAL = "external"
    """External run type."""
    ENSEMBLE = "ensemble"
    """Ensemble run type."""


class RunTypeConfiguration(BaseModel):
    """
    Defines the configuration for the type of the run that is being executed
    on an application.

    You can import the `RunTypeConfiguration` class directly from `cloud`:

    ```python
    from nextmv.cloud import RunTypeConfiguration
    ```

    Parameters
    ----------
    run_type : RunType
        Type of the run.
    definition_id : str, optional
        ID of the definition for the run type. Defaults to None.
    reference_id : str, optional
        ID of the reference for the run type. Defaults to None.
    """

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
    """
    RunQueuing configuration for a run.

    You can import the `RunQueuing` class directly from `cloud`:

    ```python
    from nextmv.cloud import RunQueuing
    ```

    Parameters
    ----------
    priority : int, optional
        Priority of the run in the queue. 1 is the highest priority, 9 is the
        lowest priority. Defaults to None.
    disabled : bool, optional
        Whether the run should be queued, or not. If True, the run will not be
        queued. If False, the run will be queued. Defaults to None.
    """

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
        """
        Validations done after parsing the model.

        Raises
        ------
        ValueError
            If priority is not between 1 and 9, or if disabled is not a
            boolean value.
        """

        if self.priority is not None and (self.priority < 1 or self.priority > 9):
            raise ValueError("Priority must be between 1 and 9.")

        if self.disabled is not None and self.disabled not in {True, False}:
            raise ValueError("Disabled must be a boolean value.")


class RunConfiguration(BaseModel):
    """
    Configuration for an app run.

    You can import the `RunConfiguration` class directly from `cloud`:

    ```python
    from nextmv.cloud import RunConfiguration
    ```

    Parameters
    ----------
    execution_class : str, optional
        Execution class for the instance. Defaults to None.
    format : Format, optional
        Format for the run configuration. Defaults to None.
    run_type : RunTypeConfiguration, optional
        Run type configuration for the run. Defaults to None.
    secrets_collection_id : str, optional
        ID of the secrets collection to use for the run. Defaults to None.
    queuing : RunQueuing, optional
        Queuing configuration for the run. Defaults to None.
    """

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
    """
    Result of a run used to configure a new application run as an
    external one.

    You can import the `ExternalRunResult` class directly from `cloud`:

    ```python
    from nextmv.cloud import ExternalRunResult
    ```

    Parameters
    ----------
    output_upload_id : str, optional
        ID of the output upload. Defaults to None.
    error_upload_id : str, optional
        ID of the error upload. Defaults to None.
    status : str, optional
        Status of the run. Must be "succeeded" or "failed". Defaults to None.
    error_message : str, optional
        Error message of the run. Defaults to None.
    execution_duration : int, optional
        Duration of the run, in milliseconds. Defaults to None.
    """

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
        """
        Validations done after parsing the model.

        Raises
        ------
        ValueError
            If the status value is not "succeeded" or "failed".
        """

        valid_statuses = {"succeeded", "failed"}
        if self.status is not None and self.status not in valid_statuses:
            raise ValueError("Invalid status value, must be one of: " + ", ".join(valid_statuses))


class TrackedRunStatus(str, Enum):
    """
    The status of a tracked run.

    You can import the `TrackedRunStatus` class directly from `cloud`:

    ```python
    from nextmv.cloud import TrackedRunStatus
    ```

    Parameters
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

    You can import the `TrackedRun` class directly from `cloud`:

    ```python
    from nextmv.cloud import TrackedRun
    ```

    Parameters
    ----------
    input : Input or dict[str, Any] or str
        The input of the run being tracked. Please note that if the input
        format is JSON, then the input data must be JSON serializable. This
        field is required.
    output : Output or dict[str, Any] or str
        The output of the run being tracked. Please note that if the output
        format is JSON, then the output data must be JSON serializable. This
        field is required. Only JSON output_format is supported.
    status : TrackedRunStatus
        The status of the run being tracked. This field is required.
    duration : int, optional
        The duration of the run being tracked, in milliseconds. This field is
        optional. Defaults to None.
    error : str, optional
        An error message if the run failed. You should only specify this if the
        run failed (the `status` is `TrackedRunStatus.FAILED`), otherwise an
        exception will be raised. This field is optional. Defaults to None.
    logs : list[str], optional
        The logs of the run being tracked. Each element of the list is a line in
        the log. This field is optional. Defaults to None.

    Raises
    ------
    ValueError
        If the status value is invalid, if an error message is provided for a
        successful run, or if input/output formats are not JSON or
        input/output dicts are not JSON serializable.
    """

    input: Union[Input, dict[str, Any], str]
    """The input of the run being tracked."""
    output: Union[Output, dict[str, Any], str]
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
        """
        Validations done after parsing the model.

        Raises
        ------
        ValueError
            If the status value is invalid, if an error message is provided for
            a successful run, or if input/output formats are not JSON or
            input/output dicts are not JSON serializable.
        """

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
                raise ValueError("Input is dict[str, Any] but it is not JSON serializable") from e

        if isinstance(self.output, Output):
            if self.output.output_format != OutputFormat.JSON:
                raise ValueError("Output.output_format must be JSON.")
        elif isinstance(self.output, dict):
            try:
                _ = json.dumps(self.output)
            except (TypeError, OverflowError) as e:
                raise ValueError("Output is dict[str, Any] but it is not JSON serializable") from e

    def logs_text(self) -> str:
        """
        Returns the logs as a single string.

        Each log entry is separated by a newline character.

        Returns
        -------
        str
            The logs as a single string. If no logs are present, an empty
            string is returned.

        Raises
        ------
        TypeError
            If `self.logs` is not a string or a list of strings.
        """

        if self.logs is None:
            return ""

        if isinstance(self.logs, str):
            return self.logs

        if isinstance(self.logs, list):
            return "\\n".join(self.logs)

        raise TypeError("Logs must be a string or a list of strings.")
