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
from typing import Any

from pydantic import AliasChoices, Field, field_validator

from nextmv._serialization import serialize_json
from nextmv.base_model import BaseModel
from nextmv.input import Input, InputFormat
from nextmv.output import Asset, Output, OutputFormat, Statistics
from nextmv.status import StatusV2


def run_duration(start: datetime | float, end: datetime | float) -> int:
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
    format_output: FormatOutput | None = Field(
        serialization_alias="output",
        validation_alias=AliasChoices("output", "format_output"),
        default=None,
    )
    """Output format for the run configuration."""


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

    run_type: RunType | None = Field(
        serialization_alias="type",
        validation_alias=AliasChoices("type", "run_type"),
        default=None,
    )
    """Type of the run."""
    definition_id: str | None = None
    """ID of the definition for the run type."""
    reference_id: str | None = None
    """ID of the reference for the run type."""

    @field_validator("run_type", mode="before")
    @classmethod
    def validate_run_type(cls, v):
        """Convert empty string to None for run_type validation."""
        if v == "":
            return None
        return v


class StatisticsIndicator(BaseModel):
    """
    Statistics indicator of a run.

    You can import the `StatisticsIndicator` class directly from `nextmv`:

    ```python
    from nextmv import StatisticsIndicator
    ```

    Parameters
    ----------
    name : str
        Name of the indicator.
    value : Any
        Value of the indicator.

    Examples
    --------
    >>> from nextmv import StatisticsIndicator
    >>> indicator = StatisticsIndicator(name="total_cost", value=1250.75)
    >>> indicator.name
    'total_cost'
    >>> indicator.value
    1250.75

    >>> # Boolean indicator
    >>> bool_indicator = StatisticsIndicator(name="optimal", value=True)
    >>> bool_indicator.name
    'optimal'
    >>> bool_indicator.value
    True
    """

    name: str
    """Name of the indicator."""
    value: Any
    """Value of the indicator."""


class RunInfoStatistics(BaseModel):
    """
    Statistics information for a run.

    You can import the `RunInfoStatistics` class directly from `nextmv`:

    ```python
    from nextmv import RunInfoStatistics
    ```

    Parameters
    ----------
    status : str
        Status of the statistics in the run.
    error : str, optional
        Error message if the statistics could not be retrieved. Defaults to None.
    indicators : list[StatisticsIndicator], optional
        List of statistics indicators. Defaults to None.

    Examples
    --------
    >>> from nextmv import RunInfoStatistics, StatisticsIndicator
    >>> indicators = [
    ...     StatisticsIndicator(name="total_cost", value=1250.75),
    ...     StatisticsIndicator(name="optimal", value=True)
    ... ]
    >>> stats = RunInfoStatistics(status="success", indicators=indicators)
    >>> stats.status
    'success'
    >>> len(stats.indicators)
    2

    >>> # Statistics with error
    >>> error_stats = RunInfoStatistics(
    ...     status="error",
    ...     error="Failed to calculate statistics"
    ... )
    >>> error_stats.status
    'error'
    >>> error_stats.error
    'Failed to calculate statistics'
    """

    status: str
    """Status of the statistics in the run."""

    error: str | None = None
    """Error message if the statistics could not be retrieved."""
    indicators: list[StatisticsIndicator] | None = None
    """List of statistics indicators."""


class OptionsSummaryItem(BaseModel):
    """
    Summary item for options used in a run.

    You can import the `OptionsSummaryItem` class directly from `nextmv`:

    ```python
    from nextmv import OptionsSummaryItem
    ```

    Parameters
    ----------
    name : str
        Name of the option.
    value : Any
        Value of the option.
    source : str
        Source of the option.

    Examples
    --------
    >>> from nextmv import OptionsSummaryItem
    >>> option = OptionsSummaryItem(
    ...     name="time_limit",
    ...     value=30,
    ...     source="config"
    ... )
    >>> option.name
    'time_limit'
    >>> option.value
    30
    >>> option.source
    'config'

    >>> # Option from environment variable
    >>> env_option = OptionsSummaryItem(
    ...     name="solver_type",
    ...     value="gurobi",
    ...     source="environment"
    ... )
    >>> env_option.source
    'environment'
    """

    name: str
    """Name of the option."""
    value: Any
    """Value of the option."""
    source: str
    """Source of the option."""


