"""
This module defines the cloud ensemble get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, EnsembleDefinitionIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    app_id: AppIDOption,
    ensemble_definition_id: EnsembleDefinitionIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the ensemble definition information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get a Nextmv Cloud ensemble definition.

    This command is useful to get the attributes of an existing Nextmv Cloud
    ensemble definition by its ID.

    [bold][underline]Examples[/underline][/bold]

    - Get the ensemble definition with the ID [magenta]prod-ensemble[/magenta] from
      application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud ensemble get --app-id hare-app \\
        --ensemble-definition-id prod-ensemble[/dim]

    - Get the ensemble definition with the ID [magenta]prod-ensemble[/magenta] and
      save the information to an [magenta]ensemble.json[/magenta] file.
        $ [dim]nextmv cloud ensemble get --app-id hare-app \\
            --ensemble-definition-id prod-ensemble --output ensemble.json[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Getting ensemble definition...")
    ensemble_definition = cloud_app.ensemble_definition(ensemble_definition_id=ensemble_definition_id)
    ensemble_definition_dict = ensemble_definition.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(ensemble_definition_dict, f, indent=2)

        success(msg=f"Ensemble definition information saved to [magenta]{output}[/magenta].")

        return

    print_json(ensemble_definition_dict)
