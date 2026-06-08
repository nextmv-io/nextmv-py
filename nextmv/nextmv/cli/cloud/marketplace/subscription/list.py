"""
This module defines the cloud marketplace subscription list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import DebugOption, ProfileOption
from nextmv.cloud.client import Client
from nextmv.cloud.marketplace import list_marketplace_subscriptions

# Set up subcommand application.
app = typer.Typer()


@app.command()
def list(
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the subscription list information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    _: DebugOption = False,
    profile: ProfileOption = None,
) -> None:
    """
    List all marketplace subscriptions.

    [bold][underline]Examples[/underline][/bold]

    - List all marketplace subscriptions.
        $ [dim]nextmv cloud marketplace subscription list[/dim]

    - List all subscriptions using the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud marketplace subscription list --profile hare[/dim]

    - List all subscriptions and save the information to a [magenta]subscriptions.json[/magenta] file.
        $ [dim]nextmv cloud marketplace subscription list --output subscriptions.json[/dim]
    """

    client = Client(profile=profile)
    in_progress(msg="Listing subscriptions...")

    subscriptions = list_marketplace_subscriptions(client)
    subscriptions_dicts = [sub.to_dict() for sub in subscriptions]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(subscriptions_dicts, f, indent=2)

        success(msg=f"Subscription list information saved to [magenta]{output}[/magenta].")

        return

    print_json(subscriptions_dicts)
