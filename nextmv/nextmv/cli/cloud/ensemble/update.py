"""
This module defines the cloud ensemble update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import error, print_json, success
from nextmv.cli.options import AppIDOption, EnsembleDefinitionIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def update(
    app_id: AppIDOption,
    ensemble_definition_id: EnsembleDefinitionIDOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="A new description for the ensemble definition.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="A new name for the ensemble definition.",
            metavar="NAME",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated ensemble definition information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Update a Nextmv Cloud ensemble definition.

    You can update the name and/or description of an existing ensemble
    definition. To modify run groups or evaluation rules, you need to delete
    and recreate the ensemble definition.

    [bold][underline]Examples[/underline][/bold]

    - Update the name of an ensemble definition.
        $ [dim]nextmv cloud ensemble update --app-id hare-app \\
            --ensemble-definition-id prod-ensemble --name "Updated Production Ensemble"[/dim]

    - Update the description of an ensemble definition.
        $ [dim]nextmv cloud ensemble update --app-id hare-app \\
            --ensemble-definition-id prod-ensemble \\
            --description "Updated ensemble for production workloads"[/dim]

    - Update both name and description.
        $ [dim]nextmv cloud ensemble update --app-id hare-app \\
            --ensemble-definition-id prod-ensemble --name "Production Ensemble v2" \\
            --description "Enhanced ensemble configuration for production"[/dim]

    - Update and save the result to a file.
        $ [dim]nextmv cloud ensemble update --app-id hare-app \\
            --ensemble-definition-id prod-ensemble --name "New Name" \\
            --description "New Description" --output updated.json[/dim]
    """

    if name is None and description is None:
        error("Provide at least one option to update: --name or --description.")

    cloud_app = build_app(app_id=app_id, profile=profile)

    ensemble_definition = cloud_app.update_ensemble_definition(
        id=ensemble_definition_id,
        name=name,
        description=description,
    )
    success(
        f"Ensemble definition [magenta]{ensemble_definition_id}[/magenta] updated successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(ensemble_definition.to_dict(), f, indent=2)

        success(msg=f"Updated ensemble definition information saved to [magenta]{output}[/magenta].")

        return

    print_json(ensemble_definition.to_dict())
