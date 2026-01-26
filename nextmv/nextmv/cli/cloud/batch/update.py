"""
This module defines the cloud batch update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, BatchExperimentIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def update(
    app_id: AppIDOption,
    batch_experiment_id: BatchExperimentIDOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Updated description of the batch experiment.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Updated name of the batch experiment.",
            metavar="NAME",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated batch experiment information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Update a Nextmv Cloud batch experiment.

    Update the name and/or description of a batch experiment. Any fields not
    specified will remain unchanged.

    [bold][underline]Examples[/underline][/bold]

    - Update the name of a batch experiment.
        $ [dim]nextmv cloud batch update --app-id hare-app --batch-experiment-id carrot-feast \\
            --name "Spring Carrot Harvest"[/dim]

    - Update the description of a batch experiment.
        $ [dim]nextmv cloud batch update --app-id hare-app --batch-experiment-id bunny-hop-routes \\
            --description "Optimizing hop paths through the meadow"[/dim]

    - Update both name and description and save the result.
        $ [dim]nextmv cloud batch update --app-id hare-app --batch-experiment-id lettuce-delivery \\
            --name "Warren Lettuce Express" --description "Fast lettuce delivery to all burrows" \\
            --output updated-batch.json[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)

    in_progress(msg="Updating batch experiment...")
    batch_experiment = cloud_app.update_batch_experiment(
        batch_experiment_id=batch_experiment_id,
        name=name,
        description=description,
    )

    batch_experiment_dict = batch_experiment.to_dict()
    success(
        f"Batch experiment [magenta]{batch_experiment_id}[/magenta] updated successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(batch_experiment_dict, f, indent=2)

        success(msg=f"Updated batch experiment information saved to [magenta]{output}[/magenta].")
        return

    print_json(batch_experiment_dict)
