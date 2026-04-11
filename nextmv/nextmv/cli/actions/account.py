"""Core account management actions.

Pure functions that wrap SDK calls. No CLI or MCP presentation concerns.

Account management requires an SSO-enabled organization. Most operations
take an account ID; create takes a name and a list of admin email
addresses.
"""

from typing import Any

from nextmv.cli.framework.options import AccountIdOption, NameOption
from nextmv.cloud import Client
from nextmv.cloud.account import Account


def get_account(
    client: Client,
    account_id: AccountIdOption,
) -> dict[str, Any]:
    """Get details of a Nextmv Cloud account.

    Returns the account dict including ID, name, and administrator list.
    """
    return Account.get(client=client, account_id=account_id).to_dict()


def get_queue(
    client: Client,
    account_id: AccountIdOption,
) -> dict[str, Any]:
    """Get the run queue for a Nextmv Cloud account.

    Returns the account's current queue state, including queued and
    running jobs.
    """
    return Account.get(client=client, account_id=account_id).queue().to_dict()


def create_account(
    client: Client,
    name: NameOption,
    admins: list[str],
) -> dict[str, Any]:
    """Create a new Nextmv Cloud account in your organization.

    To create managed accounts, SSO must be configured for your
    organization. At least one administrator email address must be
    provided.

    Returns the created account dict.
    """
    return Account.new(client=client, name=name, admins=admins).to_dict()


def update_account(
    client: Client,
    account_id: AccountIdOption,
    name: NameOption,
) -> dict[str, Any]:
    """Update a Nextmv Cloud account's name.

    Returns the updated account dict.
    """
    account = Account.get(client=client, account_id=account_id)
    return account.update(name=name).to_dict()


def delete_account(
    client: Client,
    account_id: AccountIdOption,
) -> None:
    """Delete a Nextmv Cloud account permanently.

    You must have the ``administrator`` role on the account to delete
    it. This action cannot be undone.
    """
    Account.get(client=client, account_id=account_id).delete()
