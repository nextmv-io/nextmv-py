"""
This module defines the cloud managed-input update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import error, print_json, success
from nextmv.cli.options import AppIDOption, ManagedInputIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def update(
    app_id: AppIDOption,
    managed_input_id: ManagedInputIDOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="A new description for the managed input.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="A new name for the managed input.",
            metavar="NAME",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated managed input information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Updates a Nextmv Cloud application managed input.

    [bold][underline]Examples[/underline][/bold]

    - Update a managed input's name.
        $ [dim]nextmv cloud managed-input update --app-id hare-app \
            --managed-input-id inp_123456789 --name "Updated Test Input"[/dim]

    - Update a managed input's description.
        $ [dim]nextmv cloud managed-input update --app-id hare-app --managed-input-id inp_123456789 \\
            --description "Updated test case for validation"[/dim]

    - Update a managed input's name and description at once.
        $ [dim]nextmv cloud managed-input update --app-id hare-app --managed-input-id inp_123456789 \\
            --name "Updated Test Input" --description "Updated test case for validation"[/dim]

    - Update a managed input and save the updated information to a [magenta]updated_managed_input.json[/magenta] file.
        $ [dim]nextmv cloud managed-input update --app-id hare-app --managed-input-id inp_123456789 \\
            --name "Updated Test Input" --output updated_managed_input.json[/dim]
    """

    if name is None and description is None:
        error("Provide at least one option to update: --name or --description.")

    cloud_app = build_app(app_id=app_id, profile=profile)

    updated_managed_input = cloud_app.update_managed_input(
        managed_input_id=managed_input_id,
        name=name,
        description=description,
    )
    success(
        f"Managed input [magenta]{managed_input_id}[/magenta] updated successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
    updated_managed_input_dict = updated_managed_input.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(updated_managed_input_dict, f, indent=2)

        success(msg=f"Updated managed input information saved to [magenta]{output}[/magenta].")

        return

    print_json(updated_managed_input_dict)
