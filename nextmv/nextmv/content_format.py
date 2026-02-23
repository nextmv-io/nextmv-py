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
