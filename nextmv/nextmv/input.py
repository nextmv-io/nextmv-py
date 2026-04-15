"""
Module for handling input sources and data.

This module provides classes and functions for loading and handling input data
in various formats for decision problems. It supports JSON and multi-file
formats and can load data from standard input or files.

Classes
-------
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

Attributes
----------
INPUTS_KEY : str
    Key used for identifying inputs in the run.
"""

import copy
import csv
import json
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from nextmv._serialization import serialize_json
from nextmv.content_format import ContentFormat
from nextmv.deprecated import deprecated
from nextmv.manifest import MANIFEST_FILE_NAME, Manifest
from nextmv.options import Options

INPUTS_KEY = "inputs"
"""
Inputs key constant used for identifying inputs in the run.
"""


class InputFormat(str, Enum):
    """
    !!! warning
        `InputFormat` is deprecated, use `nextmv.ContentFormat` instead.

    Format of an `Input`.

    You can import the `InputFormat` class directly from `nextmv`:

    ```python
    from nextmv import InputFormat
    ```

    This enum specifies the supported formats for input data.

    Attributes
    ----------
    JSON : str
        !!! warning
            `InputFormat.JSON` is deprecated, use `ContentFormat.JSON` instead.

        JSON format, utf-8 encoded.
    TEXT : str
        !!! warning
            `InputFormat.TEXT` is deprecated, use `ContentFormat.MULTI_FILE` instead.

        Text format, utf-8 encoded.
    CSV_ARCHIVE : str
        !!! warning
            `InputFormat.CSV_ARCHIVE` is deprecated, use `ContentFormat.MULTI_FILE` instead.

        CSV archive format: multiple CSV files.
    MULTI_FILE : str
        !!! warning
            `InputFormat.MULTI_FILE` is deprecated, use `ContentFormat.MULTI_FILE` instead.

        Multi-file format, used for loading multiple files in a single input.
    """

    JSON = "json"
    """
    !!! warning
        `InputFormat.JSON` is deprecated, use `ContentFormat.JSON` instead.

    JSON format, utf-8 encoded.
    """
    TEXT = "text"
    """
    !!! warning
        `InputFormat.TEXT` is deprecated, use `ContentFormat.MULTI_FILE` instead.

    Text format, utf-8 encoded.
    """
    CSV_ARCHIVE = "csv-archive"
    """
    !!! warning
        `InputFormat.CSV_ARCHIVE` is deprecated, use `ContentFormat.MULTI_FILE` instead.

    CSV archive format: multiple CSV files.
    """
    MULTI_FILE = "multi-file"
    """
    !!! warning
        `InputFormat.MULTI_FILE` is deprecated, use `ContentFormat.MULTI_FILE` instead.

    Multi-file format, used for loading multiple files in a single input.
    """


@dataclass
class DataFile:
    """
    Represents data to be read from a file.

    You can import the `DataFile` class directly from `nextmv`:

    ```python
    from nextmv import DataFile
    ```

    This class is used to define data that will be read from a file in the
    filesystem. It includes the name of the file, and the reader function that
    will handle the loading, and deserialization of the data from the file.
    This `DataFile` class is typically used in the `Input`, when the
    `Input.input_format` is set to `ContentFormat.MULTI_FILE`. Given that it is
    difficul to handle every edge case of how data is deserialized, and read
    from a file, this class exists so that the user can implement the `reader`
    callable of their choice and provide it with any `reader_args` and
    `reader_kwargs` they might need.

    Parameters
    ----------
    name : str
        Name of the data (input) file. The file extension should be included in
        the name.
    reader : Callable[[str], Any]
        Callable that reads the data from the file. This should be a function
        implemented by the user. There are convenience functions that you can
        use as a reader as well. The `reader` must receive, at the very minimum,
        the following arguments:

        - `file_path`: a `str` argument which is the location where this
          data will be read from. This includes the dir and name of the
          file. As such, the `name` parameter of this class is going to be
          passed to the `reader` function, joined with the directory where the
          file will be read from.

        The `reader` can also receive additional arguments, and keyword
        arguments. The `reader_args` and `reader_kwargs` parameters of this
        class can be used to provide those additional arguments.

        The `reader` function should return the data that will be used in the
        model.
    """

    name: str
    """
    Name of the data (input) file. The file extension should be included in the
    name.
    """
    loader: Callable[[str], Any]
    """
    Callable that reads (loads) the data from the file. This should be a function
    implemented by the user. There are convenience functions that you can use
    as a `loader` as well. The `loader` must receive, at the very minimum, the
    following arguments:

    - `file_path`: a `str` argument which is the location where this
       data will be read from. This includes the dir and name of the
       file. As such, the `name` parameter of this class is going to be
       passed to the `loader` function, joined with the directory where the
       file will be read from.

    The `loader` can also receive additional arguments, and keyword arguments.
    The `loader_args` and `loader_kwargs` parameters of this class can be used
    to provide those additional arguments.

    The `loader` function should return the data that will be used in the model.
    """
    loader_kwargs: dict[str, Any] | None = None
    """
    Optional keyword arguments to pass to the loader function. This can be used
    to customize the behavior of the loader.
    """
    loader_args: list[Any] | None = None
    """
    Optional positional arguments to pass to the loader function. This can be
    used to customize the behavior of the loader.
    """
    input_data_key: str | None = None
    """
    Use this parameter to set a custom key to represent your file.

    When using `ContentFormat.MULTI_FILE` as the `input_format` of the `Input`,
    the data from the file is loaded to the `.data` parameter of the `Input`.
    In that case, the type of `.data` is `dict[str, Any]`, where each key
    represents the file name (with extension) and the value is the data that is
    actually loaded from the file using the `loader` function. You can set a
    custom key to represent your file by using this attribute.
    """


