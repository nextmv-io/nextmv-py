"""
Module for handling output destinations and data.

This module provides classes and functions for handling the output of decision
problems, including formatting, serialization, and writing to various
destinations.

Classes
-------
RunStatistics
    Statistics about a general run.
ResultStatistics
    Statistics about a specific result.
DataPoint
    A data point representing a 2D coordinate.
Series
    A series of data points for visualization or analysis.
SeriesData
    Data container for multiple series of data points.
Statistics
    Complete statistics container for a solution, including run metrics and result data.
OutputFormat
    Enumeration of supported output formats.
VisualSchema
    Enumeration of supported visualization schemas.
Visual
    Visual schema definition for an asset.
Asset
    Represents downloadable information that is part of the `Output`.
Output
    A class for representing the output of a decision problem.
OutputWriter
    Base class for writing outputs to different destinations.
LocalOutputWriter
    Class for writing outputs to local files or stdout.

Functions
---------
write
    Write the output to the specified destination.
"""

import copy
import csv
import datetime
import json
import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Union

from pydantic import AliasChoices, Field

from nextmv.base_model import BaseModel
from nextmv.deprecated import deprecated
from nextmv.logger import reset_stdout
from nextmv.options import Options


class RunStatistics(BaseModel):
    """
    Statistics about a general run.

    You can import the `RunStatistics` class directly from `nextmv`:

    ```python
    from nextmv import RunStatistics
    ```

    Parameters
    ----------
    duration : float, optional
        Duration of the run in seconds.
    iterations : int, optional
        Number of iterations.
    custom : Union[Any, dict[str, Any]], optional
        Custom statistics created by the user. Can normally expect a `dict[str,
        Any]`.

    Examples
    --------
    >>> from nextmv.output import RunStatistics
    >>> stats = RunStatistics(duration=10.5, iterations=100)
    >>> stats.duration
    10.5
    >>> stats.custom = {"convergence": 0.001}
    >>> stats.to_dict()
    {'duration': 10.5, 'iterations': 100, 'custom': {'convergence': 0.001}}
    """

    duration: Optional[float] = None
    """Duration of the run in seconds."""
    iterations: Optional[int] = None
    """Number of iterations."""
    custom: Optional[
        Union[
            Any,
            dict[str, Any],
        ]
    ] = None
    """Custom statistics created by the user. Can normally expect a `dict[str,
    Any]`."""


class ResultStatistics(BaseModel):
    """
    Statistics about a specific result.

    You can import the `ResultStatistics` class directly from `nextmv`:

    ```python
    from nextmv import ResultStatistics
    ```

    Parameters
    ----------
    duration : float, optional
        Duration of the run in seconds.
    value : float, optional
        Value of the result.
    custom : Union[Any, dict[str, Any]], optional
        Custom statistics created by the user. Can normally expect a `dict[str,
        Any]`.

    Examples
    --------
    >>> from nextmv.output import ResultStatistics
    >>> result_stats = ResultStatistics(duration=5.2, value=42.0)
    >>> result_stats.value
    42.0
    >>> result_stats.custom = {"gap": 0.05}
    >>> result_stats.to_dict()
    {'duration': 5.2, 'value': 42.0, 'custom': {'gap': 0.05}}
    """

    duration: Optional[float] = None
    """Duration of the run in seconds."""
    value: Optional[float] = None
    """Value of the result."""
    custom: Optional[
        Union[
            Any,
            dict[str, Any],
        ]
    ] = None
    """Custom statistics created by the user. Can normally expect a `dict[str,
    Any]`."""


class DataPoint(BaseModel):
    """
    A data point representing a 2D coordinate.

    You can import the `DataPoint` class directly from `nextmv`:

    ```python
    from nextmv import DataPoint
    ```

    Parameters
    ----------
    x : float
        X coordinate of the data point.
    y : float
        Y coordinate of the data point.

    Examples
    --------
    >>> from nextmv.output import DataPoint
    >>> point = DataPoint(x=3.5, y=4.2)
    >>> point.x
    3.5
    >>> point.to_dict()
    {'x': 3.5, 'y': 4.2}
    """

    x: float
    """X coordinate of the data point."""
    y: float
    """Y coordinate of the data point."""


