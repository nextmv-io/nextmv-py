"""
This module defines the cloud batch get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, BatchExperimentIDOption, ProfileOption
from nextmv.polling import default_polling_options

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    app_id: AppIDOption,
    batch_experiment_id: BatchExperimentIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Waits for the batch experiment to complete and saves the results to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    timeout: Annotated[
        int,
        typer.Option(
            help="The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.",
            metavar="TIMEOUT_SECONDS",
        ),
    ] = -1,
    wait: Annotated[
        bool,
        typer.Option(
            "--wait",
            "-w",
            help="Wait for the batch experiment to complete. Results are printed to [magenta]stdout[/magenta]. "
            "Specify output location with --output.",
        ),
    ] = False,
    profile: ProfileOption = None,
) -> None:
    """
    Get a Nextmv Cloud batch experiment, including its runs.

    Use the --wait flag to wait for the batch experiment to
    complete, polling for results. Using the --output flag will
    also activate waiting, and allows you to specify a destination file for the
    results.

    [bold][underline]Examples[/underline][/bold]

    - Get the batch experiment with ID [magenta]carrot-optimization[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud batch get --app-id hare-app --batch-experiment-id carrot-optimization[/dim]

    - Get the batch experiment and wait for it to complete if necessary.
        $ [dim]nextmv cloud batch get --app-id hare-app --batch-experiment-id bunny-hop-test --wait[/dim]

    - Get the batch experiment and save the results to a file.
        $ [dim]nextmv cloud batch get --app-id hare-app --batch-experiment-id warren-planning \\
            --output results.json[/dim]

    - Get the batch experiment using a specific profile.
        $ [dim]nextmv cloud batch get --app-id hare-app --batch-experiment-id lettuce-routes --profile prod[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)

    # Build the polling options.
    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    # Determine if we should wait
    should_wait = wait or (output is not None and output != "")

    in_progress(msg="Getting batch experiment...")
    if should_wait:
        batch_experiment = cloud_app.batch_experiment_with_polling(
            batch_id=batch_experiment_id,
            polling_options=polling_options,
        )
    else:
        batch_experiment = cloud_app.batch_experiment(batch_id=batch_experiment_id)

    batch_experiment_dict = batch_experiment.to_dict()

    # Handle output
    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(batch_experiment_dict, f, indent=2)

        success(msg=f"Batch experiment results saved to [magenta]{output}[/magenta].")

        return

    print_json(batch_experiment_dict)
