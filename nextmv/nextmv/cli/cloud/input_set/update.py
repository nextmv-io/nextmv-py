"""
This module defines the cloud input-set update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_client
from nextmv.cli.message import error, in_progress, print_json, success
from nextmv.cli.options import AppIDOption, InputSetIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def update(
    app_id: AppIDOption,
    input_set_id: InputSetIDOption,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="A new name for the input set.",
            metavar="NAME",
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="A new description for the input set.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated input set information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Update an existing input set.

    This command updates the metadata of an existing input set. You can update
    the name and/or description of the input set.

    [bold][underline]Examples[/underline][/bold]

    - Update an input set's name.
        $ [green]nextmv cloud input-set update --app-id my-app --input-set-id my-input-set \\
            --name "New Name"[/green]

    - Update an input set's description.
        $ [green]nextmv cloud input-set update --app-id my-app --input-set-id my-input-set \\
            --description "Updated description"[/green]

    - Update both name and description.
        $ [green]nextmv cloud input-set update --app-id my-app --input-set-id my-input-set \\
            --name "New Name" --description "Updated description"[/green]

    - Update and save to a file.
        $ [green]nextmv cloud input-set update --app-id my-app --input-set-id my-input-set \\
            --name "New Name" --output updated-input-set.json[/green]
    """

    if name is None and description is None:
        error("Provide at least one option to update: [code]--name[/code] or [code]--description[/code].")

    client = build_client(profile)
    in_progress(msg="Updating input set...")

    # Build the request payload
    payload: dict = {}

    if name is not None:
        payload["name"] = name

    if description is not None:
        payload["description"] = description

    response = client.request(
        method="PUT",
        endpoint=f"/v1/applications/{app_id}/experiments/inputsets/{input_set_id}",
        payload=payload,
    )
    input_set_data = response.json()

    success(f"Input set [magenta]{input_set_id}[/magenta] updated successfully.")

    if output is not None:
        with open(output, "w") as f:
            json.dump(input_set_data, f, indent=2)

        success(msg=f"Updated input set information saved to [magenta]{output}[/magenta].")

        return

    print_json(input_set_data)
