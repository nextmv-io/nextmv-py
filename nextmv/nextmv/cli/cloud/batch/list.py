"""
This module defines the cloud batch list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.actions.batch import list_batches as _list_batches
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.client import Client

# Set up subcommand application.
app = typer.Typer()


@app.command()
def list(
    app_id: AppIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the list of batch experiments to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    List all Nextmv Cloud batch experiments for an application.

    This command retrieves all batch experiments associated with the specified
    application.

    [bold][underline]Examples[/underline][/bold]

    - List all batch experiments for application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud batch list --app-id hare-app[/dim]

    - List all batch experiments and save to a file.
        $ [dim]nextmv cloud batch list --app-id hare-app --output experiments.json[/dim]

    - List all batch experiments using a specific profile.
        $ [dim]nextmv cloud batch list --app-id hare-app --profile prod[/dim]
    """

    client = Client(profile=profile)
    in_progress(msg="Listing batch experiments...")
    batch_experiments_dict = _list_batches(client, app_id)

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(batch_experiments_dict, f, indent=2)

        success(msg=f"Batch experiments list saved to [magenta]{output}[/magenta].")

        return

    print_json(batch_experiments_dict)
