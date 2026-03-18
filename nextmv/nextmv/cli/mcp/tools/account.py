"""MCP tools for cloud account management."""

from typing import Any

from mcp.server.fastmcp import FastMCP

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

        from nextmv.cloud.account import Account

        client = _helpers._get_client()
        account = Account.get(client=client, account_id=account_id)
        return account.to_dict()

    @mcp.tool()
    def cloud_get_queue(account_id: str) -> dict[str, Any]:
        """Get the run queue for a Nextmv Cloud account.

        Returns information about currently queued and running runs
        across all applications in the account, including queue
        depth and concurrency usage.

        Args:
            account_id: The account ID.
        """

        from nextmv.cloud.account import Account

        client = _helpers._get_client()
        account = Account.get(client=client, account_id=account_id)
        queue = account.queue()
        return queue.to_dict()
