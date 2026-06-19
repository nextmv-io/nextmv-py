"""
This module defines the cloud ensemble list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_cloud_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, DebugOption, NoPaginationOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def list(
    app_id: AppIDOption,
    no_pagination: NoPaginationOption = False,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the list of ensemble definitions to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    _: DebugOption = False,
    profile: ProfileOption = None,
) -> None:
    """
    List all Nextmv Cloud ensemble definitions for an application.

    This command retrieves all ensemble definitions associated with the
    specified application. By default this command paginates the list of
    definitions, which means multiple API calls may be made to retrieve all
    definitions. You may use the --no-pagination option to disable pagination.

    [bold][underline]Examples[/underline][/bold]

    - List all ensemble definitions for application [magenta]hare-app[/magenta].

        $ [dim]nextmv cloud ensemble list --app-id hare-app[/dim]

    - List all ensemble definitions and save to a file.

        $ [dim]nextmv cloud ensemble list --app-id hare-app --output ensembles.json[/dim]

    - List all ensemble definitions using a specific profile.

        $ [dim]nextmv cloud ensemble list --app-id hare-app --profile prod[/dim]

    - List all ensemble definitions without pagination.

        $ [dim]nextmv cloud ensemble list --app-id hare-app --no-pagination[/dim]
    """

    cloud_app, _ = build_cloud_app(app_id=app_id, profile=profile)
    in_progress(msg="Listing ensemble definitions...")
    ensembles = cloud_app.list_ensemble_definitions(no_pagination)
    ensembles_dict = [ensemble.to_dict() for ensemble in ensembles]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(ensembles_dict, f, indent=2)

        success(msg=f"Ensemble definitions list saved to [magenta]{output}[/magenta].")

        return

    print_json(ensembles_dict)
