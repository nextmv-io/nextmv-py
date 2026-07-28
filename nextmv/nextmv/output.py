"""
Module for handling output destinations and data.

This module provides classes and functions for handling the output of decision
problems, including formatting, serialization, and writing to various
destinations.

Classes
-------
SolutionFile
    Represents a solution to be written as a file.
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

Attributes
----------
ASSETS_KEY : str
    Assets key constant used for identifying assets in the run output.
METRICS_KEY : str
    Metrics key constant used for identifying metrics in the run output.
SOLUTIONS_KEY : str
    Solutions key constant used for identifying solutions in the run output.
OUTPUTS_KEY : str
    Outputs key constant used for identifying outputs in the run output.
"""

import copy
import csv
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from pydantic import AliasChoices, Field

from nextmv._serialization import serialize_json
from nextmv.base_model import BaseModel
from nextmv.content_format import ContentFormat
from nextmv.deprecated import deprecated
from nextmv.logger import reset_stdout
from nextmv.manifest import Manifest, resolve_manifest
from nextmv.options import Options

ASSETS_KEY = "assets"
"""
Assets key constant used for identifying assets in the run output.
"""
STATISTICS_KEY = "statistics"
"""
Deprecated: Use METRICS_KEY instead. Statistics key constant used for identifying statistics in the run output.
"""
METRICS_KEY = "metrics"
"""
Metrics key constant used for identifying metrics in the run output.
"""
SOLUTIONS_KEY = "solutions"
"""
Solutions key constant used for identifying solutions in the run output.
"""
OUTPUTS_KEY = "outputs"
"""
Outputs key constant used for identifying outputs in the run output.
"""


class RunStatistics(BaseModel):
    """
    !!! warning
        `RunStatistics` is deprecated, use `metrics` on the `Output` directly.

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

    duration: float | None = None
    """Duration of the run in seconds."""
    iterations: int | None = None
    """Number of iterations."""
    custom: Any | dict[str, Any] | None = None
    """Custom statistics created by the user. Can normally expect a `dict[str,
    Any]`."""


class ResultStatistics(BaseModel):
    """
    !!! warning
        `ResultStatistics` is deprecated, use `metrics` on the `Output` directly.

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

    duration: float | None = None
    """Duration of the run in seconds."""
    value: float | None = None
    """Value of the result."""
    custom: Any | dict[str, Any] | None = None
    """Custom statistics created by the user. Can normally expect a `dict[str,
    Any]`."""


class DataPoint(BaseModel):
    """
    !!! warning
        `DataPoint` is deprecated, use `metrics` on the `Output` directly.

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
    !!! warning
        `Series` is deprecated, use `metrics` on the `Output` directly.

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

    name: str | None = None
    """Name of the series."""
    data_points: list[DataPoint] | None = None
    """Data of the series."""


class SeriesData(BaseModel):
    """
    !!! warning
        `SeriesData` is deprecated, use `metrics` on the `Output` directly.

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

    value: Series | None = None
    """A series for the value of the solution."""
    custom: list[Series] | None = None
    """A list of series for custom statistics."""


