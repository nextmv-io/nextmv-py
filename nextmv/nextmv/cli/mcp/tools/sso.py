"""MCP tools for cloud SSO management."""

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.sso import delete_domain, get_sso_configuration
from nextmv.cli.mcp import framework as mcp_fw


def register(mcp: FastMCP) -> None:
    """Register cloud SSO tools.

    Only read-only and surgical operations are exposed via MCP. Creating,
    updating, enabling, disabling, and deleting the SSO configuration are
    destructive organization-wide actions that require confirmation in
    their CLI flow; they are intentionally not available to MCP clients.
    """

    mcp_fw.tool(mcp, get_sso_configuration, name="cloud_get_sso_configuration")

    mcp_fw.tool(
        mcp,
        delete_domain,
        name="cloud_sso_delete_domain",
        result_message="Deleted SSO domain mapping for {domain}",
    )
