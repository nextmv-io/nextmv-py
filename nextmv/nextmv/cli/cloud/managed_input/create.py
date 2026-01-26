"""
This module defines the cloud managed-input create command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import enum_values, error, in_progress, print_json
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.input import InputFormat
from nextmv.run import Format, FormatInput

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    app_id: AppIDOption,
    content_format: Annotated[
        InputFormat | None,
        typer.Option(
            "--content-format",
            "-c",
            help=f"The content format for the managed input. "
            f"Allowed values are: {enum_values(InputFormat)}. Default is JSON.",
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
            help="The ID to assign to the new managed input. If not provided, a random ID will be generated.",
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
            help="ID of the run to use for the managed input. Either --upload-id or --run-id must be specified.",
            envvar="NEXTMV_RUN_ID",
            metavar="RUN_ID",
        ),
    ] = None,
    upload_id: Annotated[
        str | None,
        typer.Option(
            "--upload-id",
            "-u",
            help="ID of the upload to use for the managed input. Either --upload-id or --run-id must be specified.",
            metavar="UPLOAD_ID",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Cloud application managed input.

    A managed input can be created from either an upload or a run. Use the
    --upload-id flag to create from an upload, or the --run-id flag to create
    from a run output.

    You can get an upload ID by using the [code]nextmv cloud upload
    create[/code] command. The [magenta].upload_id[/magenta] field in the
    command output contains the upload ID, and the
    [magenta].upload_url[/magenta] field contains a pre-signed URL to upload
    the data to. You may use the [code]nextmv cloud data upload[/code] command
    to upload the data to the upload URL.

    If no ID is provided, a unique ID will be automatically generated. If no
    name is provided, the ID will be used as the name.

    [bold][underline]Examples[/underline][/bold]

    - Create a managed input from an upload.
        $ [dim]nextmv cloud managed-input create --app-id hare-app --name "Test Input 1" \
            --upload-id upl_123456789[/dim]

    - Create a managed input from a run.
        $ [dim]nextmv cloud managed-input create --app-id hare-app --name "Baseline Run" \
            --run-id run_123456789[/dim]

    - Create a managed input with a specific ID and description.
        $ [dim]nextmv cloud managed-input create --app-id hare-app --name "Test Input" \\
            --managed-input-id inp_custom --description "Test case for validation" --upload-id upl_123456789[/dim]

    - Create a managed input with custom format.
        $ [dim]nextmv cloud managed-input create --app-id hare-app --name "CSV Input" \\
            --upload-id upl_123456789 --content-format csv[/dim]
    """

    if upload_id is None and run_id is None:
        error(
            "Either --upload-id or --run-id must be specified. "
            "Use nextmv cloud upload create to create an upload first, "
            "or specify an existing run ID."
        )

    cloud_app = build_app(app_id=app_id, profile=profile)

    # Build format if content_format is provided
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
