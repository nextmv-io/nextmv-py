"""
This module defines the cloud input-set create command for the Nextmv CLI.
"""

import json
from datetime import datetime
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import error, in_progress, print_json
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.input_set import ManagedInput
from nextmv.safe import safe_id

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    app_id: AppIDOption,
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="A name for the input set.",
            metavar="NAME",
        ),
    ],
    input_set_id: Annotated[
        str | None,
        typer.Option(
            "--input-set-id",
            "-s",
            help="An optional ID for the input set. If not provided, a random ID will be generated.",
            envvar="NEXTMV_INPUT_SET_ID",
            metavar="INPUT_SET_ID",
        ),
    ] = None,
    instance_id: Annotated[
        str | None,
        typer.Option(
            "--instance-id",
            "-i",
            help="Instance ID to filter runs from.",
            metavar="INSTANCE_ID",
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="An optional description for the input set.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    run_ids: Annotated[
        list[str] | None,
        typer.Option(
            "--run-ids",
            "-r",
            help="List of run IDs to include in the input set (max 20). Pass multiple run IDs by repeating the flag.",
            metavar="RUN_IDS",
        ),
    ] = None,
    start_time: Annotated[
        datetime | None,
        typer.Option(
            "--start-time",
            formats=["%Y-%m-%dT%H:%M:%S%z"],
            help="Start time for filtering runs in [magenta]RFC 3339[/magenta] format. "
            "Object format: [dim]'2024-01-01T00:00:00Z'[/dim]",
            metavar="START_TIME",
        ),
    ] = None,
    end_time: Annotated[
        datetime | None,
        typer.Option(
            "--end-time",
            formats=["%Y-%m-%dT%H:%M:%S%z"],
            help="End time for filtering runs in [magenta]RFC 3339[/magenta] format. "
            "Object format: [dim]'2024-01-01T00:00:00Z'[/dim]",
            metavar="END_TIME",
        ),
    ] = None,
    maximum_runs: Annotated[
        int | None,
        typer.Option(
            "--maximum-runs",
            "-m",
            help="Maximum number of runs to include (max [magenta]20[/magenta]).",
            metavar="MAXIMUM_RUNS",
        ),
    ] = 20,
    managed_inputs: Annotated[
        str | None,
        typer.Option(
            "--managed-inputs",
            help="Managed inputs for the input set. Data should be valid [magenta]json[/magenta]. Object "
            "format: [dim][{'id': 'id', 'name': 'name', 'description': 'description'}][/dim].",
            metavar="MANAGED_INPUTS",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Cloud input set for experiments.

    An input set is a collection of inputs that can be reused across multiple
    experiments.

    1. --run-ids: Create from a list of existing run IDs.
    2. --managed-inputs: Create from existing managed inputs in the application.
    3. --instance-id with --start-time and --end-time:
       Create from instance runs matching the time range criteria.

    [bold][underline]Examples[/underline][/bold]

    - Create an input set for application [magenta]hare-app[/magenta] from runs.
      A random input set ID will be generated if one is not provided.
        $ [dim]nextmv cloud input-set create --app-id hare-app \\
            --name "Hare Input Set" --run-ids run-1 --run-ids run-2 --run-ids run-3"[/dim]

    - Create an input set with a specific ID.
        $ [dim]nextmv cloud input-set create --app-id hare-app --input-set-id hare-input-set \\
            --name "Hare Input Set" --run-ids run-1 --run-ids run-2 --run-ids run-3"[/dim]

    - Create an input set using existing managed inputs.
        $ [dim]nextmv cloud input-set create --app-id hare-app --name "Hare Input Set" \\
            --managed-inputs '[{"id": "hare-input-1", "name": "hare input", "description": "hare description"}]'[/dim]

    - Create an input set from runs using a specific instance and time range.
        $ [dim]nextmv cloud input-set create --app-id hare-app --name "Hare Input Set" \\
            --instance-id hare-instance --start-time "2024-01-01T00:00:00Z" \\
            --end-time "2024-01-31T23:59:59Z"[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Creating input set...")

    # Generate a random input set ID if one is not provided.
    if input_set_id is None:
        input_set_id = safe_id("input-set")

    managed_inputs = []
    if managed_inputs is not None:
        for d in json.loads(managed_inputs):
            i = ManagedInput.from_dict(d)
            if i is None:
                error(f"[magenta]{d}[/magenta] is not a valid [yellow]ManagedInput[/yellow]")
            managed_inputs.append(i)

    input_set = cloud_app.new_input_set(
        input_set_id,
        name,
        description=description,
        instance_id=instance_id,
        run_ids=run_ids,
        start_time=start_time,
        end_time=end_time,
        maximum_runs=maximum_runs,
        inputs=managed_inputs,
    )
    print_json(input_set.to_dict())
