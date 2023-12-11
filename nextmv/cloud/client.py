"""Module with the client class."""

import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class Client:
    """Client that interacts directly with the Nextmv Cloud API. The API key
    must be provided either in the constructor or via the NEXTMV_API_KEY"""

    api_key: str | None = None
    """API key to use for authenticating with the Nextmv Cloud API. If not
    provided, the client will look for the NEXTMV_API_KEY environment
    variable."""
    url: str = "https://api.cloud.nextmv.io"
    """URL of the Nextmv Cloud API."""
    headers: dict[str, str] | None = None
    """Headers to use for requests to the Nextmv Cloud API."""

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

    def post(
        self,
        endpoint: str,
        payload: dict[str, Any],
        query_params: dict[str, Any] | None = None,
    ) -> requests.Response:
        """
        Send a POST request to the Nextmv Cloud API.

        Args:
            endpoint: Endpoint to send the request to.
            payload: Payload to send with the request.
            query_params: Query parameters to send with the request.

        Returns:
            Response from the Nextmv Cloud API.
        """

        response = requests.post(
            url=f"{self.url}/{endpoint}",
            json=payload,
            headers=self.headers,
            params=query_params,
        )
        response.raise_for_status()

        return response

    def get(
        self,
        endpoint: str,
        query_params: dict[str, Any] | None = None,
    ) -> requests.Response:
        """
        Send a GET request to the Nextmv Cloud API.

        Args:
            endpoint: Endpoint to send the request to.
            query_params: Query parameters to send with the request.

        Returns:
            Response from the Nextmv Cloud API.
        """

        response = requests.get(
            url=f"{self.url}/{endpoint}",
            headers=self.headers,
            params=query_params,
        )
        response.raise_for_status()

        return response