class Series(BaseModel):
    """
    A series of data points for visualization or analysis.

    You can import the `Series` class directly from `nextmv`:

    ```python
    from nextmv import Series
    ```

    Parameters
    ----------
    name : str, optional
        Name of the series.
    data_points : list[DataPoint], optional
        Data points of the series.

    Examples
    --------
    >>> from nextmv.output import Series, DataPoint
    >>> points = [DataPoint(x=1.0, y=2.0), DataPoint(x=2.0, y=3.0)]
    >>> series = Series(name="Example Series", data_points=points)
    >>> series.name
    'Example Series'
    >>> len(series.data_points)
    2
    """

    name: Optional[str] = None
    """Name of the series."""
    data_points: Optional[list[DataPoint]] = None
    """Data of the series."""


class SeriesData(BaseModel):
    """
    Data container for multiple series of data points.

    You can import the `SeriesData` class directly from `nextmv`:

    ```python
    from nextmv import SeriesData
    ```

    Parameters
    ----------
    value : Series, optional
        A series for the value of the solution.
    custom : list[Series], optional
        A list of series for custom statistics.

    Examples
    --------
    >>> from nextmv.output import SeriesData, Series, DataPoint
    >>> value_series = Series(name="Solution Value", data_points=[DataPoint(x=0, y=10), DataPoint(x=1, y=5)])
    >>> custom_series = [Series(name="Gap", data_points=[DataPoint(x=0, y=0.5), DataPoint(x=1, y=0.1)])]
    >>> series_data = SeriesData(value=value_series, custom=custom_series)
    >>> series_data.value.name
    'Solution Value'
    >>> len(series_data.custom)
    1
    """

    value: Optional[Series] = None
    """A series for the value of the solution."""
    custom: Optional[list[Series]] = None
    """A list of series for custom statistics."""


class Statistics(BaseModel):
    """
    Complete statistics container for a solution, including run metrics and
    result data.

    You can import the `Statistics` class directly from `nextmv`:

    ```python
    from nextmv import Statistics
    ```

    Parameters
    ----------
    run : RunStatistics, optional
        Statistics about the run.
    result : ResultStatistics, optional
        Statistics about the last result.
    series_data : SeriesData, optional
        Series data about some metric.
    statistics_schema : str, optional
        Schema (version). This class only supports `v1`.

    Examples
    --------
    >>> from nextmv.output import Statistics, RunStatistics, ResultStatistics
    >>> run_stats = RunStatistics(duration=10.0, iterations=50)
    >>> result_stats = ResultStatistics(value=100.0)
    >>> stats = Statistics(run=run_stats, result=result_stats, statistics_schema="v1")
    >>> stats.run.duration
    10.0
    >>> stats.result.value
    100.0
    """

    run: Optional[RunStatistics] = None
    """Statistics about the run."""
    result: Optional[ResultStatistics] = None
    """Statistics about the last result."""
    series_data: Optional[SeriesData] = None
    """Data of the series."""
    statistics_schema: Optional[str] = Field(
        serialization_alias="schema",
        validation_alias=AliasChoices("schema", "statistics_schema"),
        default="v1",
    )
    """Schema (version). This class only supports `v1`."""


class OutputFormat(str, Enum):
    """
    Enumeration of supported output formats.

    You can import the `OutputFormat` class directly from `nextmv`:

    ```python
    from nextmv import OutputFormat
    ```

    This enum defines the different formats that can be used for outputting data.
    Each format has specific requirements and behaviors when writing.

    Attributes
    ----------
    JSON : str
        JSON format, utf-8 encoded.
    CSV_ARCHIVE : str
        CSV archive format: multiple CSV files.
    """

    JSON = "json"
    """JSON format, utf-8 encoded."""
    CSV_ARCHIVE = "csv-archive"
    """CSV archive format: multiple CSV files."""