class Statistics(BaseModel):
    """
    !!! warning
        `Statistics` is deprecated, use `Metrics` instead.

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

    run: RunStatistics | None = None
    """Statistics about the run."""
    result: ResultStatistics | None = None
    """Statistics about the last result."""
    series_data: SeriesData | None = None
    """Data of the series."""
    statistics_schema: str | None = Field(
        serialization_alias="schema",
        validation_alias=AliasChoices("schema", "statistics_schema"),
        default="v1",
    )
    """Schema (version). This class only supports `v1`."""


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

    visual_type: str | None = Field(
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

    id: str | None = None
    """
    The ID of the asset. This ID will be populated by the Nextmv platform and can be used
    to download the asset later.
    """
    content: Any | None = None
    """
    Content of the asset. The type must be serializable to JSON. Can be empty when
    fetching the asset metadata only (e.g.: via the asset list endpoint).
    """
    content_type: str | None = "json"
    """Content type of the asset. Only `json` is allowed"""
    description: str | None = None
    """Description of the asset."""
    visual: Visual | None = None
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


class OutputFormat(str, Enum):
    """
    !!! warning
        `OutputFormat` is deprecated, use `ContentFormat` instead.

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
        !!! warning
            `OutputFormat.JSON` is deprecated, use `ContentFormat.JSON` instead.

        JSON format, utf-8 encoded.
    CSV_ARCHIVE : str
        !!! warning
            `OutputFormat.CSV_ARCHIVE` is deprecated, use `ContentFormat.MULTI_FILE` instead.

        CSV archive format: multiple CSV files.
    MULTI_FILE : str
        !!! warning
            `OutputFormat.MULTI_FILE` is deprecated, use `ContentFormat.MULTI_FILE` instead.

        Multi-file format: multiple files in a directory.
    TEXT : str
        !!! warning
            `OutputFormat.TEXT` is deprecated, use `ContentFormat.MULTI_FILE` instead.

        Text format, utf-8 encoded.
    """

    JSON = "json"
    """
    !!! warning
        `OutputFormat.JSON` is deprecated, use `ContentFormat.JSON` instead.

    JSON format, utf-8 encoded.
    """
    CSV_ARCHIVE = "csv-archive"
    """
    !!! warning
        `OutputFormat.CSV_ARCHIVE` is deprecated, use `ContentFormat.MULTI_FILE` instead.

    CSV archive format: multiple CSV files.
    """
    MULTI_FILE = "multi-file"
    """
    !!! warning
        `OutputFormat.MULTI_FILE` is deprecated, use `ContentFormat.MULTI_FILE` instead.

    Multi-file format: multiple files in a directory.
    """
    TEXT = "text"
    """
    !!! warning
        `OutputFormat.TEXT` is deprecated, use `ContentFormat.MULTI_FILE` instead.

    Text format, utf-8 encoded.
    """


@dataclass
class SolutionFile:
    """
    Represents a solution to be written as a file.

    You can import the `SolutionFile` class directly from `nextmv`:

    ```python
    from nextmv import SolutionFile
    ```

    This class is used to define a solution that will be written to a file in
    the filesystem. It includes the name of the file, the data to be written,
    and the writer function that will handle the serialization of the data.
    This `SolutionFile` class is typically used in the `Output`, when the
    `Output.output_format` is set to `ContentFormat.MULTI_FILE`. Given that it
    is difficult to handle every edge case of how a solution is serialized, and
    written to a file, this class exists so that the user can implement the
    `writer` callable of their choice and provide it with any `writer_args`
    and `writer_kwargs` they might need.

    Parameters
    ----------
    name : str
        Name of the output file. The file extension should be included in the
        name.
    data : Any
        The actual data that will be written to the file. This can be any type
        that can be given to the `writer` function. For example, if the `writer`
        is a `csv.DictWriter`, then the data should be a list of dictionaries,
        where each dictionary represents a row in the CSV file.
    writer : Callable
        Callable that writes the solution data to the file. This should be a
        function implemented by the user. There are convenience functions that you
        can use as a writer as well. The `writer` must receive, at the very
        minimum, the following arguments:

        - `file_path`: a `str` argument which is the location where this solution
        will be written to. This includes the dir and the name of the file. As
        such, the `name` parameter of this class is going to be passed to this
        function joined with the directory where the file will be written.
        - `data`: the actual data that will be written to the file. This can be any
        type that can be given to the `writer` function. The `data` parameter of
        this class is going to be passed to the `writer` function.

        The `writer` can also receive additional arguments, and keyword arguments.
        The `writer_args` and `writer_kwargs` parameters of this class can be used
        to provide those additional arguments.
    writer_args : Optional[list[Any]], optional
        Positional arguments to pass to the writer function.
    writer_kwargs : Optional[dict[str, Any]], optional
        Keyword arguments to pass to the writer function.

    Examples
    --------
    >>> from nextmv import SolutionFile
    >>> solution_file = SolutionFile(
    ...     name="solution.csv",
    ...     data=[{"id": 1, "value": 100}, {"id": 2, "value": 200}],
    ...     writer=csv.DictWriter,
    ...     writer_kwargs={"fieldnames": ["id", "value"]},
    ...     writer_args=[open("solution.csv", "w", newline="")],
    ... )
    """

    name: str
    """
    Name of the solution (output) file. The file extension should be included in the
    name.
    """
    data: Any
    """
    The actual data that will be written to the file. This can be any type that
    can be given to the `writer` function. For example, if the `writer` is a
    `csv.DictWriter`, then the data should be a list of dictionaries, where
    each dictionary represents a row in the CSV file.
    """
    writer: Callable[[str, Any], None]
    """
    Callable that writes the solution data to the file. This should be a
    function implemented by the user. There are convenience functions that you
    can use as a writer as well. The `writer` must receive, at the very
    minimum, the following arguments:

    - `file_path`: a `str` argument which is the location where this solution
      will be written to. This includes the dir and the name of the file. As
      such, the `name` parameter of this class is going to be passed to this
      function joined with the directory where the file will be written.
    - `data`: the actual data that will be written to the file. This can be any
      type that can be given to the `writer` function. The `data` parameter of
      this class is going to be passed to the `writer` function.

    The `writer` can also receive additional arguments, and keyword arguments.
    The `writer_args` and `writer_kwargs` parameters of this class can be used
    to provide those additional arguments.
    """
    writer_args: list[Any] | None = None
    """
    Optional positional arguments to pass to the writer function. This can be
    used to customize the behavior of the writer.
    """
    writer_kwargs: dict[str, Any] | None = None
    """
    Optional keyword arguments to pass to the writer function. This can be used
    to customize the behavior of the writer.
    """


def json_solution_file(
    name: str,
    data: dict[str, Any],
    json_configurations: dict[str, Any] | None = None,
) -> SolutionFile:
    """
    This is a convenience function to build a `SolutionFile`. It writes the
    given `data` to a `.json` file with the provided `name`.

    You can import this function directly from `nextmv`:

    ```python
    from nextmv import json_solution_file
    ```

    Parameters
    ----------
    name : str
        Name of the output file. You don't need to include the `.json`
        extension.
    data : dict[str, Any]
        The actual data that will be written to the file. This should be a
        dictionary that can be serialized to JSON.
    json_configurations : Optional[dict[str, Any]], optional
        Optional configuration options for the JSON serialization process. You
        can use these options to configure parameters such as indentation.

    Returns
    -------
    SolutionFile
        The constructed `SolutionFile` object.

    Examples
    --------
    >>> from nextmv import json_solution_file
    >>> solution_file = json_solution_file(
    ...     name="solution",
    ...     data={"id": 1, "value": 100}
    ... )
    >>> solution_file.name
    'solution.json'
    >>> solution_file.data
    {'id': 1, 'value': 100}
    """

    if not name.endswith(".json"):
        name += ".json"

    json_configurations = json_configurations or {}

    def writer(file_path: str, write_data: dict[str, Any]) -> None:
        serialized = serialize_json(write_data, json_configurations=json_configurations)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(serialized + "\n")

    return SolutionFile(
        name=name,
        data=data,
        writer=writer,
    )


def csv_solution_file(
    name: str,
    data: list[dict[str, Any]],
    csv_configurations: dict[str, Any] | None = None,
) -> SolutionFile:
    """
    This is a convenience function to build a `SolutionFile`. It writes the
    given `data` to a `.csv` file with the provided `name`.

    You can import this function directly from `nextmv`:

    ```python
    from nextmv import csv_solution_file
    ```

    Parameters
    ----------
    name : str
        Name of the output file. You don't need to include the `.csv`
        extension.
    data : list[dict[str, Any]]
        The actual data that will be written to the file. This should be a list
        of dictionaries, where each dictionary represents a row in the CSV file.
        The keys of the dictionaries will be used as the column headers in the
        CSV file.
    csv_configurations : Optional[dict[str, Any]], optional
        Optional configuration options for the CSV serialization process.

    Returns
    -------
    SolutionFile
        The constructed `SolutionFile` object.

    Examples
    --------
    >>> from nextmv import csv_solution_file
    >>> solution_file = csv_solution_file(
    ...     name="solution",
    ...     data=[{"id": 1, "value": 100}, {"id": 2, "value": 200}]
    ... )
    >>> solution_file.name
    'solution.csv'
    >>> solution_file.data
    [{'id': 1, 'value': 100}, {'id': 2, 'value': 200}]
    """

    if not name.endswith(".csv"):
        name += ".csv"

    csv_configurations = csv_configurations or {}

    def writer(file_path: str, write_data: list[dict[str, Any]]) -> None:
        with open(file_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=write_data[0].keys(),
                **csv_configurations,
            )
            writer.writeheader()
            writer.writerows(write_data)

    return SolutionFile(
        name=name,
        data=data,
        writer=writer,
    )


def text_solution_file(name: str, data: str) -> SolutionFile:
    """
    This is a convenience function to build a `SolutionFile`. It writes the
    given `data` to a utf-8 encoded file with the provided `name`.

    You can import this function directly from `nextmv`:

    ```python
    from nextmv import text_solution_file
    ```

    You must provide the extension as part of the `name` parameter.

    Parameters
    ----------
    name : str
        Name of the output file. The file extension must be provided in the
        name.
    data : str
        The actual data that will be written to the file.

    Returns
    -------
    SolutionFile
        The constructed `SolutionFile` object.

    Examples
    --------
    >>> from nextmv import text_solution_file
    >>> solution_file = text_solution_file(
    ...     name="solution.txt",
    ...     data="This is a sample text solution."
    ... )
    >>> solution_file.name
    'solution.txt'
    >>> solution_file.data
    'This is a sample text solution.'
    """

    def writer(file_path: str, write_data: str) -> None:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(write_data + "\n")

    return SolutionFile(
        name=name,
        data=data,
        writer=writer,
    )


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

    The `solution`'s type must match the `output_format`:

    - `ContentFormat.JSON`: the data must be `dict[str, Any]` or `Any`.
    - `ContentFormat.MULTI_FILE`: the data must be `dict[str, Any]`. When
      working with multi-file, the solution is written to one or more files
      in a specific directory.

    If you are working with `ContentFormat.MULTI_FILE`, you should use
    `solution_files` instead of `solution`. When `solution_files` is not
    `None`, then the `output_format` _must_ be `ContentFormat.MULTI_FILE`.
    `solution_files` is a list of `SolutionFile` objects, which allows you to
    define the name of the file, the data to be written, and the writer
    function that will handle the serialization of the data. This is useful when
    you need to write the solution to multiple files with different formats or
    configurations.

    There are convenience functions to create `SolutionFile` objects for
    common use cases, such as:

    - `json_solution_file`: for writing JSON data to a file.
    - `csv_solution_file`: for writing CSV data to a file.
    - `text_solution_file`: for writing utf-8 encoded data to a file.

    For other data types, such as Excel, you can create your own `SolutionFile`
    objects by providing a `name`, `data`, and a `writer` function that will
    handle the serialization of the data.

    Parameters
    ----------
    options : Optional[Union[Options, dict[str, Any]]], optional
        Options that the `Output` was created with. These options can be of type
        `Options` or a simple dictionary. Default is None.
    output_format : Optional[ContentFormat], optional
        Format of the output data. Default is `ContentFormat.JSON`.
    solution : Optional[Union[dict[str, Any], Any]], optional
        The solution to the decision problem. The type must match the
        `output_format`. Default is None.
    statistics : Optional[Union[Statistics, dict[str, Any]]], optional
        Deprecated: Use Metrics instead. Statistics of the solution. Default is None.
    metrics : Optional[dict[str, Any]], optional
        Metrics of the solution. Default is None.
    csv_configurations : Optional[dict[str, Any]], optional
        Configuration for writing CSV files. Default is None.
    json_configurations : Optional[dict[str, Any]], optional
        Configuration for writing JSON files. Default is None.
    assets : Optional[list[Union[Asset, dict[str, Any]]]], optional
        List of assets to be included in the output. Default is None.
    solution_files: Optional[list[SolutionFile]], default = None
        Optional list of solution files to be included in the output. These
        files are of type `SolutionFile`, which allows for custom serialization
        and writing of the solution data to files. When this field is
        specified, then the `output_format` must be set to
        `ContentFormat.MULTI_FILE`, otherwise an exception will be raised. The
        `SolutionFile` class allows you to define the name of the file, the
        data to be written, and the writer function that will handle the
        serialization of the data. This is useful when you need to write the
        solution to multiple files with different formats or configurations.

        There are convenience functions to create `SolutionFile` objects for
        common use cases, such as:

        - `json_solution_file`: for writing JSON data to a file.
        - `csv_solution_file`: for writing CSV data to a file.
        - `text_solution_file`: for writing utf-8 encoded data to a file.

        For other data types, such as Excel, you can create your own
        `SolutionFile` objects by providing a `name`, `data`, and a `writer`
        function that will handle the serialization of the data.

    Raises
    ------
    ValueError
        If the solution is not compatible with the specified output_format.
    TypeError
        If options, statistics, or assets have unsupported types.

    Examples
    --------
    >>> from nextmv.output import Output, Statistics, RunStatistics
    >>> metrics = {"duration": 30.0, "iterations": 100}
    >>> solution = {"routes": [{"vehicle": 1, "stops": [1, 2, 3]}, {"vehicle": 2, "stops": [4, 5]}]}
    >>> output = Output(
    ...     output_format=ContentFormat.JSON,
    ...     solution=solution,
    ...     metrics=metrics,
    ...     json_configurations={"indent": 4}
    ... )
    >>> output_dict = output.to_dict()
    >>> "solution" in output_dict and "metrics" in output_dict
    True
    """

    options: Options | dict[str, Any] | None = None
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
    output_format: ContentFormat | None = None
    """
    Format of the output data. When set to `ContentFormat.MULTI_FILE`, the
    `solution_files` field must be specified and cannot be `None`.
    """
    solution: dict[str, Any] | Any | dict[str, list[dict[str, Any]]] | None = None
    """
    The solution to the decision problem. Use this filed when working with
    `output_format` of types:

    - `ContentFormat.JSON`: the data must be `dict[str, Any]` or `Any`.

    Note that when the `output_format` is set to `ContentFormat.MULTI_FILE`,
    this `solution` field is ignored, as you should use the `solution_files`
    field instead.
    """
    statistics: Statistics | dict[str, Any] | None = None
    """
    !!! warning
        `statistics` is deprecated, use `metrics` instead.

    Statistics of the solution. These statistics can be of type `Statistics` or a
    simple dictionary. If the statistics are of type `Statistics`, they will be
    serialized to a dictionary using the `to_dict` method. If they are a
    dictionary, they will be used as is.
    """
    metrics: dict[str, Any] | None = None
    """
    Metrics of the solution. These metrics should be provided as a simple or
    nested dictionary.
    """
    csv_configurations: dict[str, Any] | None = None
    """
    Optional configuration for writing CSV files. These configurations are
    passed as kwargs to the `DictWriter` class from the `csv` module.
    """
    json_configurations: dict[str, Any] | None = None
    """
    Optional configuration for writing JSON files, to be used when the
    `output_format` is `ContentFormat.JSON`. These configurations are passed as
    kwargs to the `json.dumps` function.
    """
    assets: list[Asset | dict[str, Any]] | None = None
    """
    Optional list of assets to be included in the output. These assets can be of
    type `Asset` or a simple dictionary. If the assets are of type `Asset`, they
    will be serialized to a dictionary using the `to_dict` method. If they are a
    dictionary, they will be used as is. If the assets are not provided, an
    empty list will be used.
    """
    solution_files: list[SolutionFile] | None = None
    """
    Optional list of solution files to be included in the output. These files
    are of type `SolutionFile`, which allows for custom serialization and
    writing of the solution data to files. When this field is specified, then
    the `output_format` must be set to `ContentFormat.MULTI_FILE`, otherwise an
    exception will be raised. The `SolutionFile` class allows you to define the
    name of the file, the data to be written, and the writer function that will
    handle the serialization of the data. This is useful when you need to write
    the solution to multiple files with different formats or configurations.

    There are convenience functions to create `SolutionFile` objects for
    common use cases, such as:

    - `json_solution_file`: for writing JSON data to a file.
    - `csv_solution_file`: for writing CSV data to a file.
    - `text_solution_file`: for writing utf-8 encoded data to a file.

    For other data types, such as Excel, you can create your own `SolutionFile`
    objects by providing a `name`, `data`, and a `writer` function that will
    handle the serialization of the data.
    """

    def __post_init__(self):  # noqa: C901
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

        if self.output_format is not None and type(self.output_format) is OutputFormat:
            deprecated(name="OutputFormat", reason="`OutputFormat` is deprecated, use `ContentFormat` instead")
            if self.output_format in {OutputFormat.TEXT, OutputFormat.CSV_ARCHIVE}:
                deprecated(
                    name="OutputFormat.TEXT/OutputFormat.CSV_ARCHIVE",
                    reason="`text`/`csv-archive` format is no longer supported, use `ContentFormat.MULTI_FILE` instead",
                )
            elif self.output_format in {OutputFormat.JSON, OutputFormat.MULTI_FILE}:
                self.output_format = ContentFormat(self.output_format.value)
            else:
                raise ValueError(f"unsupported output_format: {self.output_format}")

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
            statistics = None
        elif isinstance(self.statistics, Statistics):
            statistics = self.statistics.to_dict()
        elif isinstance(self.statistics, dict):
            statistics = self.statistics
        else:
            raise TypeError(
                f"unsupported statistics type: {type(self.statistics)}, supported types are `Statistics` or `dict`"
            )

        if self.metrics is None:
            metrics = {}
        elif isinstance(self.metrics, dict):
            metrics = self.metrics
        else:
            raise TypeError(f"unsupported metrics type: {type(self.metrics)}, supported type is `dict`")

        # if both metrics and statistics are None, set statistics to an
        # empty dict for backward compatibility
        if statistics is None and metrics is None:
            statistics = {}

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
            ASSETS_KEY: assets,
            METRICS_KEY: metrics,
        }

        # Only include statistics in output if it's not None
        if statistics is not None:
            output_dict[STATISTICS_KEY] = statistics

        # Add the auxiliary configurations to the output dictionary if they are
        # defined and not empty.
        if (
            self.output_format is not None
            and self.output_format == OutputFormat.CSV_ARCHIVE
            and self.csv_configurations is not None
            and self.csv_configurations != {}
        ):
            output_dict["csv_configurations"] = self.csv_configurations

        if (
            (self.output_format is None or self.output_format == ContentFormat.JSON)
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

    def write(self, output: Output | dict[str, Any] | BaseModel, *args, **kwargs) -> None:
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
    >>> from nextmv.output import LocalOutputWriter, Output, Metrics
    >>> writer = LocalOutputWriter()
    >>> output = Output(solution={"result": 42}, metrics={"time": 1.23})
    >>> # Write to stdout
    >>> writer.write(output, path=None)
    >>> # Write to a file
    >>> writer.write(output, path="results.json")
    """

    def write(
        self,
        output: Output | dict[str, Any] | BaseModel | None = None,
        path: str | None = None,
        skip_stdout_reset: bool = False,
        content_format: ContentFormat | None = None,
        manifest: Manifest | None = None,
        options: Options | dict[str, Any] | None = None,
        metrics: dict[str, Any] | None = None,
        assets: list[Asset | dict[str, Any]] | None = None,
        solution: dict[str, Any] | Any | dict[str, list[dict[str, Any]]] | None = None,
        solution_files: list[SolutionFile] | None = None,
        csv_configurations: dict[str, Any] | None = None,
        json_configurations: dict[str, Any] | None = None,
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
            Path to write the output data to. The interpretation depends on the
            output format:

            - For `ContentFormat.JSON`: file path for the JSON output. If None or
              empty, writes to stdout.
            - For `ContentFormat.MULTI_FILE`: directory path for output files. If
              None or empty, writes to a directory named "outputs" in the current
              working directory.
        skip_stdout_reset : bool, optional
            Skip resetting stdout before writing the output data. Default is False.
        content_format : ContentFormat, optional
            The content format to use for writing the output. If not provided, it
            is resolved from the manifest, the output object, or defaults to
            `ContentFormat.JSON`.
        manifest : Manifest, optional
            Manifest object used to resolve the content format and output paths. If
            not provided, a manifest is attempted to be loaded from the current
            working directory.
        options : Union[Options, dict[str, Any]], optional
            Options to include in the output. Takes priority over the options in
            the `output` argument. Default is None.
        metrics : dict[str, Any], optional
            Metrics to include in the output. Takes priority over the metrics in
            the `output` argument. Default is None.
        assets : list[Union[Asset, dict[str, Any]]], optional
            List of assets to include in the output. Takes priority over the assets
            in the `output` argument. Default is None.
        solution : Union[dict[str, Any], Any], optional
            Solution data to include in the output. Takes priority over the solution
            in the `output` argument. Only used for non-`ContentFormat.MULTI_FILE`
            formats. Default is None.
        solution_files : list[SolutionFile], optional
            List of solution files to include in the output. Takes priority over
            the solution files in the `output` argument. Only used with
            `ContentFormat.MULTI_FILE`. Default is None.
        csv_configurations : dict[str, Any], optional
            Configuration options for CSV serialization, passed as kwargs to
            `csv.DictWriter`. Default is None.
        json_configurations : dict[str, Any], optional
            Configuration options for JSON serialization, passed as kwargs to
            `json.dumps` (e.g. ``{"indent": 2}``). Default is None.

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
        >>> from nextmv import LocalOutputWriter, Output, json_solution_file
        >>> from nextmv.content_format import ContentFormat
        >>> writer = LocalOutputWriter()
        >>> # Write JSON output to stdout using an Output object
        >>> writer.write(Output(solution={"result": 42}, metrics={"duration": 1.5}))
        >>> # Write JSON output to a file
        >>> writer.write(Output(solution={"result": 42}), path="result.json")
        >>> # Write JSON output directly via arguments, without an Output object
        >>> writer.write(solution={"result": 42}, metrics={"duration": 1.5}, path="result.json")
        >>> # Write multi-file output to a directory using an Output object
        >>> solution_file = json_solution_file(name="solution", data={"result": 42})
        >>> writer.write(
        ...     Output(
        ...         output_format=ContentFormat.MULTI_FILE,
        ...         solution_files=[solution_file],
        ...     ),
        ...     path="output_dir",
        ... )
        >>> # Write multi-file output directly via arguments, without an Output object
        >>> writer.write(
        ...     content_format=ContentFormat.MULTI_FILE,
        ...     solution_files=[solution_file],
        ...     metrics={"duration": 1.5},
        ...     path="output_dir",
        ... )
        """

        # If the user forgot to reset stdout after redirecting it, we need to
        # do it here to avoid unexpected behavior.
        if sys.stdout is not sys.__stdout__ and not skip_stdout_reset:
            reset_stdout()

        output_dict = self.__output_to_dict(output)
        manifest = resolve_manifest(manifest)
        content_format = self.__resolve_content_format(output, manifest, content_format)
        options = self.__resolve_options(output_dict, options)
        metrics = self.__resolve_metrics(output_dict, metrics)
        statistics = self.__resolve_statistics(output_dict)
        assets = self.__resolve_assets(output_dict, assets)
        json_configs = self.__resolve_json_configs(json_configurations, output_dict)
        csv_configs = self.__resolve_csv_configs(csv_configurations, output_dict)

        # Can be a single path or a dict of paths.
        paths = self.__resolve_paths(content_format, path, manifest)

        # This resolves both the solution and the solution_files for all content formats.
        solution = self.__resolve_solution(content_format, output, output_dict, solution, solution_files)

        if content_format in {ContentFormat.JSON, OutputFormat.TEXT}:
            self.__write_json(
                output,
                options,
                solution,
                assets,
                metrics,
                statistics,
                path=paths,
                json_configurations=json_configs,
            )
        elif content_format == OutputFormat.CSV_ARCHIVE:
            self.__write_archive(
                options,
                solution,
                assets,
                metrics,
                statistics,
                path=paths,
                json_configurations=json_configs,
                csv_configurations=csv_configs,
            )
        elif content_format == ContentFormat.MULTI_FILE:
            self.__write_multi_file(
                assets,
                metrics,
                statistics,
                solution_files=solution,
                paths=paths,
                json_configurations=json_configs,
            )
        else:
            raise ValueError(f"unsupported content format: {content_format} in the `LocalOutputWriter.write` method")

    def __resolve_content_format(
        self,
        output: Output | dict[str, Any] | BaseModel | None = None,
        manifest: Manifest | None = None,
        content_format: ContentFormat | None = None,
    ) -> ContentFormat:
        """
        Resolve the content format to use for writing the output.

        The resolution order is:
        1. If `content_format` is explicitly provided, use it.
        2. Else if `manifest` is provided, use the format from its configuration.
        3. Else if `output` is provided, derive the format from the output type:
           - `Output`: uses `output.output_format`.
           - `dict` or `BaseModel`: defaults to `ContentFormat.JSON`.
        4. Otherwise, defaults to `ContentFormat.JSON`.

        Deprecated `OutputFormat` values are handled with a deprecation
        warning and converted to their `ContentFormat` equivalents where
        possible.

        Parameters
        ----------
        output : Union[Output, dict[str, Any], BaseModel], optional
            The output object from which to derive the content format.
        manifest : Manifest, optional
            Manifest whose configuration specifies the content format.
        content_format : ContentFormat, optional
            Explicit content format to use, taking highest precedence.

        Returns
        -------
        ContentFormat
            The resolved content format.

        Raises
        ------
        ValueError
            If the content format cannot be resolved from the provided output
            type, or if an unsupported `OutputFormat` value is encountered.
        """

        resolved_content_format = None
        if output is not None and isinstance(output, BaseModel) and not isinstance(output, Output):
            resolved_content_format = ContentFormat.JSON
        elif content_format is not None:
            resolved_content_format = content_format
        elif manifest is not None:
            resolved_content_format = manifest.configuration.content.format
        elif output is not None:
            if isinstance(output, Output) and output.output_format is not None:
                resolved_content_format = output.output_format
            elif isinstance(output, (Output, dict, BaseModel)):
                resolved_content_format = ContentFormat.JSON
            else:
                raise ValueError(
                    "`content_format` cannot be resolved from the provided `Output`, "
                    "please provide a `content_format` explicitly. "
                    f"Unsupported output type: {type(output)}, supported types are `Output`, `dict`, `BaseModel`"
                )
        else:
            resolved_content_format = ContentFormat.JSON

        if type(resolved_content_format) is ContentFormat:
            return resolved_content_format

        deprecated(
            name="OutputFormat",
            reason="using `OutputFormat` as the type for `content_format` is deprecated, use `ContentFormat` instead",
        )
        if resolved_content_format in {OutputFormat.TEXT, OutputFormat.CSV_ARCHIVE}:
            deprecated(
                name="OutputFormat.TEXT/OutputFormat.CSV_ARCHIVE",
                reason="`text`/`csv-archive` format is no longer supported, use `ContentFormat.MULTI_FILE` instead",
            )
        elif resolved_content_format in {OutputFormat.JSON, OutputFormat.MULTI_FILE}:
            return ContentFormat(resolved_content_format.value)
        else:
            raise ValueError(f"unsupported content_format: {resolved_content_format}")

        return resolved_content_format

    def __resolve_paths(
        self,
        content_format: ContentFormat,
        path: str | None = None,
        manifest: Manifest | None = None,
    ) -> str | dict[str, str]:
        """
        Resolve the output path(s) based on the content format.

        For `ContentFormat.JSON`, returns a single file path string. If an
        explicit `path` is provided it is used as-is; otherwise an empty string
        is returned, signalling that the output should be written to stdout.

        For `ContentFormat.MULTI_FILE`, returns a dictionary mapping the keys
        ``solutions``, ``metrics``, ``statistics``, and ``assets`` to their
        respective file/directory paths. The resolution order is: explicit
        ``path`` argument → manifest configuration → built-in defaults.

        Parameters
        ----------
        content_format : ContentFormat
            The content format used for writing the output.
        path : str, optional
            Explicit path provided by the caller.
        manifest : Manifest, optional
            Manifest whose configuration specifies multi-file output paths.

        Returns
        -------
        str or dict[str, str]
            A single path string for JSON output, or a mapping of output
            section names to paths for multi-file output.

        Raises
        ------
        ValueError
            If an unexpected content format is encountered.
        """
        if path is not None and content_format != ContentFormat.MULTI_FILE:
            return path

        if content_format in {ContentFormat.JSON, OutputFormat.TEXT}:
            return ""

        if content_format == OutputFormat.CSV_ARCHIVE:
            return "output"

        # At this point, we should be using multi-file, but we check it and
        # raise an exception if it's not the case, just to be safe.
        if content_format != ContentFormat.MULTI_FILE:
            raise ValueError(f"unexpected content format for the output: {content_format}")

        if path:
            return {
                "solutions": os.path.join(path, "solutions"),
                "metrics": os.path.join(path, "metrics.json"),
                "statistics": os.path.join(path, "statistics.json"),
                "assets": os.path.join(path, "assets.json"),
            }

        if manifest is not None:
            return {
                "solutions": manifest.configuration.content.multi_file.output.solutions,
                "metrics": manifest.configuration.content.multi_file.output.metrics,
                "statistics": manifest.configuration.content.multi_file.output.statistics,
                "assets": manifest.configuration.content.multi_file.output.assets,
            }

        return {
            "solutions": "outputs/solutions",
            "metrics": "outputs/metrics.json",
            "statistics": "outputs/statistics.json",
            "assets": "outputs/assets.json",
        }

    def __resolve_options(
        self,
        output_dict: dict[str, Any] | None = None,
        options: Options | dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        Resolve the options to a plain dictionary.

        If explicit ``options`` are provided they take precedence over whatever
        is stored in ``output_dict``. An `Options` instance is converted via
        its ``to_dict`` method; a plain ``dict`` is used as-is.

        Parameters
        ----------
        output_dict : dict[str, Any], optional
            Dictionary representation of the output, used as a fallback source
            for options when no explicit value is given.
        options : Options or dict[str, Any], optional
            Explicit options to resolve.

        Returns
        -------
        dict[str, Any] or None
            Resolved options dictionary, or ``None`` if no options are available.

        Raises
        ------
        TypeError
            If ``options`` is of an unsupported type.
        """
        if options is not None:
            if isinstance(options, Options):
                return options.to_dict()

            if isinstance(options, dict):
                return options

            raise TypeError(f"unsupported `options` type: {type(options)}, supported types are `Options` or `dict`")

        if output_dict:
            return output_dict.get("options")

        return None

    def __resolve_metrics(
        self,
        output_dict: dict[str, Any] | None = None,
        metrics: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        Resolve the metrics dictionary.

        Explicit ``metrics`` take precedence over any metrics stored in
        ``output_dict``.

        Parameters
        ----------
        output_dict : dict[str, Any], optional
            Dictionary representation of the output, used as a fallback source
            for metrics when no explicit value is given.
        metrics : dict[str, Any], optional
            Explicit metrics to resolve.

        Returns
        -------
        dict[str, Any] or None
            Resolved metrics dictionary, or ``None`` if no metrics are available.
        """
        if metrics is not None:
            return metrics

        if output_dict:
            return output_dict.get(METRICS_KEY)

        return None

    def __resolve_statistics(self, output_dict: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """
        Resolve the statistics dictionary from the output dictionary.

        Parameters
        ----------
        output_dict : dict[str, Any], optional
            Dictionary representation of the output from which to extract
            statistics.

        Returns
        -------
        dict[str, Any] or None
            Statistics dictionary if present in ``output_dict``, otherwise
            ``None``.
        """
        if output_dict is None:
            return None

        return output_dict.get(STATISTICS_KEY)

    def __resolve_assets(
        self,
        output_dict: dict[str, Any] | None = None,
        assets: list[Asset | dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]] | None:
        """
        Resolve the list of assets to plain dictionaries.

        Explicit ``assets`` take precedence over any assets stored in
        ``output_dict``. Each element is normalised to a ``dict``: `Asset`
        instances are converted via ``to_dict``; plain dicts are used as-is.

        Parameters
        ----------
        output_dict : dict[str, Any], optional
            Dictionary representation of the output, used as a fallback source
            for assets when no explicit value is given.
        assets : list[Asset or dict[str, Any]], optional
            Explicit list of assets to resolve.

        Returns
        -------
        list[dict[str, Any]] or None
            List of resolved asset dictionaries, or ``None`` if no assets are
            available.

        Raises
        ------
        TypeError
            If an element in ``assets`` is of an unsupported type.
        """
        if assets is not None:
            resolved_assets = []
            for ix, asset in enumerate(assets):
                if isinstance(asset, Asset):
                    resolved_assets.append(asset.to_dict())
                elif isinstance(asset, dict):
                    resolved_assets.append(asset)
                else:
                    raise TypeError(
                        f"unsupported asset {ix}, type: {type(asset)}; supported types are `Asset` or `dict`"
                    )

            return resolved_assets

        if output_dict:
            return output_dict.get(ASSETS_KEY)

        return None

    def __resolve_solution(  # noqa: C901
        self,
        content_format: ContentFormat,
        output: Output | dict[str, Any] | BaseModel | None = None,
        output_dict: dict[str, Any] | None = None,
        solution: dict[str, Any] | Any | dict[str, list[dict[str, Any]]] | None = None,
        solution_files: list[SolutionFile] | None = None,
    ) -> dict[str, Any] | Any | dict[str, list[dict[str, Any]]] | list[SolutionFile] | None:
        """
        Resolve the solution to write.

        The resolution behaviour depends on ``content_format``:

        - For non-``MULTI_FILE`` formats the explicit ``solution`` argument
          takes precedence, falling back to the value stored in
          ``output_dict``. Providing ``solution_files`` with a non-multi-file
          format raises a ``ValueError``.
        - For ``ContentFormat.MULTI_FILE`` only ``solution_files`` are
          accepted. Providing a plain ``solution`` (either directly or via
          ``output_dict``) raises a ``ValueError``.

        Parameters
        ----------
        content_format : ContentFormat
            The content format used for writing the output.
        output : Output or dict[str, Any] or BaseModel, optional
            Original output object, used to retrieve ``solution_files`` when
            they are not passed explicitly.
        output_dict : dict[str, Any], optional
            Dictionary representation of the output.
        solution : dict[str, Any] or Any, optional
            Explicit solution data for non-multi-file formats.
        solution_files : list[SolutionFile], optional
            Explicit list of solution files for multi-file format.

        Returns
        -------
        dict[str, Any] or Any or list[SolutionFile] or None
            The resolved solution or solution files, or ``None`` if none are
            available.

        Raises
        ------
        ValueError
            If ``solution_files`` are provided for a non-multi-file format, or
            if a plain ``solution`` is provided for ``ContentFormat.MULTI_FILE``.
        """

        if content_format != ContentFormat.MULTI_FILE:
            if solution_files is not None:
                raise ValueError(
                    f"`solution_files` are not `None`, but `content_format` is different from "
                    f"`ContentFormat.MULTI_FILE`: {content_format}. If you want to use `solution_files`, "
                    f"set `content_format` to `ContentFormat.MULTI_FILE`."
                )

            # We need to handle the special case where base model is passed and
            # we don't extract solutions.
            if output is not None and isinstance(output, BaseModel) and not isinstance(output, Output):
                return output_dict

            if solution is not None:
                return solution

            if "solution" in output_dict.keys():
                return output_dict["solution"]

            return output_dict

        # At this point we are working with multi-file.
        # We do not support a solution with multi-file because we don't know
        # what the user's intent is for serialization.
        if solution is not None:
            raise ValueError(
                "`solution` is not `None`, but `content_format` is `ContentFormat.MULTI_FILE`. "
                "Only use `solution_files` with this content format."
            )

        # Same here, in case the user passes the solution via the output.
        if output_dict:
            sol = output_dict.get("solution")
            if sol:
                raise ValueError(
                    "`Output.solution` is not `None`, but `content_format` is `ContentFormat.MULTI_FILE`. "
                    "Only use `Output.solution_files` with this content format."
                )

        if solution_files is not None:
            return solution_files

        elif output is not None and isinstance(output, Output) and output.solution_files is not None:
            return output.solution_files

        return None

    def __resolve_json_configs(
        self,
        json_configurations: dict[str, Any] | None = None,
        output_dict: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        Resolve the JSON serialization configuration.

        Explicit ``json_configurations`` take precedence over any configuration
        stored in ``output_dict``.

        Parameters
        ----------
        json_configurations : dict[str, Any], optional
            Explicit JSON configuration options (e.g. ``indent``).
        output_dict : dict[str, Any], optional
            Dictionary representation of the output, used as a fallback source
            for JSON configuration when no explicit value is given.

        Returns
        -------
        dict[str, Any] or None
            Resolved JSON configuration dictionary, or ``None`` if none are
            available.
        """
        if json_configurations is not None:
            return json_configurations

        if output_dict:
            return output_dict.get("json_configurations", {})

        return None

    def __resolve_csv_configs(
        self,
        csv_configurations: dict[str, Any] | None = None,
        output_dict: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        Resolve the CSV serialization configuration.

        Explicit ``csv_configurations`` take precedence over any configuration
        stored in ``output_dict``.

        Parameters
        ----------
        csv_configurations : dict[str, Any], optional
            Explicit CSV configuration options passed as kwargs to
            ``csv.DictWriter``.
        output_dict : dict[str, Any], optional
            Dictionary representation of the output, used as a fallback source
            for CSV configuration when no explicit value is given.

        Returns
        -------
        dict[str, Any] or None
            Resolved CSV configuration dictionary, or ``None`` if none are
            available.
        """
        if csv_configurations is not None:
            return csv_configurations

        if output_dict:
            return output_dict.get("csv_configurations", {})

    def __output_to_dict(self, output: Output | dict[str, Any] | BaseModel | None = None) -> dict[str, Any]:
        """
        Convert the output to a dictionary, based on its type.

        Parameters
        ----------
        output : Union[Output, dict[str, Any], BaseModel]
            The output to convert to a dictionary.

        Returns
        -------
        dict[str, Any]
            The dictionary representation of the output.
        """

        if output is None:
            return {}

        if isinstance(output, Output):
            return output.to_dict()

        if isinstance(output, BaseModel):
            return output.to_dict()

        if isinstance(output, dict):
            return output

        raise TypeError(f"unsupported `output` type: {type(output)}, supported types are `Output`, `dict`, `BaseModel`")

    def __write_json(
        self,
        output: Output | dict[str, Any] | BaseModel | None = None,
        options: dict[str, Any] | None = None,
        solution: dict[str, Any] | Any | dict[str, list[dict[str, Any]]] | None = None,
        assets: list[dict[str, Any]] | None = None,
        metrics: dict[str, Any] | None = None,
        statistics: dict[str, Any] | None = None,
        path: str | None = None,
        json_configurations: dict[str, Any] | None = None,
    ) -> None:
        """
        Write output in JSON format.

        Assembles a JSON payload from the provided components and writes it
        either to the file at ``path`` or to stdout when ``path`` is ``None``
        or an empty string.

        Parameters
        ----------
        output : Union[Output, dict[str, Any], BaseModel], optional
            Output data to write. Can be an Output object, a dictionary, or a
            BaseModel.
        options : dict[str, Any], optional
            Options dictionary to include in the output payload.
        solution : dict[str, Any] or Any, optional
            Solution data to include in the output payload.
        assets : list[dict[str, Any]], optional
            List of asset dictionaries to include in the output payload.
        metrics : dict[str, Any], optional
            Metrics dictionary to include in the output payload.
        statistics : dict[str, Any], optional
            Statistics dictionary to include in the output payload. Omitted
            from the payload when ``None``.
        path : str, optional
            File path to write the serialized JSON to. When ``None`` or an
            empty string the payload is printed to stdout instead.
        json_configurations : dict[str, Any], optional
            Additional keyword arguments forwarded to the JSON serializer
            (e.g. ``{"indent": 2}``).
        """
        json_configurations = json_configurations or {}

        output_dict = {
            "options": options or {},
            "solution": solution or {},
            ASSETS_KEY: assets or [],
            METRICS_KEY: metrics or {},
        }

        if statistics is not None:
            output_dict[STATISTICS_KEY] = statistics

        if output is not None and isinstance(output, BaseModel) and not isinstance(output, Output):
            output_dict = solution

        if output is not None and isinstance(output, dict) and "solution" not in solution.keys():
            output_dict = solution

        serialized = serialize_json(
            output_dict,
            json_configurations=json_configurations,
        )

        if path is None or path == "":
            print(serialized, file=sys.stdout)
            return

        with open(path, "w", encoding="utf-8") as file:
            file.write(serialized + "\n")

    def __write_archive(
        self,
        options: dict[str, Any] | None = None,
        solution: dict[str, Any] | Any | dict[str, list[dict[str, Any]]] | None = None,
        assets: list[dict[str, Any]] | None = None,
        metrics: dict[str, Any] | None = None,
        statistics: dict[str, Any] | None = None,
        path: str | None = None,
        json_configurations: dict[str, Any] | None = None,
        csv_configurations: dict[str, Any] | None = None,
    ) -> None:
        """
        Write output in CSV archive format.

        The non-solution fields (options, assets, metrics, statistics) are
        serialized to JSON and printed to stdout.  The solution — which must
        be a ``dict`` mapping table names to lists of row dicts — is written
        as one CSV file per key inside ``path`` (or ``"output"`` by default).

        Parameters
        ----------
        options : dict[str, Any], optional
            Options dictionary included in the JSON payload written to stdout.
        solution : dict[str, Any] or Any, optional
            Solution data. When not ``None`` it must be a ``dict`` whose
            values are lists of row dictionaries; each entry becomes a
            separate CSV file.
        assets : list[dict[str, Any]], optional
            List of asset dictionaries included in the JSON payload.
        metrics : dict[str, Any], optional
            Metrics dictionary included in the JSON payload.
        statistics : dict[str, Any], optional
            Statistics dictionary included in the JSON payload. Omitted when
            ``None``.
        path : str, optional
            Directory path to write the CSV files to. Defaults to
            ``"output"`` when ``None`` or empty.
        json_configurations : dict[str, Any], optional
            Additional keyword arguments forwarded to the JSON serializer.
        csv_configurations : dict[str, Any], optional
            Additional keyword arguments forwarded to ``csv.DictWriter``.

        Raises
        ------
        ValueError
            If ``path`` refers to an existing file rather than a directory, or
            if ``solution`` is not a ``dict``.
        """

        json_configurations = json_configurations or {}
        csv_configurations = csv_configurations or {}

        dir_path = "output"
        if path is not None and path != "":
            if os.path.isfile(path):
                raise ValueError(f"The path refers to an existing file: {path}")

            dir_path = path

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        output_json = {
            "options": options or {},
            ASSETS_KEY: assets or [],
            METRICS_KEY: metrics or {},
        }

        if statistics is not None:
            output_json[STATISTICS_KEY] = statistics

        serialized = serialize_json(
            output_json,
            json_configurations=json_configurations,
        )
        print(serialized, file=sys.stdout)

        if solution is None:
            return

        if not isinstance(solution, dict):
            raise ValueError("For `OutputFormat.CSV_ARCHIVE`, when `solution` is not `None`, it must be a `dict`.")

        for file_name, data in solution.items():
            file_path = os.path.join(dir_path, f"{file_name}.csv")
            with open(file_path, "w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=data[0].keys(),
                    **csv_configurations,
                )
                writer.writeheader()
                writer.writerows(data)

    def __write_multi_file(
        self,
        assets: list[dict[str, Any]] | None = None,
        metrics: dict[str, Any] | None = None,
        statistics: dict[str, Any] | None = None,
        solution_files: list[SolutionFile] | None = None,
        paths: dict[str, str] | None = None,
        json_configurations: dict[str, Any] | None = None,
    ) -> None:
        """
        Write output to multiple files.

        Dispatches each output section (statistics, metrics, assets, and
        solution files) to the appropriate helper methods, each of which
        creates the necessary directory structure and writes the data.

        Parameters
        ----------
        assets : list[dict[str, Any]], optional
            List of asset dictionaries to write.
        metrics : dict[str, Any], optional
            Metrics dictionary to write.
        statistics : dict[str, Any], optional
            Statistics dictionary to write.
        solution_files : list[SolutionFile], optional
            Solution files to write. Each file is written using its own
            ``writer`` callable.
        paths : dict[str, str], optional
            Mapping of output section names (``"solutions"``, ``"metrics"``,
            ``"statistics"``, ``"assets"``) to their destination paths.
        json_configurations : dict[str, Any], optional
            Additional keyword arguments forwarded to the JSON serializer
            for non-solution sections.
        """

        json_configurations = json_configurations or {}

        self.__write_multi_file_element(
            element_key=STATISTICS_KEY,
            paths=paths,
            element=statistics,
            json_configurations=json_configurations,
        )
        self.__write_multi_file_element(
            element_key=METRICS_KEY,
            paths=paths,
            element=metrics,
            json_configurations=json_configurations,
        )
        self.__write_multi_file_element(
            element_key=ASSETS_KEY,
            paths=paths,
            element=assets,
            json_configurations=json_configurations,
        )
        self.__write_multi_file_solution(paths, solution_files)

    def __write_multi_file_element(
        self,
        element_key: str,
        paths: dict[str, str],
        element: dict[str, Any] | None = None,
        json_configurations: dict[str, Any] | None = None,
    ):
        """
        Write a single output section (e.g. metrics, statistics, assets) to a
        JSON file.

        The element is serialized under its key (e.g.
        ``{"metrics": {...}}``) and written to the file path looked up from
        ``paths`` using ``element_key``.  The parent directory is created
        automatically when it does not yet exist.

        Parameters
        ----------
        element_key : str
            Key used to look up the destination path in ``paths`` and to wrap
            the element in the serialized payload.
        paths : dict[str, str]
            Mapping of section names to file paths.
        element : dict[str, Any], optional
            The data to serialize and write. Skipped when ``None`` or empty.
        json_configurations : dict[str, Any], optional
            Additional keyword arguments forwarded to the JSON serializer.

        Raises
        ------
        ValueError
            If the path resolved for ``element_key`` is a directory rather
            than a file path (i.e. has no file extension).
        """

        if element is None or not element:
            return

        element_path = paths.get(element_key)

        _, ext = os.path.splitext(element_path)
        if ext:
            # element_path points to a file; ensure the parent directory exists.
            os.makedirs(os.path.dirname(element_path), exist_ok=True)
        else:
            raise ValueError(f"expected a file path for element '{element_key}', but got a dir: {element_path}")

        # The element is expected behind its key.
        keyed_element = {element_key: element}
        serialized = serialize_json(keyed_element, json_configurations=json_configurations)
        with open(element_path, "w", encoding="utf-8") as file:
            file.write(serialized + "\n")

    def __write_multi_file_solution(
        self,
        paths: dict[str, str],
        solution_files: list[SolutionFile] | None = None,
    ):
        """
        Write each `SolutionFile` to the solutions directory.

        The destination directory is derived from ``paths[SOLUTIONS_KEY]`` and
        is created automatically when it does not yet exist.  Each
        `SolutionFile` is written by calling its ``writer`` callable with the
        resolved file path, the data, and any additional ``writer_args`` /
        ``writer_kwargs``.

        Parameters
        ----------
        paths : dict[str, str]
            Mapping of section names to paths. The ``"solutions"`` key must
            point to the target directory.
        solution_files : list[SolutionFile], optional
            List of solution files to write. When ``None`` the method returns
            immediately without writing anything.

        Raises
        ------
        TypeError
            If any element of ``solution_files`` is not a `SolutionFile`
            instance.
        """

        if solution_files is None:
            return

        path = paths.get(SOLUTIONS_KEY)
        os.makedirs(path, exist_ok=True)

        for solution_file in solution_files:
            if not isinstance(solution_file, SolutionFile):
                raise TypeError(
                    f"unsupported solution_file type: {type(solution_file)}, supported type is `SolutionFile`"
                )

            file_path = os.path.join(path, solution_file.name)
            if solution_file.writer_args is None:
                solution_file.writer_args = []
            if solution_file.writer_kwargs is None:
                solution_file.writer_kwargs = {}

            # Call the writer function with the final path, and user provided
            # arguments and keyword arguments.
            solution_file.writer(
                file_path,
                solution_file.data,
                *solution_file.writer_args,
                **solution_file.writer_kwargs,
            )


_LOCAL_OUTPUT_WRITER = LocalOutputWriter()
"""Default LocalOutputWriter instance used by the write function."""


def write(
    output: Output | dict[str, Any] | BaseModel | None = None,
    path: str | None = None,
    skip_stdout_reset: bool = False,
    writer: OutputWriter | None = _LOCAL_OUTPUT_WRITER,
    content_format: ContentFormat | None = None,
    manifest: Manifest | None = None,
    options: Options | dict[str, Any] | None = None,
    metrics: dict[str, Any] | None = None,
    assets: list[Asset | dict[str, Any]] | None = None,
    solution: dict[str, Any] | Any | dict[str, list[dict[str, Any]]] | None = None,
    solution_files: list[SolutionFile] | None = None,
    csv_configurations: dict[str, Any] | None = None,
    json_configurations: dict[str, Any] | None = None,
) -> None:
    """
    Write the output to the specified destination.

    You can import the `write` function directly from `nextmv`:

    ```python
    from nextmv import write
    ```

    This is a convenience function for writing output data using a provided
    writer. By default, it uses the `LocalOutputWriter` to write to local
    sources like files or stdout. When working with the local filesystem,
    please consider the following.

    To use this function you have two main options:

    - Provide arguments directly, such as `solution`, `metrics`, `assets`,
      `solution_files`.
    - Provide an `Output` object to the `output` argument. The `Output` class
      is in charge of aggregating output elements.

    This function will resolve each of the required element in the following
    order:

    1. If the argument is provided, it takes priority. For example, if you use
       the `solution` argument and the `output` argument (passing an `Output`
       class with a valid `.solution` field), the `solution` argument will be
       used.
    2. If the argument is not provided, but the `output` argument is provided
       and has the corresponding field, the value from the `Output` object will
       be used.
    3. If neither the argument nor the `Output` field is provided, the element
       will be considered not available and treated as `None`.

    There are two special cases to consider: the `path` and the
    `content_format` arguments.

    1. If the argument is provided, it is used as it takes priority.
    2. If a `manifest` object is used, then it is used to resolve the `path`
       and `content_format`.
    3. If a `manifest` object is not given, a manifest is attempted to be
       loaded from the current working directory. If an `app.yaml` manifest
       exists, then the manifest is used to resolve the `path` and
       `content_format`.
    4. If the `output` argument is provided and is an `Output` object, then its
       `output_format` field is used to resolve the `content_format`.
    5. If none of the above applies, the `content_format` defaults to
       `ContentFormat.JSON` and the `path` uses default values based on the
       content format.

    It is preferred that you either use the `manifest` argument or rely on an
    `app.yaml` manifest to be present so that the `path` and `content_format`
    are resolved from the manifest configuration.

    This function detects if stdout was redirected and resets it to avoid
    unexpected behavior. If you want to skip this behavior, set the
    `skip_stdout_reset` parameter to `True`.

    Parameters
    ----------
    output : Union[Output, dict[str, Any], BaseModel]
        Output data to write. Can be an Output object, a dictionary, or a BaseModel.
    path : str, optional
        Path to write the output data to. The interpretation depends on the
        output format:

        - For `ContentFormat.JSON`: file path for the JSON output. If None or
          empty, writes to stdout.
        - For `ContentFormat.MULTI_FILE`: directory path for output files. If
          None or empty, writes to a directory named "output" in the current
          working directory.
    skip_stdout_reset : bool, optional
        Skip resetting stdout before writing the output data. Default is False.
    writer : OutputWriter, optional
        The writer to use for writing the output. Default is a
        `LocalOutputWriter` instance.
    content_format : ContentFormat, optional
        The content format to use for writing the output. If not provided, it
        is resolved from the manifest, the output object, or defaults to
        `ContentFormat.JSON`.
    manifest : Manifest, optional
        Manifest object used to resolve the content format and output paths. If
        not provided, a manifest is attempted to be loaded from the current
        working directory.
    options : Union[Options, dict[str, Any]], optional
        Options to include in the output. Takes priority over the options in
        the `output` argument. Default is None.
    metrics : dict[str, Any], optional
        Metrics to include in the output. Takes priority over the metrics in
        the `output` argument. Default is None.
    assets : list[Union[Asset, dict[str, Any]]], optional
        List of assets to include in the output. Takes priority over the assets
        in the `output` argument. Default is None.
    solution : Union[dict[str, Any], Any], optional
        Solution data to include in the output. Takes priority over the solution
        in the `output` argument. Only used for non-`ContentFormat.MULTI_FILE`
        formats. Default is None.
    solution_files : list[SolutionFile], optional
        List of solution files to include in the output. Takes priority over
        the solution files in the `output` argument. Only used with
        `ContentFormat.MULTI_FILE`. Default is None.
    csv_configurations : dict[str, Any], optional
        Configuration options for CSV serialization, passed as kwargs to
        `csv.DictWriter`. Default is None.
    json_configurations : dict[str, Any], optional
        Configuration options for JSON serialization, passed as kwargs to
        `json.dumps` (e.g. ``{"indent": 2}``). Default is None.

    Raises
    ------
    ValueError
        If the Output.output_format is not supported.
    TypeError
        If the output is of an unsupported type.

    Examples
    --------
    >>> from nextmv import write, Output, json_solution_file
    >>> from nextmv.content_format import ContentFormat
    >>> # Write JSON output to stdout using an Output object
    >>> write(Output(solution={"result": 42}, metrics={"duration": 1.5}))
    >>> # Write JSON output to a file
    >>> write(Output(solution={"result": 42}), path="result.json")
    >>> # Write JSON output directly via arguments, without an Output object
    >>> write(solution={"result": 42}, metrics={"duration": 1.5}, path="result.json")
    >>> # Write JSON output with custom indentation
    >>> write(solution={"result": 42}, json_configurations={"indent": 2})
    >>> # Write multi-file output to a directory using an Output object
    >>> solution_file = json_solution_file(name="solution", data={"result": 42})
    >>> write(
    ...     Output(
    ...         output_format=ContentFormat.MULTI_FILE,
    ...         solution_files=[solution_file],
    ...     ),
    ...     path="output_dir",
    ... )
    >>> # Write multi-file output directly via arguments, without an Output object
    >>> write(
    ...     content_format=ContentFormat.MULTI_FILE,
    ...     solution_files=[solution_file],
    ...     metrics={"duration": 1.5},
    ...     path="output_dir",
    ... )
    """

    writer.write(
        output,
        path,
        skip_stdout_reset,
        content_format,
        manifest,
        options,
        metrics,
        assets,
        solution,
        solution_files,
        csv_configurations,
        json_configurations,
    )
