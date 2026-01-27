"""
This module defines the cloud account get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_client
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AccountIDOption, ProfileOption
from nextmv.cloud.account import Account

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    account_id: AccountIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the account information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get the information of a Nextmv Cloud account.

    This command is useful to get the attributes of an existing Nextmv Cloud
    account by its ID.

    [bold][underline]Examples[/underline][/bold]

    - Get the account with the ID [magenta]bunny-logistics[/magenta].
        $ [dim]nextmv cloud account get --account-id bunny-logistics[/dim]

    - Get the account with the ID [magenta]cottontail-couriers[/magenta] and save the information to an
      [magenta]account.json[/magenta] file.
        $ [dim]nextmv cloud account get --account-id cottontail-couriers --output account.json[/dim]
    """

    client = build_client(profile)
    in_progress(msg="Getting account...")

    cloud_account = Account.get(
        client=client,
        account_id=account_id,
    )
    cloud_account_dict = cloud_account.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(cloud_account_dict, f, indent=2)

        success(msg=f"Account information saved to [magenta]{output}[/magenta].")

        return

    print_json(cloud_account_dict)
