"""
This module defines the cloud marketplace subscription delete command for the Nextmv CLI.
"""

import typer

from nextmv.cli.configuration.config import build_marketplace_subscription
from nextmv.cli.message import confirmation, info, success
from nextmv.cli.options import DebugOption, MarketplaceSubscriptionIDOption, ProfileOption, YesOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    subscription_id: MarketplaceSubscriptionIDOption,
    yes: YesOption = False,
    profile: ProfileOption = None,
    _: DebugOption = False,
) -> None:
    """
    Delete a marketplace subscription.

    Use the --yes flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete a marketplace subscription.

        $ [dim]nextmv cloud marketplace subscription delete --subscription-id my-partner-marketplace-hare[/dim]

    - Delete a marketplace subscription without confirmation prompt.

        $ [dim]nextmv cloud marketplace subscription delete --subscription-id my-partner-marketplace-hare \\
            --yes[/dim]
    """

    if not yes:
        confirm = confirmation(
            f"Are you sure you want to delete subscription with ID [magenta]{subscription_id}[/magenta]?",
        )

        if not confirm:
            info(f"Subscription [magenta]{subscription_id}[/magenta] will not be deleted.")
            return

    subscription = build_marketplace_subscription(subscription_id=subscription_id, profile=profile)
    subscription.delete()
    success(
        f"Subscription [magenta]{subscription_id}[/magenta] deleted successfully. Re-subscribe with "
        f"[code]nextmv cloud marketplace subscription create --subscription-id {subscription_id}[/code]."
    )
