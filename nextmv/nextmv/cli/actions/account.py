"""Core account management actions.

Pure functions that wrap SDK calls. No CLI or MCP concerns.
"""

from typing import Any

from nextmv.cloud import Client
from nextmv.cloud.account import Account


def get_account(client: Client, account_id: str) -> dict[str, Any]:
    """Get account details."""
    return Account.get(client=client, account_id=account_id).to_dict()


def get_queue(client: Client, account_id: str) -> dict[str, Any]:
    """Get the run queue for an account."""
    return Account.get(client=client, account_id=account_id).queue().to_dict()
