"""
This module defines the cloud input-set update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import error, in_progress, print_json, success
from nextmv.cli.options import AppIDOption, InputSetIDOption, ProfileOption
from nextmv.cloud.input_set import ManagedInput

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
    managed_inputs: Annotated[
        str | None,
        typer.Option(
            "--managed-inputs",
            help="Managed inputs for the input set. Data should be valid [magenta]json[/magenta]. Object "
            "format: [dim][{'id': 'id', 'name': 'name', 'description': 'description'}][/dim].",
            metavar="MANAGED_INPUTS",
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
    Updates a Nextmv Cloud input set.

    This command updates the metadata of an existing input set. You can update
    the name, description, or managed inputs of the input set.

    [bold][underline]Examples[/underline][/bold]

    - Update an input set's name.
        $ [dim]nextmv cloud input-set update --app-id hare-app \\
            --input-set-id hare-input-set --name "New Name"[/dim]

    - Update an input set's description.
        $ [dim]nextmv cloud input-set update --app-id hare-app \\
            --input-set-id hare-input-set --description "Updated description"[/dim]

    - Update an input set's managed inputs.
        $ [dim]nextmv cloud input-set update --app-id hare-app --input-set-id hare-input-set \\
            --managed-inputs '[{"id": "hare-input-1", "name": "hare input", "description": "hare description"}]'[/dim]

    - Update both name and description.
        $ [dim]nextmv cloud input-set update --app-id hare-app --input-set-id hare-input-set \\
            --name "New Name" --description "Updated description"[/dim]

    - Update and save to a file.
        $ [dim]nextmv cloud input-set update --app-id hare-app --input-set-id hare-input-set \\
            --name "New Name" --output updated_input_set.json[/dim]
    """

    if name is None and description is None and managed_inputs is None:
        error("Provide at least one option: --name, --description, or --managed-inputs.")

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Updating input set...")

    managed_input_list = []
    if managed_inputs is not None:
        for d in json.loads(managed_inputs):
            i = ManagedInput.from_dict(d)
            if i is None:
                error(f"[magenta]{d}[/magenta] is not a valid [yellow]ManagedInput[/yellow]")
            managed_input_list.append(i)

    updated_input_set = cloud_app.update_input_set(
        id=input_set_id,
        name=name,
        description=description,
        inputs=managed_input_list,
    )
    success(
        f"Input set [magenta]{input_set_id}[/magenta] updated successfully in application [magenta]{app_id}[/magenta]."
    )
    updated_input_set_dict = updated_input_set.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(updated_input_set_dict, f, indent=2)

        success(msg=f"Updated input set information saved to [magenta]{output}[/magenta].")

        return

    print_json(updated_input_set_dict)