class VisualSchema(str, Enum):
    """
    Enumeration of supported visualization schemas.

    You can import the `VisualSchema` class directly from `nextmv`:

    ```python
    from nextmv import VisualSchema
    ```

    This enum defines the different visualization libraries or rendering methods
    that can be used to display custom asset data in the Nextmv Console.

    Attributes
    ----------
    CHARTJS : str
        Tells Nextmv Console to render the custom asset data with the Chart.js library.
    GEOJSON : str
        Tells Nextmv Console to render the custom asset data as GeoJSON on a map.
    PLOTLY : str
        Tells Nextmv Console to render the custom asset data with the Plotly library.
    """

    CHARTJS = "chartjs"
    """Tells Nextmv Console to render the custom asset data with the Chart.js
    library."""
    GEOJSON = "geojson"
    """Tells Nextmv Console to render the custom asset data as GeoJSON on a
    map."""
    PLOTLY = "plotly"
    """Tells Nextmv Console to render the custom asset data with the Plotly
    library."""


class Visual(BaseModel):
    """
    Visual schema definition for an asset.

    You can import the `Visual` class directly from `nextmv`:

    ```python
    from nextmv import Visual
    ```

    This class defines how an asset is plotted in the Nextmv Console,
    including the schema type, label, and display type.

    Parameters
    ----------
    visual_schema : VisualSchema
        Schema of the visual asset.
    label : str
        Label for the custom tab of the visual asset in the Nextmv Console.
    visual_type : str, optional
        Defines the type of custom visual. Default is "custom-tab".

    Raises
    ------
    ValueError
        If an unsupported schema or visual_type is provided.

    Examples
    --------
    >>> from nextmv.output import Visual, VisualSchema
    >>> visual = Visual(visual_schema=VisualSchema.CHARTJS, label="Performance Chart")
    >>> visual.visual_schema
    <VisualSchema.CHARTJS: 'chartjs'>
    >>> visual.label
    'Performance Chart'
    """

    visual_schema: VisualSchema = Field(
        serialization_alias="schema",
        validation_alias=AliasChoices("schema", "visual_schema"),
    )
    """Schema of the visual asset."""
    label: str
    """Label for the custom tab of the visual asset in the Nextmv Console."""

    visual_type: Optional[str] = Field(
        serialization_alias="type",
        validation_alias=AliasChoices("type", "visual_type"),
        default="custom-tab",
    )
    """Defines the type of custom visual, currently there is only one type:
    `custom-tab`. This renders the visual in its own tab view of the run
    details."""

    def __post_init__(self):
        """
        Validate the visual schema and type.

        Raises
        ------
        ValueError
            If the visual_schema is not in VisualSchema or if visual_type is not 'custom-tab'.
        """
        if self.visual_schema not in VisualSchema:
            raise ValueError(f"unsupported schema: {self.visual_schema}, supported schemas are {VisualSchema}")

        if self.visual_type != "custom-tab":
            raise ValueError(f"unsupported visual_type: {self.visual_type}, supported types are `custom-tab`")


class Asset(BaseModel):
    """
    Represents downloadable information that is part of the `Output`.

    You can import the `Asset` class directly from `nextmv`:

    ```python
    from nextmv import Asset
    ```

    An asset contains content that can be serialized to JSON and optionally
    includes visual information for rendering in the Nextmv Console.

    Parameters
    ----------
    name : str
        Name of the asset.
    content : Any
        Content of the asset. The type must be serializable to JSON.
    content_type : str, optional
        Content type of the asset. Only "json" is currently supported. Default is "json".
    description : str, optional
        Description of the asset. Default is None.
    visual : Visual, optional
        Visual schema of the asset. Default is None.

    Raises
    ------
    ValueError
        If the content_type is not "json".

    Examples
    --------
    >>> from nextmv.output import Asset, Visual, VisualSchema
    >>> visual = Visual(visual_schema=VisualSchema.CHARTJS, label="Solution Progress")
    >>> asset = Asset(
    ...     name="optimization_progress",
    ...     content={"iterations": [1, 2, 3], "values": [10, 8, 7]},
    ...     description="Optimization progress over iterations",
    ...     visual=visual
    ... )
    >>> asset.name
    'optimization_progress'
    """

    name: str
    """Name of the asset."""
    content: Any
    """Content of the asset. The type must be serializable to JSON."""

    content_type: Optional[str] = "json"
    """Content type of the asset. Only `json` is allowed"""
    description: Optional[str] = None
    """Description of the asset."""
    visual: Optional[Visual] = None
    """Visual schema of the asset."""

    def __post_init__(self):
        """
        Validate the content type.

        Raises
        ------
        ValueError
            If the content_type is not "json".
        """
        if self.content_type != "json":
            raise ValueError(f"unsupported content_type: {self.content_type}, supported types are `json`")


