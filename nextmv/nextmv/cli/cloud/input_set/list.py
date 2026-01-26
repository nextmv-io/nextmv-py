"""
This module defines the cloud input-set list command for the Nextmv CLI.
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
            help="Saves the input set list to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    List all input sets of a Nextmv Cloud application.

    This command retrieves all input sets that exist for a given Nextmv Cloud
    application.

    [bold][underline]Examples[/underline][/bold]

    - List all input sets of application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud input-set list --app-id hare-app[/dim]

    - List all input sets using the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud input-set list --app-id hare-app --profile hare[/dim]

    - List all input sets and save the information to a [magenta]input-sets.json[/magenta] file.
        $ [dim]nextmv cloud input-set list --app-id hare-app --output input-sets.json[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Listing input sets...")
    input_sets = cloud_app.list_input_sets()
    input_sets_dicts = [input_set.to_dict() for input_set in input_sets]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(input_sets_dicts, f, indent=2)

        success(msg=f"Input set list information saved to [magenta]{output}[/magenta].")

        return

    print_json(input_sets_dicts)
