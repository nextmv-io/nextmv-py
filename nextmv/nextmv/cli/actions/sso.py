"""Core SSO management actions.

Pure functions that wrap SDK calls. No CLI or MCP concerns.
"""

from nextmv.cloud import Client
from nextmv.cloud.sso import SSOConfiguration


def delete_domain(client: Client, domain: str) -> None:
    """Delete a domain mapping from the SSO configuration."""
    SSOConfiguration.get(client=client).delete_domain(domain=domain)