@dataclass
class Output:
    """
    Output of a decision problem.

    You can import the `Output` class directly from `nextmv`:

    ```python
    from nextmv import Output
    ```

    This class is used to structure the output of a decision problem that
    can later be written to various destinations. It supports different output
    formats and allows for customization of the serialization process.

    Parameters
    ----------
    options : Optional[Union[Options, dict[str, Any]]], optional
        Options that the `Output` was created with. These options can be of type
        `Options` or a simple dictionary. Default is None.
    output_format : Optional[OutputFormat], optional
        Format of the output data. Default is `OutputFormat.JSON`.
    solution : Optional[Union[dict[str, Any], Any, dict[str, list[dict[str, Any]]]]], optional
        The solution to the decision problem. The type must match the
        `output_format`. Default is None.
    statistics : Optional[Union[Statistics, dict[str, Any]]], optional
        Statistics of the solution. Default is None.
    csv_configurations : Optional[dict[str, Any]], optional
        Configuration for writing CSV files. Default is None.
    json_configurations : Optional[dict[str, Any]], optional
        Configuration for writing JSON files. Default is None.
    assets : Optional[list[Union[Asset, dict[str, Any]]]], optional
        List of assets to be included in the output. Default is None.

    Raises
    ------
    ValueError
        If the solution is not compatible with the specified output_format.
    TypeError
        If options, statistics, or assets have unsupported types.

    Notes
    -----
    The solution's type must match the `output_format`:

    - `OutputFormat.JSON`: the data must be `dict[str, Any]` or `Any`.
    - `OutputFormat.CSV_ARCHIVE`: the data must be `dict[str, list[dict[str, Any]]]`.
      The keys represent the file names where the data should be written. The values
      are lists of dictionaries, where each dictionary represents a row in the CSV file.

    Examples
    --------
    >>> from nextmv.output import Output, OutputFormat, Statistics, RunStatistics
    >>> run_stats = RunStatistics(duration=30.0, iterations=100)
    >>> stats = Statistics(run=run_stats)
    >>> solution = {"routes": [{"vehicle": 1, "stops": [1, 2, 3]}, {"vehicle": 2, "stops": [4, 5]}]}
    >>> output = Output(
    ...     output_format=OutputFormat.JSON,
    ...     solution=solution,
    ...     statistics=stats,
    ...     json_configurations={"indent": 4}
    ... )
    >>> output_dict = output.to_dict()
    >>> "solution" in output_dict and "statistics" in output_dict
    True
    """

    options: Optional[Union[Options, dict[str, Any]]] = None
    """
    Options that the `Output` was created with. These options can be of type
    `Options` or a simple dictionary. If the options are of type `Options`,
    they will be serialized to a dictionary using the `to_dict` method. If
    they are a dictionary, they will be used as is. If the options are not
    provided, an empty dictionary will be used. If the options are of type
    `dict`, then the dictionary should have the following structure:

    ```python
    {
        "duration": "30",
        "threads": 4,
    }
    ```
    """
    output_format: Optional[OutputFormat] = OutputFormat.JSON
    """Format of the output data. Default is `OutputFormat.JSON`."""
    solution: Optional[
        Union[
            Union[dict[str, Any], Any],  # JSON
            dict[str, list[dict[str, Any]]],  # CSV_ARCHIVE
        ]
    ] = None
    """The solution to the decision problem."""
    statistics: Optional[Union[Statistics, dict[str, Any]]] = None
    """
    Statistics of the solution. These statistics can be of type `Statistics` or a
    simple dictionary. If the statistics are of type `Statistics`, they will be
    serialized to a dictionary using the `to_dict` method. If they are a
    dictionary, they will be used as is. If the statistics are not provided, an
    empty dictionary will be used.
    """
    csv_configurations: Optional[dict[str, Any]] = None
    """
    Optional configuration for writing CSV files, to be used when the
    `output_format` is `OutputFormat.CSV_ARCHIVE`. These configurations are
    passed as kwargs to the `DictWriter` class from the `csv` module.
    """
    json_configurations: Optional[dict[str, Any]] = None
    """
    Optional configuration for writing JSON files, to be used when the
    `output_format` is `OutputFormat.JSON`. These configurations are passed as
    kwargs to the `json.dumps` function.
    """
    assets: Optional[list[Union[Asset, dict[str, Any]]]] = None
    """
    Optional list of assets to be included in the output. These assets can be of
    type `Asset` or a simple dictionary. If the assets are of type `Asset`, they
    will be serialized to a dictionary using the `to_dict` method. If they are a
    dictionary, they will be used as is. If the assets are not provided, an
    empty list will be used.
    """

    def __post_init__(self):
        """
        Initialize and validate the Output instance.

        This method performs two main tasks:
        1. Creates a deep copy of the options to preserve the original values
        2. Validates that the solution matches the specified output_format

        Raises
        ------
        ValueError
            If the solution is not compatible with the specified output_format.
        """
        # Capture a snapshot of the options that were used to create the class
        # so even if they are changed later, we have a record of the original.
        init_options = self.options
        new_options = copy.deepcopy(init_options)
        self.options = new_options

        if self.solution is None:
            return

        if self.output_format == OutputFormat.JSON:
            try:
                _ = json.dumps(self.solution, default=_custom_serial)
            except (TypeError, OverflowError) as e:
                raise ValueError(
                    f"Output has output_format OutputFormat.JSON and "
                    f"Output.solution is of type {type(self.solution)}, which is not JSON serializable"
                ) from e

        elif self.output_format == OutputFormat.CSV_ARCHIVE and not isinstance(self.solution, dict):
            raise ValueError(
                f"unsupported Output.solution type: {type(self.solution)} with "
                "output_format OutputFormat.CSV_ARCHIVE, supported type is `dict`"
            )

    def to_dict(self) -> dict[str, Any]:  # noqa: C901
        """
        Convert the `Output` object to a dictionary.

        Returns
        -------
        dict[str, Any]
            The dictionary representation of the `Output` object.
        """

        # Options need to end up as a dict, so we achieve that based on the
        # type of options that were used to create the class.
        if self.options is None:
            options = {}
        elif isinstance(self.options, Options):
            options = self.options.to_dict()
        elif isinstance(self.options, dict):
            options = self.options
        else:
            raise TypeError(f"unsupported options type: {type(self.options)}, supported types are `Options` or `dict`")

        # Statistics need to end up as a dict, so we achieve that based on the
        # type of statistics that were used to create the class.
        if self.statistics is None:
            statistics = {}
        elif isinstance(self.statistics, Statistics):
            statistics = self.statistics.to_dict()
        elif isinstance(self.statistics, dict):
            statistics = self.statistics
        else:
            raise TypeError(
                f"unsupported statistics type: {type(self.statistics)}, supported types are `Statistics` or `dict`"
            )

        # Assets need to end up as a list of dicts, so we achieve that based on
        # the type of each asset in the list.
        assets = []
        if isinstance(self.assets, list):
            for ix, asset in enumerate(self.assets):
                if isinstance(asset, Asset):
                    assets.append(asset.to_dict())
                elif isinstance(asset, dict):
                    assets.append(asset)
                else:
                    raise TypeError(
                        f"unsupported asset {ix}, type: {type(asset)}; supported types are `Asset` or `dict`"
                    )
        elif self.assets is not None:
            raise TypeError(f"unsupported assets type: {type(self.assets)}, supported types are `list`")

        output_dict = {
            "options": options,
            "solution": self.solution if self.solution is not None else {},
            "statistics": statistics,
            "assets": assets,
        }

        # Add the auxiliary configurations to the output dictionary if they are
        # defined and not empty.
        if (
            self.output_format == OutputFormat.CSV_ARCHIVE
            and self.csv_configurations is not None
            and self.csv_configurations != {}
        ):
            output_dict["csv_configurations"] = self.csv_configurations
        elif (
            self.output_format == OutputFormat.JSON
            and self.json_configurations is not None
            and self.json_configurations != {}
        ):
            output_dict["json_configurations"] = self.json_configurations

        return output_dict


