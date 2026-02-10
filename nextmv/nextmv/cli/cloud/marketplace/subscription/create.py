"""
This module defines the cloud marketplace subscription create command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_client
from nextmv.cli.message import in_progress, print_json
from nextmv.cli.options import ProfileOption
from nextmv.cloud.marketplace import MarketplaceSubscription

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    subscription_id: Annotated[
        str,
        typer.Option(
            "--subscription-id",
            "-s",
            help="The ID of the marketplace application and partner to subscribe to. "
            "Format of the subscription ID: [dim]<PARTNER_ID>-<APP_ID>[/dim].",
            envvar="NEXTMV_MARKETPLACE_SUBSCRIPTION_ID",
            metavar="SUBSCRIPTION_ID",
        ),
    ],
    profile: ProfileOption = None,
) -> None:
    """
    Create a new marketplace subscription.

    Subscribe to a marketplace application by providing the subscription ID,
    which combines the partner ID and application ID in the format
    [dim]<PARTNER_ID>-<APP_ID>[/dim]. This allows you to access and use the
    marketplace application in your account.

    [bold][underline]Examples[/underline][/bold]

    - Subscribe to a marketplace application.
        $ [dim]nextmv cloud marketplace subscription create --subscription-id my-partner-marketplace-hare[/dim]

    - Subscribe to a marketplace application using the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud marketplace subscription create --subscription-id my-partner-marketplace-hare \\
            --profile hare[/dim]
    """

    client = build_client(profile)
    in_progress(msg="Creating subscription...")
    subscription = MarketplaceSubscription.new(client, subscription_id)
    print_json(subscription.to_dict())
