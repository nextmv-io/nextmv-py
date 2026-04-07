"""MCP tools for cloud account management."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.account import get_account as _get_account
from nextmv.cli.actions.account import get_queue as _get_queue
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud account tools."""

    @mcp.tool()
    def cloud_get_account(account_id: str) -> dict[str, Any]:
        """Get details of a Nextmv Cloud account.

        Returns account information including organization name,
        plan details, and usage limits.

        Args:
            account_id: The account ID to retrieve.
        """

        client = _helpers._get_client()
        return _get_account(client, account_id=account_id)

    @mcp.tool()
    def cloud_get_queue(account_id: str) -> dict[str, Any]:
        """Get the run queue for a Nextmv Cloud account.

        Returns information about currently queued and running runs
        across all applications in the account, including queue
        depth and concurrency usage.

        Args:
            account_id: The account ID.
        """

        client = _helpers._get_client()
        return _get_queue(client, account_id=account_id)
