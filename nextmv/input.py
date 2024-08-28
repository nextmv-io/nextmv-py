"""Module for handling input sources and data."""

import csv
import json
import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from nextmv.options import Options


class InputFormat(str, Enum):
    """Format of an `Input`."""

    JSON = "JSON"
    """JSON format, utf-8 encoded."""
    TEXT = "TEXT"
    """Text format, utf-8 encoded."""
    CSV = "CSV"
    """CSV format, utf-8 encoded."""
    CSV_ARCHIVE = "CSV_ARCHIVE"
    """CSV archive format: multiple CSV files."""


@dataclass
class Input:
    """
    Input for a decision problem.

    Parameters
    ----------
    data : Any
        The actual data.
    input_format : InputFormat, optional
        Format of the input data. Default is `InputFormat.JSON`.
    options : Options, optional
        Options that the input was created with.
    """

    data: Union[Dict[str, Any], str, List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]
    """The actual data. The data can be of various types, depending on the
    input format."""

    input_format: Optional[InputFormat] = InputFormat.JSON
    """Format of the input data. Default is `InputFormat.JSON`."""

    options: Optional[Options] = None
    """Options that the `Input` were created with."""


class InputLoader:
    """Base class for loading inputs."""

    def load(
        self,
        input_format: InputFormat = InputFormat.JSON,
        options: Optional[Options] = None,
        *args,
        **kwargs,
    ) -> Input:
        """
        Read the input data. This method should be implemented by
        subclasses.

        Parameters
        ----------
        input_format : InputFormat, optional
            Format of the input data. Default is `InputFormat.JSON`.
        options : Options, optional
            Options for loading the input data.
        *args
            Additional positional arguments.
        **kwargs
            Additional keyword arguments.

        Returns
        -------
        Input
            The input data.

        Raises
        ------
        NotImplementedError
            If the method is not implemented.
        """

        raise NotImplementedError


class LocalInputLoader(InputLoader):
    """
    Class for loading local inputs. This class can load input data from the
    local filesystem, by using stdin, a file, or a directory, where applicable.
    Call the `load` method to read the input data.
    """

    def _read_text(path: str) -> str:
        with open(path, encoding="utf-8") as f:
            return f.read()

    def _read_csv(path: str) -> List[Dict[str, Any]]:
        with open(path, encoding="utf-8") as f:
            return list(csv.DictReader(f, quoting=csv.QUOTE_NONNUMERIC))

    def _read_json(path: str) -> Dict[str, Any]:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    STDIN_READERS = {
        InputFormat.JSON: lambda: json.load(sys.stdin),
        InputFormat.TEXT: lambda: sys.stdin.read(),
        InputFormat.CSV: lambda: list(csv.DictReader(sys.stdin, quoting=csv.QUOTE_NONNUMERIC)),
    }
    FILE_READERS = {
        InputFormat.JSON: _read_json,
        InputFormat.TEXT: _read_text,
        InputFormat.CSV: _read_csv,
    }

    def load(
        self,
        input_format: Optional[InputFormat] = InputFormat.JSON,
        options: Optional[Options] = None,
        path: Optional[str] = None,
    ) -> Input:
        """
        Load the input data. The input data can be in various formats. For
        `InputFormat.JSON`, `InputFormat.TEXT`, and `InputFormat.CSV`, the data
        can be streamed from stdin or read from a file. When the `path`
        argument is provided (and valid), the input data is read from the file
        specified by `path`, otherwise, it is streamed from stdin. For
        `InputFormat.CSV_ARCHIVE`, the input data is read from the directory
        specified by `path`. If the `path` is not provided, the default
        location `input` is used. The directory should contain one or more
        files, where each file in the directory is a CSV file.

        The `Input` that is returned contains the `data` attribute. This data
        can be of different types, depending on the provided `input_format`:

        - `InputFormat.JSON`: the data is a `Dict[str, Any]`.
        - `InputFormat.TEXT`: the data is a `str`.
        - `InputFormat.CSV`: the data is a `List[Dict[str, Any]]`.
        - `InputFormat.CSV_ARCHIVE`: the data is a `Dict[str, List[Dict[str, Any]]]`.
          Each key is the name of the CSV file, minus the `.csv` extension.

        Parameters
        ----------
        input_format : InputFormat, optional
            Format of the input data. Default is `InputFormat.JSON`.
        options : Options, optional
            Options for loading the input data.
        path : str, optional
            Path to the input data.

        Returns
        -------
        Input
            The input data.

        Raises
        ------
        ValueError
            If the path is not a directory when working with CSV_ARCHIVE.
        """
        data: Any = None

        if input_format in [InputFormat.JSON, InputFormat.TEXT, InputFormat.CSV]:
            data = self._load_utf8_encoded(path=path, input_format=input_format)
        elif input_format == InputFormat.CSV_ARCHIVE:
            data = self._load_archive(path=path)

        return Input(data=data, input_format=input_format, options=options)

    def _load_utf8_encoded(
        self,
        path: Optional[str] = None,
        input_format: Optional[InputFormat] = InputFormat.JSON,
        use_file_reader: bool = False,
    ) -> Union[Dict[str, Any], str, List[Dict[str, Any]]]:
        """
        Load a JSON file.

        Parameters
        ----------
        path : str
            Path to the JSON file.

        Returns
        -------
        Dict[str, Any]
            The JSON data.
        """

        # If we forcibly want to use the file reader, we can do so.
        if use_file_reader:
            return self.FILE_READERS[input_format](path)

        # Otherwise, we can use the stdin reader if no path is provided.
        if path is None or path == "":
            return self.STDIN_READERS[input_format]()

        # Lastly, we can use the file reader if a path is provided.
        return self.FILE_READERS[input_format](path)

    def _load_archive(self, path: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load a CSV archive.

        Parameters
        ----------
        path : str
            Path to the CSV archive.

        Returns
        -------
        Dict[str, List[Dict[str, Any]]]
            The CSV data.
        """

        dir_path = "input"
        if path is not None and path != "":
            if not os.path.isdir(path):
                raise ValueError(f"Path {path} is not a directory")

            dir_path = path

        if not os.path.isdir(dir_path):
            raise ValueError(f'Expected input directoy "{dir_path}" to exist as a default location')

        data = {}
        csv_ext = ".csv"
        for file in os.listdir(dir_path):
            if file.endswith(csv_ext):
                stripped = file.strip(csv_ext[1:]).strip(".")  # Python 3.8 forces this, instead of using removesuffix()
                data[stripped] = self._load_utf8_encoded(
                    path=os.path.join(dir_path, file),
                    input_format=InputFormat.CSV,
                    use_file_reader=True,
                )

        return data
