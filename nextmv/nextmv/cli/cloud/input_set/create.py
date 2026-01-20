"""
This module defines the cloud input-set create command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_client
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption

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
            metavar="INPUT_SET_ID",
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
    instance_id: Annotated[
        str | None,
        typer.Option(
            "--instance-id",
            "-i",
            help="Instance ID to filter runs from.",
            metavar="INSTANCE_ID",
        ),
    ] = None,
    run_ids: Annotated[
        str | None,
        typer.Option(
            "--run-ids",
            help="Comma-separated list of run IDs to include in the input set (max 20).",
            metavar="RUN_IDS",
        ),
    ] = None,
    start_time: Annotated[
        str | None,
        typer.Option(
            "--start-time",
            help="Start time for filtering runs (RFC3339 format).",
            metavar="START_TIME",
        ),
    ] = None,
    end_time: Annotated[
        str | None,
        typer.Option(
            "--end-time",
            help="End time for filtering runs (RFC3339 format).",
            metavar="END_TIME",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        typer.Option(
            "--limit",
            "-l",
            help="Maximum number of runs to include (default: 20, max: 20).",
            metavar="LIMIT",
        ),
    ] = None,
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
    Create a new input set for experiments.

    An input set is a collection of inputs that can be reused across multiple
    experiments. You can create an input set from historical runs by specifying
    run IDs, or by filtering runs based on instance ID and time range.

    [bold][underline]Examples[/underline][/bold]

    - Create an input set with a name.
        $ [green]nextmv cloud input-set create --app-id my-app --name "My Input Set"[/green]

    - Create an input set from specific runs.
        $ [green]nextmv cloud input-set create --app-id my-app --name "My Input Set" \\
            --run-ids "run-1,run-2,run-3"[/green]

    - Create an input set from runs within a time range.
        $ [green]nextmv cloud input-set create --app-id my-app --name "My Input Set" \\
            --start-time "2024-01-01T00:00:00Z" --end-time "2024-01-31T23:59:59Z"[/green]

    - Create an input set from a specific instance with a limit.
        $ [green]nextmv cloud input-set create --app-id my-app --name "My Input Set" \\
            --instance-id my-instance --limit 10[/green]

    - Create an input set with an ID and description.
        $ [green]nextmv cloud input-set create --app-id my-app --name "My Input Set" \\
            --input-set-id my-input-set --description "Input set for testing"[/green]
    """

    client = build_client(profile)
    in_progress(msg="Creating input set...")

    # Build the request payload
    payload: dict = {
        "name": name,
    }

    if input_set_id is not None:
        payload["id"] = input_set_id

    if description is not None:
        payload["description"] = description

    if instance_id is not None:
        payload["instance_id"] = instance_id

    if run_ids is not None:
        payload["run_ids"] = [r.strip() for r in run_ids.split(",")]

    if start_time is not None:
        payload["start_time"] = start_time

    if end_time is not None:
        payload["end_time"] = end_time

    if limit is not None:
        payload["maximum_runs"] = limit

    response = client.request(
        method="POST",
        endpoint=f"/v1/applications/{app_id}/experiments/inputsets",
        payload=payload,
    )
    input_set_data = response.json()

    if output is not None:
        with open(output, "w") as f:
            json.dump(input_set_data, f, indent=2)

        success(msg=f"Input set information saved to [magenta]{output}[/magenta].")

        return

    print_json(input_set_data)
