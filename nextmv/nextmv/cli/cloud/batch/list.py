"""
This module defines the cloud batch list command for the Nextmv CLI.
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

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Listing batch experiments...")
    batch_experiments = cloud_app.list_batch_experiments()
    batch_experiments_dict = [exp.to_dict() for exp in batch_experiments]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(batch_experiments_dict, f, indent=2)

        success(msg=f"Batch experiments list saved to [magenta]{output}[/magenta].")

        return

    print_json(batch_experiments_dict)
