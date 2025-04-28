"""Module for handling input sources and data."""

import copy
import csv
import json
import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Union

from nextmv.deprecated import deprecated
from nextmv.options import Options


class InputFormat(str, Enum):
    """Format of an `Input`."""

    JSON = "json"
    """JSON format, utf-8 encoded."""
    TEXT = "text"
    """Text format, utf-8 encoded."""
    CSV = "csv"
    """CSV format, utf-8 encoded."""
    CSV_ARCHIVE = "csv-archive"
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

    data: Union[
        Union[dict[str, Any], Any],  # JSON
        str,  # TEXT
        list[dict[str, Any]],  # CSV
        dict[str, list[dict[str, Any]]],  # CSV_ARCHIVE
    ]
    """The actual data. The data can be of various types, depending on the
    input format."""

    input_format: Optional[InputFormat] = InputFormat.JSON
    """Format of the input data. Default is `InputFormat.JSON`."""
    options: Optional[Options] = None
    """Options that the `Input` were created with."""

    def __post_init__(self):
        """Check that the data matches the format given to initialize the
        class."""

        if self.input_format == InputFormat.JSON:
            try:
                _ = json.dumps(self.data)
            except (TypeError, OverflowError) as e:
                raise ValueError(
                    f"Input has input_format InputFormat.JSON and "
                    f"data is of type {type(self.data)}, which is not JSON serializable"
                ) from e

        elif self.input_format == InputFormat.TEXT and not isinstance(self.data, str):
            raise ValueError(
                f"unsupported Input.data type: {type(self.data)} with "
                "input_format InputFormat.TEXT, supported type is `str`"
            )

        elif self.input_format == InputFormat.CSV and not isinstance(self.data, list):
            raise ValueError(
                f"unsupported Input.data type: {type(self.data)} with "
                "input_format InputFormat.CSV, supported type is `list`"
            )

        elif self.input_format == InputFormat.CSV_ARCHIVE and not isinstance(self.data, dict):
            raise ValueError(
                f"unsupported Input.data type: {type(self.data)} with "
                "input_format InputFormat.CSV_ARCHIVE, supported type is `dict`"
            )

        # Capture a snapshot of the options that were used to create the class
        # so even if they are changed later, we have a record of the original.
        init_options = self.options
        new_options = copy.deepcopy(init_options)
        self.options = new_options

    def to_dict(self) -> dict[str, any]:
        """
        Convert the input to a dictionary.

        Parameters
        ----------
        None

        Returns
        -------
        dict[str, any]
            The input as a dictionary.
        """

        return {
            "data": self.data,
            "input_format": self.input_format.value,
            "options": self.options.to_dict() if self.options is not None else None,
        }


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

    def _read_text(path: str, _) -> str:
        with open(path, encoding="utf-8") as f:
            return f.read().rstrip("\n")

    def _read_csv(path: str, csv_configurations: Optional[dict[str, Any]]) -> list[dict[str, Any]]:
        with open(path, encoding="utf-8") as f:
            return list(csv.DictReader(f, **csv_configurations))

    def _read_json(path: str, _) -> Union[dict[str, Any], Any]:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    # All of these readers are callback functions.
    STDIN_READERS = {
        InputFormat.JSON: lambda _: json.load(sys.stdin),
        InputFormat.TEXT: lambda _: sys.stdin.read().rstrip("\n"),
        InputFormat.CSV: lambda csv_configurations: list(csv.DictReader(sys.stdin, **csv_configurations)),
    }
    # These callbacks were not implemented with lambda because we needed
    # multiple lines. By using `open`, we needed the `with` to be able to close
    # the file.
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
        csv_configurations: Optional[dict[str, Any]] = None,
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

        - `InputFormat.JSON`: the data is a `dict[str, Any]`.
        - `InputFormat.TEXT`: the data is a `str`.
        - `InputFormat.CSV`: the data is a `list[dict[str, Any]]`.
        - `InputFormat.CSV_ARCHIVE`: the data is a `dict[str, list[dict[str, Any]]]`.
          Each key is the name of the CSV file, minus the `.csv` extension.

        Parameters
        ----------
        input_format : InputFormat, optional
            Format of the input data. Default is `InputFormat.JSON`.
        options : Options, optional
            Options for loading the input data.
        path : str, optional
            Path to the input data.
        csv_configurations : dict[str, Any], optional
            Configurations for loading CSV files. The default `DictReader` is
            used when loading a CSV file, so you have the option to pass in a
            dictionary with custom kwargs for the `DictReader`.

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
        if csv_configurations is None:
            csv_configurations = {}

        if input_format in [InputFormat.JSON, InputFormat.TEXT, InputFormat.CSV]:
            data = self._load_utf8_encoded(path=path, input_format=input_format, csv_configurations=csv_configurations)
        elif input_format == InputFormat.CSV_ARCHIVE:
            data = self._load_archive(path=path, csv_configurations=csv_configurations)

        return Input(data=data, input_format=input_format, options=options)

    def _load_utf8_encoded(
        self,
        csv_configurations: Optional[dict[str, Any]],
        path: Optional[str] = None,
        input_format: Optional[InputFormat] = InputFormat.JSON,
        use_file_reader: bool = False,
    ) -> Union[dict[str, Any], str, list[dict[str, Any]]]:
        """
        Load a utf-8 encoded file. Can come from stdin or a file in the
        filesystem.
        """

        # If we forcibly want to use the file reader, we can do so.
        if use_file_reader:
            return self.FILE_READERS[input_format](path, csv_configurations)

        # Otherwise, we can use the stdin reader if no path is provided.
        if path is None or path == "":
            return self.STDIN_READERS[input_format](csv_configurations)

        # Lastly, we can use the file reader if a path is provided.
        return self.FILE_READERS[input_format](path, csv_configurations)

    def _load_archive(
        self,
        csv_configurations: Optional[dict[str, Any]],
        path: Optional[str] = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Load files from a directory. Will only load CSV files.
        """

        dir_path = "input"
        if path is not None and path != "":
            if not os.path.isdir(path):
                raise ValueError(f"path {path} is not a directory")

            dir_path = path

        if not os.path.isdir(dir_path):
            raise ValueError(f'expected input directoy "{dir_path}" to exist as a default location')

        data = {}
        csv_ext = ".csv"
        for file in os.listdir(dir_path):
            if file.endswith(csv_ext):
                stripped = file.removesuffix(csv_ext)
                data[stripped] = self._load_utf8_encoded(
                    path=os.path.join(dir_path, file),
                    input_format=InputFormat.CSV,
                    use_file_reader=True,
                    csv_configurations=csv_configurations,
                )

        return data


def load_local(
    input_format: Optional[InputFormat] = InputFormat.JSON,
    options: Optional[Options] = None,
    path: Optional[str] = None,
    csv_configurations: Optional[dict[str, Any]] = None,
) -> Input:
    """
    DEPRECATION WARNING
    ----------
    `load_local` is deprecated, use `load` instead.

    This is a convenience function for instantiating a `LocalInputLoader`
    and calling its `load` method.

    Load the input data. The input data can be in various formats. For
    `InputFormat.JSON`, `InputFormat.TEXT`, and `InputFormat.CSV`, the data can
    be streamed from stdin or read from a file. When the `path` argument is
    provided (and valid), the input data is read from the file specified by
    `path`, otherwise, it is streamed from stdin. For
    `InputFormat.CSV_ARCHIVE`, the input data is read from the directory
    specified by `path`. If the `path` is not provided, the default location
    `input` is used. The directory should contain one or more files, where each
    file in the directory is a CSV file.

    The `Input` that is returned contains the `data` attribute. This data can
    be of different types, depending on the provided `input_format`:

    - `InputFormat.JSON`: the data is a `dict[str, Any]`.
    - `InputFormat.TEXT`: the data is a `str`.
    - `InputFormat.CSV`: the data is a `list[dict[str, Any]]`.
    - `InputFormat.CSV_ARCHIVE`: the data is a `dict[str, list[dict[str, Any]]]`.
        Each key is the name of the CSV file, minus the `.csv` extension.

    Parameters
    ----------
    input_format : InputFormat, optional
        Format of the input data. Default is `InputFormat.JSON`.
    options : Options, optional
        Options for loading the input data.
    path : str, optional
        Path to the input data.
    csv_configurations : dict[str, Any], optional
        Configurations for loading CSV files. The default `DictReader` is used
        when loading a CSV file, so you have the option to pass in a dictionary
        with custom kwargs for the `DictReader`.

    Returns
    -------
    Input
        The input data.

    Raises
    ------
    ValueError
        If the path is not a directory when working with CSV_ARCHIVE.
    """

    deprecated(
        name="load_local",
        reason="`load_local` is deprecated, use `load` instead.",
    )

    loader = LocalInputLoader()
    return loader.load(input_format, options, path, csv_configurations)


_LOCAL_INPUT_LOADER = LocalInputLoader()


def load(
    input_format: Optional[InputFormat] = InputFormat.JSON,
    options: Optional[Options] = None,
    path: Optional[str] = None,
    csv_configurations: Optional[dict[str, Any]] = None,
    loader: Optional[InputLoader] = _LOCAL_INPUT_LOADER,
) -> Input:
    """
    This is a convenience function for loading an `Input`, i.e.: load the input
    data. The `loader` is used to call the `.load` method. Note that the
    default loader is the `LocalInputLoader`.

    The input data can be in various formats. For
    `InputFormat.JSON`, `InputFormat.TEXT`, and `InputFormat.CSV`, the data can
    be streamed from stdin or read from a file. When the `path` argument is
    provided (and valid), the input data is read from the file specified by
    `path`, otherwise, it is streamed from stdin. For
    `InputFormat.CSV_ARCHIVE`, the input data is read from the directory
    specified by `path`. If the `path` is not provided, the default location
    `input` is used. The directory should contain one or more files, where each
    file in the directory is a CSV file.

    The `Input` that is returned contains the `data` attribute. This data can
    be of different types, depending on the provided `input_format`:

    - `InputFormat.JSON`: the data is a `dict[str, Any]`.
    - `InputFormat.TEXT`: the data is a `str`.
    - `InputFormat.CSV`: the data is a `list[dict[str, Any]]`.
    - `InputFormat.CSV_ARCHIVE`: the data is a `dict[str, list[dict[str, Any]]]`.
        Each key is the name of the CSV file, minus the `.csv` extension.

    Parameters
    ----------
    input_format: InputFormat, optional
        Format of the input data. Default is `InputFormat.JSON`.
    options: Options, optional
        Options for loading the input data.
    path: str, optional
        Path to the input data.
    csv_configurations: dict[str, Any], optional
        Configurations for loading CSV files. The default `DictReader` is used
        when loading a CSV file, so you have the option to pass in a dictionary
        with custom kwargs for the `DictReader`.
    loader: InputLoader, optional
        The loader to use for loading the input data. Default is
        `LocalInputLoader`.

    Returns
    -------
    Input
        The input data.

    Raises
    ------
    ValueError
        If the path is not a directory when working with CSV_ARCHIVE.
    """

    return loader.load(input_format, options, path, csv_configurations)
