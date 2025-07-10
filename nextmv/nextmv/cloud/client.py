"""Module with the client class.

This module provides the `Client` class for interacting with the Nextmv Cloud
API, and a helper function `get_size` to determine the size of objects.

Classes
-------
Client
    Client that interacts directly with the Nextmv Cloud API.

Functions
---------
get_size(obj)
    Finds the size of an object in bytes.
"""

import os
from dataclasses import dataclass, field
from typing import IO, Any, Optional, Union
from urllib.parse import urljoin

import requests
import yaml
from requests.adapters import HTTPAdapter, Retry

from nextmv._serialization import deflated_serialize_json

_MAX_LAMBDA_PAYLOAD_SIZE: int = 500 * 1024 * 1024
"""int: Maximum size of the payload handled by the Nextmv Cloud API.

This constant defines the upper limit for the size of data payloads that can
be sent to the Nextmv Cloud API, specifically for lambda functions. It is set
to 500 MiB.
"""


@dataclass
class Client:
    """
    Client that interacts directly with the Nextmv Cloud API.

    You can import the `Client` class directly from `cloud`:

    ```python
    from nextmv.cloud import Client
    ```

    The API key will be searched, in order of precedence, in:

    1. The `api_key` argument in the constructor.
    2. The `NEXTMV_API_KEY` environment variable.
    3. The `~/.nextmv/config.yaml` file used by the Nextmv CLI.

    Parameters
    ----------
    api_key : str, optional
        API key to use for authenticating with the Nextmv Cloud API. If not
        provided, the client will look for the `NEXTMV_API_KEY` environment
        variable.
    allowed_methods : list[str]
        Allowed HTTP methods to use for retries in requests to the Nextmv
        Cloud API. Defaults to ``["GET", "POST", "PUT", "DELETE"]``.
    backoff_factor : float
        Exponential backoff factor to use for requests to the Nextmv Cloud
        API. Defaults to ``1``.
    backoff_jitter : float
        Jitter to use for requests to the Nextmv Cloud API when backing off.
        Defaults to ``0.1``.
    backoff_max : float
        Maximum backoff time to use for requests to the Nextmv Cloud API, in
        seconds. Defaults to ``60``.
    configuration_file : str
        Path to the configuration file used by the Nextmv CLI. Defaults to
        ``"~/.nextmv/config.yaml"``.
    headers : dict[str, str], optional
        Headers to use for requests to the Nextmv Cloud API. Automatically
        set up with the API key.
    max_retries : int
        Maximum number of retries to use for requests to the Nextmv Cloud
        API. Defaults to ``10``.
    status_forcelist : list[int]
        Status codes to retry for requests to the Nextmv Cloud API. Defaults
        to ``[429]``.
    timeout : float
        Timeout to use for requests to the Nextmv Cloud API, in seconds.
        Defaults to ``20``.
    url : str
        URL of the Nextmv Cloud API. Defaults to
        ``"https://api.cloud.nextmv.io"``.
    console_url : str
        URL of the Nextmv Cloud console. Defaults to
        ``"https://cloud.nextmv.io"``.

    Examples
    --------
    >>> client = Client(api_key="YOUR_API_KEY")
    >>> response = client.request(method="GET", endpoint="/v1/applications")
    >>> print(response.json())
    """

    api_key: Optional[str] = None
    """API key to use for authenticating with the Nextmv Cloud API. If not
    provided, the client will look for the NEXTMV_API_KEY environment
    variable."""
    allowed_methods: list[str] = field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE"],
    )
    """Allowed HTTP methods to use for retries in requests to the Nextmv Cloud
    API."""
    backoff_factor: float = 1
    """Exponential backoff factor to use for requests to the Nextmv Cloud
    API."""
    backoff_jitter: float = 0.1
    """Jitter to use for requests to the Nextmv Cloud API when backing off."""
    backoff_max: float = 60
    """Maximum backoff time to use for requests to the Nextmv Cloud API, in
    seconds."""
    configuration_file: str = "~/.nextmv/config.yaml"
    """Path to the configuration file used by the Nextmv CLI."""
    headers: Optional[dict[str, str]] = None
    """Headers to use for requests to the Nextmv Cloud API."""
    max_retries: int = 10
    """Maximum number of retries to use for requests to the Nextmv Cloud
    API."""
    status_forcelist: list[int] = field(
        default_factory=lambda: [429],
    )
    """Status codes to retry for requests to the Nextmv Cloud API."""
    timeout: float = 20
    """Timeout to use for requests to the Nextmv Cloud API."""
    url: str = "https://api.cloud.nextmv.io"
    """URL of the Nextmv Cloud API."""
    console_url: str = "https://cloud.nextmv.io"
    """URL of the Nextmv Cloud console."""

    def __post_init__(self):
        """
        Initializes the client after dataclass construction.

        This method handles the logic for API key retrieval and header
        setup. It checks for the API key in the constructor, environment
        variables, and the configuration file, in that order.

        Raises
        ------
        ValueError
            If `api_key` is an empty string.
            If no API key is found in any of the lookup locations.
            If a profile is specified via `NEXTMV_PROFILE` but not found in
            the configuration file.
            If `apikey` is not found in the configuration file for the
            selected profile.
        """

        if self.api_key is not None and self.api_key != "":
            self._set_headers_api_key(self.api_key)
            return

        if self.api_key == "":
            raise ValueError("api_key cannot be empty")

        api_key_env = os.getenv("NEXTMV_API_KEY")
        if api_key_env is not None:
            self.api_key = api_key_env
            self._set_headers_api_key(api_key_env)
            return

        config_path = os.path.expanduser(self.configuration_file)
        if not os.path.exists(config_path):
            raise ValueError(
                f"no API key set in constructor or NEXTMV_API_KEY env var, and {self.configuration_file} does not exist"
            )

        with open(config_path) as f:
            config = yaml.safe_load(f)

        profile = os.getenv("NEXTMV_PROFILE")
        parent = config
        if profile is not None:
            parent = config.get(profile)
            if parent is None:
                raise ValueError(f"profile {profile} set via NEXTMV_PROFILE but not found in {self.configuration_file}")

        api_key = parent.get("apikey")
        if api_key is None:
            raise ValueError(f"no apiKey found in {self.configuration_file}")
        self.api_key = api_key

        endpoint = parent.get("endpoint")
        if endpoint is not None:
            self.url = f"https://{endpoint}"

        self._set_headers_api_key(api_key)

    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Any] = None,
        headers: Optional[dict[str, str]] = None,
        payload: Optional[dict[str, Any]] = None,
        query_params: Optional[dict[str, Any]] = None,
        json_configurations: Optional[dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Makes a request to the Nextmv Cloud API.

        Parameters
        ----------
        method : str
            HTTP method to use (e.g., "GET", "POST").
        endpoint : str
            API endpoint to send the request to (e.g., "/v1/applications").
        data : Any, optional
            Data to send in the request body. Typically used for form data.
            Cannot be used if `payload` is also provided.
        headers : dict[str, str], optional
            Additional headers to send with the request. These will override
            the default client headers if keys conflict.
        payload : dict[str, Any], optional
            JSON payload to send with the request. Prefer using this over
            `data` for JSON requests. Cannot be used if `data` is also
            provided.
        query_params : dict[str, Any], optional
            Query parameters to append to the request URL.
        json_configurations : dict[str, Any], optional
            Additional configurations for JSON serialization. This allows
            customization of the Python `json.dumps` function, such as
            specifying `indent` for pretty printing or `default` for custom
            serialization functions.

        Returns
        -------
        requests.Response
            The response object from the Nextmv Cloud API.

        Raises
        ------
        requests.HTTPError
            If the response status code is not in the 2xx range.
        ValueError
            If both `data` and `payload` are provided.
            If the `payload` size exceeds `_MAX_LAMBDA_PAYLOAD_SIZE`.
            If the `data` size exceeds `_MAX_LAMBDA_PAYLOAD_SIZE`.

        Examples
        --------
        >>> client = Client(api_key="YOUR_API_KEY")
        >>> # Get a list of applications
        >>> response = client.request(method="GET", endpoint="/v1/applications")
        >>> print(response.status_code)
        200
        >>> # Create a new run
        >>> run_payload = {
        ...     "applicationId": "app_id",
        ...     "instanceId": "instance_id",
        ...     "input": {"value": 10}
        ... }
        >>> response = client.request(
        ...     method="POST",
        ...     endpoint="/v1/runs",
        ...     payload=run_payload
        ... )
        >>> print(response.json()["id"])
        run_xxxxxxxxxxxx
        """

        if payload is not None and data is not None:
            raise ValueError("cannot use both data and payload")

        if (
            payload is not None
            and get_size(payload, json_configurations=json_configurations) > _MAX_LAMBDA_PAYLOAD_SIZE
        ):
            raise ValueError(
                f"payload size of {get_size(payload, json_configurations=json_configurations)} bytes exceeds "
                + f"the maximum allowed size of {_MAX_LAMBDA_PAYLOAD_SIZE} bytes"
            )

        if data is not None and get_size(data, json_configurations=json_configurations) > _MAX_LAMBDA_PAYLOAD_SIZE:
            raise ValueError(
                f"data size of {get_size(data, json_configurations=json_configurations)} bytes exceeds "
                + f"the maximum allowed size of {_MAX_LAMBDA_PAYLOAD_SIZE} bytes"
            )

        session = requests.Session()
        retries = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            backoff_jitter=self.backoff_jitter,
            backoff_max=self.backoff_max,
            status_forcelist=self.status_forcelist,
            allowed_methods=self.allowed_methods,
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)

        kwargs: dict[str, Any] = {
            "url": urljoin(self.url, endpoint),
            "timeout": self.timeout,
        }
        kwargs["headers"] = headers if headers is not None else self.headers
        if data is not None:
            kwargs["data"] = data
        if payload is not None:
            if isinstance(payload, (dict, list)):
                data = deflated_serialize_json(payload, json_configurations=json_configurations)
                kwargs["data"] = data
            else:
                raise ValueError("payload must be a dictionary or a list")
        if query_params is not None:
            kwargs["params"] = query_params

        response = session.request(method=method, **kwargs)

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"request to {endpoint} failed with status code {response.status_code} and message: {response.text}"
            ) from e

        return response

    def upload_to_presigned_url(
        self,
        data: Optional[Union[dict[str, Any], str]],
        url: str,
        json_configurations: Optional[dict[str, Any]] = None,
        tar_file: Optional[str] = None,
    ) -> None:
        """
        Uploads data to a presigned URL.

        This method is typically used for uploading large input or output files
        directly to cloud storage, bypassing the main API for efficiency.

        Parameters
        ----------
        data : Union[dict[str, Any], str], optional
            The data to upload. If a dictionary is provided, it will be
            JSON-serialized. If a string is provided, it will be uploaded
            as is.
        url : str
            The presigned URL to which the data will be uploaded.
        json_configurations : dict[str, Any], optional
            Additional configurations for JSON serialization. This allows
            customization of the Python `json.dumps` function, such as
            specifying `indent` for pretty printing or `default` for custom
            serialization functions.
        tar_file : str, optional
            If provided, this will be used to upload a tar file instead of
            a JSON string or dictionary. This is useful for uploading large
            files that are already packaged as a tarball. If this is provided,
            `data` is expected to be `None`.

        Raises
        ------
        ValueError
            If `data` is not a dictionary or a string.
        requests.HTTPError
            If the upload request fails.

        Examples
        --------
        Assume `presigned_upload_url` is obtained from a previous API call.
        >>> client = Client(api_key="YOUR_API_KEY")
        >>> input_data = {"value": 42, "items": [1, 2, 3]}
        >>> client.upload_to_presigned_url(data=input_data, url="PRE_SIGNED_URL") # doctest: +SKIP
        """

        upload_data: Optional[str] = None
        if data is not None:
            if isinstance(data, dict):
                upload_data = deflated_serialize_json(data, json_configurations=json_configurations)
            elif isinstance(data, str):
                upload_data = data
            else:
                raise ValueError("data must be a dictionary or a string")

        session = requests.Session()
        retries = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            backoff_jitter=self.backoff_jitter,
            backoff_max=self.backoff_max,
            status_forcelist=self.status_forcelist,
            allowed_methods=self.allowed_methods,
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)

        kwargs: dict[str, Any] = {
            "url": url,
            "timeout": self.timeout,
        }

        if upload_data is not None:
            kwargs["data"] = upload_data
        elif tar_file is not None and tar_file != "":
            if not os.path.exists(tar_file):
                raise ValueError(f"tar_file {tar_file} does not exist")
            kwargs["data"] = open(tar_file, "rb")
        else:
            raise ValueError("either data or tar_file must be provided")

        response = session.put(**kwargs)

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"upload to presigned URL {url} failed with "
                f"status code {response.status_code} and message: {response.text}"
            ) from e

    def _set_headers_api_key(self, api_key: str) -> None:
        """
        Sets the Authorization and Content-Type headers.

        This is an internal method used to configure the necessary headers
        for API authentication and content type specification.

        Parameters
        ----------
        api_key : str
            The API key to be included in the Authorization header.
        """

        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }


def get_size(obj: Union[dict[str, Any], IO[bytes], str], json_configurations: Optional[dict[str, Any]] = None) -> int:
    """
    Finds the size of an object in bytes.

    This function supports dictionaries (JSON-serialized), file-like objects
    (by reading their content), and strings.

    Parameters
    ----------
    obj : dict[str, Any] or IO[bytes] or str
        The object whose size is to be determined.
        - If a dict, it's converted to a JSON string.
        - If a file-like object (e.g., opened file), its size is read.
        - If a string, its UTF-8 encoded byte length is calculated.
    json_configurations : dict[str, Any], optional
        Additional configurations for JSON serialization. This allows
        customization of the Python `json.dumps` function, such as specifying
        `indent` for pretty printing or `default` for custom serialization
        functions.

    Returns
    -------
    int
        The size of the object in bytes.

    Raises
    ------
    TypeError
        If the object type is not supported (i.e., not a dict,
        file-like object, or string).

    Examples
    --------
    >>> my_dict = {"key": "value", "number": 123}
    >>> get_size(my_dict)
    30
    >>> import io
    >>> my_string = "Hello, Nextmv!"
    >>> string_io = io.StringIO(my_string)
    >>> # To get size of underlying buffer for StringIO, we need to encode
    >>> string_bytes_io = io.BytesIO(my_string.encode('utf-8'))
    >>> get_size(string_bytes_io)
    14
    >>> get_size("Hello, Nextmv!")
    14
    """

    if isinstance(obj, dict):
        obj_str = deflated_serialize_json(obj, json_configurations=json_configurations)
        return len(obj_str.encode("utf-8"))

    elif hasattr(obj, "read"):
        obj.seek(0, 2)  # Move the cursor to the end of the file
        size = obj.tell()
        obj.seek(0)  # Reset the cursor to the beginning of the file
        return size

    elif isinstance(obj, str):
        return len(obj.encode("utf-8"))

    else:
        raise TypeError("Unsupported type. Only dictionaries, file objects (IO[bytes]), and strings are supported.")
