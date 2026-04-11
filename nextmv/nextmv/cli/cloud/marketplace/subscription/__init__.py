"""Cloud marketplace subscription command tree for the Nextmv CLI.

All four commands (list, get, create, delete) wrap pure action
functions in ``nextmv.cli.actions.marketplace`` via ``cli.command()``.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.marketplace import (
    create_marketplace_subscription,
    delete_marketplace_subscription,
    get_marketplace_subscription,
    list_marketplace_subs,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Manage Nextmv Marketplace subscriptions.

    These commands allow you to view and manage your subscriptions to
    Marketplace applications.
    """
    pass


LIST_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "List all marketplace subscriptions.",
        "nextmv cloud marketplace subscription list",
    ),
    (
        "List all subscriptions and save the information to a "
        "[magenta]subscriptions.json[/magenta] file.",
        "nextmv cloud marketplace subscription list --output subscriptions.json",
    ),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get a marketplace subscription.",
        "nextmv cloud marketplace subscription get --subscription-id my-partner-marketplace-hare",
    ),
    (
        "Get a marketplace subscription and save the information to a file.",
        "nextmv cloud marketplace subscription get \\\n"
        "    --subscription-id my-partner-marketplace-hare \\\n"
        "    --output subscription.json",
    ),
)

CREATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Subscribe to a marketplace application.",
        "nextmv cloud marketplace subscription create \\\n"
        "    --subscription-id my-partner-marketplace-hare",
    ),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Delete a marketplace subscription.",
        "nextmv cloud marketplace subscription delete \\\n"
        "    --subscription-id my-partner-marketplace-hare",
    ),
    (
        "Delete a marketplace subscription without confirmation prompt.",
        "nextmv cloud marketplace subscription delete \\\n"
        "    --subscription-id my-partner-marketplace-hare --yes",
    ),
)


list = cli.command(  # noqa: A001
    app,
    list_marketplace_subs,
    name="list",
    progress="Listing subscriptions...",
    output_flag=True,
    saved_noun="Subscription list information",
    examples=LIST_EXAMPLES,
)

get = cli.command(
    app,
    get_marketplace_subscription,
    name="get",
    progress="Getting subscription...",
    output_flag=True,
    saved_noun="Subscription information",
    examples=GET_EXAMPLES,
)

create = cli.command(
    app,
    create_marketplace_subscription,
    name="create",
    progress="Creating subscription...",
    examples=CREATE_EXAMPLES,
)

delete = cli.command(
    app,
    delete_marketplace_subscription,
    name="delete",
    progress="Deleting subscription...",
    delete_confirm=cli.DeleteConfirmation(
        confirm=(
            "Are you sure you want to delete subscription with ID "
            "[magenta]{subscription_id}[/magenta]?"
        ),
        decline="Subscription [magenta]{subscription_id}[/magenta] will not be deleted.",
        succeeded=(
            "Subscription [magenta]{subscription_id}[/magenta] deleted successfully. "
            "Re-subscribe with [code]nextmv cloud marketplace subscription create "
            "--subscription-id {subscription_id}[/code]."
        ),
    ),
    examples=DELETE_EXAMPLES,
)
