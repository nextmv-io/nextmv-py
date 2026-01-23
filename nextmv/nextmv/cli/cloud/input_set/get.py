"""
This module defines the cloud input-set get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_client
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, InputSetIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    app_id: AppIDOption,
    input_set_id: InputSetIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the input set information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get an Nextmv Cloud input set.

    This command retrieves the details of an existing input set, including
    its name, description, and the list of inputs it contains.

    [bold][underline]Examples[/underline][/bold]

    - Get an input set with the ID [magenta]hare-input-set[/magenta].
        $ [green]nextmv cloud input-set get --app-id hare-app --input-set-id hare-input-set[/green]

    - Get an input set with the ID [magenta]hare-input-set[/magenta] and save
      the information to a [magenta]input-set.json[/magenta] file.
        $ [green]nextmv cloud input-set get --app-id hare-app --input-set-id hare-input-set \\
            --output input-set.json[/green]
    """

    client = build_client(profile)
    in_progress(msg="Getting input set...")

    response = client.request(
        method="GET",
        endpoint=f"/v1/applications/{app_id}/experiments/inputsets/{input_set_id}",
    )
    input_set_data = response.json()

    if output is not None:
        with open(output, "w") as f:
            json.dump(input_set_data, f, indent=2)

        success(msg=f"Input set information saved to [magenta]{output}[/magenta].")

        return

    print_json(input_set_data)
