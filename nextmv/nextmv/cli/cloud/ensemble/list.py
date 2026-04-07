"""
This module defines the cloud ensemble list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.actions.ensemble import list_ensembles as _list_ensembles
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
            help="Saves the list of ensemble definitions to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    List all Nextmv Cloud ensemble definitions for an application.

    This command retrieves all ensemble definitions associated with the specified
    application.

    [bold][underline]Examples[/underline][/bold]

    - List all ensemble definitions for application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud ensemble list --app-id hare-app[/dim]

    - List all ensemble definitions and save to a file.
        $ [dim]nextmv cloud ensemble list --app-id hare-app --output ensembles.json[/dim]

    - List all ensemble definitions using a specific profile.
        $ [dim]nextmv cloud ensemble list --app-id hare-app --profile prod[/dim]
    """

    client = Client(profile=profile)
    in_progress(msg="Listing ensemble definitions...")
    ensembles_dict = _list_ensembles(client, app_id)

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(ensembles_dict, f, indent=2)

        success(msg=f"Ensemble definitions list saved to [magenta]{output}[/magenta].")

        return

    print_json(ensembles_dict)
