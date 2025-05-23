"""
Module for handling input sources and data.

This module provides classes and functions for loading and handling input data
in various formats for decision problems. It supports JSON, plain text, CSV,
and CSV archive formats and can load data from standard input or files.

Classes
-------
InputFormat
    Enum defining supported input data formats (JSON, TEXT, CSV, CSV_ARCHIVE).
Input
    Container for input data with format specification and options.
InputLoader
    Base class for loading inputs from various sources.
LocalInputLoader
    Class for loading inputs from local files or stdin.

Functions
---------
load
    Load input data using a specified loader.
"""

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
    """
    Format of an `Input`.

    You can import the `InputFormat` class directly from `nextmv`:

    ```python
    from nextmv import InputFormat
    ```

    This enum specifies the supported formats for input data.

    Attributes
    ----------
    JSON : str
        JSON format, utf-8 encoded.
    TEXT : str
        Text format, utf-8 encoded.
    CSV : str
        CSV format, utf-8 encoded.
    CSV_ARCHIVE : str
        CSV archive format: multiple CSV files.
    """

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

    You can import the `Input` class directly from `nextmv`:

    ```python
    from nextmv import Input
    ```

    Parameters
    ----------
    data : Union[dict[str, Any], str, list[dict[str, Any]], dict[str, list[dict[str, Any]]]]
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
    """
    The actual data.

    The data can be of various types, depending on the input format:

    - For `JSON`: `Union[dict[str, Any], Any]`
    - For `TEXT`: `str`
    - For `CSV`: `list[dict[str, Any]]`
    - For `CSV_ARCHIVE`: `dict[str, list[dict[str, Any]]]`
    """

    input_format: Optional[InputFormat] = InputFormat.JSON
    """
    Format of the input data.

    Default is `InputFormat.JSON`.
    """

    options: Optional[Options] = None
    """
    Options that the `Input` was created with.

    A copy of the options is made during initialization, ensuring the original
    options remain unchanged even if modified later.
    """

    def __post_init__(self):
        """
        Check that the data matches the format given to initialize the class.

        This method is automatically called after the dataclass is initialized.
        It validates that the data provided is of the correct type according to
        the specified input_format and makes a deep copy of the options to ensure
        the input maintains its own copy.

        Raises
        ------
        ValueError
            If the data type doesn't match the expected type for the given format.
        """

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

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the input to a dictionary.

        This method serializes the Input object to a dictionary format that can be
        easily converted to JSON or other serialization formats.

        Returns
        -------
        dict[str, Any]
            A dictionary containing the input data, format, and options.

            The structure is:
            ```python
            {
                "data": <the input data>,
                "input_format": <the input format as a string>,
                "options": <the options as a dictionary or None>
            }
            ```

        Examples
        --------
        >>> from nextmv.input import Input, InputFormat
        >>> input_obj = Input(data={"key": "value"}, input_format=InputFormat.JSON)
        >>> input_dict = input_obj.to_dict()
        >>> print(input_dict)
        {'data': {'key': 'value'}, 'input_format': 'json', 'options': None}
        """

        return {
            "data": self.data,
            "input_format": self.input_format.value,
            "options": self.options.to_dict() if self.options is not None else None,
        }


class InputLoader:
    """
    Base class for loading inputs.

    You can import the `InputLoader` class directly from `nextmv`:

    ```python
    from nextmv import InputLoader
    ```

    This abstract class defines the interface for input loaders. Subclasses must
    implement the `load` method to provide concrete input loading functionality.
    """

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
    Class for loading local inputs.

    You can import the `LocalInputLoader` class directly from `nextmv`:

    ```python
    from nextmv import LocalInputLoader
    ```

    This class can load input data from the local filesystem, by using stdin,
    a file, or a directory, where applicable. It supports various input formats
    like JSON, TEXT, CSV, and CSV archive.

    Call the `load` method to read the input data.

    Examples
    --------
    >>> from nextmv.input import LocalInputLoader, InputFormat
    >>> loader = LocalInputLoader()
    >>> # Load JSON from stdin or file
    >>> input_obj = loader.load(input_format=InputFormat.JSON, path="data.json")
    >>> # Load CSV from a file
    >>> input_obj = loader.load(input_format=InputFormat.CSV, path="data.csv")
    """

    def _read_text(path: str, _) -> str:
        """
        Read a text file and return its contents.

        Parameters
        ----------
        path : str
            Path to the text file.
        _ : Any
            Placeholder for unused parameter (for API consistency).

        Returns
        -------
        str
            Contents of the text file with trailing newlines removed.
        """
        with open(path, encoding="utf-8") as f:
            return f.read().rstrip("\n")

    def _read_csv(path: str, csv_configurations: Optional[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Read a CSV file and return its contents as a list of dictionaries.

        Parameters
        ----------
        path : str
            Path to the CSV file.
        csv_configurations : dict[str, Any], optional
            Configuration parameters for the CSV DictReader.

        Returns
        -------
        list[dict[str, Any]]
            List of dictionaries where each dictionary represents a row in the CSV.
        """
        with open(path, encoding="utf-8") as f:
            return list(csv.DictReader(f, **csv_configurations))

    def _read_json(path: str, _) -> Union[dict[str, Any], Any]:
        """
        Read a JSON file and return its parsed contents.

        Parameters
        ----------
        path : str
            Path to the JSON file.
        _ : Any
            Placeholder for unused parameter (for API consistency).

        Returns
        -------
        Union[dict[str, Any], Any]
            Parsed JSON data.
        """
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    # All of these readers are callback functions.
    STDIN_READERS = {
        InputFormat.JSON: lambda _: json.load(sys.stdin),
        InputFormat.TEXT: lambda _: sys.stdin.read().rstrip("\n"),
        InputFormat.CSV: lambda csv_configurations: list(csv.DictReader(sys.stdin, **csv_configurations)),
    }
    """
    Dictionary of functions to read from standard input.

    Each key is an InputFormat, and each value is a function that reads from
    standard input in that format.
    """

    # These callbacks were not implemented with lambda because we needed
    # multiple lines. By using `open`, we needed the `with` to be able to close
    # the file.
    FILE_READERS = {
        InputFormat.JSON: _read_json,
        InputFormat.TEXT: _read_text,
        InputFormat.CSV: _read_csv,
    }
    """
    Dictionary of functions to read from files.

    Each key is an InputFormat, and each value is a function that reads from
    a file in that format.
    """

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
        Load a utf-8 encoded file from stdin or filesystem.

        This internal method handles loading data in various formats from either
        standard input or a file.

        Parameters
        ----------
        csv_configurations : dict[str, Any], optional
            Configuration parameters for the CSV DictReader.
        path : str, optional
            Path to the file to read from. If None or empty, reads from stdin.
        input_format : InputFormat, optional
            Format of the input data. Default is JSON.
        use_file_reader : bool, optional
            Whether to force using the file reader even if path is None.
            Default is False.

        Returns
        -------
        Union[dict[str, Any], str, list[dict[str, Any]]]
            Data read from stdin or file in the specified format.
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
        Load CSV files from a directory.

        This internal method loads all CSV files from a specified directory,
        organizing them into a dictionary where each key is the filename
        (without .csv extension) and each value is the parsed CSV content.

        Parameters
        ----------
        csv_configurations : dict[str, Any], optional
            Configuration parameters for the CSV DictReader.
        path : str, optional
            Path to the directory containing CSV files. If None or empty,
            uses "./input" as the default directory.

        Returns
        -------
        dict[str, list[dict[str, Any]]]
            Dictionary mapping filenames to CSV contents.

        Raises
        ------
        ValueError
            If the path is not a directory or the default directory doesn't exist.
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
    !!! warning
        `load_local` is deprecated, use `load` instead.

    Load input data from local sources.

    This is a convenience function for instantiating a `LocalInputLoader`
    and calling its `load` method.

    Parameters
    ----------
    input_format : InputFormat, optional
        Format of the input data. Default is `InputFormat.JSON`.
    options : Options, optional
        Options for loading the input data.
    path : str, optional
        Path to the input data.
    csv_configurations : dict[str, Any], optional
        Configurations for loading CSV files. Custom kwargs for
        Python's `csv.DictReader`.

    Returns
    -------
    Input
        The loaded input data in an Input object.

    Raises
    ------
    ValueError
        If the path is invalid or data format is incorrect.

    See Also
    --------
    load : The recommended function to use instead.
    """

    deprecated(
        name="load_local",
        reason="`load_local` is deprecated, use `load` instead.",
    )

    loader = LocalInputLoader()
    return loader.load(input_format, options, path, csv_configurations)


_LOCAL_INPUT_LOADER = LocalInputLoader()
"""Default instance of LocalInputLoader used by the load function."""


def load(
    input_format: Optional[InputFormat] = InputFormat.JSON,
    options: Optional[Options] = None,
    path: Optional[str] = None,
    csv_configurations: Optional[dict[str, Any]] = None,
    loader: Optional[InputLoader] = _LOCAL_INPUT_LOADER,
) -> Input:
    """
    Load input data using the specified loader.

    You can import the `load` function directly from `nextmv`:

    ```python
    from nextmv import load
    ```

    This is a convenience function for loading an `Input` object. By default,
    it uses the `LocalInputLoader` to load data from local sources.

    The input data can be in various formats and can be loaded from different
    sources depending on the loader:

    - `InputFormat.JSON`: the data is a `dict[str, Any]`
    - `InputFormat.TEXT`: the data is a `str`
    - `InputFormat.CSV`: the data is a `list[dict[str, Any]]`
    - `InputFormat.CSV_ARCHIVE`: the data is a `dict[str, list[dict[str, Any]]]`
        Each key is the name of the CSV file, minus the `.csv` extension.

    Parameters
    ----------
    input_format : InputFormat, optional
        Format of the input data. Default is `InputFormat.JSON`.
    options : Options, optional
        Options for loading the input data.
    path : str, optional
        Path to the input data. For file-based loaders:
        - If provided, reads from the specified file or directory
        - If None, typically reads from stdin (for JSON, TEXT, CSV)
          or uses a default directory (for CSV_ARCHIVE)
    csv_configurations : dict[str, Any], optional
        Configurations for loading CSV files. Custom kwargs for
        Python's `csv.DictReader`.
    loader : InputLoader, optional
        The loader to use for loading the input data.
        Default is an instance of `LocalInputLoader`.

    Returns
    -------
    Input
        The loaded input data in an Input object.

    Raises
    ------
    ValueError
        If the path is invalid or data format is incorrect.

    Examples
    --------
    >>> from nextmv.input import load, InputFormat
    >>> # Load JSON from stdin
    >>> input_obj = load(input_format=InputFormat.JSON)
    >>> # Load CSV from a file
    >>> input_obj = load(input_format=InputFormat.CSV, path="data.csv")
    >>> # Load CSV archive from a directory
    >>> input_obj = load(input_format=InputFormat.CSV_ARCHIVE, path="input_dir")
    """

    return loader.load(input_format, options, path, csv_configurations)
