"""
This module defines the cloud account update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_account
from nextmv.cli.message import print_json, success
from nextmv.cli.options import AccountIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def update(
    account_id: AccountIDOption,
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="A new name for the account.",
            metavar="NAME",
        ),
    ],
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated account information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Updates information of a Nextmv Cloud account.

    This command allows you to update the name of an existing account.

    [bold][underline]Examples[/underline][/bold]

    - Update the account named [magenta]hare-delivery[/magenta] to [magenta]Hare Delivery Co[/magenta].
        $ [dim]nextmv cloud account update --account-id hare-delivery \\
            --name "Hare Delivery Co"[/dim]

    - Update an account and save the updated information to an [magenta]updated_account.json[/magenta] file.
        $ [dim]nextmv cloud account update --account-id cottontail-couriers \\
            --name "Cottontail Express" --output updated_account.json[/dim]
    """

    cloud_account = build_account(account_id=account_id, profile=profile)
    updated_account = cloud_account.update(name=name)
    success(f"Account [magenta]{account_id}[/magenta] updated successfully.")
    updated_account_dict = updated_account.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(updated_account_dict, f, indent=2)

        success(msg=f"Updated account information saved to [magenta]{output}[/magenta].")

        return

    print_json(updated_account_dict)
