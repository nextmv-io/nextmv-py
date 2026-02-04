"""
Single Sign-On (SSO) functionality for the Nextmv Cloud API.

This module provides classes and methods to manage Single Sign-On (SSO)
configurations for Nextmv Cloud organizations (accounts).

Classes
-------
SSOConfiguration
    Represents the SSO configuration for a Nextmv Cloud organization (account)
    and provides methods to create, retrieve, update, enable, disable, and
    delete SSO configurations.
"""

from pydantic import Field

from nextmv.base_model import BaseModel
from nextmv.cloud.client import Client


class SSOConfiguration(BaseModel):
    """
    Configuration for Single Sign-On (SSO) in Nextmv Cloud.

    You can import the `SSOConfiguration` class directly from `cloud`:

    ```python
    from nextmv.cloud import SSOConfiguration
    ```

    Attributes
    ----------
    allow_non_domain_users : bool, optional
        Whether to allow users who are not part of the SSO domain to access the
        Nextmv Cloud organization (account). Default is `False`.
    enabled : bool, optional
        Whether SSO is enabled for the Nextmv Cloud organization (account).
    metadata_url : str, optional
        The URL to the SSO metadata document.
    metadata_document : str, optional
        The SSO metadata document as a string.
    client : Client
        Client to use for interacting with the Nextmv Cloud API. This is an
        SDK-specific attribute and it is not part of the API representation of
        an SSO configuration.
    sso_endpoint : str
        Base endpoint for SSO operations. This is an SDK-specific attribute and
        it is not part of the API representation of an SSO configuration.
    """

    allow_non_domain_users: bool = False
    """
    Whether to allow users who are not part of the SSO domain to access the
    Nextmv Cloud organization (account).
    """

    enabled: bool | None = None
    """
    Whether SSO is enabled for the Nextmv Cloud organization (account).
    """
    metadata_url: str | None = None
    """
    The URL to the SSO metadata document.
    """
    metadata_document: str | None = None
    """
    The SSO metadata document as a string.
    """

    # SDK-specific attributes for convenience when using methods.
    client: Client = Field(exclude=True)
    """Client to use for interacting with the Nextmv Cloud API."""
    sso_endpoint: str = Field(exclude=True, default="v1/enterprise/sso")

    @classmethod
    def get(cls, client: Client) -> "SSOConfiguration":
        """
        Retrieve the SSO configuration for the current Nextmv Cloud
        organization (account).

        Parameters
        ----------
        client : Client
            Client to use for interacting with the Nextmv Cloud API.

        Returns
        -------
        SSOConfiguration
            The SSO configuration for the organization (account).

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        response = client.request(
            method="GET",
            endpoint=cls.sso_endpoint,
        )

        return cls.from_dict({"client": client} | response.json())

    @classmethod
    def new(
        cls,
        client: Client,
        allow_non_domain_users: bool = False,
        enabled: bool | None = None,
        metadata_url: str | None = None,
        metadata_document: str | None = None,
    ) -> "SSOConfiguration":
        """
        Create a new SSO configuration for the current Nextmv Cloud
        organization (account).

        Parameters
        ----------
        client : Client
            Client to use for interacting with the Nextmv Cloud API.
        allow_non_domain_users : bool, optional
            Whether to allow users who are not part of the SSO domain to access
            the Nextmv Cloud organization (account). Default is `False`.
        enabled : bool, optional
            Whether SSO is enabled for the Nextmv Cloud organization (account).
        metadata_url : str, optional
            The URL to the SSO metadata document.
        metadata_document : str, optional
            The SSO metadata document as a string.

        Returns
        -------
        SSOConfiguration
            The newly created SSO configuration for the organization (account).

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        payload = {
            "allow_non_domain_users": allow_non_domain_users,
            "enabled": enabled,
            "metadata_url": metadata_url,
            "metadata_document": metadata_document,
        }

        response = client.request(
            method="POST",
            endpoint=cls.sso_endpoint,
            json=payload,
        )

        return cls.from_dict({"client": client} | response.json())

    def delete(self) -> None:
        """
        Delete the SSO configuration for the current Nextmv Cloud
        organization (account).

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        self.client.request(
            method="DELETE",
            endpoint=self.sso_endpoint,
        )

    def disable(self) -> None:
        """
        Disable SSO for the current Nextmv Cloud organization (account).

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        self.client.request(
            method="PUT",
            endpoint=f"{self.sso_endpoint}/disable",
        )

    def enable(self) -> None:
        """
        Enable SSO for the current Nextmv Cloud organization (account).

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        self.client.request(
            method="PUT",
            endpoint=f"{self.sso_endpoint}/enable",
        )

    def update(
        self,
        metadata_url: str | None = None,
        metadata_document: str | None = None,
    ) -> "SSOConfiguration":
        """
        Update the SSO configuration for the current Nextmv Cloud
        organization (account).

        If you wish to enable or disable SSO, please use the `enable` and
        `disable` methods instead.

        Parameters
        ----------
        metadata_url : str, optional
            The URL to the SSO metadata document.
        metadata_document : str, optional
            The SSO metadata document as a string.

        Returns
        -------
        SSOConfiguration
            The updated SSO configuration for the organization (account).

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        config = self.get(self.client)
        config_dict = config.to_dict()
        payload = config_dict.copy()

        if metadata_url is not None and metadata_url != "":
            payload["metadata_url"] = metadata_url
        if metadata_document is not None and metadata_document != "":
            payload["metadata_document"] = metadata_document

        response = self.client.request(
            method="PUT",
            endpoint=self.sso_endpoint,
            json=payload,
        )

        return self.from_dict({"client": self.client} | response.json())
