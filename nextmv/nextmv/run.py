"""
This module contains definitions for an app run.

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
FormatOutput
    Output format for a run configuration.
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

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from pydantic import AliasChoices, Field

from nextmv._serialization import serialize_json
from nextmv.base_model import BaseModel
from nextmv.input import Input, InputFormat
from nextmv.output import Output, OutputFormat
from nextmv.status import Status, StatusV2


def run_duration(start: Union[datetime, float], end: Union[datetime, float]) -> int:
    """
    Calculate the duration of a run in milliseconds.

    You can import the `run_duration` function directly from `nextmv`:

    ```python
    from nextmv import run_duration
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


class FormatInput(BaseModel):
    """
    Input format for a run configuration.

    You can import the `FormatInput` class directly from `nextmv`:

    ```python
    from nextmv import FormatInput
    ```

    Parameters
    ----------
    input_type : InputFormat, optional
        Type of the input format. Defaults to `InputFormat.JSON`.

    Examples
    --------
    >>> from nextmv import FormatInput, InputFormat
    >>> format_input = FormatInput()
    >>> format_input.input_type
    <InputFormat.JSON: 'json'>

    >>> format_input = FormatInput(input_type=InputFormat.TEXT)
    >>> format_input.input_type
    <InputFormat.TEXT: 'text'>
    """

    input_type: InputFormat = Field(
        serialization_alias="type",
        validation_alias=AliasChoices("type", "input_type"),
        default=InputFormat.JSON,
    )
    """Type of the input format."""


class FormatOutput(BaseModel):
    """
    Output format for a run configuration.

    You can import the `FormatOutput` class directly from `nextmv`:

    ```python
    from nextmv import FormatOutput
    ```

    Parameters
    ----------
    output_type : OutputFormat, optional
        Type of the output format. Defaults to `OutputFormat.JSON`.

    Examples
    --------
    >>> from nextmv import FormatOutput, OutputFormat
    >>> format_output = FormatOutput()
    >>> format_output.output_type
    <OutputFormat.JSON: 'json'>

    >>> format_output = FormatOutput(output_type=OutputFormat.CSV_ARCHIVE)
    >>> format_output.output_type
    <OutputFormat.CSV_ARCHIVE: 'csv_archive'>
    """

    output_type: OutputFormat = Field(
        serialization_alias="type",
        validation_alias=AliasChoices("type", "output_type"),
        default=OutputFormat.JSON,
    )
    """Type of the output format."""


class Format(BaseModel):
    """
    Format for a run configuration.

    You can import the `Format` class directly from `nextmv`:

    ```python
    from nextmv import Format
    ```

    Parameters
    ----------
    format_input : FormatInput
        Input format for the run configuration.
    format_output : FormatOutput, optional
        Output format for the run configuration. Defaults to None.

    Examples
    --------
    >>> from nextmv import Format, FormatInput, FormatOutput, InputFormat, OutputFormat
    >>> format_config = Format(
    ...     format_input=FormatInput(input_type=InputFormat.JSON),
    ...     format_output=FormatOutput(output_type=OutputFormat.JSON)
    ... )
    >>> format_config.format_input.input_type
    <InputFormat.JSON: 'json'>
    >>> format_config.format_output.output_type
    <OutputFormat.JSON: 'json'>
    """

    format_input: FormatInput = Field(
        serialization_alias="input",
        validation_alias=AliasChoices("input", "format_input"),
    )
    """Input format for the run configuration."""
    format_output: Optional[FormatOutput] = Field(
        serialization_alias="output",
        validation_alias=AliasChoices("output", "format_output"),
        default=None,
    )
    """Output format for the run configuration."""


class Metadata(BaseModel):
    """
    Metadata of a run, whether it was successful or not.

    You can import the `Metadata` class directly from `nextmv`:

    ```python
    from nextmv import Metadata
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
    format : Format
        Format of the input and output of the run.
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
    format: Format
    """Format of the input and output of the run."""
    status_v2: StatusV2
    """Status of the run."""

    status: Optional[Status] = None
    """Deprecated: use status_v2."""