def json_data_file(
    name: str,
    json_configurations: dict[str, Any] | None = None,
    input_data_key: str | None = None,
) -> DataFile:
    """
    This is a convenience function to create a `DataFile` that reads JSON data.

    You can import the `json_data_file` function directly from `nextmv`:

    ```python
    from nextmv import json_data_file
    ```

    Parameters
    ----------
    name : str
        Name of the data file. You don't need to include the `.json` extension.
    json_configurations : dict[str, Any], optional
        JSON-specific configurations for reading the data.
    input_data_key : str, optional
        A custom key to represent the data from this file.

        When using `ContentFormat.MULTI_FILE` as the `input_format` of the `Input`,
        the data from the file is loaded to the `.data` parameter of the `Input`.
        In that case, the type of `.data` is `dict[str, Any]`, where each key
        represents the file name (with extension) and the value is the data that is
        actually loaded from the file using the `loader` function. You can set a
        custom key to represent your file by using this attribute.

    Returns
    -------
    DataFile
        A `DataFile` instance that reads JSON data from a file with the given
        name.

    Examples
    --------
    >>> from nextmv import json_data_file
    >>> data_file = json_data_file("my_data")
    >>> data = data_file.read()
    >>> print(data)
    {
        "key": "value",
        "another_key": [1, 2, 3]
    }
    """

    if not name.endswith(".json"):
        name += ".json"

    json_configurations = json_configurations or {}

    def loader(file_path: str) -> dict[str, Any] | Any:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f, **json_configurations)

    return DataFile(
        name=name,
        loader=loader,
        input_data_key=input_data_key,
    )


def csv_data_file(
    name: str,
    csv_configurations: dict[str, Any] | None = None,
    input_data_key: str | None = None,
) -> DataFile:
    """
    This is a convenience function to create a `DataFile` that reads CSV data.

    You can import the `csv_data_file` function directly from `nextmv`:

    ```python
    from nextmv import csv_data_file
    ```

    Parameters
    ----------
    name : str
        Name of the data file. You don't need to include the `.csv` extension.
    csv_configurations : dict[str, Any], optional
        CSV-specific configurations for reading the data.
    input_data_key : str, optional
        A custom key to represent the data from this file.

        When using `ContentFormat.MULTI_FILE` as the `input_format` of the `Input`,
        the data from the file is loaded to the `.data` parameter of the `Input`.
        In that case, the type of `.data` is `dict[str, Any]`, where each key
        represents the file name (with extension) and the value is the data that is
        actually loaded from the file using the `loader` function. You can set a
        custom key to represent your file by using this attribute.

    Returns
    -------
    DataFile
        A `DataFile` instance that reads CSV data from a file with the given
        name.

    Examples
    --------
    >>> from nextmv import csv_data_file
    >>> data_file = csv_data_file("my_data")
    >>> data = data_file.read()
    >>> print(data)
    [
        {"column1": "value1", "column2": "value2"},
        {"column1": "value3", "column2": "value4"}
    ]
    """

    if not name.endswith(".csv"):
        name += ".csv"

    csv_configurations = csv_configurations or {}

    def loader(file_path: str) -> list[dict[str, Any]]:
        with open(file_path, encoding="utf-8") as f:
            return list(csv.DictReader(f, **csv_configurations))

    return DataFile(
        name=name,
        loader=loader,
        input_data_key=input_data_key,
    )


