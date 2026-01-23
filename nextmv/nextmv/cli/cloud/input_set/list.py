"""
This module defines the cloud input-set list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_client
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
        $ [green]nextmv cloud input-set list --app-id hare-app[/green]

    - List all input sets using the profile named [magenta]hare[/magenta].
        $ [green]nextmv cloud input-set list --app-id hare-app --profile hare[/green]

    - List all input sets and save the information to a [magenta]input-sets.json[/magenta] file.
        $ [green]nextmv cloud input-set list --app-id hare-app --output input-sets.json[/green]
    """

    client = build_client(profile)
    in_progress(msg="Listing input sets...")

    response = client.request(
        method="GET",
        endpoint=f"/v1/applications/{app_id}/experiments/inputsets",
    )
    input_sets_data = response.json()

    if output is not None:
        with open(output, "w") as f:
            json.dump(input_sets_data, f, indent=2)

        success(msg=f"Input set list saved to [magenta]{output}[/magenta].")

        return

    print_json(input_sets_data)
