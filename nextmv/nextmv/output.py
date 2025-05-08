"""Module for handling output destinations and data."""

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

    Parameters
    ----------
    duration : float, optional
        Duration of the run in seconds.
    iterations : int, optional
        Number of iterations.
    custom : Union[Any, dict[str, Any]], optional
        Custom statistics created by the user. Can normally expect a `dict[str,
        Any]`.
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

    Parameters
    ----------
    duration : float, optional
        Duration of the run in seconds.
    value : float, optional
        Value of the result.
    custom : Union[Any, dict[str, Any]], optional
        Custom statistics created by the user. Can normally expect a `dict[str,
        Any]`.
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
    A data point.

    Parameters
    ----------
    x : float
        X coordinate of the data point.
    y : float
        Y coordinate of the data point.
    """

    x: float
    """X coordinate of the data point."""
    y: float
    """Y coordinate of the data point."""


class Series(BaseModel):
    """
    A series of data points.

    Parameters
    ----------
    name : str, optional
        Name of the series.
    data_points : list[DataPoint], optional
        Data of the series.
    """

    name: Optional[str] = None
    """Name of the series."""
    data_points: Optional[list[DataPoint]] = None
    """Data of the series."""


class SeriesData(BaseModel):
    """
    Data of a series.

    Parameters
    ----------
    value : Series, optional
        A series for the value of the solution.
    custom : list[Series], optional
        A list of series for custom statistics.
    """

    value: Optional[Series] = None
    """A series for the value of the solution."""
    custom: Optional[list[Series]] = None
    """A list of series for custom statistics."""


class Statistics(BaseModel):
    """
    Statistics of a solution.

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
    """Format of an `Input`."""

    JSON = "json"
    """JSON format, utf-8 encoded."""
    CSV_ARCHIVE = "csv-archive"
    """CSV archive format: multiple CSV files."""


class VisualSchema(str, Enum):
    """Schema of a visual asset."""

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
    Visual schema of an asset that defines how it is plotted in the Nextmv
    Console.
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
        if self.visual_schema not in VisualSchema:
            raise ValueError(f"unsupported schema: {self.visual_schema}, supported schemas are {VisualSchema}")

        if self.visual_type != "custom-tab":
            raise ValueError(f"unsupported visual_type: {self.visual_type}, supported types are `custom-tab`")