def text_data_file(name: str, input_data_key: str | None = None) -> DataFile:
    """
    This is a convenience function to create a `DataFile` that reads utf-8
    encoded text data.

    You can import the `text_data_file` function directly from `nextmv`:

    ```python
    from nextmv import text_data_file
    ```

    You must provide the extension as part of the `name` parameter.

    Parameters
    ----------
    name : str
        Name of the data file. The file extension must be provided in the name.
    input_data_key : str, optional
        A custom key to represent the data from this file.

        When using `ContentFormat.MULTI_FILE` as the `input_format` of the `Input`,
        the data from the file is loaded to the `.data` parameter of the `Input`.
        In that case, the type of `.data` is `dict[str, Any]`, where each key
        represents the file name (with extension) and the value is the data that is
        actually loaded from the file using the `loader` function. You can set a
        custom key to represent your file by using this attribute.

    Returns
    -------
    DataFile
        A `DataFile` instance that reads text data from a file with the given
        name.

    Examples
    --------
    >>> from nextmv import text_data_file
    >>> data_file = text_data_file("my_data")
    >>> data = data_file.read()
    >>> print(data)
    This is some text data.
    """

    def loader(file_path: str) -> str:
        with open(file_path, encoding="utf-8") as f:
            return f.read().rstrip("\n")

    return DataFile(
        name=name,
        loader=loader,
        input_data_key=input_data_key,
    )