class OutputWriter:
    """
    Base class for writing outputs.

    You can import the `OutputWriter` class directly from `nextmv`:

    ```python
    from nextmv import OutputWriter
    ```

    This is an abstract base class that defines the interface for writing outputs
    to different destinations. Subclasses should implement the `write` method.

    Examples
    --------
    >>> class CustomOutputWriter(OutputWriter):
    ...     def write(self, output, path=None, **kwargs):
    ...         # Custom implementation for writing output
    ...         print(f"Writing output to {path}")
    """

    def write(self, output: Union[Output, dict[str, Any], BaseModel], *args, **kwargs) -> None:
        """
        Write the output data.

        This is an abstract method that should be implemented by subclasses.

        Parameters
        ----------
        output : Union[Output, dict[str, Any], BaseModel]
            The output data to write.
        *args
            Variable length argument list.
        **kwargs
            Arbitrary keyword arguments.

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError


class LocalOutputWriter(OutputWriter):
    """
    Class for writing outputs to local files or stdout.

    You can import the `LocalOutputWriter` class directly from `nextmv`:

    ```python
    from nextmv import LocalOutputWriter
    ```

    This class implements the OutputWriter interface to write output data to
    local files or stdout. The destination and format depend on the output
    format and the provided path.

    Examples
    --------
    >>> from nextmv.output import LocalOutputWriter, Output, Statistics
    >>> writer = LocalOutputWriter()
    >>> output = Output(solution={"result": 42}, statistics=Statistics())
    >>> # Write to stdout
    >>> writer.write(output, path=None)
    >>> # Write to a file
    >>> writer.write(output, path="results.json")
    """

    def _write_json(
        output: Union[Output, dict[str, Any], BaseModel],
        output_dict: dict[str, Any],
        path: Optional[str] = None,
    ) -> None:
        """
        Write output in JSON format.

        Parameters
        ----------
        output : Union[Output, dict[str, Any], BaseModel]
            The output object containing configuration.
        output_dict : dict[str, Any]
            Dictionary representation of the output to write.
        path : str, optional
            Path to write the output. If None or empty, writes to stdout.
        """
        json_configurations = {}
        if hasattr(output, "json_configurations") and output.json_configurations is not None:
            json_configurations = output.json_configurations

        indent, custom_serial = 2, _custom_serial
        if "indent" in json_configurations:
            indent = json_configurations["indent"]
            del json_configurations["indent"]
        if "default" in json_configurations:
            custom_serial = json_configurations["default"]
            del json_configurations["default"]

        serialized = json.dumps(
            output_dict,
            indent=indent,
            default=custom_serial,
            **json_configurations,
        )

        if path is None or path == "":
            print(serialized, file=sys.stdout)
            return

        with open(path, "w", encoding="utf-8") as file:
            file.write(serialized + "\n")

    def _write_archive(
        output: Union[Output, dict[str, Any], BaseModel],
        output_dict: dict[str, Any],
        path: Optional[str] = None,
    ) -> None:
        """
        Write output in CSV archive format.

        Parameters
        ----------
        output : Union[Output, dict[str, Any], BaseModel]
            The output object containing configuration and solution data.
        output_dict : dict[str, Any]
            Dictionary representation of the output to write.
        path : str, optional
            Directory path to write the CSV files. If None or empty,
            writes to a directory named "output" in the current working directory.

        Raises
        ------
        ValueError
            If the path is an existing file instead of a directory.
        """
        dir_path = "output"
        if path is not None and path != "":
            if os.path.isfile(path):
                raise ValueError(f"The path refers to an existing file: {path}")

            dir_path = path

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        serialized = json.dumps(
            {
                "options": output_dict.get("options", {}),
                "statistics": output_dict.get("statistics", {}),
                "assets": output_dict.get("assets", []),
            },
            indent=2,
        )
        print(serialized, file=sys.stdout)

        if output.solution is None:
            return

        csv_configurations = output.csv_configurations
        if csv_configurations is None:
            csv_configurations = {}

        for file_name, data in output.solution.items():
            file_path = os.path.join(dir_path, f"{file_name}.csv")
            with open(file_path, "w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=data[0].keys(),
                    **csv_configurations,
                )
                writer.writeheader()
                writer.writerows(data)

    # Callback functions for writing the output data.
    FILE_WRITERS = {
        OutputFormat.JSON: _write_json,
        OutputFormat.CSV_ARCHIVE: _write_archive,
    }
    """Dictionary mapping output formats to writer functions."""

    def write(
        self,
        output: Union[Output, dict[str, Any], BaseModel],
        path: Optional[str] = None,
        skip_stdout_reset: bool = False,
    ) -> None:
        """
        Write the output to the local filesystem or stdout.

        This method writes the provided output to the specified path or to stdout,
        depending on the output format and the path parameter.

        Parameters
        ----------
        output : Union[Output, dict[str, Any], BaseModel]
            Output data to write. Can be an Output object, a dictionary, or a BaseModel.
        path : str, optional
            Path to write the output data to. The interpretation depends on the output format:
            - For OutputFormat.JSON: File path for the JSON output. If None or empty, writes to stdout.
            - For OutputFormat.CSV_ARCHIVE: Directory path for CSV files. If None or empty,
              writes to a directory named "output" in the current working directory.
        skip_stdout_reset : bool, optional
            Skip resetting stdout before writing the output data. Default is False.

        Raises
        ------
        ValueError
            If the Output.output_format is not supported.
        TypeError
            If the output is of an unsupported type.

        Notes
        -----
        This function detects if stdout was redirected and resets it to avoid
        unexpected behavior. If you want to skip this behavior, set the
        skip_stdout_reset parameter to True.

        If the output is a dict or a BaseModel, it will be written as JSON. If
        the output is an Output object, it will be written according to its
        output_format.

        Examples
        --------
        >>> from nextmv.output import LocalOutputWriter, Output
        >>> writer = LocalOutputWriter()
        >>> # Write JSON to a file
        >>> writer.write(Output(solution={"result": 42}), path="result.json")
        >>> # Write JSON to stdout
        >>> writer.write({"simple": "data"})
        """

        # If the user forgot to reset stdout after redirecting it, we need to
        # do it here to avoid unexpected behavior.
        if sys.stdout is not sys.__stdout__ and not skip_stdout_reset:
            reset_stdout()

        if isinstance(output, Output):
            output_format = output.output_format
        elif isinstance(output, dict):
            output_format = OutputFormat.JSON
        elif isinstance(output, BaseModel):
            output_format = OutputFormat.JSON
        else:
            raise TypeError(
                f"unsupported output type: {type(output)}, supported types are `Output`, `dict`, `BaseModel`"
            )

        output_dict = {}
        if isinstance(output, Output):
            output_dict = output.to_dict()
        elif isinstance(output, BaseModel):
            output_dict = output.to_dict()
        elif isinstance(output, dict):
            output_dict = output
        else:
            raise TypeError(
                f"unsupported output type: {type(output)}, supported types are `Output`, `dict`, `BaseModel`"
            )

        self.FILE_WRITERS[output_format](
            output=output,
            output_dict=output_dict,
            path=path,
        )


def write_local(
    output: Union[Output, dict[str, Any]],
    path: Optional[str] = None,
    skip_stdout_reset: bool = False,
) -> None:
    """
    !!! warning
        `write_local` is deprecated, use `write` instead.

    Write the output to the local filesystem or stdout.

    This is a convenience function for instantiating a `LocalOutputWriter` and
    calling its `write` method.

    Parameters
    ----------
    output : Union[Output, dict[str, Any]]
        Output data to write. Can be an Output object or a dictionary.
    path : str, optional
        Path to write the output data to. The interpretation depends on the
        output format:

        - For `OutputFormat.JSON`: File path for the JSON output. If None or
          empty, writes to stdout.
        - For `OutputFormat.CSV_ARCHIVE`: Directory path for CSV files. If None
          or empty, writes to a directory named "output" in the current working
          directory.
    skip_stdout_reset : bool, optional
        Skip resetting stdout before writing the output data. Default is False.

    Raises
    ------
    ValueError
        If the Output.output_format is not supported.
    TypeError
        If the output is of an unsupported type.

    Notes
    -----
    This function detects if stdout was redirected and resets it to avoid
    unexpected behavior. If you want to skip this behavior, set the
    skip_stdout_reset parameter to True.

    Examples
    --------
    >>> from nextmv.output import write_local, Output
    >>> # Write JSON to a file
    >>> write_local(Output(solution={"result": 42}), path="result.json")
    >>> # Write JSON to stdout
    >>> write_local({"simple": "data"})
    """

    deprecated(
        name="write_local",
        reason="`write_local` is deprecated, use `write` instead.",
    )

    writer = LocalOutputWriter()
    writer.write(output, path, skip_stdout_reset)


_LOCAL_OUTPUT_WRITER = LocalOutputWriter()
"""Default LocalOutputWriter instance used by the write function."""


def write(
    output: Union[Output, dict[str, Any], BaseModel],
    path: Optional[str] = None,
    skip_stdout_reset: bool = False,
    writer: Optional[OutputWriter] = _LOCAL_OUTPUT_WRITER,
) -> None:
    """
    Write the output to the specified destination.

    You can import the `write` function directly from `nextmv`:

    ```python
    from nextmv import write
    ```

    This is a convenience function for writing output data using a provided writer.
    By default, it uses the `LocalOutputWriter` to write to files or stdout.

    Parameters
    ----------
    output : Union[Output, dict[str, Any], BaseModel]
        Output data to write. Can be an Output object, a dictionary, or a BaseModel.
    path : str, optional
        Path to write the output data to. The interpretation depends on the
        output format:

        - For `OutputFormat.JSON`: File path for the JSON output. If None or
          empty, writes to stdout.
        - For `OutputFormat.CSV_ARCHIVE`: Directory path for CSV files. If None
          or empty, writes to a directory named "output" in the current working
          directory.
    skip_stdout_reset : bool, optional
        Skip resetting stdout before writing the output data. Default is False.
    writer : OutputWriter, optional
        The writer to use for writing the output. Default is a
        `LocalOutputWriter` instance.

    Raises
    ------
    ValueError
        If the Output.output_format is not supported.
    TypeError
        If the output is of an unsupported type.

    Examples
    --------
    >>> from nextmv.output import write, Output, OutputFormat
    >>> # Write JSON to a file
    >>> write(Output(solution={"result": 42}), path="result.json")
    >>> # Write CSV archive
    >>> data = {"vehicles": [{"id": 1, "capacity": 100}, {"id": 2, "capacity": 150}]}
    >>> write(Output(output_format=OutputFormat.CSV_ARCHIVE, solution=data), path="output_dir")
    """

    writer.write(output, path, skip_stdout_reset)


def _custom_serial(obj: Any) -> str:
    """
    JSON serializer for objects not serializable by default json serializer.

    This function provides custom serialization for datetime objects, converting
    them to ISO format strings.

    Parameters
    ----------
    obj : Any
        The object to serialize.

    Returns
    -------
    str
        The serialized representation of the object.

    Raises
    ------
    TypeError
        If the object type is not supported for serialization.
    """

    if isinstance(obj, (datetime.datetime | datetime.date)):
        return obj.isoformat()

    raise TypeError(f"Type {type(obj)} not serializable")
