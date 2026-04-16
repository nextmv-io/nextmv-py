"""
Module for handling content formats of an app's input and output.

Classes
-------
ContentFormat
    Format of the content of an app's input and output. This is used to specify
    how the app should read and write data.
"""

from enum import Enum


class ContentFormat(str, Enum):
    """
    Format of the content of an app's input and output. This is used to specify
    how the app should read and write data.

    You can import the `ContentFormat` class directly from `nextmv`:

    ```python
    from nextmv import ContentFormat
    ```

    Attributes
    ----------
    JSON : str
        JSON format, utf-8 encoded.
    MULTI_FILE : str
        Multi-file format, used for loading multiple files in a single input.
    """

    JSON = "json"
    """
    JSON format, utf-8 encoded. JSON is read from stdin and written to stdout.
    """
    MULTI_FILE = "multi-file"
    """
    Multi-file format. Read/write one or more files from/to disk (a directory).
    """

    @property
    def description(self) -> str:
        """
        A human-friendly description of the content format.
        """

        descriptions = {
            ContentFormat.JSON: "JSON format, utf-8 encoded. JSON is read from stdin and written to stdout.",
            ContentFormat.MULTI_FILE: "Multi-file format. Read/write one or more files from/to disk (a directory).",
        }

        return descriptions[self]


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