class Asset(BaseModel):
    """
    An asset represents downloadable information that is part of the `Output`.
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
        if self.content_type != "json":
            raise ValueError(f"unsupported content_type: {self.content_type}, supported types are `json`")


@dataclass
class Output:
    """
    Output of a decision problem. This class is used to be later be written to
    some location.

    The output can be in different formats, such as JSON (default) or
    CSV_ARCHIVE.

    If you used options, you can also include them in the output, to be
    serialized to the write location.

    The most important part of the output is the solution, which represents the
    result of the decision problem. The solution’s type must match the
    `output_format`:

    - `OutputFormat.JSON`: the data must be `dict[str, Any]`.
    - `OutputFormat.CSV_ARCHIVE`: the data must be `dict[str, list[dict[str,
      Any]]]`. The keys represent the file names where the data should be
      written. The values are lists of dictionaries, where each dictionary
      represents a row in the CSV file.

    The statistics are used to keep track of different metrics that were
    obtained after the run was completed. Although it can be a simple
    dictionary, we recommend using the `Statistics` class to ensure that the
    data is correctly formatted.

    Parameters
    ----------
    options : Options, optional
        Options that the `Input` were created with.
    output_format : OutputFormat, optional
        Format of the output data. Default is `OutputFormat.JSON`.
    solution : Union[dict[str, Any], dict[str, list[dict[str, Any]]], optional
        The solution to the decision problem.
    statistics : Union[Statistics, dict[str, Any], optional
        Statistics of the solution.
    """

    options: Optional[Options] = None
    """Options that the `Input` were created with."""
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
    """Statistics of the solution."""
    csv_configurations: Optional[dict[str, Any]] = None
    """Optional configuration for writing CSV files, to be used when the
    `output_format` is OutputFormat.CSV_ARCHIVE. These configurations are
    passed as kwargs to the `DictWriter` class from the `csv` module."""
    assets: Optional[list[Asset]] = None
    """Optional list of assets to be included in the output."""

    def __post_init__(self):
        """Check that the solution matches the format given to initialize the
        class."""

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

    def to_dict(self) -> dict[str, any]:
        """
        Convert the `Output` object to a dictionary.

        Returns
        -------
        dict[str, any]
            The dictionary representation of the `Output` object.
        """

        output_dict = {
            "options": self.options.to_dict() if self.options is not None else {},
            "solution": self.solution if self.solution is not None else {},
            "statistics": self.statistics.to_dict() if self.statistics is not None else {},
            "assets": [asset.to_dict() for asset in self.assets] if self.assets is not None else [],
        }

        if self.output_format == OutputFormat.CSV_ARCHIVE:
            output_dict["csv_configurations"] = self.csv_configurations

        return output_dict


class OutputWriter:
    """Base class for writing outputs."""

    def write(self, output: Union[Output, dict[str, Any], BaseModel], *args, **kwargs) -> None:
        """
        Write the output data. This method should be implemented by subclasses.
        """

        raise NotImplementedError


class LocalOutputWriter(OutputWriter):
    """
    Class for write outputs to local files or stdout. Call the `write` method
    to write the output data.
    """

    def _write_json(
        output: Union[Output, dict[str, Any], BaseModel],
        options: dict[str, Any],
        statistics: dict[str, Any],
        assets: list[dict[str, Any]],
        path: Optional[str] = None,
    ) -> None:
        if isinstance(output, dict):
            final_output = output
        elif isinstance(output, BaseModel):
            final_output = output.to_dict()
        else:
            solution = output.solution if output.solution is not None else {}
            final_output = {
                "options": options,
                "solution": solution,
                "statistics": statistics,
                "assets": assets,
            }

        serialized = json.dumps(
            final_output,
            indent=2,
            default=_custom_serial,
        )

        if path is None or path == "":
            print(serialized, file=sys.stdout)
            return

        with open(path, "w", encoding="utf-8") as file:
            file.write(serialized + "\n")

    def _write_archive(
        output: Output,
        options: dict[str, Any],
        statistics: dict[str, Any],
        assets: list[dict[str, Any]],
        path: Optional[str] = None,
    ) -> None:
        dir_path = "output"
        if path is not None and path != "":
            if os.path.isfile(path):
                raise ValueError(f"The path refers to an existing file: {path}")

            dir_path = path

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        serialized = json.dumps(
            {
                "options": options,
                "statistics": statistics,
                "assets": assets,
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

    def write(
        self,
        output: Union[Output, dict[str, Any], BaseModel],
        path: Optional[str] = None,
        skip_stdout_reset: bool = False,
    ) -> None:
        """
        Write the `output` to the local filesystem. Consider the following for
        the `path` parameter, depending on the `Output.output_format`:

        - `OutputFormat.JSON`: the `path` is the file where the JSON data will
            be written. If empty or `None`, the data will be written to stdout.
        - `OutputFormat.CSV_ARCHIVE`: the `path` is the directory where the CSV
            files will be written. If empty or `None`, the data will be written
            to a directory named `output` under the current working directory.
            The `Output.options` and `Output.statistics` will be written to
            stdout.

        This function detects if stdout was redirected and resets it to avoid
        unexpected behavior. If you want to skip this behavior, set the
        `skip_stdout_reset` parameter to `True`.

        If the `output` is a `dict`, it will be simply written to the specified
        `path`, as a passthrough. On the other hand, if the `output` is of type
        `Output`, a more structured object will be written, which adheres to
        the schema specified by the corresponding `Output` class.

        Parameters
        ----------
        output: Output, dict[str, Any]
            Output data to write.
        path : str
            Path to write the output data to.
        skip_stdout_reset : bool, optional
            Skip resetting stdout before writing the output data. Default is
            `False`.

        Raises
        ------
        ValueError
            If the `Output.output_format` is not supported.
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

        statistics = self._extract_statistics(output)
        options = self._extract_options(output)
        assets = self._extract_assets(output)

        self.FILE_WRITERS[output_format](
            output=output,
            options=options,
            statistics=statistics,
            assets=assets,
            path=path,
        )

    @staticmethod
    def _extract_statistics(output: Union[Output, dict[str, Any]]) -> dict[str, Any]:
        """Extract JSON-serializable statistics."""

        statistics = {}

        if not isinstance(output, Output):
            return statistics

        stats = output.statistics

        if stats is None:
            return statistics

        if isinstance(stats, Statistics):
            statistics = stats.to_dict()
        elif isinstance(stats, dict):
            statistics = stats
        else:
            raise TypeError(f"unsupported statistics type: {type(stats)}, supported types are `Statistics` or `dict`")

        return statistics

    @staticmethod
    def _extract_options(output: Union[Output, dict[str, Any]]) -> dict[str, Any]:
        """Extract JSON-serializable options."""

        options = {}

        if not isinstance(output, Output):
            return options

        opt = output.options

        if opt is None:
            return options

        if isinstance(opt, Options):
            options = opt.to_dict()
        elif isinstance(opt, dict):
            options = opt
        else:
            raise TypeError(f"unsupported options type: {type(opt)}, supported types are `Options` or `dict`")

        return options

    @staticmethod
    def _extract_assets(output: Union[Output, dict[str, Any]]) -> list[dict[str, Any]]:
        """Extract JSON-serializable assets."""

        assets = []

        if not isinstance(output, Output):
            return assets

        assts = output.assets

        if assts is None:
            return assets

        for ix, asset in enumerate(assts):
            if isinstance(asset, Asset):
                assets.append(asset.to_dict())
            elif isinstance(asset, dict):
                assets.append(asset)
            else:
                raise TypeError(f"unsupported asset {ix}, type: {type(asset)}; supported types are `Asset` or `dict`")

        return assets


def write_local(
    output: Union[Output, dict[str, Any]],
    path: Optional[str] = None,
    skip_stdout_reset: bool = False,
) -> None:
    """
    DEPRECATION WARNING
    ----------
    `write_local` is deprecated, use `write` instead.

    This is a convenience function for instantiating a `LocalOutputWriter` and
    calling its `write` method.

    Write the `output` to the local filesystem. Consider the following for the
    `path` parameter, depending on the `Output.output_format`:

    - `OutputFormat.JSON`: the `path` is the file where the JSON data will
        be written. If empty or `None`, the data will be written to stdout.
    - `OutputFormat.CSV_ARCHIVE`: the `path` is the directory where the CSV
        files will be written. If empty or `None`, the data will be written
        to a directory named `output` under the current working directory.
        The `Output.options` and `Output.statistics` will be written to
        stdout.

    This function detects if stdout was redirected and resets it to avoid
    unexpected behavior. If you want to skip this behavior, set the
    `skip_stdout_reset` parameter to `True`.

    Parameters
    ----------
    output : Output, dict[str, Any]
        Output data to write.
    path : str
        Path to write the output data to.
    skip_stdout_reset : bool, optional
        Skip resetting stdout before writing the output data. Default is
        `False`.

    Raises
    ------
    ValueError
        If the `Output.output_format` is not supported.
    """

    deprecated(
        name="write_local",
        reason="`write_local` is deprecated, use `write` instead.",
    )

    writer = LocalOutputWriter()
    writer.write(output, path, skip_stdout_reset)


_LOCAL_OUTPUT_WRITER = LocalOutputWriter()


def write(
    output: Union[Output, dict[str, Any], BaseModel],
    path: Optional[str] = None,
    skip_stdout_reset: bool = False,
    writer: Optional[OutputWriter] = _LOCAL_OUTPUT_WRITER,
) -> None:
    """
    This is a convenience function for writing an `Output`, i.e.: write the
    output to the specified destination. The `writer` is used to call the
    `.write` method. Note that the default writes is the `LocalOutputWriter`.

    Consider the following for the `path` parameter, depending on the
    `Output.output_format`:

    - `OutputFormat.JSON`: the `path` is the file where the JSON data will
        be written. If empty or `None`, the data will be written to stdout.
    - `OutputFormat.CSV_ARCHIVE`: the `path` is the directory where the CSV
        files will be written. If empty or `None`, the data will be written
        to a directory named `output` under the current working directory.
        The `Output.options` and `Output.statistics` will be written to
        stdout.

    This function detects if stdout was redirected and resets it to avoid
    unexpected behavior. If you want to skip this behavior, set the
    `skip_stdout_reset` parameter to `True`.

    Parameters
    ----------
    output : Output, dict[str, Any]
        Output data to write.
    path : str
        Path to write the output data to.
    skip_stdout_reset : bool, optional
        Skip resetting stdout before writing the output data. Default is
        `False`.

    Raises
    ------
    ValueError
        If the `Output.output_format` is not supported.
    """

    writer.write(output, path, skip_stdout_reset)


def _custom_serial(obj: Any):
    """JSON serializer for objects not serializable by default one."""

    if isinstance(obj, (datetime.datetime | datetime.date)):
        return obj.isoformat()

    raise TypeError(f"Type {type(obj)} not serializable")