class RunInformation(BaseModel):
    """
    Information of a run.

    You can import the `RunInformation` class directly from `nextmv`:

    ```python
    from nextmv import RunInformation
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
    """
    URL to the run in the Nextmv console.
    """
    synced_run_id: Optional[str] = None
    """
    ID of the synced remote run, if applicable. When the `Application.sync`
    method is used, this field marks the association between the local run
    (`id`) and the remote run (`synced_run_id`). This field is None if the run
    was not created using `Application.sync` or if the run has not been synced
    yet.
    """
    synced_at: Optional[datetime] = None
    """
    Timestamp when the run was synced with the remote run. This field is
    None if the run was not created using `Application.sync` or if the run
    has not been synced yet.
    """


class ErrorLog(BaseModel):
    """
    Error log of a run, when it was not successful.

    You can import the `ErrorLog` class directly from `nextmv`:

    ```python
    from nextmv import ErrorLog
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

    You can import the `RunResult` class directly from `nextmv`:

    ```python
    from nextmv import RunResult
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

    You can import the `RunLog` class directly from `nextmv`:

    ```python
    from nextmv import RunLog
    ```

    Parameters
    ----------
    log : str
        Log of the run.

    Examples
    --------
    >>> from nextmv import RunLog
    >>> run_log = RunLog(log="Optimization completed successfully")
    >>> run_log.log
    'Optimization completed successfully'

    >>> # Multi-line log
    >>> multi_line_log = RunLog(log="Starting optimization\\nProcessing data\\nCompleted")
    >>> multi_line_log.log
    'Starting optimization\\nProcessing data\\nCompleted'
    """

    log: str
    """Log of the run."""


class RunType(str, Enum):
    """
    The actual type of the run.

    You can import the `RunType` class directly from `nextmv`:

    ```python
    from nextmv import RunType
    ```

    Parameters
    ----------
    STANDARD : str
        Standard run type.
    EXTERNAL : str
        External run type.
    ENSEMBLE : str
        Ensemble run type.

    Examples
    --------
    >>> from nextmv import RunType
    >>> run_type = RunType.STANDARD
    >>> run_type
    <RunType.STANDARD: 'standard'>
    >>> run_type.value
    'standard'

    >>> # Creating from string
    >>> external_type = RunType("external")
    >>> external_type
    <RunType.EXTERNAL: 'external'>

    >>> # All available types
    >>> list(RunType)
    [<RunType.STANDARD: 'standard'>, <RunType.EXTERNAL: 'external'>, <RunType.ENSEMBLE: 'ensemble'>]
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

    You can import the `RunTypeConfiguration` class directly from `nextmv`:

    ```python
    from nextmv import RunTypeConfiguration
    ```

    Parameters
    ----------
    run_type : RunType
        Type of the run.
    definition_id : str, optional
        ID of the definition for the run type. Defaults to None.
    reference_id : str, optional
        ID of the reference for the run type. Defaults to None.

    Examples
    --------
    >>> from nextmv import RunTypeConfiguration, RunType
    >>> config = RunTypeConfiguration(run_type=RunType.STANDARD)
    >>> config.run_type
    <RunType.STANDARD: 'standard'>
    >>> config.definition_id is None
    True

    >>> # External run with reference
    >>> external_config = RunTypeConfiguration(
    ...     run_type=RunType.EXTERNAL,
    ...     reference_id="ref-12345"
    ... )
    >>> external_config.run_type
    <RunType.EXTERNAL: 'external'>
    >>> external_config.reference_id
    'ref-12345'

    >>> # Ensemble run with definition
    >>> ensemble_config = RunTypeConfiguration(
    ...     run_type=RunType.ENSEMBLE,
    ...     definition_id="def-67890"
    ... )
    >>> ensemble_config.run_type
    <RunType.ENSEMBLE: 'ensemble'>
    >>> ensemble_config.definition_id
    'def-67890'
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

    You can import the `RunQueuing` class directly from `nextmv`:

    ```python
    from nextmv import RunQueuing
    ```

    Parameters
    ----------
    priority : int, optional
        Priority of the run in the queue. 1 is the highest priority, 9 is the
        lowest priority. Defaults to None.
    disabled : bool, optional
        Whether the run should be queued, or not. If True, the run will not be
        queued. If False, the run will be queued. Defaults to None.

    Examples
    --------
    >>> from nextmv import RunQueuing
    >>> queuing = RunQueuing(priority=1, disabled=False)
    >>> queuing.priority
    1
    >>> queuing.disabled
    False

    >>> # High priority run
    >>> high_priority = RunQueuing(priority=1)
    >>> high_priority.priority
    1

    >>> # Disabled queuing
    >>> no_queue = RunQueuing(disabled=True)
    >>> no_queue.disabled
    True
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

    You can import the `RunConfiguration` class directly from `nextmv`:

    ```python
    from nextmv import RunConfiguration
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

    Examples
    --------
    >>> from nextmv import RunConfiguration, RunQueuing
    >>> config = RunConfiguration(
    ...     execution_class="large",
    ...     queuing=RunQueuing(priority=1)
    ... )
    >>> config.execution_class
    'large'
    >>> config.queuing.priority
    1

    >>> # Basic configuration
    >>> basic_config = RunConfiguration()
    >>> basic_config.format is None
    True
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

    def resolve(
        self,
        input: Union[Input, dict[str, Any], BaseModel, str],
        dir_path: Optional[str] = None,
    ) -> None:
        """
        Resolves the run configuration by modifying or setting the `format`,
        based on the type of input that is provided.

        Parameters
        ----------
        input : Input or dict[str, Any] or BaseModel or str
            The input to use for resolving the run configuration.
        dir_path : str, optional
            The directory path where inputs can be loaded from.

        Examples
        --------
        >>> from nextmv import RunConfiguration
        >>> config = RunConfiguration()
        >>> config.resolve({"key": "value"})
        >>> config.format.format_input.input_type
        <InputFormat.JSON: 'json'>

        >>> config = RunConfiguration()
        >>> config.resolve("text input")
        >>> config.format.format_input.input_type
        <InputFormat.TEXT: 'text'>

        >>> config = RunConfiguration()
        >>> config.resolve({}, dir_path="/path/to/files")
        >>> config.format.format_input.input_type
        <InputFormat.MULTI_FILE: 'multi_file'>
        """

        # If the value is set by the user, do not change it.
        if self.format is not None:
            return

        self.format = Format(
            format_input=FormatInput(input_type=InputFormat.JSON),
            format_output=FormatOutput(output_type=OutputFormat.JSON),
        )

        if isinstance(input, dict):
            self.format.format_input.input_type = InputFormat.JSON
        elif isinstance(input, str):
            self.format.format_input.input_type = InputFormat.TEXT
        elif dir_path is not None and dir_path != "":
            # Kinda hard to detect if we should be working with CSV_ARCHIVE or
            # MULTI_FILE, so we default to MULTI_FILE.
            self.format.format_input.input_type = InputFormat.MULTI_FILE
        elif isinstance(input, Input):
            self.format.format_input.input_type = input.input_format

        # As input and output are symmetric, we set the output according to the input
        # format.
        if self.format.format_input.input_type == InputFormat.JSON:
            self.format.format_output = FormatOutput(output_type=OutputFormat.JSON)
        elif self.format.format_input.input_type == InputFormat.TEXT:  # Text still maps to json
            self.format.format_output = FormatOutput(output_type=OutputFormat.JSON)
        elif self.format.format_input.input_type == InputFormat.CSV_ARCHIVE:
            self.format.format_output = FormatOutput(output_type=OutputFormat.CSV_ARCHIVE)
        elif self.format.format_input.input_type == InputFormat.MULTI_FILE:
            self.format.format_output = FormatOutput(output_type=OutputFormat.MULTI_FILE)
        else:
            self.format.format_output = FormatOutput(output_type=OutputFormat.JSON)


class ExternalRunResult(BaseModel):
    """
    Result of a run used to configure a new application run as an
    external one.

    You can import the `ExternalRunResult` class directly from `nextmv`:

    ```python
    from nextmv import ExternalRunResult
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

    Examples
    --------
    >>> from nextmv import ExternalRunResult
    >>> # Successful external run
    >>> result = ExternalRunResult(
    ...     output_upload_id="upload-12345",
    ...     status="succeeded",
    ...     execution_duration=5000
    ... )
    >>> result.status
    'succeeded'
    >>> result.execution_duration
    5000

    >>> # Failed external run
    >>> failed_result = ExternalRunResult(
    ...     error_upload_id="error-67890",
    ...     status="failed",
    ...     error_message="Optimization failed due to invalid constraints",
    ...     execution_duration=2000
    ... )
    >>> failed_result.status
    'failed'
    >>> failed_result.error_message
    'Optimization failed due to invalid constraints'
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

    You can import the `TrackedRunStatus` class directly from `nextmv`:

    ```python
    from nextmv import TrackedRunStatus
    ```

    Parameters
    ----------
    SUCCEEDED : str
        The run succeeded.
    FAILED : str
        The run failed.

    Examples
    --------
    >>> from nextmv import TrackedRunStatus
    >>> status = TrackedRunStatus.SUCCEEDED
    >>> status
    <TrackedRunStatus.SUCCEEDED: 'succeeded'>
    >>> status.value
    'succeeded'

    >>> # Creating from string
    >>> failed_status = TrackedRunStatus("failed")
    >>> failed_status
    <TrackedRunStatus.FAILED: 'failed'>

    >>> # All available statuses
    >>> list(TrackedRunStatus)
    [<TrackedRunStatus.SUCCEEDED: 'succeeded'>, <TrackedRunStatus.FAILED: 'failed'>]
    """

    SUCCEEDED = "succeeded"
    """The run succeeded."""
    FAILED = "failed"
    """The run failed."""


@dataclass
class TrackedRun:
    """
    An external run that is tracked in the Nextmv platform.

    You can import the `TrackedRun` class directly from `nextmv`:

    ```python
    from nextmv import TrackedRun
    ```

    Parameters
    ----------
    status : TrackedRunStatus
        The status of the run being tracked. This field is required.
    input : Input or dict[str, Any] or str, optional
        The input of the run being tracked. Please note that if the input
        format is JSON, then the input data must be JSON serializable. If both
        `input` and `input_dir_path` are specified, the `input` is ignored, and
        the files in the directory are used instead. Defaults to None.
    output : Output or dict[str, Any] or str, optional
        The output of the run being tracked. Please note that if the output
        format is JSON, then the output data must be JSON serializable. If both
        `output` and `output_dir_path` are specified, the `output` is ignored, and
        the files in the directory are used instead. Defaults to None.
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
    name : str, optional
        Optional name for the run being tracked. Defaults to None.
    description : str, optional
        Optional description for the run being tracked. Defaults to None.
    input_dir_path : str, optional
        Path to a directory containing input files. If specified, the calling
        function will package the files in the directory into a tar file and upload
        it as a large input. This is useful for non-JSON input formats, such as
        when working with `CSV_ARCHIVE` or `MULTI_FILE`. If both `input` and
        `input_dir_path` are specified, the `input` is ignored, and the files in
        the directory are used instead. Defaults to None.
    output_dir_path : str, optional
        Path to a directory containing output files. If specified, the calling
        function will package the files in the directory into a tar file and upload
        it as a large output. This is useful for non-JSON output formats, such as
        when working with `CSV_ARCHIVE` or `MULTI_FILE`. If both `output` and
        `output_dir_path` are specified, the `output` is ignored, and the files
        are saved in the directory instead. Defaults to None.

    Examples
    --------
    >>> from nextmv import TrackedRun, TrackedRunStatus
    >>> # Successful run
    >>> run = TrackedRun(
    ...     status=TrackedRunStatus.SUCCEEDED,
    ...     input={"vehicles": 5, "locations": 10},
    ...     output={"routes": [{"stops": [1, 2, 3]}]},
    ...     duration=5000,
    ...     name="test-run",
    ...     description="A test optimization run"
    ... )
    >>> run.status
    <TrackedRunStatus.SUCCEEDED: 'succeeded'>
    >>> run.duration
    5000

    >>> # Failed run with error
    >>> failed_run = TrackedRun(
    ...     status=TrackedRunStatus.FAILED,
    ...     input={"vehicles": 0},
    ...     error="No vehicles available for routing",
    ...     duration=1000,
    ...     logs=["Starting optimization", "Error: No vehicles found"]
    ... )
    >>> failed_run.status
    <TrackedRunStatus.FAILED: 'failed'>
    >>> failed_run.error
    'No vehicles available for routing'

    >>> # Run with directory-based input/output
    >>> dir_run = TrackedRun(
    ...     status=TrackedRunStatus.SUCCEEDED,
    ...     input_dir_path="/path/to/input/files",
    ...     output_dir_path="/path/to/output/files",
    ...     duration=10000
    ... )
    >>> dir_run.input_dir_path
    '/path/to/input/files'

    Raises
    ------
    ValueError
        If the status value is invalid, if an error message is provided for a
        successful run, or if input/output formats are not JSON or
        input/output dicts are not JSON serializable.
    """

    status: TrackedRunStatus
    """The status of the run being tracked"""

    input: Optional[Union[Input, dict[str, Any], str]] = None
    """
    The input of the run being tracked. Please note that if the input
    format is JSON, then the input data must be JSON serializable. If both
    `input` and `input_dir_path` are specified, the `input` is ignored, and
    the files in the directory are used instead.
    """
    output: Optional[Union[Output, dict[str, Any], str]] = None
    """
    The output of the run being tracked. Please note that if the output
    format is JSON, then the output data must be JSON serializable. If both
    `output` and `output_dir_path` are specified, the `output` is ignored, and
    the files in the directory are used instead.
    """
    duration: Optional[int] = None
    """The duration of the run being tracked, in milliseconds."""
    error: Optional[str] = None
    """An error message if the run failed. You should only specify this if the
    run failed, otherwise an exception will be raised."""
    logs: Optional[list[str]] = None
    """The logs of the run being tracked. Each element of the list is a line in
    the log."""
    name: Optional[str] = None
    """
    Optional name for the run being tracked.
    """
    description: Optional[str] = None
    """
    Optional description for the run being tracked.
    """
    input_dir_path: Optional[str] = None
    """
    Path to a directory containing input files. If specified, the calling
    function will package the files in the directory into a tar file and upload
    it as a large input. This is useful for non-JSON input formats, such as
    when working with `CSV_ARCHIVE` or `MULTI_FILE`. If both `input` and
    `input_dir_path` are specified, the `input` is ignored, and the files in
    the directory are used instead.
    """
    output_dir_path: Optional[str] = None
    """
    Path to a directory containing output files. If specified, the calling
    function will package the files in the directory into a tar file and upload
    it as a large output. This is useful for non-JSON output formats, such as
    when working with `CSV_ARCHIVE` or `MULTI_FILE`. If both `output` and
    `output_dir_path` are specified, the `output` is ignored, and the files
    are saved in the directory instead.
    """

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
            try:
                _ = serialize_json(self.input.data)
            except (TypeError, OverflowError) as e:
                raise ValueError("Input.data is not JSON serializable") from e
        elif isinstance(self.input, dict):
            try:
                _ = serialize_json(self.input)
            except (TypeError, OverflowError) as e:
                raise ValueError("Input is dict[str, Any] but it is not JSON serializable") from e

        if isinstance(self.output, Output):
            try:
                _ = serialize_json(self.output.data)
            except (TypeError, OverflowError) as e:
                raise ValueError("Output.data is not JSON serializable") from e
        elif isinstance(self.output, dict):
            try:
                _ = serialize_json(self.output)
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

        Examples
        --------
        >>> from nextmv import TrackedRun, TrackedRunStatus
        >>> run = TrackedRun(
        ...     status=TrackedRunStatus.SUCCEEDED,
        ...     logs=["Starting optimization", "Processing data", "Optimization complete"]
        ... )
        >>> run.logs_text()
        'Starting optimization\\nProcessing data\\nOptimization complete'

        >>> # Single string log
        >>> run_with_string_log = TrackedRun(
        ...     status=TrackedRunStatus.SUCCEEDED,
        ...     logs="Single log entry"
        ... )
        >>> run_with_string_log.logs_text()
        'Single log entry'

        >>> # No logs
        >>> run_no_logs = TrackedRun(status=TrackedRunStatus.SUCCEEDED)
        >>> run_no_logs.logs_text()
        ''

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
