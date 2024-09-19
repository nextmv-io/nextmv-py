"""Module for handling output destinations and data."""

import copy
import csv
import datetime
import json
import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import Field

from nextmv.base_model import BaseModel
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
    custom : Union[Any, Dict[str, Any]], optional
        Custom statistics created by the user. Can normally expect a `Dict[str,
        Any]`.
    """

    duration: Optional[float] = None
    """Duration of the run in seconds."""
    iterations: Optional[int] = None
    """Number of iterations."""
    custom: Optional[
        Union[
            Any,
            Dict[str, Any],
        ]
    ] = None
    """Custom statistics created by the user. Can normally expect a `Dict[str,
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
    custom : Union[Any, Dict[str, Any]], optional
        Custom statistics created by the user. Can normally expect a `Dict[str,
        Any]`.
    """

    duration: Optional[float] = None
    """Duration of the run in seconds."""
    value: Optional[float] = None
    """Value of the result."""
    custom: Optional[
        Union[
            Any,
            Dict[str, Any],
        ]
    ] = None
    """Custom statistics created by the user. Can normally expect a `Dict[str,
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
    data_points : List[DataPoint], optional
        Data of the series.
    """

    name: Optional[str] = None
    """Name of the series."""
    data_points: Optional[List[DataPoint]] = None
    """Data of the series."""


class SeriesData(BaseModel):
    """
    Data of a series.

    Parameters
    ----------
    value : Series, optional
        A series for the value of the solution.
    custom : List[Series], optional
        A list of series for custom statistics.
    """

    value: Optional[Series] = None
    """A series for the value of the solution."""
    custom: Optional[List[Series]] = None
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
    statistics_schema: Optional[str] = Field(alias="schema", default="v1")
    """Schema (version). This class only supports `v1`."""


class OutputFormat(str, Enum):
    """Format of an `Input`."""

    JSON = "JSON"
    """JSON format, utf-8 encoded."""
    CSV_ARCHIVE = "CSV_ARCHIVE"
    """CSV archive format: multiple CSV files."""


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

    - `OutputFormat.JSON`: the data must be `Dict[str, Any]`.
    - `OutputFormat.CSV_ARCHIVE`: the data must be `Dict[str, List[Dict[str,
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
    solution : Union[Dict[str, Any], Dict[str, List[Dict[str, Any]]], optional
        The solution to the decision problem.
    statistics : Union[Statistics, Dict[str, Any], optional
        Statistics of the solution.
    """

    options: Optional[Options] = None
    """Options that the `Input` were created with."""
    output_format: Optional[OutputFormat] = OutputFormat.JSON
    """Format of the output data. Default is `OutputFormat.JSON`."""
    solution: Optional[
        Union[
            Union[Dict[str, Any], Any],  # JSON
            Dict[str, List[Dict[str, Any]]],  # CSV_ARCHIVE
        ]
    ] = None
    """The solution to the decision problem."""
    statistics: Optional[Union[Statistics, Dict[str, Any]]] = None
    """Statistics of the solution."""
    csv_configurations: Optional[Dict[str, Any]] = None
    """Optional configuration for writing CSV files, to be used when the
    `output_format` is OutputFormat.CSV_ARCHIVE. These configurations are
    passed as kwargs to the `DictWriter` class from the `csv` module."""

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


class OutputWriter:
    """Base class for writing outputs."""

    def write(self, output: Output, *args, **kwargs) -> None:
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
        output: Union[Output, Dict[str, Any]],
        options: Dict[str, Any],
        statistics: Dict[str, Any],
        path: Optional[str] = None,
    ) -> None:
        solution = {}
        if isinstance(output, Output):
            sol = output.solution
        elif isinstance(output, Dict):
            sol = output.get("solution")

        if sol is not None:
            solution = sol

        serialized = json.dumps(
            {
                "options": options,
                "solution": solution,
                "statistics": statistics,
            },
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
        options: Dict[str, Any],
        statistics: Dict[str, Any],
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
        output: Union[Output, Dict[str, Any]],
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

        Parameters
        ----------
        output: Output, Dict[str, Any]
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
        elif isinstance(output, Dict):
            output_format = OutputFormat.JSON
        else:
            raise TypeError(f"unsupported output type: {type(output)}, supported types are `Output` or `Dict`")

        statistics = self._extract_statistics(output)
        options = self._extract_options(output)

        self.FILE_WRITERS[output_format](
            output=output,
            options=options,
            statistics=statistics,
            path=path,
        )

    @staticmethod
    def _extract_statistics(output: Union[Output, Dict[str, Any]]) -> Dict[str, Any]:
        """Extract JSON-serializable statistics."""

        statistics = {}

        if isinstance(output, Output):
            stats = output.statistics
        elif isinstance(output, Dict):
            stats = output.get("statistics")

        if stats is None:
            return statistics

        if isinstance(stats, Statistics):
            statistics = stats.to_dict()
        elif isinstance(stats, Dict):
            statistics = stats
        else:
            raise TypeError(f"unsupported statistics type: {type(stats)}, supported types are `Statistics` or `Dict`")

        return statistics

    @staticmethod
    def _extract_options(output: Union[Output, Dict[str, Any]]) -> Dict[str, Any]:
        """Extract JSON-serializable options."""

        options = {}

        if isinstance(output, Output):
            opt = output.options
        elif isinstance(output, Dict):
            opt = output.get("options")

        if opt is None:
            return options

        if isinstance(opt, Options):
            options = opt.to_dict()
        elif isinstance(opt, Dict):
            options = opt
        else:
            raise TypeError(f"unsupported options type: {type(opt)}, supported types are `Options` or `Dict`")

        return options


def write_local(
    output: Union[Output, Dict[str, Any]],
    path: Optional[str] = None,
    skip_stdout_reset: bool = False,
) -> None:
    """
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
    output : Output, Dict[str, Any]
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

    writer = LocalOutputWriter()
    writer.write(output, path, skip_stdout_reset)


def _custom_serial(obj: Any):
    """JSON serializer for objects not serializable by default one."""

    if isinstance(obj, (datetime.datetime | datetime.date)):
        return obj.isoformat()

    raise TypeError(f"Type {type(obj)} not serializable")