class Run(BaseModel):
    """
    Information about a run in the Nextmv platform.

    You can import the `Run` class directly from `nextmv`:

    ```python
    from nextmv import Run
    ```

    Parameters
    ----------
    id : str
        ID of the run.
    user_email : str
        Email of the user who initiated the run.
    name : str
        Name of the run.
    description : str
        Description of the run.
    created_at : datetime
        Timestamp when the run was created.
    application_id : str
        ID of the application associated with the run.
    application_instance_id : str
        ID of the application instance associated with the run.
    application_version_id : str
        ID of the application version associated with the run.
    run_type : RunTypeConfiguration
        Configuration for the type of the run.
    execution_class : str
        Class name for the execution of a job.
    runtime : str
        Runtime environment for the run.
    status_v2 : StatusV2
        Status of the run.
    queuing_priority : int, optional
        Priority of the run in the queue. Defaults to None.
    queuing_disabled : bool, optional
        Whether the run is disabled from queuing. Defaults to None.
    experiment_id : str, optional
        ID of the experiment associated with the run. Defaults to None.
    statistics : RunInfoStatistics, optional
        Statistics of the run. Defaults to None.
    input_id : str, optional
        ID of the input associated with the run. Defaults to None.
    option_set : str, optional
        ID of the option set associated with the run. Defaults to None.
    options : dict[str, str], optional
        Options associated with the run. Defaults to None.
    request_options : dict[str, str], optional
        Request options associated with the run. Defaults to None.
    options_summary : list[OptionsSummaryItem], optional
        Summary of options used in the run. Defaults to None.
    scenario_id : str, optional
        ID of the scenario associated with the run. Defaults to None.
    repetition : int, optional
        Repetition number of the run. Defaults to None.
    input_set_id : str, optional
        ID of the input set associated with the run. Defaults to None.

    Examples
    --------
    >>> from nextmv import Run, RunTypeConfiguration, RunType, StatusV2
    >>> from datetime import datetime
    >>> run = Run(
    ...     id="run-12345",
    ...     user_email="user@example.com",
    ...     name="Test Run",
    ...     description="A test optimization run",
    ...     created_at=datetime.now(),
    ...     application_id="app-123",
    ...     application_instance_id="instance-456",
    ...     application_version_id="version-789",
    ...     run_type=RunTypeConfiguration(run_type=RunType.STANDARD),
    ...     execution_class="small",
    ...     runtime="python",
    ...     status_v2=StatusV2.SUCCEEDED
    ... )
    >>> run.id
    'run-12345'
    >>> run.name
    'Test Run'
    """

    id: str
    """ID of the run."""
    user_email: str
    """Email of the user who initiated the run."""
    name: str
    """Name of the run."""
    description: str
    """Description of the run."""
    created_at: datetime
    """Timestamp when the run was created."""
    application_id: str
    """ID of the application associated with the run."""
    application_instance_id: str
    """ID of the application instance associated with the run."""
    application_version_id: str
    """ID of the application version associated with the run."""
    run_type: RunTypeConfiguration
    """Configuration for the type of the run."""
    execution_class: str
    """Class name for the execution of a job."""
    runtime: str
    """Runtime environment for the run."""
    status_v2: StatusV2
    """Status of the run."""

    queuing_priority: int | None = None
    """Priority of the run in the queue."""
    queuing_disabled: bool | None = None
    """Whether the run is disabled from queuing."""
    experiment_id: str | None = None
    """ID of the experiment associated with the run."""
    statistics: RunInfoStatistics | None = None
    """Statistics of the run."""
    input_id: str | None = None
    """ID of the input associated with the run."""
    option_set: str | None = None
    """ID of the option set associated with the run."""
    options: dict[str, str] | None = None
    """Options associated with the run."""
    request_options: dict[str, str] | None = None
    """Request options associated with the run."""
    options_summary: list[OptionsSummaryItem] | None = None
    """Summary of options used in the run."""
    scenario_id: str | None = None
    """ID of the scenario associated with the run."""
    repetition: int | None = None
    """Repetition number of the run."""
    input_set_id: str | None = None
    """ID of the input set associated with the run."""


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
    statistics: dict[str, Any] | None = None
    """User defined statistics of the run."""

    def run_is_finalized(self) -> bool:
        """
        Checks if the run has reached a finalized state.

        Returns
        -------
        bool
            True if the run status is one of `succeeded`, `failed`, or
            `canceled`. False otherwise.
        """

        return self.status_v2 in {
            StatusV2.succeeded,
            StatusV2.failed,
            StatusV2.canceled,
        }


