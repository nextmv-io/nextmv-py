"""Module with the client class."""

import os
import random
import sys
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter, Retry


@dataclass
class Client:
    """
    Client that interacts directly with the Nextmv Cloud API. The API key
    must be provided either in the constructor or via the NEXTMV_API_KEY
    environment variable.
    """

    api_key: str | None = None
    """API key to use for authenticating with the Nextmv Cloud API. If not
    provided, the client will look for the NEXTMV_API_KEY environment
    variable."""
    backoff_factor: float = 0.8
    """Exponential backoff factor to use for requests to the Nextmv Cloud
    API."""
    backoff_jitter: float = 0.1
    """Jitter to use for requests to the Nextmv Cloud API when backing off."""
    headers: dict[str, str] | None = None
    """Headers to use for requests to the Nextmv Cloud API."""
    initial_delay: float = 0.1
    """Initial delay to use for requests to the Nextmv Cloud API when backing
    off."""
    max_lambda_payload_size: int = 500 * 1024 * 1024
    """Maximum size of the payload handled by the Nextmv Cloud API."""
    max_retries: int = 10
    """Maximum number of retries to use for requests to the Nextmv Cloud
    API."""
    max_wait: int = 60
    """Maximum number of seconds that a request will wait for when retrying. If
    exponential backoff is used, this is the maximum value of the backoff.
    After this value is achieved, the backof stops increasing."""
    status_forcelist: list[int] = field(
        default_factory=lambda: [500, 502, 503, 504, 507, 509],
    )
    """Status codes to retry for requests to the Nextmv Cloud API."""
    timeout: float = 20
    """Timeout to use for requests to the Nextmv Cloud API."""
    url: str = "https://api.cloud.nextmv.io"
    """URL of the Nextmv Cloud API."""

    def __post_init__(self):
        """Logic to run after the class is initialized."""

        if self.api_key is None:
            api_key = os.getenv("NEXTMV_API_KEY")
            if api_key is None:
                raise ValueError(
                    "no API key provided. Either set it in the constructor or "
                    "set the NEXTMV_API_KEY environment variable."
                )
            self.api_key = api_key

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def request(
        self,
        method: str,
        endpoint: str,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
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

        if payload is not None and get_size(payload) > self.max_lambda_payload_size:
            raise ValueError(
                f"payload size of {get_size(payload)} bytes exceeds the maximum "
                f"allowed size of {self.max_lambda_payload_size} bytes"
            )

        if data is not None and get_size(data) > self.max_lambda_payload_size:
            raise ValueError(
                f"data size of {get_size(data)} bytes exceeds the maximum "
                f"allowed size of {self.max_lambda_payload_size} bytes"
            )

        session = requests.Session()
        retries = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            backoff_jitter=self.backoff_jitter,
            status_forcelist=self.status_forcelist,
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

        # Backoff logic for 429 responses.
        delay = self.initial_delay
        for n in range(1, self.max_retries + 1):
            response = session.request(method=method, **kwargs)
            if response.status_code == 429:
                time.sleep(min(delay, self.max_wait))
                delay = self.backoff_factor * 2**n + random.uniform(0, self.backoff_jitter)
                continue

            break

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"request to {endpoint} failed with status code {response.status_code} and message: {response.text}"
            ) from e

        return response


def get_size(obj: dict | Any, seen: set | Any = None) -> int:
    """Recursively finds size of objects"""

    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0

    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, "__dict__"):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, "__iter__") and not isinstance(obj, str | bytes | bytearray):
        size += sum([get_size(i, seen) for i in obj])
    return size
