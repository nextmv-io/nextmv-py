"""
This module defines the cloud marketplace subscription get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_marketplace_subscription
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import DebugOption, MarketplaceSubscriptionIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    subscription_id: MarketplaceSubscriptionIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the subscription information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    _: DebugOption = False,
    profile: ProfileOption = None,
) -> None:
    """
    Get a marketplace subscription.

    [bold][underline]Examples[/underline][/bold]

    - Get a marketplace subscription.
        $ [dim]nextmv cloud marketplace subscription get --subscription-id my-partner-marketplace-hare[/dim]

    - Get a marketplace subscription and save the information to a [magenta]subscription.json[/magenta] file.
        $ [dim]nextmv cloud marketplace subscription get --subscription-id my-partner-marketplace-hare \\
            --output subscription.json[/dim]
    """

    in_progress(msg="Getting subscription...")
    subscription = build_marketplace_subscription(subscription_id=subscription_id, profile=profile)
    subscription_dict = subscription.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(subscription_dict, f, indent=2)

        success(msg=f"Subscription information saved to [magenta]{output}[/magenta].")

        return

    print_json(subscription_dict)
