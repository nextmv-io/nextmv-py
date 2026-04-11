"""CLI-only workflows for the cloud input_set domain.

The input_set create and update commands accept a ``--managed-inputs`` JSON
string (a list of objects with ``id``, ``name``, ``description`` fields)
and the create command also accepts ``--start-time``/``--end-time`` RFC
3339 timestamps. These are parsed here before calling the thin actions.
The MCP side accepts a plainer ``managed_input_ids: list[str]`` shape.
"""

import json
from datetime import datetime
from typing import Annotated

import typer

from nextmv.cli.actions.input_set import create_input_set
from nextmv.cli.framework.options import AppIdRequiredOption, InputSetIdOption
from nextmv.cli.message import error, in_progress, print_json, success
from nextmv.cloud.client import Client
from nextmv.cloud.input_set import ManagedInput
from nextmv.safe import safe_id


def _parse_managed_inputs(managed_inputs: str | None) -> list[ManagedInput] | None:
    """Parse a ``--managed-inputs`` JSON string into SDK objects.

    Expects a JSON array of objects, each with ``id``, ``name``, and
    ``description`` keys. Exits the CLI with a clear error if any entry
    cannot be parsed.
    """
    if managed_inputs is None:
        return None

    result: list[ManagedInput] = []
    for d in json.loads(managed_inputs):
        mi = ManagedInput.from_dict(d)
        if mi is None:
            error(f"[magenta]{d}[/magenta] is not a valid [yellow]ManagedInput[/yellow]")
        result.append(mi)
    return result or None


def run_create_input_set(
    client: Client,
    app_id: AppIdRequiredOption,
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
            help=(
                "List of run IDs to include in the input set (max 20). "
                "Pass multiple run IDs by repeating the flag."
            ),
            metavar="RUN_IDS",
        ),
    ] = None,
    start_time: Annotated[
        datetime | None,
        typer.Option(
            "--start-time",
            formats=["%Y-%m-%dT%H:%M:%S%z"],
            help=(
                "Start time for filtering runs in [magenta]RFC 3339[/magenta] format. "
                "Object format: [dim]'2024-01-01T00:00:00Z'[/dim]"
            ),
            metavar="START_TIME",
        ),
    ] = None,
    end_time: Annotated[
        datetime | None,
        typer.Option(
            "--end-time",
            formats=["%Y-%m-%dT%H:%M:%S%z"],
            help=(
                "End time for filtering runs in [magenta]RFC 3339[/magenta] format. "
                "Object format: [dim]'2024-01-01T00:00:00Z'[/dim]"
            ),
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
            help=(
                "Managed inputs for the input set. Data should be valid [magenta]json[/magenta]. Object "
                "format: [dim][{'id': 'id', 'name': 'name', 'description': 'description'}][/dim]."
            ),
            metavar="MANAGED_INPUTS",
        ),
    ] = None,
) -> None:
    """Create a new Nextmv Cloud input set for experiments.

    An input set is a collection of inputs that can be reused across
    multiple experiments. You can build one from:

    1. ``--run-ids``: a list of existing run IDs.
    2. ``--managed-inputs``: existing managed inputs in the application.
    3. ``--instance-id`` with ``--start-time`` and ``--end-time``: runs
       from an instance matching a time range.
    """

    in_progress(msg="Creating input set...")

    # Generate a random input set ID if one is not provided.
    if input_set_id is None:
        input_set_id = safe_id("input-set")

    managed_input_list = _parse_managed_inputs(managed_inputs)
    managed_input_ids = (
        [mi.id for mi in managed_input_list] if managed_input_list else None
    )

    # The thin action's ManagedInput reconstruction loses the name/description
    # fields. When the CLI user provides them, call the SDK directly to
    # preserve the richer data.
    if managed_input_list:
        from nextmv.cloud import Application

        cloud_app = Application(client=client, id=app_id)
        input_set = cloud_app.new_input_set(
            id=input_set_id,
            name=name,
            description=description,
            instance_id=instance_id,
            run_ids=run_ids,
            start_time=start_time,
            end_time=end_time,
            maximum_runs=maximum_runs,
            inputs=managed_input_list,
        )
        print_json(input_set.to_dict())
        return

    input_set_dict = create_input_set(
        client,
        app_id=app_id,
        input_set_id=input_set_id,
        name=name,
        description=description,
        instance_id=instance_id,
        maximum_runs=maximum_runs,
        run_ids=run_ids,
        managed_input_ids=managed_input_ids,
        start_time=start_time,
        end_time=end_time,
    )
    print_json(input_set_dict)


def run_update_input_set(
    client: Client,
    app_id: AppIdRequiredOption,
    input_set_id: InputSetIdOption,
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
            help=(
                "Managed inputs for the input set. Data should be valid [magenta]json[/magenta]. Object "
                "format: [dim][{'id': 'id', 'name': 'name', 'description': 'description'}][/dim]."
            ),
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
) -> None:
    """Update a Nextmv Cloud input set.

    This command updates the metadata of an existing input set. You can
    update the name, description, or managed inputs of the input set.
    """

    from pathlib import Path

    from nextmv.cloud import Application

    if name is None and description is None and managed_inputs is None:
        error("Provide at least one option: --name, --description, or --managed-inputs.")

    in_progress(msg="Updating input set...")
    managed_input_list = _parse_managed_inputs(managed_inputs) or []

    cloud_app = Application(client=client, id=app_id)
    updated_input_set = cloud_app.update_input_set(
        id=input_set_id,
        name=name,
        description=description,
        inputs=managed_input_list,
    )
    success(
        f"Input set [magenta]{input_set_id}[/magenta] updated successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
    updated_dict = updated_input_set.to_dict()

    if output is not None and output != "":
        Path(output).write_text(json.dumps(updated_dict, indent=2))
        success(f"Updated input set information saved to [magenta]{output}[/magenta].")
        return

    print_json(updated_dict)
