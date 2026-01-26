"""
This module defines the cloud batch metadata command for the Nextmv CLI.
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
def metadata(
    app_id: AppIDOption,
    batch_experiment_id: BatchExperimentIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the batch experiment metadata to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get metadata for a Nextmv Cloud batch experiment.

    This command retrieves metadata for a specific batch experiment, including
    status, creation date, and other high-level information without the full
    run details.

    [bold][underline]Examples[/underline][/bold]

    - Get metadata for batch experiment [magenta]bunny-warren-optimization[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud batch metadata --app-id hare-app --batch-experiment-id bunny-warren-optimization[/dim]

    - Get metadata and save to a file.
        $ [dim]nextmv cloud batch metadata --app-id hare-app --batch-experiment-id lettuce-delivery \\
            --output metadata.json[/dim]

    - Get metadata using a specific profile.
        $ [dim]nextmv cloud batch metadata --app-id hare-app --batch-experiment-id hop-schedule --profile prod[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Getting batch experiment metadata...")
    batch_metadata = cloud_app.batch_experiment_metadata(batch_id=batch_experiment_id)
    batch_metadata_dict = batch_metadata.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(batch_metadata_dict, f, indent=2)

        success(msg=f"Batch experiment metadata saved to [magenta]{output}[/magenta].")
        return

    print_json(batch_metadata_dict)