class SyncedRun(BaseModel):
    """
    Information about a run that has been synced to a remote application.

    You can import the `SyncedRun` class directly from `nextmv`:

    ```python
    from nextmv import SyncedRun
    ```

    Parameters
    ----------
    run_id : str
        ID of the synced remote run. When the `Application.sync` method is
        used, this field marks the association between the local run (`id`) and
        the remote run (`synced_run.id`).
    synced_at : datetime
        Timestamp when the run was synced with the remote run.
    app_id : str
        The ID of the remote application that the local run was synced to.
    instance_id : Optional[str], optional
        The instance of the remote application that the local run was synced
        to. This field is optional and may be None. If it is not specified, it
        indicates that the run was synced against the default instance of the
        app. Defaults to None.
    """

    run_id: str
    """
    ID of the synced remote run. When the `Application.sync` method is used,
    this field marks the association between the local run (`id`) and the
    remote run (`synced_run.id`)
    """
    synced_at: datetime
    """
    Timestamp when the run was synced with the remote run.
    """
    app_id: str
    """
    The ID of the remote application that the local run was synced to.
    """

    instance_id: str | None = None
    """
    The instance of the remote application that the local run was synced to.
    This field is optional and may be None. If it is not specified, it
    indicates that the run was synced against the default instance of the app.
    """


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
    synced_runs: list[SyncedRun] | None = None
    """
    List of synced runs associated with this run, if applicable. When the
    `Application.sync` method is used, this field contains the associations
    between the local run (`id`) and the remote runs (`synced_run.id`). This
    field is None if the run was not created using `Application.sync` or if the
    run has not been synced yet. It is possible to sync a single local run to
    multiple remote runs. A remote run is identified by its application ID and
    instance (if applicable). A local run cannot be synced to a remote run if
    it is already present, this is, if there exists a record in the list with
    the same application ID and instance. If there is not a repeated remote
    run, a new record is added to the list.
    """

    def to_run(self) -> Run:
        """
        Transform this `RunInformation` instance into a `Run` instance.

        This method maps all available attributes from the `RunInformation`
        and its metadata to create a `Run` instance. Attributes that are not
        available in RunInformation are set to None or appropriate defaults.

        Returns
        -------
        Run
            A Run instance with attributes populated from this RunInformation.

        Examples
        --------
        >>> from nextmv import RunInformation, Metadata, Format, FormatInput, FormatOutput
        >>> from nextmv import StatusV2, RunTypeConfiguration, RunType
        >>> from datetime import datetime
        >>> metadata = Metadata(
        ...     application_id="app-123",
        ...     application_instance_id="instance-456",
        ...     application_version_id="version-789",
        ...     created_at=datetime.now(),
        ...     duration=5000.0,
        ...     error="",
        ...     input_size=1024.0,
        ...     output_size=2048.0,
        ...     format=Format(
        ...         format_input=FormatInput(),
        ...         format_output=FormatOutput()
        ...     ),
        ...     status_v2=StatusV2.SUCCEEDED
        ... )
        >>> run_info = RunInformation(
        ...     id="run-123",
        ...     description="Test run",
        ...     name="Test",
        ...     user_email="user@example.com",
        ...     metadata=metadata
        ... )
        >>> run = run_info.to_run()
        >>> run.id
        'run-123'
        >>> run.application_id
        'app-123'
        """
        return Run(
            id=self.id,
            user_email=self.user_email,
            name=self.name,
            description=self.description,
            created_at=self.metadata.created_at,
            application_id=self.metadata.application_id,
            application_instance_id=self.metadata.application_instance_id,
            application_version_id=self.metadata.application_version_id,
            run_type=RunTypeConfiguration(),  # Default empty configuration
            execution_class="",  # Not available in RunInformation
            runtime="",  # Not available in RunInformation
            status_v2=self.metadata.status_v2,
            # Optional fields that are not available in RunInformation
            queuing_priority=None,
            queuing_disabled=None,
            experiment_id=None,
            statistics=None,
            input_id=None,
            option_set=None,
            options=None,
            request_options=None,
            options_summary=None,
            scenario_id=None,
            repetition=None,
            input_set_id=None,
        )

    def add_synced_run(self, synced_run: SyncedRun) -> bool:
        """
        Add a synced run to the RunInformation.

        This method adds a `SyncedRun` instance to the list of synced runs
        associated with this `RunInformation`. If the list is None, it
        initializes it first. If the run has already been synced, then it is
        not added to the list. A run is already synced if there exists a record
        in the list with the same application ID. This method returns True if
        the synced run was added, and False otherwise.

        Parameters
        ----------
        synced_run : SyncedRun
            The SyncedRun instance to add.

        Returns
        -------
        bool
            True if the synced run was added, False if it was already present.
        """

        if self.synced_runs is None:
            self.synced_runs = [synced_run]

            return True

        if synced_run.instance_id is None:
            for existing_run in self.synced_runs:
                if existing_run.app_id == synced_run.app_id:
                    return False
        else:
            for existing_run in self.synced_runs:
                if existing_run.app_id == synced_run.app_id and existing_run.instance_id == synced_run.instance_id:
                    return False

        self.synced_runs.append(synced_run)

        return True

    def is_synced(self, app_id: str, instance_id: str | None = None) -> tuple[SyncedRun, bool]:
        """
        Check if the run has been synced to a specific application and instance.

        This method checks if there exists a `SyncedRun` in the list of synced
        runs that matches the given application ID and optional instance ID.

        Parameters
        ----------
        app_id : str
            The application ID to check.
        instance_id : Optional[str], optional
            The instance ID to check. If None, only the application ID is
            considered. Defaults to None.

        Returns
        -------
        tuple[SyncedRun, bool]
            A tuple containing the SyncedRun instance if found, and a boolean
            indicating whether the run has been synced to the specified
            application and instance.
        """

        if self.synced_runs is None:
            return None, False

        if instance_id is None:
            for existing_run in self.synced_runs:
                if existing_run.app_id == app_id:
                    return existing_run, True
        else:
            for existing_run in self.synced_runs:
                if existing_run.app_id == app_id and existing_run.instance_id == instance_id:
                    return existing_run, True

        return None, False


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

    error: str | None = None
    """Error message."""
    stdout: str | None = None
    """Standard output."""
    stderr: str | None = None
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

    error_log: ErrorLog | None = None
    """Error log of the run. Only available if the run failed."""
    output: dict[str, Any] | None = None
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


