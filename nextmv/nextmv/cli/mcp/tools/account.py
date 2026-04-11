"""MCP tools for cloud account management."""

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.account import (
    create_account,
    delete_account,
    get_account,
    get_queue,
    update_account,
)
from nextmv.cli.mcp import framework as mcp_fw


def register(mcp: FastMCP) -> None:
    """Register cloud account tools."""

    mcp_fw.tool(mcp, get_account, name="cloud_get_account")
    mcp_fw.tool(mcp, get_queue, name="cloud_get_queue")
    mcp_fw.tool(mcp, create_account, name="cloud_create_account")
    mcp_fw.tool(mcp, update_account, name="cloud_update_account")
    mcp_fw.tool(
        mcp,
        delete_account,
        name="cloud_delete_account",
        result_message="Deleted account {account_id}",
    )
