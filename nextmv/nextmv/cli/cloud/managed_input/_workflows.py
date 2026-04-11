"""CLI-only workflows for the cloud managed_input domain.

The ``managed-input create`` CLI command accepts a ``--content-format``
flag that the thin action doesn't expose (the action sticks to the
SDK's default JSON format). The workflow translates the flag into an
SDK ``Format`` object before calling ``Application.new_managed_input``.
The ``update`` command has a precondition check and an ``--output`` file
save that don't fit the framework's default flow.
"""

import json
from pathlib import Path
from typing import Annotated

import typer

from nextmv.cli.actions.managed_input import update_managed_input
from nextmv.cli.framework.options import AppIdRequiredOption, ManagedInputIdOption
from nextmv.cli.message import enum_values, error, in_progress, print_json, success
from nextmv.cloud import Application
from nextmv.cloud.client import Client
from nextmv.input import InputFormat
from nextmv.run import Format, FormatInput


def run_create_managed_input(
    client: Client,
    app_id: AppIdRequiredOption,
    content_format: Annotated[
        InputFormat | None,
        typer.Option(
            "--content-format",
            "-c",
            help=(
                f"The content format for the managed input. "
                f"Allowed values are: {enum_values(InputFormat)}. Default is JSON."
            ),
            metavar="CONTENT_FORMAT",
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="An optional description for the managed input.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    managed_input_id: Annotated[
        str | None,
        typer.Option(
            "--managed-input-id",
            "-m",
            help=(
                "The ID to assign to the new managed input. If not provided, "
                "a random ID will be generated."
            ),
            envvar="NEXTMV_MANAGED_INPUT_ID",
            metavar="MANAGED_INPUT_ID",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="A name for the managed input. If not provided, the ID will be used as the name.",
            metavar="NAME",
        ),
    ] = None,
    run_id: Annotated[
        str | None,
        typer.Option(
            "--run-id",
            "-r",
            help=(
                "ID of the run to use for the managed input. "
                "Either --upload-id or --run-id must be specified."
            ),
            envvar="NEXTMV_RUN_ID",
            metavar="RUN_ID",
        ),
    ] = None,
    upload_id: Annotated[
        str | None,
        typer.Option(
            "--upload-id",
            "-u",
            help=(
                "ID of the upload to use for the managed input. "
                "Either --upload-id or --run-id must be specified."
            ),
            metavar="UPLOAD_ID",
        ),
    ] = None,
) -> None:
    """Create a new Nextmv Cloud application managed input.

    A managed input can be created from either an upload or a run. Use
    the ``--upload-id`` flag to create from an upload, or the ``--run-id``
    flag to create from a run output.

    You can get an upload ID by using ``nextmv cloud upload create``. The
    ``upload_id`` field in the command output contains the upload ID, and
    the ``upload_url`` field contains a pre-signed URL to upload the data
    to. You may use ``nextmv cloud data upload`` to upload the data to
    the upload URL.

    If no ID is provided, a unique ID will be automatically generated. If
    no name is provided, the ID will be used as the name.
    """

    if upload_id is None and run_id is None:
        error(
            "Either --upload-id or --run-id must be specified. "
            "Use nextmv cloud upload create to create an upload first, "
            "or specify an existing run ID."
        )

    cloud_app = Application(client=client, id=app_id)

    format_obj = None
    if content_format is not None:
        format_obj = Format(
            format_input=FormatInput(
                input_type=InputFormat(content_format),
            ),
        )

    in_progress(msg="Creating managed input...")
    managed_input = cloud_app.new_managed_input(
        id=managed_input_id,
        name=name,
        description=description,
        upload_id=upload_id,
        run_id=run_id,
        format=format_obj,
    )
    print_json(managed_input.to_dict())


def run_update_managed_input(
    client: Client,
    app_id: AppIdRequiredOption,
    managed_input_id: ManagedInputIdOption,
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
) -> None:
    """Update a Nextmv Cloud application managed input.

    Updates the name and/or description of an existing managed input. At
    least one of ``--name`` or ``--description`` must be provided.
    """

    if name is None and description is None:
        error("Provide at least one option to update: --name or --description.")

    in_progress(msg="Updating managed input...")
    updated_dict = update_managed_input(
        client,
        app_id=app_id,
        managed_input_id=managed_input_id,
        name=name,
        description=description,
    )
    success(
        f"Managed input [magenta]{managed_input_id}[/magenta] updated successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )

    if output is not None and output != "":
        Path(output).write_text(json.dumps(updated_dict, indent=2))
        success(f"Updated managed input information saved to [magenta]{output}[/magenta].")
        return

    print_json(updated_dict)