class TimestampedRunLog(BaseModel):
    """
    Timestamped log entry of a run.

    You can import the `TimestampedRunLog` class directly from `nextmv`:

    ```python
    from nextmv import TimestampedRunLog
    ```

    Parameters
    ----------
    timestamp : datetime
        Timestamp of the log entry.
    log : str
        Log message.

    Examples
    --------
    >>> from nextmv import TimestampedRunLog
    >>> from datetime import datetime
    >>> log_entry = TimestampedRunLog(
    ...     timestamp=datetime(2023, 1, 1, 12, 0, 0),
    ...     log="Optimization started"
    ... )
    >>> log_entry.timestamp
    datetime.datetime(2023, 1, 1, 12, 0)
    >>> log_entry.log
    'Optimization started'
    """

    timestamp: datetime
    """Timestamp of the log entry."""
    log: str
    """Log message."""


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

    priority: int | None = None
    """
    Priority of the run in the queue. 1 is the highest priority, 9 is the
    lowest priority.
    """
    disabled: bool | None = None
    """
    Whether the run should be queued, or not. If True, the run will not be
    queued. If False, the run will be queued.
    """

    def model_post_init(self, __context) -> None:
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
    integration_id : str, optional
        ID of the integration to use for the run. Defaults to None.

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

    execution_class: str | None = None
    """Execution class for the instance."""
    format: Format | None = None
    """Format for the run configuration."""
    run_type: RunTypeConfiguration | None = None
    """Run type configuration for the run."""
    secrets_collection_id: str | None = None
    """ID of the secrets collection to use for the run."""
    queuing: RunQueuing | None = None
    """Queuing configuration for the run."""
    integration_id: str | None = None
    """ID of the integration to use for the run."""

    def model_post_init(self, __context) -> None:
        """
        Validations done after parsing the model.

        Raises
        ------
        ValueError
            If execution_class is an empty string.
        """

        if self.integration_id is None or self.integration_id == "":
            return

        integration_val = "integration"
        if self.execution_class is not None and self.execution_class != "" and self.execution_class != integration_val:
            raise ValueError(f"When integration_id is set, execution_class must be `{integration_val}` or None.")

        self.execution_class = integration_val

    def resolve(
        self,
        input: Input | dict[str, Any] | BaseModel | str,
        dir_path: str | None = None,
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

    output_upload_id: str | None = None
    """ID of the output upload."""
    error_upload_id: str | None = None
    """ID of the error upload."""
    status: str | None = None
    """Status of the run."""
    error_message: str | None = None
    """Error message of the run."""
    execution_duration: int | None = None
    """Duration of the run, in milliseconds."""
    statistics_upload_id: str | None = None
    """
    ID of the statistics upload. Use this field when working with `CSV_ARCHIVE`
    or `MULTI_FILE` output formats.
    """
    assets_upload_id: str | None = None
    """
    ID of the assets upload. Use this field when working with `CSV_ARCHIVE`
    or `MULTI_FILE` output formats.
    """

    def model_post_init(self, __context) -> None:
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
        `output` and `output_dir_path` are specified, the `output` is ignored,
        and the files in the directory are used instead. Defaults to None.
    duration : int, optional
        The duration of the run being tracked, in milliseconds. This field is
        optional. Defaults to None.
    error : str, optional
        An error message if the run failed. You should only specify this if the
        run failed (the `status` is `TrackedRunStatus.FAILED`), otherwise an
        exception will be raised. This field is optional. Defaults to None.
    logs : str or list[str], optional
        The logs of the run being tracked. If the logs are provided as a list,
        each element of the list is a line in the log. This field is optional.
        Defaults to None.
    name : str, optional
        Optional name for the run being tracked. Defaults to None.
    description : str, optional
        Optional description for the run being tracked. Defaults to None.
    input_dir_path : str, optional
        Path to a directory containing input files. If specified, the calling
        function will package the files in the directory into a tar file and
        upload it as a large input. This is useful for non-JSON input formats,
        such as when working with `CSV_ARCHIVE` or `MULTI_FILE`. If both
        `input` and `input_dir_path` are specified, the `input` is ignored, and
        the files in the directory are used instead. Defaults to None.
    output_dir_path : str, optional
        Path to a directory containing output files. If specified, the calling
        function will package the files in the directory into a tar file and
        upload it as a large output. This is useful for non-JSON output
        formats, such as when working with `CSV_ARCHIVE` or `MULTI_FILE`. If
        both `output` and `output_dir_path` are specified, the `output` is
        ignored, and the files are saved in the directory instead. Defaults to
        None.
    statistics : Statistics or dict[str, Any], optional
        Statistics of the run being tracked. Only use this field if you want to
        track statistics for `CSV_ARCHIVE` or `MULTI_FILE` output formats. If
        you are working with `JSON` or `TEXT` output formats, this field will
        be ignored, as the statistics are extracted directly from the `output`.
        This field is optional. Defaults to None.
    assets : list[Asset or dict[str, Any]], optional
        Assets associated with the run being tracked. Only use this field if
        you want to track assets for `CSV_ARCHIVE` or `MULTI_FILE` output
        formats. If you are working with `JSON` or `TEXT` output formats, this
        field will be ignored, as the assets are extracted directly from the
        `output`. This field is optional. Defaults to None.

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
        successful run, or if input/output formats are not JSON or input/output
        dicts are not JSON serializable.
    """

    status: TrackedRunStatus
    """The status of the run being tracked"""

    input: Input | dict[str, Any] | str | None = None
    """
    The input of the run being tracked. Please note that if the input
    format is JSON, then the input data must be JSON serializable. If both
    `input` and `input_dir_path` are specified, the `input` is ignored, and
    the files in the directory are used instead.
    """
    output: Output | dict[str, Any] | str | None = None
    """
    The output of the run being tracked. Please note that if the output
    format is JSON, then the output data must be JSON serializable. If both
    `output` and `output_dir_path` are specified, the `output` is ignored, and
    the files in the directory are used instead.
    """
    duration: int | None = None
    """The duration of the run being tracked, in milliseconds."""
    error: str | None = None
    """An error message if the run failed. You should only specify this if the
    run failed, otherwise an exception will be raised."""
    logs: str | list[str] | None = None
    """The logs of the run being tracked. If a list, each element is a line in
    the log."""
    name: str | None = None
    """
    Optional name for the run being tracked.
    """
    description: str | None = None
    """
    Optional description for the run being tracked.
    """
    input_dir_path: str | None = None
    """
    Path to a directory containing input files. If specified, the calling
    function will package the files in the directory into a tar file and upload
    it as a large input. This is useful for non-JSON input formats, such as
    when working with `CSV_ARCHIVE` or `MULTI_FILE`. If both `input` and
    `input_dir_path` are specified, the `input` is ignored, and the files in
    the directory are used instead.
    """
    output_dir_path: str | None = None
    """
    Path to a directory containing output files. If specified, the calling
    function will package the files in the directory into a tar file and upload
    it as a large output. This is useful for non-JSON output formats, such as
    when working with `CSV_ARCHIVE` or `MULTI_FILE`. If both `output` and
    `output_dir_path` are specified, the `output` is ignored, and the files
    are saved in the directory instead.
    """
    statistics: Statistics | dict[str, Any] | None = None
    """
    Statistics of the run being tracked. Only use this field if you want to
    track statistics for `CSV_ARCHIVE` or `MULTI_FILE` output formats. If you
    are working with `JSON` or `TEXT` output formats, this field will be
    ignored, as the statistics are extracted directly from the `output`.
    """
    assets: list[Asset | dict[str, Any]] | None = None
    """
    Assets associated with the run being tracked. Only use this field if you
    want to track assets for `CSV_ARCHIVE` or `MULTI_FILE` output formats.
    If you are working with `JSON` or `TEXT` output formats, this field will
    be ignored, as the assets are extracted directly from the `output`.
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
                _ = serialize_json(self.output.solution)
            except (TypeError, OverflowError) as e:
                raise ValueError("`Output.solution` is not JSON serializable") from e
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
