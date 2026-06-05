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
from collections.abc import Generator
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Any
from urllib.parse import urljoin

import requests
import yaml
from requests.adapters import HTTPAdapter, Retry

from nextmv import deprecated
from nextmv._serialization import deflated_serialize_json

_MAX_LAMBDA_PAYLOAD_SIZE: int = 500 * 1024 * 1024
"""int: Maximum size of the payload handled by the Nextmv Cloud API.

This constant defines the upper limit for the size of data payloads that can
be sent to the Nextmv Cloud API, specifically for lambda functions. It is set
to 500 MiB.
"""

# Some useful constants.
_CONFIG_DIR = Path.home() / ".nextmv"
_CONFIG_FILE = _CONFIG_DIR / "config.yaml"
_API_KEY_KEY = "apikey"
_ENDPOINT_KEY = "endpoint"


@dataclass
class Client:
    """
    Client that interacts directly with the Nextmv Cloud API.

    You can import the `Client` class directly from `cloud`:

    ```python
    from nextmv.cloud import Client
    ```

    The `Client` class is configured mainly with an API key and an endpoint
    URL. There are multiple ways to provide these configurations, and the
    client will check for them in the following order of precedence:

    1. The `api_key` and `url` attributes set directly on the client
       instance.
    2. The `NEXTMV_API_KEY` and `NEXTMV_ENDPOINT` environment variables.
    3. If the `NEXTMV_PROFILE` environment variable is set, it is used to
       look up the API key and endpoint for that profile in the configuration
       file (`~/.nextmv/config.yaml`).
    4. If the `profile` attribute is set on the client, it is used to look
       up the API key and endpoint for that profile in the configuration file.
    5. If the `profile` attribute is not set, the default profile is used to
       look up the API key and endpoint in the configuration file.
    6. If all of the above lookups fail, an exception is raised indicating that
       the API key is missing, and the endpoint falls back to the hardcoded
       default URL of `https://api.cloud.nextmv.io`.

    Attributes
    ----------
    api_key : str, optional
        API key to use for authenticating with the Nextmv Cloud API. Resolved
        from the constructor argument, the `NEXTMV_API_KEY` environment
        variable, or the configuration file (in that order). Raises
        `ValueError` if no key is found anywhere.
    allowed_methods : list[str]
        HTTP methods for which failed requests are eligible for retry.
        Defaults to `["GET", "POST", "PUT", "DELETE"]`. Adjust this list to
        restrict retries to idempotent methods only (e.g., `["GET"]`).
    backoff_factor : float
        Multiplier applied between retry attempts using exponential backoff.
        A value of `1` means the successive delays will be 1s, 2s, 4s,
        … (before jitter). Defaults to `1`.
    backoff_jitter : float
        Random jitter (in seconds) added to each backoff delay to avoid
        thundering-herd problems. Defaults to `0.1`.
    backoff_max : float
        Upper bound on the backoff delay, in seconds. No single wait between
        retries will exceed this value. Defaults to `60`.
    configuration_file : str
        **Deprecated** — no longer used. Kept for backwards compatibility.
        Previously held the path to the Nextmv CLI configuration file.
    headers : dict[str, str], optional
        HTTP headers sent with every request. Automatically populated during
        `__post_init__` with `Authorization: Bearer <api_key>` and
        `Content-Type: application/json`. Override by passing a custom dict
        to individual :meth:`request` calls via the `headers` parameter.
    max_retries : int
        Total number of retry attempts allowed per request. Defaults to
        `10`. Set to `0` to disable retries.
    profile : str, optional
        Named profile to use when looking up credentials in the configuration
        file (`~/.nextmv/config.yaml`). Overridden by the
        `NEXTMV_PROFILE` environment variable when that variable is set.
    status_forcelist : list[int]
        HTTP status codes that trigger an automatic retry. Defaults to
        `[429]` (Too Many Requests). Add codes such as `500`, `502`,
        or `503` to also retry on server errors.
    timeout : float
        Maximum number of seconds to wait for the server to send a response.
        Defaults to `20`. Increase for large payloads or slow connections.
    url : str, optional
        Base URL of the Nextmv Cloud API. Resolved from the constructor
        argument, the `NEXTMV_ENDPOINT` environment variable, or the
        configuration file (in that order). Defaults to
        `"https://api.cloud.nextmv.io"` when not set anywhere.
    console_url : str
        URL of the Nextmv Cloud web console. Defaults to
        `"https://cloud.nextmv.io"`. Not used for API requests; provided
        for convenience when constructing deep-links into the console.

    Examples
    --------
    Authenticate with an explicit API key:

    >>> client = Client(api_key="YOUR_API_KEY")
    >>> response = client.request(method="GET", endpoint="/v1/applications")
    >>> print(response.status_code)
    200

    Authenticate via the `NEXTMV_API_KEY` environment variable (the
    `api_key` argument can be omitted):

    >>> import os
    >>> os.environ["NEXTMV_API_KEY"] = "YOUR_API_KEY"
    >>> client = Client()

    Use a named profile from the configuration file:

    >>> client = Client(profile="staging")

    Override the profile with an environment variable:

    >>> os.environ["NEXTMV_PROFILE"] = "production"
    >>> client = Client()  # uses the "production" profile

    Customise retry and timeout behaviour:

    >>> client = Client(
    ...     api_key="YOUR_API_KEY",
    ...     max_retries=3,
    ...     backoff_factor=0.5,
    ...     backoff_jitter=0.05,
    ...     backoff_max=30,
    ...     status_forcelist=[429, 500, 502, 503],
    ...     timeout=60,
    ... )

    Point the client at a self-hosted or staging API endpoint:

    >>> client = Client(
    ...     api_key="YOUR_API_KEY",
    ...     url="https://staging.api.example.com",
    ... )
    """

    api_key: str | None = None
    """
    API key to use for authenticating with the Nextmv Cloud API.

    The API key is determined in the following order of precedence:
    1. This `api_key` attribute set on the client.
    2. The `NEXTMV_API_KEY` environment variable.
    3. If the `NEXTMV_PROFILE` environment variable is set, it is used to look
    up the API key for that profile in the configuration file.
    4. If the `profile` attribute is set on the client, it is used to look up
    the API key for that profile in the configuration file.
    5. If the `profile` attribute is not set, the default profile is used to
    look up the API key in the configuration file.
    6. If all of the above lookups fail, an exception is raised indicating that
    the API key is missing.
    """
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
    configuration_file: str | None = None
    """
    Deprecated. This attribute is no longer being used. Use the `profile`
    attribute to specify different configurations instead.
    """
    headers: dict[str, str] | None = None
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
    url: str | None = None
    """
    URL (endpoint) of the Nextmv Cloud API.

    The endpoint is determined in the following order of precedence:
    1. This `url` attribute set on the client.
    2. The `NEXTMV_ENDPOINT` environment variable.
    3. If the `NEXTMV_PROFILE` environment variable is set, it is used to look
    up the endpoint for that profile in the configuration file.
    4. If the `profile` attribute is set on the client, it is used to look up
    the endpoint for that profile in the configuration file.
    5. If the `profile` attribute is not set, the default profile is used to
    look up the endpoint in the configuration file.
    6. If all of the above lookups fail, the hardcoded default URL of
    `https://api.cloud.nextmv.io` is used.
    """
    console_url: str = "https://cloud.nextmv.io"
    """URL of the Nextmv Cloud console."""
    profile: str | None = None
    """
    Profile to use from the configuration file. Profiles allow you to configure
    multiple sets of API keys and endpoints in the configuration file and
    select between them.

    The profile is determined in the following order of precedence:
    1. The `NEXTMV_PROFILE` environment variable.
    2. This `profile` attribute set on the client.
    """

    def __post_init__(self):
        """
        Initializes the client after dataclass construction.

        This method handles the logic for API key retrieval and header
        setup. It checks for the API key in the constructor, environment
        variables, and the configuration file, in that order.

        Raises
        ------
        ValueError
            If no API key is found after checking the constructor argument,
            the ``NEXTMV_API_KEY`` environment variable, and the
            configuration file (for the resolved profile or the default
            profile). A ``None`` or empty ``api_key`` is treated as unset
            and causes the lookup to fall through to the next source.
            If a profile is specified via ``NEXTMV_PROFILE`` or the
            ``profile`` attribute but is not found in the configuration file.
            If ``apikey`` is not found in the configuration file for the
            selected profile.
        """

        profile = self.__resolve_profile()
        self.url = self.__resolve_endpoint(profile)
        self.api_key = self.__resolve_api_key(profile)
        self.__set_headers_api_key(self.api_key)

        if self.configuration_file is not None and self.configuration_file != "":
            deprecated(
                name="Client.configuration_file",
                reason="`Client.configuration_file` is deprecated, use `Client.profile` to work with another profile",
            )

    def request(  # noqa: C901
        self,
        method: str,
        endpoint: str,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
        json_configurations: dict[str, Any] | None = None,
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
        List all applications:

        >>> client = Client(api_key="YOUR_API_KEY")
        >>> response = client.request(method="GET", endpoint="/v1/applications")
        >>> print(response.status_code)
        200
        >>> apps = response.json()
        >>> print([a["id"] for a in apps["items"]])
        ['my-app', 'another-app']

        Create a new run with a JSON payload:

        >>> run_payload = {
        ...     "applicationId": "my-app",
        ...     "instanceId": "candidate",
        ...     "input": {"value": 10},
        ... }
        >>> response = client.request(
        ...     method="POST",
        ...     endpoint="/v1/runs",
        ...     payload=run_payload,
        ... )
        >>> print(response.json()["id"])
        run_xxxxxxxxxxxx

        Retrieve a specific run using query parameters:

        >>> response = client.request(
        ...     method="GET",
        ...     endpoint="/v1/runs",
        ...     query_params={"applicationId": "my-app", "limit": 5},
        ... )
        >>> print(len(response.json()["items"]))
        5

        Send a request with custom headers (e.g., to pass a request ID):

        >>> response = client.request(
        ...     method="GET",
        ...     endpoint="/v1/applications",
        ...     headers={**client.headers, "X-Request-Id": "abc-123"},
        ... )

        Send a JSON payload with custom serialization (pretty-printed):

        >>> response = client.request(
        ...     method="POST",
        ...     endpoint="/v1/runs",
        ...     payload={"applicationId": "my-app", "input": {}},
        ...     json_configurations={"indent": 2},
        ... )
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
            if isinstance(payload, dict | list):
                data = deflated_serialize_json(payload, json_configurations=json_configurations)
                kwargs["data"] = data
            else:
                raise ValueError("payload must be a dictionary or a list")
        if query_params is not None:
            kwargs["params"] = query_params

        try:
            response = session.request(method=method, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise requests.exceptions.ConnectionError(
                f"could not connect to {self.url}: the server may be unreachable. "
                "Check your network connectivity and verify the endpoint URL is correct."
            ) from e
        except requests.exceptions.Timeout as e:
            raise requests.exceptions.Timeout(
                f"request to {endpoint} timed out after {self.timeout}s waiting for {self.url}. "
                "The server may be unreachable or under heavy load. "
                "Consider increasing the `timeout` attribute on the Client."
            ) from e

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            err = requests.HTTPError(
                f"request to {endpoint} failed with status code {response.status_code} and message: {response.text}"
            )
            err.response = response

            raise err from e

        return response

    def request_with_pagination(
        self,
        method: str,
        endpoint: str,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
        json_configurations: dict[str, Any] | None = None,
        max_pages: int = 1000,
    ) -> list[dict[str, Any]]:
        """
        Makes paginated requests to the Nextmv Cloud API and returns all items.

        This method automatically handles pagination by following the
        `next_page_token` provided in API responses. It collects all items
        across pages and returns them as a single list.

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
            Query parameters to append to the request URL. The `pagereturn`
            parameter is automatically added to enable pagination.
        json_configurations : dict[str, Any], optional
            Additional configurations for JSON serialization. This allows
            customization of the Python `json.dumps` function, such as
            specifying `indent` for pretty printing or `default` for custom
            serialization functions.
        max_pages : int, optional
            Maximum number of pages to fetch. Defaults to 1000. This prevents
            infinite loops if the API returns malformed pagination tokens.

        Returns
        -------
        list[dict[str, Any]]
            A list containing all items from all pages. If the API response
            does not contain an "items" field, an empty list is returned.

        Raises
        ------
        requests.HTTPError
            If any request fails with a non-2xx status code.
        ValueError
            If both `data` and `payload` are provided.
            If the `payload` or `data` size exceeds `_MAX_LAMBDA_PAYLOAD_SIZE`.
            If the maximum number of pages is exceeded.

        Examples
        --------
        Fetch all applications across multiple pages:

        >>> client = Client(api_key="YOUR_API_KEY")
        >>> apps = client.request_with_pagination(
        ...     method="GET",
        ...     endpoint="/v1/applications",
        ... )
        >>> print(len(apps))
        150
        >>> print([a["id"] for a in apps[:3]])
        ['app-1', 'app-2', 'app-3']

        Fetch all runs for a specific application with query filters:

        >>> runs = client.request_with_pagination(
        ...     method="GET",
        ...     endpoint="/v1/runs",
        ...     query_params={"applicationId": "my-app", "status": "completed"},
        ... )
        >>> print(len(runs))
        500

        Limit the number of pages to prevent excessive API calls:

        >>> items = client.request_with_pagination(
        ...     method="GET",
        ...     endpoint="/v1/applications",
        ...     max_pages=10,
        ... )
        """
        return list(
            self._paginate(
                method=method,
                endpoint=endpoint,
                data=data,
                headers=headers,
                payload=payload,
                query_params=query_params,
                json_configurations=json_configurations,
                max_pages=max_pages,
            )
        )

    def iter_with_pagination(
        self,
        method: str,
        endpoint: str,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
        json_configurations: dict[str, Any] | None = None,
        max_pages: int = 1000,
    ) -> Generator[dict[str, Any], None, None]:
        """
        Generator that yields items from paginated API responses one at a time.

        This method is a memory-efficient alternative to
        :meth:`request_with_pagination`. Instead of collecting all items in
        memory before returning, it yields items as they are fetched, making
        it suitable for processing very large result sets that might not fit
        in memory.

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
            Query parameters to append to the request URL. The `pagereturn`
            parameter is automatically added to enable pagination.
        json_configurations : dict[str, Any], optional
            Additional configurations for JSON serialization. This allows
            customization of the Python `json.dumps` function, such as
            specifying `indent` for pretty printing or `default` for custom
            serialization functions.
        max_pages : int, optional
            Maximum number of pages to fetch. Defaults to 1000. This prevents
            infinite loops if the API returns malformed pagination tokens.

        Yields
        ------
        dict[str, Any]
            Individual items from the API response, one at a time.

        Raises
        ------
        requests.HTTPError
            If any request fails with a non-2xx status code.
        ValueError
            If both `data` and `payload` are provided.
            If the `payload` or `data` size exceeds `_MAX_LAMBDA_PAYLOAD_SIZE`.
            If the maximum number of pages is exceeded.
            If the API response structure is invalid or unexpected.

        Examples
        --------
        Process applications one at a time without loading all into memory:

        >>> client = Client(api_key="YOUR_API_KEY")
        >>> for app in client.iter_with_pagination(
        ...     method="GET",
        ...     endpoint="/v1/applications",
        ... ):
        ...     print(f"Processing {app['id']}")
        ...     # Process each app individually
        Processing app-1
        Processing app-2
        ...

        Use with filtering and early termination:

        >>> for run in client.iter_with_pagination(
        ...     method="GET",
        ...     endpoint="/v1/runs",
        ...     query_params={"applicationId": "my-app"},
        ... ):
        ...     if run["status"] == "failed":
        ...         print(f"Found failed run: {run['id']}")
        ...         break  # Stop iteration early

        Collect results with list comprehension or generator expression:

        >>> app_ids = [
        ...     app["id"]
        ...     for app in client.iter_with_pagination(
        ...         method="GET",
        ...         endpoint="/v1/applications",
        ...         max_pages=5,
        ...     )
        ... ]
        """
        yield from self._paginate(
            method=method,
            endpoint=endpoint,
            data=data,
            headers=headers,
            payload=payload,
            query_params=query_params,
            json_configurations=json_configurations,
            max_pages=max_pages,
        )

    def upload_to_presigned_url(
        self,
        data: dict[str, Any] | str | None,
        url: str,
        json_configurations: dict[str, Any] | None = None,
        tar_file: str | None = None,
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
        Upload a dictionary as JSON (presigned URL obtained from a prior API
        call):

        >>> client = Client(api_key="YOUR_API_KEY")
        >>> input_data = {"stops": [{"id": "A"}, {"id": "B"}], "config": {"max_duration": 30}}
        >>> client.upload_to_presigned_url(data=input_data, url="PRE_SIGNED_URL")  # doctest: +SKIP

        Upload a raw JSON string:

        >>> client.upload_to_presigned_url(  # doctest: +SKIP
        ...     data='{"stops": [{"id": "A"}]}',
        ...     url="PRE_SIGNED_URL",
        ... )

        Upload a pre-built tarball (e.g., a packaged application):

        >>> client.upload_to_presigned_url(  # doctest: +SKIP
        ...     data=None,
        ...     url="PRE_SIGNED_URL",
        ...     tar_file="/path/to/app.tar.gz",
        ... )
        """

        upload_data: str | None = None
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
            with open(tar_file, "rb") as f:
                kwargs["data"] = f.read()
        else:
            raise ValueError("either data or tar_file must be provided")

        try:
            response = session.put(**kwargs)
        except requests.exceptions.ConnectionError as e:
            raise requests.exceptions.ConnectionError(
                "could not connect to upload URL: the server may be unreachable. "
                "Check your network connectivity and verify the URL is correct."
            ) from e
        except requests.exceptions.Timeout as e:
            raise requests.exceptions.Timeout(
                f"upload request timed out after {self.timeout}s. "
                "The server may be unreachable or under heavy load. "
                "Consider increasing the `timeout` attribute on the Client."
            ) from e

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            err = requests.HTTPError(
                f"upload to presigned URL {url} failed with "
                f"status code {response.status_code} and message: {response.text}"
            )
            err.response = response
            raise err from e

    def __resolve_profile(self) -> str | None:
        """
        Resolves the active profile name.

        Checks, in order of precedence: the `NEXTMV_PROFILE` environment
        variable and then the `profile` attribute set on the client.

        Returns
        -------
        str or None
            The resolved profile name, or `None` if no profile is set.
        """
        profile_env = os.getenv("NEXTMV_PROFILE")
        if profile_env is not None:
            profile_env = profile_env.strip()
            if profile_env != "":
                if profile_env.lower() == "default":
                    return None

                return profile_env

        if self.profile is not None:
            profile = self.profile.strip()
            if profile != "":
                if profile.lower() == "default":
                    return None

                return profile

        return None

    def __resolve_endpoint(self, profile: str | None) -> str:
        """
        Resolves the API endpoint URL.

        Checks, in order of precedence: the `url` attribute set on the
        client, the `NEXTMV_ENDPOINT` environment variable, the endpoint
        for the given profile in the configuration file, and finally the
        default endpoint for the default profile in the configuration file.
        Falls back to the hardcoded default URL if all other lookups fail.

        Parameters
        ----------
        profile : str or None
            The profile name to use when looking up the endpoint in the
            configuration file. If `None` or empty, the default profile
            is used.

        Returns
        -------
        str
            The resolved API endpoint URL.
        """
        if self.url is not None and self.url != "":
            url = self.url
        elif url_env := os.getenv("NEXTMV_ENDPOINT"):
            url = url_env
        elif profile is not None and profile != "":
            url = retrieve_endpoint_from_config(profile)
        else:
            # The fallback behavior is to attempt to retrieve the default endpoint
            # from the config file. If everything fails, we return the hardcoded
            # default endpoint.
            try:
                url = retrieve_endpoint_from_config()
            except (RuntimeError, ValueError):
                url = "https://api.cloud.nextmv.io"

        if not url.startswith("https://") and not url.startswith("http://"):
            url = f"https://{url}"

        return url

    def __resolve_api_key(self, profile: str | None) -> str:
        """
        Resolves the API key.

        Checks, in order of precedence: the `api_key` attribute set on the
        client, the `NEXTMV_API_KEY` environment variable, the API key for
        the given profile in the configuration file, and finally the API key
        for the default profile in the configuration file.

        Parameters
        ----------
        profile : str or None
            The profile name to use when looking up the API key in the
            configuration file. If `None` or empty, the default profile
            is used.

        Returns
        -------
        str
            The resolved API key.

        Raises
        ------
        RuntimeError
            If no configuration file is found when falling back to the
            configuration file lookup.
        ValueError
            If the API key is not set or is empty in the configuration file
            for the resolved profile.
        """
        if self.api_key is not None and self.api_key != "":
            return self.api_key

        api_key_env = os.getenv("NEXTMV_API_KEY")
        if api_key_env is not None and api_key_env != "":
            return api_key_env

        if profile is not None and profile != "":
            api_key = retrieve_key_from_config(profile)
            return api_key

        # The fallback behavior is to attempt to retrieve the default api key
        # from the config file. If the key is missing, an exception is raised.
        try:
            api_key = retrieve_key_from_config()
        except (RuntimeError, ValueError) as e:
            raise ValueError(
                "API key is missing. Please set the API key in one of the following ways: "
                "1. Pass it directly to the Client constructor. "
                "2. Set the NEXTMV_API_KEY environment variable. "
                "3. Set the API key in the configuration file for the default profile. "
                "4. If using profiles, set the API key in the configuration file for the selected profile and ensure "
                "the profile is selected via the NEXTMV_PROFILE environment variable or the Client constructor."
            ) from e

        return api_key

    def __set_headers_api_key(self, api_key: str) -> None:
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

    def _paginate(
        self,
        method: str,
        endpoint: str,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
        json_configurations: dict[str, Any] | None = None,
        max_pages: int = 1000,
    ) -> Generator[dict[str, Any], None, None]:
        """
        Internal generator that handles pagination logic.

        This is a private method used by both `request_with_pagination` and
        `iter_with_pagination` to avoid code duplication. It yields individual
        items from paginated API responses.

        Parameters
        ----------
        method : str
            HTTP method to use (e.g., "GET", "POST").
        endpoint : str
            API endpoint to send the request to.
        data : Any, optional
            Data to send in the request body.
        headers : dict[str, str], optional
            Additional headers to send with the request.
        payload : dict[str, Any], optional
            JSON payload to send with the request.
        query_params : dict[str, Any], optional
            Query parameters to append to the request URL.
        json_configurations : dict[str, Any], optional
            Additional configurations for JSON serialization.
        max_pages : int, optional
            Maximum number of pages to fetch. Defaults to 1000.

        Yields
        ------
        dict[str, Any]
            Individual items from the API response.

        Raises
        ------
        requests.HTTPError
            If any request fails with a non-2xx status code.
        ValueError
            If both `data` and `payload` are provided.
            If the `payload` or `data` size exceeds `_MAX_LAMBDA_PAYLOAD_SIZE`.
            If the maximum number of pages is exceeded.
            If the API response structure is invalid or unexpected.
        """
        query_params = (query_params or {}) | {"pagereturn": "true"}
        page_count = 0

        while True:
            if page_count >= max_pages:
                raise ValueError(
                    f"exceeded maximum number of pages ({max_pages}). "
                    "Increase max_pages parameter if you expect more pages, "
                    "or check for potential pagination loop issues."
                )

            resp = self.request(
                method=method,
                endpoint=endpoint,
                data=data,
                headers=headers,
                payload=payload,
                query_params=query_params,
                json_configurations=json_configurations,
            )

            # Validate response structure
            try:
                resp_json = resp.json()
            except requests.exceptions.JSONDecodeError as e:
                raise ValueError(
                    f"API response from {endpoint} is not valid JSON. "
                    f"Response status: {resp.status_code}, body: {resp.text[:200]}"
                ) from e

            if not isinstance(resp_json, dict):
                raise ValueError(
                    f"API response from {endpoint} is not a dictionary. Got {type(resp_json).__name__} instead."
                )

            page_count += 1

            # Yield items from the current page one at a time
            page_items = resp_json.get("items")
            if page_items is not None:
                if not isinstance(page_items, list):
                    raise ValueError(
                        f"API response 'items' field from {endpoint} is not a list. "
                        f"Got {type(page_items).__name__} instead."
                    )
                yield from page_items

            # Check for next page token
            next_token = resp_json.get("next_page_token")
            if next_token:
                if not isinstance(next_token, str):
                    raise ValueError(
                        f"API response 'next_page_token' from {endpoint} is not a string. "
                        f"Got {type(next_token).__name__} instead."
                    )
                query_params["pagetoken"] = next_token
            else:
                break


def get_size(obj: dict[str, Any] | IO[bytes] | str, json_configurations: dict[str, Any] | None = None) -> int:
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


def _load_config() -> dict[str, Any]:
    """
    Load the current configuration from the config file. Returns an empty
    dictionary if no configuration file exists.

    Returns
    -------
    dict[str, Any]
        The current configuration as a dictionary.
    """

    if not _CONFIG_FILE.exists():
        return {}

    with _CONFIG_FILE.open() as file:
        config = yaml.safe_load(file)

    if config is None:
        return {}
    return config


def retrieve_key_from_config(profile: str | None = None) -> str:
    """
    Retrieves the API key for the given profile. If no profile is given, the
    default profile is used. If the API key is missing, an exception is raised.
    If the config is not available, an exception is raised.

    Parameters
    ----------
    profile : str | None
        The profile name to use. If None, the default profile is used.

    Returns
    -------
    str
        The API key for the selected profile or the default configuration.

    Raises
    ------
    RuntimeError
        If no configuration file is found.
    ValueError
        If the requested profile does not exist, or if the API key (for either
        the selected profile or the default configuration) is not set or is
        empty.
    """

    config = _load_config()
    if config == {}:
        raise RuntimeError(f"No configuration file at {_CONFIG_FILE} found.")

    if profile is not None:
        if profile not in config:
            raise ValueError(f"Profile `{profile}` does not exist.")

        api_key = config[profile].get(_API_KEY_KEY)
        if api_key is None or api_key == "":
            raise ValueError(f"API key for profile `{profile}` is not set or is empty.")
    else:
        api_key = config.get(_API_KEY_KEY)
        if api_key is None or api_key == "":
            raise ValueError("Default API key is not set or is empty.")

    return api_key


def retrieve_endpoint_from_config(profile: str | None = None) -> str:
    """
    Retrieves the endpoint for the given profile. If no profile is given, the
    default profile is used. If the endpoint is missing, an exception is
    raised. If the config is not available, an exception is raised.

    Parameters
    ----------
    profile : str | None
        The profile name to use. If None, the default profile is used.

    Returns
    -------
    str
        The endpoint for the selected profile or the default configuration.

    Raises
    ------
    RuntimeError
        If no configuration file is found.
    ValueError
        If the requested profile does not exist, or if the endpoint (for either
        the selected profile or the default configuration) is not set or is
        empty.
    """

    config = _load_config()
    if config == {}:
        raise RuntimeError(f"No configuration file at {_CONFIG_FILE} found.")

    if profile is not None:
        if profile not in config:
            raise ValueError(f"Profile `{profile}` does not exist.")

        endpoint = config[profile].get(_ENDPOINT_KEY)
        if endpoint is None or endpoint == "":
            raise ValueError(f"Endpoint for profile `{profile}` is not set or is empty.")
    else:
        endpoint = config.get(_ENDPOINT_KEY)
        if endpoint is None or endpoint == "":
            raise ValueError("Default endpoint is not set or is empty.")

    return f"https://{endpoint}"
