"""
Module for declarations related to upload and download URLs in Nextmv Cloud.

Classes
-------
DownloadURL
    Represents a download URL for fetching content from Nextmv Cloud.
UploadURL
    Represents an upload URL for sending content to Nextmv Cloud.
"""

from nextmv.base_model import BaseModel


class DownloadURL(BaseModel):
    """
    Result of getting a download URL.

    You can import the `DownloadURL` class directly from `cloud`:

    ```python
    from nextmv.cloud import DownloadURL
    ```

    This class represents a download URL that can be used to fetch content
    from Nextmv Cloud, typically used for downloading large run results.

    Attributes
    ----------
    url : str
        URL to use for downloading the file.

    Examples
    --------
    >>> download_url = DownloadURL(url="https://example.com/download")
    >>> response = requests.get(download_url.url)
    """

    url: str
    """URL to use for downloading the file."""


class UploadURL(BaseModel):
    """
    Result of getting an upload URL.

    You can import the `UploadURL` class directly from `cloud`:

    ```python
    from nextmv.cloud import UploadURL
    ```

    This class represents an upload URL that can be used to send data to
    Nextmv Cloud, typically used for uploading large inputs for runs.

    Attributes
    ----------
    upload_id : str
        ID of the upload, used to reference the uploaded content.
    upload_url : str
        URL to use for uploading the file.

    Examples
    --------
    >>> upload_url = UploadURL(upload_id="123", upload_url="https://example.com/upload")
    >>> with open("large_input.json", "rb") as f:
    ...     requests.put(upload_url.upload_url, data=f)
    """

    upload_id: str
    """ID of the upload."""
    upload_url: str
    """URL to use for uploading the file."""
