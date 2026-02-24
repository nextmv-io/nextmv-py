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

from pathlib import Path

from pydantic import Field

from nextmv.base_model import BaseModel
from nextmv.cloud.client import Client


def _resolve_metadata_document(metadata_document: str | None = None) -> str | None:
    """
    Resolve the SSO metadata document from a string or a file path.

    Parameters
    ----------
    metadata_document : str, optional
        The SSO metadata document as a string or a path to a file containing
        the document.

    Returns
    -------
    str, optional
        The SSO metadata document as a string, or `None` if not provided.

    Raises
    ------
    RuntimeError
        If the metadata document is a file path and the file cannot be read.
    """
    if metadata_document is None or metadata_document == "":
        return None

    meta_path = Path(metadata_document)
    if meta_path.is_file():
        try:
            return meta_path.read_text()
        except (OSError, UnicodeDecodeError) as e:
            raise RuntimeError(f"Failed to read metadata document from file {meta_path}: {e}") from e

    return metadata_document


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
    mapped_domains : list[str], optional
        A list of mapped domains in the SSO configuration. This is read only, mapped
        domains are added through an explicit command.
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
    mapped_domains: list[str] = Field(default_factory=list)
    """
    A list of mapped domains in the SSO configuration. Mapped domains redirect
    additional domains to your IDP for federated authentication.
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
            endpoint="v1/enterprise/sso",
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
        mapped_domains: list[str] | None = None,
    ) -> None:
        """
        Create a new SSO configuration for the current Nextmv Cloud
        organization (account).

        This method does not return the created configuration. To retrieve
        the configuration after creation, use the `get` method.

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
        mapped_domains : list[str], optional
            A list of mapped domains in the SSO configuration.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        metadata_document = _resolve_metadata_document(metadata_document)

        payload = {
            "allow_non_domain_users": allow_non_domain_users,
            "enabled": enabled,
            "metadata_url": metadata_url,
            "metadata_document": metadata_document,
        }

        client.request(
            method="POST",
            endpoint="v1/enterprise/sso",
            payload=payload,
        )

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

    def delete_domain(self, domain: str) -> None:
        """
        Deletes a domain from an existing SSO configuration for the current Nextmv
        Cloud organization (account).

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        self.client.request(
            method="DELETE",
            endpoint=f"{self.sso_endpoint}/domains/{domain}",
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
    ) -> None:
        """
        Update the SSO configuration for the current Nextmv Cloud
        organization (account).

        This method does not return the updated configuration. To retrieve the
        configuration after updating, use the `get` method. If you wish to
        enable or disable SSO, please use the `enable` and `disable` methods
        instead.

        Parameters
        ----------
        metadata_url : str, optional
            The URL to the SSO metadata document.
        metadata_document : str, optional
            The SSO metadata document as a string.

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
            metadata_document = _resolve_metadata_document(metadata_document)
            payload["metadata_document"] = metadata_document

        self.client.request(
            method="PUT",
            endpoint=self.sso_endpoint,
            payload=payload,
        )
