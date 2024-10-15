"""Module with the client class."""

import json
import os
from dataclasses import dataclass, field
from typing import IO, Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import requests
import yaml
from requests.adapters import HTTPAdapter, Retry

_MAX_LAMBDA_PAYLOAD_SIZE: int = 500 * 1024 * 1024
"""Maximum size of the payload handled by the Nextmv Cloud API."""


@dataclass
class Client:
    """
    Client that interacts directly with the Nextmv Cloud API. The API key will
    be searched, in order of precedence, in: the api_key arg in the
    constructor, the NEXTMV_API_KEY environment variable, the
    ~/.nextmv/config.yaml file used by the Nextmv CLI.
    """

    api_key: Optional[str] = None
    """API key to use for authenticating with the Nextmv Cloud API. If not
    provided, the client will look for the NEXTMV_API_KEY environment
    variable."""
    allowed_methods: List[str] = field(
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
    headers: Optional[Dict[str, str]] = None
    """Headers to use for requests to the Nextmv Cloud API."""
    max_retries: int = 10
    """Maximum number of retries to use for requests to the Nextmv Cloud
    API."""
    status_forcelist: List[int] = field(
        default_factory=lambda: [429, 500, 502, 503, 504, 507, 509],
    )
    """Status codes to retry for requests to the Nextmv Cloud API."""
    timeout: float = 20
    """Timeout to use for requests to the Nextmv Cloud API."""
    url: str = "https://api.cloud.nextmv.io"
    """URL of the Nextmv Cloud API."""

    def __post_init__(self):
        """Logic to run after the class is initialized."""

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
                "no API key set in constructor or NEXTMV_API_KEY env var, and ~/.nextmv/config.yaml does not exist"
            )

        with open(config_path) as f:
            config = yaml.safe_load(f)

        profile = os.getenv("NEXTMV_PROFILE")
        parent = config
        if profile is not None:
            parent = config.get(profile)
            if parent is None:
                raise ValueError(f"profile {profile} set via NEXTMV_PROFILE but not found in ~/.nextmv/config.yaml")

        api_key = parent.get("apikey")
        if api_key is None:
            raise ValueError("no apiKey found in ~/.nextmv/config.yaml")
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
        headers: Optional[Dict[str, str]] = None,
        payload: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Method to make a request to the Nextmv Cloud API.

        Args:
            method: HTTP method to use. Valid methods include: GET, POST.
            endpoint: Endpoint to send the request to.
            data: Data to send with the request.
            headers: Headers to send with the request.
            payload: Payload to send with the request. Prefer using this over
                data.
            query_params: Query parameters to send with the request.

        Returns:
            Response from the Nextmv Cloud API.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
            ValueError: If both data and payload are provided.
            ValueError: If the payload size exceeds the maximum allowed size.
            ValueError: If the data size exceeds the maximum allowed size.
        """

        if payload is not None and data is not None:
            raise ValueError("cannot use both data and payload")

        if payload is not None and get_size(payload) > _MAX_LAMBDA_PAYLOAD_SIZE:
            raise ValueError(
                f"payload size of {get_size(payload)} bytes exceeds the maximum "
                f"allowed size of {_MAX_LAMBDA_PAYLOAD_SIZE} bytes"
            )

        if data is not None and get_size(data) > _MAX_LAMBDA_PAYLOAD_SIZE:
            raise ValueError(
                f"data size of {get_size(data)} bytes exceeds the maximum "
                f"allowed size of {_MAX_LAMBDA_PAYLOAD_SIZE} bytes"
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

        kwargs = {
            "url": urljoin(self.url, endpoint),
            "timeout": self.timeout,
        }
        kwargs["headers"] = headers if headers is not None else self.headers
        if data is not None:
            kwargs["data"] = data
        if payload is not None:
            kwargs["json"] = payload
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

    def _set_headers_api_key(self, api_key: str) -> None:
        """Sets the API key to use for requests to the Nextmv Cloud API."""

        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }


def get_size(obj: Union[Dict[str, Any], IO[bytes]]) -> int:
    """Finds the size of an object in bytes."""

    if isinstance(obj, dict):
        obj_str = json.dumps(obj, separators=(",", ":"))
        return len(obj_str.encode("utf-8"))

    elif hasattr(obj, "read"):
        obj.seek(0, 2)  # Move the cursor to the end of the file
        size = obj.tell()
        obj.seek(0)  # Reset the cursor to the beginning of the file
        return size

    else:
        raise TypeError("Unsupported type. Only dictionaries and file objects are supported.")
