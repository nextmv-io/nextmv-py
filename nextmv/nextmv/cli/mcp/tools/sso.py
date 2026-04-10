"""MCP tools for cloud SSO management."""

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.sso import delete_domain as _delete_domain
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud SSO tools."""

    @mcp.tool()
    def cloud_sso_delete_domain(domain: str) -> str:
        """Delete a domain mapping from the SSO configuration.

        Removes a domain from the current Nextmv Cloud organization's
        SSO configuration. After deletion, users with email addresses
        in that domain will no longer be redirected to the SSO
        identity provider.

        Args:
            domain: The domain to remove (e.g., ``"example.com"``).
        """

        client = _helpers._get_client()
        _delete_domain(client, domain=domain)
        return f"Deleted SSO domain mapping for {domain}"