@dataclass
class Input:
    """
    Input for a decision problem.

    You can import the `Input` class directly from `nextmv`:

    ```python
    from nextmv import Input
    ```

    The `data`'s type must match the `input_format`:

    - `ContentFormat.JSON`: the data is `Union[dict[str, Any], Any]`. This just
       means that the data must be JSON-deserializable, which includes dicts and
       lists.
    - `ContentFormat.MULTI_FILE`: the data is `dict[str, Any]`, where for each
       item, the key is the file name (with the extension) and the actual data
       from the file is the value. When working with multi-file, data is loaded
       from one or more files in a specific directory. Given that each file can
       be of different types (JSON, CSV, Excel, etc...), the data captured from
       each might vary. To reflect this, the data is loaded as a dict of items.
       You can have a custom key for the data, that is not the file name, if
       you use the `input_data_key` parameter of the `DataFile` class.

    Parameters
    ----------
    data : Union[dict[str, Any], Any, dict[str, Any]]
        The actual data.
    input_format : ContentFormat, optional
        Format of the input data. Default is `ContentFormat.JSON`.
    options : Options, optional
        Options that the input was created with.

    Raises
    ------
    ValueError
        If the data type doesn't match the expected type for the given format.
    ValueError
        If the `input_format` is not one of the supported formats.
    """

    data: dict[str, Any] | Any | str | list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | dict[str, Any]
    """
    The actual data.

    The data can be of various types, depending on the input format:

    - For `ContentFormat.JSON`: `Union[dict[str, Any], Any]`
    - For `ContentFormat.MULTI_FILE`: `dict[str, Any]`
    """

    input_format: ContentFormat | None = ContentFormat.JSON
    """
    Format of the input data.

    Default is `ContentFormat.JSON`.
    """

    options: Options | None = None
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

        # Support deprecated formats but warn the user about them.
        if type(self.input_format) is InputFormat:
            deprecated(name="InputFormat", reason="`InputFormat` is deprecated, use `ContentFormat` instead")

            if self.input_format in {InputFormat.TEXT, InputFormat.CSV_ARCHIVE}:
                deprecated(
                    name="InputFormat.TEXT/InputFormat.CSV_ARCHIVE",
                    reason="`text`/`csv-archive` format is no longer supported, use `ContentFormat.MULTI_FILE` instead",
                )
            elif self.input_format in {InputFormat.JSON, InputFormat.MULTI_FILE}:
                self.input_format = ContentFormat(self.input_format.value)
            else:
                raise ValueError(f"unsupported input_format: {self.input_format}")

        if self.input_format == ContentFormat.JSON:
            try:
                _ = serialize_json(self.data)
            except (TypeError, OverflowError) as e:
                raise ValueError(
                    f"Input has input_format `ContentFormat.JSON` and "
                    f"data is of type {type(self.data)}, which is not JSON serializable"
                ) from e

        elif (
            type(self.input_format) is InputFormat
            and self.input_format == InputFormat.TEXT
            and not isinstance(self.data, str)
        ):
            raise ValueError(
                f"unsupported Input.data type: {type(self.data)} with "
                "input_format InputFormat.TEXT, supported type is `str`"
            )

        elif (
            type(self.input_format) is InputFormat
            and self.input_format == InputFormat.CSV_ARCHIVE
            and not isinstance(self.data, dict)
        ):
            raise ValueError(
                f"unsupported Input.data type: {type(self.data)} with "
                "input_format InputFormat.CSV_ARCHIVE, supported type is `dict`"
            )

        elif self.input_format == ContentFormat.MULTI_FILE and not isinstance(self.data, dict):
            raise ValueError(
                f"unsupported Input.data type: {type(self.data)} with "
                "input_format `ContentFormat.MULTI_FILE`, supported type is `dict`"
            )

        # Capture a snapshot of the options that were used to create the class
        # so even if they are changed later, we have a record of the original.
        init_options = self.options
        new_options = copy.deepcopy(init_options)
        self.options = new_options

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the input to a dictionary.

        This method serializes the Input object to a dictionary format that can
        be easily converted to JSON or other serialization formats. When the
        `input_type` is set to `ContentFormat.MULTI_FILE`, it will not include
        the `data` field, as it is uncertain how data is deserialized from the file.

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
        >>> from nextmv.input import Input, ContentFormat
        >>> input_obj = Input(data={"key": "value"}, input_format=ContentFormat.JSON)
        >>> input_dict = input_obj.to_dict()
        >>> print(input_dict)
        {'data': {'key': 'value'}, 'input_format': 'json', 'options': None}
        """

        input_dict = {
            "input_format": self.input_format.value,
            "options": self.options.to_dict() if self.options is not None else None,
        }

        if self.input_format == ContentFormat.MULTI_FILE:
            return input_dict

        input_dict["data"] = self.data

        return input_dict


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
        input_format: ContentFormat = ContentFormat.JSON,
        options: Options | None = None,
        *args,
        **kwargs,
    ) -> Input:
        """
        Read the input data. This method should be implemented by
        subclasses.

        Parameters
        ----------
        input_format : ContentFormat, optional
            Format of the input data. Default is `ContentFormat.JSON`.
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
    a file, or a directory, where applicable. It supports JSON and multi-file
    formats.

    Call the `load` method to read the input data.

    Examples
    --------
    >>> from nextmv.input import LocalInputLoader, ContentFormat
    >>> loader = LocalInputLoader()
    >>> # Load JSON from stdin or file
    >>> input_obj = loader.load(input_format=ContentFormat.JSON, path="data.json")
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

    def _read_csv(path: str, csv_configurations: dict[str, Any] | None) -> list[dict[str, Any]]:
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

    def _read_json(path: str, _) -> dict[str, Any] | Any:
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
        ContentFormat.JSON: lambda _: json.load(sys.stdin),
        InputFormat.TEXT: lambda _: sys.stdin.read().rstrip("\n"),
    }
    """
    Dictionary of functions to read from standard input.

    Each key is a ContentFormat, and each value is a function that reads from
    standard input in that format.
    """

    # These callbacks were not implemented with lambda because we needed
    # multiple lines. By using `open`, we needed the `with` to be able to close
    # the file.
    FILE_READERS = {
        ContentFormat.JSON: _read_json,
        InputFormat.TEXT: _read_text,
        "CSV": _read_csv,
    }
    """
    Dictionary of functions to read from files.

    Each key is a ContentFormat, and each value is a function that reads from
    a file in that format.
    """

    def load(  # noqa: C901
        self,
        input_format: ContentFormat | None = None,
        options: Options | None = None,
        path: str | None = None,
        csv_configurations: dict[str, Any] | None = None,
        data_files: list[DataFile] | None = None,
        manifest: Manifest | None = None,
    ) -> Input:
        """
        Load the input data. For `ContentFormat.JSON`, the data can be streamed
        from stdin or read from a file. When the `path` argument is provided
        (and valid), the input data is read from the file specified by `path`,
        otherwise, it is streamed from stdin.

        The `Input` that is returned contains the `data` attribute. This data
        can be of different types, depending on the provided `input_format`:

        - `ContentFormat.JSON`: the data is a `dict[str, Any]`.
        - `ContentFormat.MULTI_FILE`: the data is a `dict[str, Any]`, where
          each key is the file name (with extension) and the value is the data
          read from the file. The data can be of any type, depending on the
          file type and the reader function provided in the `DataFile`
          instances.

        Parameters
        ----------
        input_format : ContentFormat, optional
            Format of the input data. Default is `ContentFormat.JSON`.
        options : Options, optional
            Options for loading the input data.
        path : str, optional
            Path to the input data.
        csv_configurations : dict[str, Any], optional
            Configurations for loading CSV files. The default `DictReader` is
            used when loading a CSV file, so you have the option to pass in a
            dictionary with custom kwargs for the `DictReader`.
        data_files : list[DataFile], optional
            List of `DataFile` instances to read from. This is used when the
            `input_format` is set to `ContentFormat.MULTI_FILE`. Each
            `DataFile` instance should have a `name` (the file name with
            extension) and a `loader` function that reads the data from the
            file. The `loader` function should accept the file path as its
            first argument and return the data read from the file. The `loader`
            can also accept additional positional and keyword arguments, which
            can be provided through the `loader_args` and `loader_kwargs`
            attributes of the `DataFile` instance.
        manifest : Manifest, optional
            The manifest to use for loading the input data. If not provided,
            the method will look for an `app.yaml` file in the current working
            directory and use it as the manifest if it exists. The manifest can
            provide default values for `input_format`, `path`, and `options`,
            which can be overridden by the corresponding arguments if they are
            provided directly to the method.

        Returns
        -------
        Input
            The input data.

        Raises
        ------
        ValueError
            If the path is not a valid directory.
        """

        manifest = self.__resolve_manifest(manifest)
        content_format = self.__resolve_content_format(input_format, manifest)
        path = self.__resolve_path(content_format=content_format, path=path, manifest=manifest)

        data: Any = None
        if csv_configurations is None:
            csv_configurations = {}

        if content_format == ContentFormat.JSON:
            data = self.__load_utf8_encoded(
                path=path,
                input_format=content_format,
                csv_configurations=csv_configurations,
            )
        elif content_format == ContentFormat.MULTI_FILE:
            if data_files is None:
                raise ValueError("`data_files` must be provided when input_format is `ContentFormat.MULTI_FILE`")

            if not isinstance(data_files, list):
                raise ValueError("`data_files` must be a list of `DataFile` instances")

            data = self.__load_multi_file(data_files=data_files, path=path)
        elif type(content_format) is InputFormat and content_format == InputFormat.TEXT:
            data = self.__load_utf8_encoded(
                path=path,
                input_format=content_format,
                csv_configurations=csv_configurations,
            )
        elif type(content_format) is InputFormat and content_format == InputFormat.CSV_ARCHIVE:
            data = self.__load_archive(path=path, csv_configurations=csv_configurations)

        options = self.__resolve_options(options, manifest)

        return Input(data=data, input_format=content_format, options=options)

    def __load_utf8_encoded(
        self,
        csv_configurations: dict[str, Any] | None,
        path: str | None = None,
        input_format: ContentFormat | str | None = ContentFormat.JSON,
        use_file_reader: bool = False,
    ) -> dict[str, Any] | str | list[dict[str, Any]]:
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
        input_format : ContentFormat, optional
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

    def __load_archive(
        self,
        csv_configurations: dict[str, Any] | None,
        path: str | None = None,
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
                data[stripped] = self.__load_utf8_encoded(
                    path=os.path.join(dir_path, file),
                    input_format="CSV",
                    use_file_reader=True,
                    csv_configurations=csv_configurations,
                )

        return data

    def __load_multi_file(
        self,
        data_files: list[DataFile],
        path: str | None = None,
    ) -> dict[str, Any]:
        """
        Load multiple files from a directory.

        This internal method loads all supported files from a specified
        directory, organizing them into a dictionary where each key is the
        filename and each value is the parsed file content. Supports CSV files
        (parsed as list of dictionaries), JSON files (parsed as JSON objects),
        and any other utf-8 encoded text files (loaded as plain text strings).
        It also supports Excel files, loading them as DataFrames.

        Parameters
        ----------
        data_files : list[DataFile]
            List of `DataFile` instances to read from.
        path : str, optional
            Path to the directory containing files. If None or empty,
            uses "./inputs" as the default directory.

        Returns
        -------
        dict[str, Any]
            Dictionary mapping filenames to file contents. CSV files are loaded
            as lists of dictionaries, JSON files as parsed JSON objects, and
            other utf-8 text files as strings. Excel files are loaded as
            DataFrames.

        Raises
        ------
        ValueError
            If the path is not a directory or the default directory doesn't exist.
        """

        dir_path = INPUTS_KEY
        if path is not None and path != "":
            if not os.path.isdir(path):
                raise ValueError(f"path {path} is not a directory")

            dir_path = path

        if not os.path.isdir(dir_path):
            raise ValueError(f'expected input directoy "{dir_path}" to exist as a default location')

        data = {}

        for data_file in data_files:
            name = data_file.name
            file_path = os.path.join(dir_path, name)

            if data_file.loader_args is None:
                data_file.loader_args = []
            if data_file.loader_kwargs is None:
                data_file.loader_kwargs = {}

            d = data_file.loader(
                file_path,
                *data_file.loader_args,
                **data_file.loader_kwargs,
            )

            key = name
            if data_file.input_data_key is not None:
                key = data_file.input_data_key

            if data.get(key) is not None:
                raise ValueError(f"Duplicate input data key found: {key}")

            data[key] = d

        return data

    def __resolve_manifest(self, manifest: Manifest | None = None) -> Manifest | None:
        if manifest is not None:
            return manifest

        if os.path.exists(MANIFEST_FILE_NAME):
            return Manifest.from_yaml()

        return None

    def __resolve_content_format(
        self,
        input_format: ContentFormat | None = None,
        manifest: Manifest | None = None,
    ) -> ContentFormat:
        content_format = None
        if input_format is not None:
            content_format = input_format
        elif manifest is not None:
            content_format = manifest.configuration.content.format
        else:
            content_format = ContentFormat.JSON

        if type(content_format) is ContentFormat:
            return content_format

        deprecated(
            name="InputFormat",
            reason="using `InputFormat` as the type for `input_format` is deprecated, use `ContentFormat` instead",
        )
        if content_format in {InputFormat.TEXT, InputFormat.CSV_ARCHIVE}:
            deprecated(
                name="InputFormat.TEXT/InputFormat.CSV_ARCHIVE",
                reason="`text`/`csv-archive` format is no longer supported, use `ContentFormat.MULTI_FILE` instead",
            )
        elif content_format in {InputFormat.JSON, InputFormat.MULTI_FILE}:
            content_format = ContentFormat(content_format.value)
        else:
            raise ValueError(f"unsupported input_format: {content_format}")

        return content_format

    def __resolve_path(
        self,
        content_format: ContentFormat,
        path: str | None = None,
        manifest: Manifest | None = None,
    ) -> str:
        if path is not None:
            return path

        if content_format in {ContentFormat.JSON, InputFormat.TEXT}:
            return ""

        if content_format == InputFormat.CSV_ARCHIVE:
            return "input"

        # At this point, we should be using multi-file, but we check it and
        # raise an exception if it's not the case, just to be safe.
        if content_format != ContentFormat.MULTI_FILE:
            raise ValueError(f"unexpected content format: {content_format}")

        if manifest is not None:
            return manifest.configuration.content.multi_file.input.path

        return "inputs"

    def __resolve_options(options: Options | None = None, manifest: Manifest | None = None) -> Options:
        if options is not None:
            return options

        if manifest is not None:
            return manifest.extract_options()

        return None


_LOCAL_INPUT_LOADER = LocalInputLoader()
"""Default instance of LocalInputLoader used by the load function."""


def load(
    input_format: ContentFormat | None = ContentFormat.JSON,
    options: Options | None = None,
    path: str | None = None,
    csv_configurations: dict[str, Any] | None = None,
    loader: InputLoader | None = _LOCAL_INPUT_LOADER,
    data_files: list[DataFile] | None = None,
    manifest: Manifest | None = None,
) -> Input:
    """
    Load input data using the specified loader.

    You can import the `load` function directly from `nextmv`:

    ```python
    from nextmv import load
    ```

    This is a convenience function for loading an `Input` object. By default,
    it uses the `LocalInputLoader` to load data from local sources. When
    working with the local filesystem, please consider the following:

    There are two main ways in which you can use this function:

    - Having an `app.yaml` (app manifest) present in the current working
      directory (recommended). In this case, you just use the function as
      `load()`, and it will automatically resolve the `input_format`, `path`,
      and `options` from the manifest. Alternatively, you can also provide the
      manifest explicitly as the `manifest` argument.
    - Providing the `input_format`, `path`, and `options` arguments directly to
      the function.

    When both a manifest can be used (via the current working directory or the
    `manifest` argument) and the `input_format`, `path`, or `options` arguments
    are provided directly, the function will prioritize using the provided
    arguments over the manifest values. This allows you to override the
    manifest values when needed, while still having the convenience of using
    the manifest for default configurations.

    The input data can be in various formats and can be loaded from different
    sources depending on the loader:

    - `ContentFormat.JSON`: the data is a `dict[str, Any]`
    - `ContentFormat.MULTI_FILE`: the data is a `dict[str, Any]`, where each
      key is the file name (with extension) and the value is the data read from
      the file. This is used for loading multiple files in a single input,
      where each file can be of different types (JSON, CSV, Excel, etc.). The
      data is loaded as a dict of items, where each item corresponds to a file
      and its content.

    When working with `input_format` as `ContentFormat.MULTI_FILE`, the
    `data_files` argument must be provided. This argument is a list of
    `DataFile` instances, each representing a file to be read. Each `DataFile`
    instance should have a `name` (the file name with extension) and a `loader`
    function that reads the data from the file. The `loader` function should
    accept the file path as its first argument and return the data read from
    the file. The `loader` can also accept additional positional and keyword
    arguments, which can be provided through the `loader_args` and
    `loader_kwargs` attributes of the `DataFile` instance.

    There are convenience functions that can be used to create `DataFile`
    classes, such as:

    - `json_data_file`: Creates a `DataFile` that reads JSON data.
    - `csv_data_file`: Creates a `DataFile` that reads CSV data.
    - `text_data_file`: Creates a `DataFile` that reads utf-8 encoded text
      data.

    When working with data in other formats, such as Excel files, you are
    encouraged to create your own `DataFile` objects with your own
    implementation of the `loader` function. This allows you to read data
    from files in a way that suits your needs, while still adhering to the
    `DataFile` interface.

    Parameters
    ----------
    input_format : ContentFormat, optional
        Format of the input data. Default is `ContentFormat.JSON`.
    options : Options, optional
        Options for loading the input data.
    path : str, optional
        Path to the input data. For file-based loaders:
        - If provided, reads from the specified file or directory
        - If None, reads from stdin (for JSON) or uses a default directory
          (for multi-file)
    csv_configurations : dict[str, Any], optional
        Configurations for loading CSV files. Custom kwargs for
        Python's `csv.DictReader`.
    loader : InputLoader, optional
        The loader to use for loading the input data.
        Default is an instance of `LocalInputLoader`.
    data_files : list[DataFile], optional
        List of `DataFile` instances to read from. This is used when the
        `input_format` is set to `ContentFormat.MULTI_FILE`. Each `DataFile`
        instance should have a `name` (the file name with extension) and a
        `loader` function that reads the data from the file. The `loader`
        function should accept the file path as its first argument and return
        the data read from the file. The `loader` can also accept additional
        positional and keyword arguments, which can be provided through the
        `loader_args` and `loader_kwargs` attributes of the `DataFile`
        instance.

        There are convenience functions that can be used to create `DataFile`
        classes, such as `json_data_file`, `csv_data_file`, and
        `text_data_file`. When working with data in other formats, such as
        Excel files, you are encouraged to create your own `DataFile` objects
        with your own implementation of the `loader` function. This allows you
        to read data from files in a way that suits your needs, while still
        adhering to the `DataFile` interface.
    manifest : Manifest, optional
        The manifest to use for loading the input data. If not provided, the
        function will look for an `app.yaml` file in the current working
        directory and use it as the manifest if it exists. The manifest can
        provide default values for `input_format`, `path`, and `options`, which
        can be overridden by the corresponding arguments if they are provided
        directly to the function.

    Returns
    -------
    Input
        The loaded input data in an Input object.

    Raises
    ------
    ValueError
        If one of many validations fails.

    Examples
    --------
    >>> import nextmv
    >>> input = nextmv.load()
    """

    return loader.load(
        input_format,
        options,
        path,
        csv_configurations,
        data_files,
        manifest,
    )
