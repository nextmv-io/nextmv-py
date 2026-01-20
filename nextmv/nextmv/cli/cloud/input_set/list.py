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
    List all input sets for an application.

    This command retrieves all input sets that have been created for the
    specified application.

    [bold][underline]Examples[/underline][/bold]

    - List all input sets for an application.
        $ [green]nextmv cloud input-set list --app-id my-app[/green]

    - List all input sets and save to a file.
        $ [green]nextmv cloud input-set list --app-id my-app --output input-sets.json[/green]

    - List input sets using a specific profile.
        $ [green]nextmv cloud input-set list --app-id my-app --profile my-profile[/green]
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
