"""
This module defines the cloud ensemble list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption

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

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Listing ensemble definitions...")
    ensembles = cloud_app.list_ensemble_definitions()
    ensembles_dict = [ensemble.to_dict() for ensemble in ensembles]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(ensembles_dict, f, indent=2)

        success(msg=f"Ensemble definitions list saved to [magenta]{output}[/magenta].")

        return

    print_json(ensembles_dict)
