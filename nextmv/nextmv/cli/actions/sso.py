"""Core SSO management actions.

Pure functions that wrap SDK calls. No CLI or MCP presentation concerns.

SSO is singleton per Nextmv Cloud organization: there is no ID — all
operations act on "the" SSO configuration for the authenticated
organization. Managing domain mappings is a child concern under this
singleton (``delete_domain``).
"""

from typing import Any

from nextmv.cloud import Client
from nextmv.cloud.sso import SSOConfiguration


def get_sso_configuration(client: Client) -> dict[str, Any]:
    """Get the Nextmv Cloud SSO configuration for the current organization.

    Returns the SSO configuration dict including metadata URL/document,
    enabled status, mapped domains, and allow-non-domain-users flag.
    """
    return SSOConfiguration.get(client=client).to_dict()


def create_sso_configuration(
    client: Client,
    allow_non_domain_users: bool = False,
    enabled: bool = False,
    metadata_url: str | None = None,
    metadata_document: str | None = None,
) -> dict[str, Any]:
    """Create a new Nextmv Cloud SSO configuration.

    Provide exactly one of ``metadata_url`` or ``metadata_document``.
    Set ``enabled`` to activate SSO at the time of creation (otherwise
    run ``enable_sso_configuration`` afterwards).

    Returns the created SSO configuration dict.
    """
    config = SSOConfiguration.new(
        client=client,
        allow_non_domain_users=allow_non_domain_users,
        enabled=enabled,
        metadata_url=metadata_url,
        metadata_document=metadata_document,
    )
    return config.to_dict()


def update_sso_configuration(
    client: Client,
    metadata_url: str | None = None,
    metadata_document: str | None = None,
) -> None:
    """Update the Nextmv Cloud SSO configuration.

    Updates the metadata URL or metadata document of the existing SSO
    configuration.
    """
    sso_config = SSOConfiguration.get(client=client)
    sso_config.update(metadata_url=metadata_url, metadata_document=metadata_document)


def enable_sso_configuration(client: Client) -> None:
    """Enable the Nextmv Cloud SSO configuration."""
    SSOConfiguration.get(client=client).enable()


def disable_sso_configuration(client: Client) -> None:
    """Disable the Nextmv Cloud SSO configuration."""
    SSOConfiguration.get(client=client).disable()


def delete_sso_configuration(client: Client) -> None:
    """Delete the Nextmv Cloud SSO configuration.

    This action cannot be undone, but you can create a new SSO
    configuration afterwards via ``create_sso_configuration``.
    """
    SSOConfiguration.get(client=client).delete()


def delete_domain(client: Client, domain: str) -> None:
    """Delete a domain mapping from the Nextmv Cloud SSO configuration.

    This prevents users from the deleted domain from accessing the
    organization via SSO. Re-adding a mapped domain requires contacting
    Nextmv support.
    """
    SSOConfiguration.get(client=client).delete_domain(domain=domain)
