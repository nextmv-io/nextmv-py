"""
This module defines the cloud run track command for the Nextmv CLI.
"""

import json
import sys
from pathlib import Path
from typing import Annotated

import typer

from nextmv.cli.cloud.run.create import build_run_config
from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import enum_values, error, in_progress, print_json
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.input import InputFormat
from nextmv.run import RunType, TrackedRun, TrackedRunStatus

# Set up subcommand application.
app = typer.Typer()


@app.command()
def track(
    app_id: AppIDOption,
    # Options for controlling the tracked run.
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="The output of the run being tracked. A file or directory depending on content format.",
            metavar="OUTPUT_PATH",
            rich_help_panel="Tracked run configuration",
        ),
    ],
    status: Annotated[
        TrackedRunStatus,
        typer.Option(
            "--status",
            "-s",
            help=f"Status of the tracked run. Allowed values are: {enum_values(TrackedRunStatus)}.",
            metavar="STATUS",
            rich_help_panel="Tracked run configuration",
        ),
    ],
    assets: Annotated[
        str | None,
        typer.Option(
            help="The assets of the run being tracked. A [magenta]json[/magenta] file to read the assets from.",
            metavar="ASSETS_PATH",
            rich_help_panel="Tracked run configuration",
        ),
    ] = None,
    content_format: Annotated[
        InputFormat | None,
        typer.Option(
            "--content-format",
            "-c",
            help=f"The content format of the run to track. Allowed values are: {enum_values(InputFormat)}.",
            metavar="CONTENT_FORMAT",
            rich_help_panel="Tracked run configuration",
        ),
    ] = InputFormat.JSON,
    description: Annotated[
        str | None,
        typer.Option(
            help="An optional description for the tracked run.",
            metavar="DESCRIPTION",
            rich_help_panel="Tracked run configuration",
        ),
    ] = None,
    duration: Annotated[
        int,
        typer.Option(
            "--duration",
            "-d",
            help="The duration of the run being tracked, in milliseconds.",
            metavar="DURATION_MS",
            rich_help_panel="Tracked run configuration",
        ),
    ] = 0,
    error_msg: Annotated[
        str | None,
        typer.Option(
            "--error-msg",
            "-e",
            help="An error message if the run being tracked failed.",
            metavar="ERROR_MESSAGE",
            rich_help_panel="Tracked run configuration",
        ),
    ] = None,
    input: Annotated[
        str | None,
        typer.Option(
            "--input",
            "-i",
            help="The input of the run being tracked. File or directory depending on content format. "
            "Uses [magenta]stdin[/magenta] if not defined.",
            metavar="INPUT_PATH",
            rich_help_panel="Tracked run configuration",
        ),
    ] = None,
    logs: Annotated[
        str | None,
        typer.Option(
            "--logs",
            "-l",
            help="The logs of the run being tracked. A utf-8 encoded text file to read the logs from.",
            metavar="LOGS_PATH",
            rich_help_panel="Tracked run configuration",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="An optional name for the tracked run.",
            metavar="NAME",
            rich_help_panel="Tracked run configuration",
        ),
    ] = None,
    statistics: Annotated[
        str | None,
        typer.Option(
            help="The statistics of the run being tracked. A [magenta]json[/magenta] file to read the statistics from.",
            metavar="STATISTICS_PATH",
            rich_help_panel="Tracked run configuration",
        ),
    ] = None,
    # Options for run configuration.
    instance_id: Annotated[
        str | None,
        typer.Option(
            help="The instance ID to use for the run.",
            metavar="INSTANCE_ID",
            rich_help_panel="Run configuration",
        ),
    ] = "latest",
    profile: ProfileOption = None,
) -> None:
    """
    Track an external run as a Nextmv Cloud application run.

    Please see the help of the --content-type option for details on valid
    content types.

    If the content type is [magenta]json[/magenta] or [magenta]text[/magenta],
    then input for the run can be given through [magenta]stdin[/magenta]. The
    --input option allows you to specify a file or directory path for the
    input, instead of using [magenta]stdin[/magenta]. In the case of
    [magenta]multi-file[/magenta] content type, the input must be given through
    a directory specified via the --input option.

    The --output option allows you to specify a file or directory path for the
    output of the run. The behavior depends on the content type. If the content
    type is [magenta]json[/magenta] or [magenta]text[/magenta], then a file
    path must be provided. If the content type is
    [magenta]multi-file[/magenta], then a directory path must be provided.

    Run logs, assets, and statistics can be provided via files using the
    --logs, --assets, and --statistics options, respectively. Assets and
    statistics must be provided as [magenta]json[/magenta] files, while logs
    must be provided as a utf-8 encoded text file.

    [bold][underline]Examples[/underline][/bold]

    - Track a [magenta]successful[/magenta] [magenta]json[/magenta] run via [magenta]stdin[/magenta]
      input, for an app with ID [magenta]hare-app[/magenta].
        $ [dim]cat input.json | nextmv cloud run track --app-id hare-app --status succeeded[/dim]

    - Track a [magenta]successful[/magenta] [magenta]json[/magenta] run with input from an
      [magenta]input.json[/magenta] file and output from an
      [magenta]output.json[/magenta] file, for an app with ID
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud run track --app-id hare-app --status succeeded --input input.json \\
            --output output.json[/dim]

    - Track a [magenta]successful[/magenta] [magenta]json[/magenta] run including logs from a
      [magenta]logs.log[/magenta] file, for an app with ID
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud run track --app-id hare-app --status succeeded --input input.json \\
            --output output.json --logs logs.log[/dim]

    - Track a [magenta]successful[/magenta] [magenta]json[/magenta] run with assets and statistics
      from [magenta]json[/magenta] files, for an app with ID
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud run track --app-id hare-app --status succeeded --input input.json \\
            --output output.json --assets assets.json --statistics statistics.json[/dim]

    - Track a [magenta]failed[/magenta] run with an error message, for an app with ID
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud run track --app-id hare-app --status failed --input input.json \\
            --error-msg "Solver timed out"[/dim]

    - Track a [magenta]successful[/magenta] [magenta]text[/magenta] run with text content type,
      for an app with ID [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud run track --app-id hare-app --status succeeded --input input.txt \\
            --output output.txt --content-type text[/dim]

    - Track a [magenta]successful[/magenta] [magenta]multi-file[/magenta] run from an
      [magenta]inputs[/magenta] directory with output to an
      [magenta]outputs[/magenta] directory, for an app with ID
      [magenta]hare-app[/magenta], using the [magenta]default[/magenta]
      instance.
        $ [dim]nextmv cloud run track --app-id hare-app --status succeeded --input inputs \\
            --output outputs --content-type multi-file --instance-id default[/dim]

    - Track a [magenta]successful[/magenta] run with a name, description, and duration, for an app
      with ID [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud run track --app-id hare-app --status succeeded --input input.json \\
            --output output.json --name "Production run" --description "Weekly optimization" --duration 5000[/dim]

    - Track a [magenta]successful[/magenta] [magenta]json[/magenta] run with all available options,
      for an app with ID [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud run track --app-id hare-app --status succeeded --input input.json \\
            --output output.json --logs logs.log --assets assets.json --statistics statistics.json \\
                --name "Full run" --description "Complete example" --duration 10000 --instance-id burrow[/dim]
    """

    # Validate that input is provided.
    stdin = sys.stdin.read().strip() if sys.stdin.isatty() is False else None
    if stdin is None and (input is None or input == ""):
        error("Input data must be provided via the --input flag or [magenta]stdin[/magenta].")

    # Instantiate the basic requirements to start a new run.
    cloud_app = build_app(app_id=app_id, profile=profile)
    config = build_run_config(
        run_type=RunType.EXTERNAL,
        priority=6,
        no_queuing=False,
        content_format=content_format,
    )

    # Handles the default instance.
    if instance_id == "default":
        instance_id = ""

    # Build the tracked run input.
    tracked_run = build_tracked_run_input(
        status=status,
        duration=duration,
        error_msg=error_msg,
        name=name,
        description=description,
        stdin=stdin,
        input=input,
        content_format=content_format,
        output=output,
        assets=assets,
        logs=logs,
        statistics=statistics,
    )

    # Actually track the run.
    in_progress(msg="Tracking run...")
    run_id = cloud_app.track_run(
        tracked_run=tracked_run,
        instance_id=instance_id,
        configuration=config,
    )

    print_json({"run_id": run_id})


def build_tracked_run_input(
    status: TrackedRunStatus,
    duration: int,
    error_msg: str | None,
    name: str | None,
    description: str | None,
    stdin: str | None,
    input: str | None,
    content_format: InputFormat,
    output: str,
    assets: str | None = None,
    logs: str | None = None,
    statistics: str | None = None,
) -> TrackedRun:
    """
    Builds the tracked run input for tracking a run. Starts by creating a
    TrackedRun object with the provided status, duration, error message, name,
    and description. Then resolves the input and output using helper functions.
    Finally, it reads the assets, logs, and statistics from the provided file
    paths, if any, and assigns them to the TrackedRun object.

    Parameters
    ----------
    status : TrackedRunStatus
        The status of the tracked run.
    duration : int
        The duration of the tracked run in milliseconds.
    error_msg : str | None
        An error message if the run failed.
    name : str | None
        An optional name for the tracked run.
    description : str | None
        An optional description for the tracked run.
    stdin : str | None
        The input provided via stdin, if any.
    input : str | None
        The input file or directory path, if any.
    content_format : InputFormat
        The content format of the input (json or text).
    output : str
        The output file or directory path.
    assets : str | None
        The assets file path, if any.
    logs : str | None
        The logs file path, if any.
    statistics : str | None
        The statistics file path, if any.
    """
    tracked_run = TrackedRun(
        status=TrackedRunStatus(status),
        duration=duration,
        error=error_msg,
        name=name,
        description=description,
    )
    tracked_run = resolve_input(
        tracked_run=tracked_run,
        stdin=stdin,
        input=input,
        content_format=content_format,
    )
    tracked_run = resolve_output(
        tracked_run=tracked_run,
        output=output,
        content_format=content_format,
    )

    # Handle the assets, which should be a JSON file.
    if assets is not None and assets != "":
        try:
            with open(assets) as f:
                tracked_run.assets = json.load(f)
        except json.JSONDecodeError as e:
            error(f"Failed to parse assets file [magenta]{assets}[/magenta] as [magenta]json[/magenta]: {e}.")

    # Handle the logs, which should be a text file.
    if logs is not None and logs != "":
        try:
            log_content = Path(logs).read_text()
            tracked_run.logs = log_content
        except Exception as e:
            error(f"Failed to read logs file [magenta]{logs}[/magenta]: {e}.")

    # Handle the statistics, which should be a JSON file.
    if statistics is not None and statistics != "":
        try:
            with open(statistics) as f:
                tracked_run.statistics = json.load(f)
        except json.JSONDecodeError as e:
            error(f"Failed to parse statistics file [magenta]{statistics}[/magenta] as [magenta]json[/magenta]: {e}.")

    return tracked_run


def resolve_input(
    tracked_run: TrackedRun,
    stdin: str | None,
    input: str | None,
    content_format: InputFormat,
) -> TrackedRun:
    """
    Resolves the input for the tracked run, either from stdin or from a
    file/directory.

    Parameters
    ----------
    tracked_run : TrackedRun
        The tracked run to set the input for.
    stdin : str | None
        The input provided via stdin, if any.
    input : str | None
        The input file or directory path, if any.
    content_format : InputFormat
        The content format of the input (json or text).

    Returns
    -------
    TrackedRun
        The tracked run with the resolved input.
    """
    if stdin is not None:
        # Handle the case where stdin is provided as JSON for a JSON app.
        try:
            input_data = json.loads(stdin)
            if content_format != InputFormat.JSON:
                error(
                    "Input provided via [magenta]stdin[/magenta] is [magenta]json[/magenta], "
                    f"but the specified content format is {content_format.value}. "
                    "--content-format should be set to [magenta]json[/magenta]."
                )

        except json.JSONDecodeError:
            input_data = stdin
            if content_format != InputFormat.TEXT:
                error(
                    "Input provided via [magenta]stdin[/magenta] is [magenta]text[/magenta], "
                    f"but the specified content format is {content_format.value}. "
                    "--content-format should be set to [magenta]text[/magenta]."
                )

        tracked_run.input = input_data

        return tracked_run

    # We know that input was defined because otherwise we would have failed
    # early if both stdin and input were undefined.
    input_path = Path(input)

    if input_path.is_file():
        if content_format == InputFormat.JSON:
            try:
                with input_path.open("r") as f:
                    input_data = json.load(f)

                tracked_run.input = input_data

                return tracked_run

            except json.JSONDecodeError as e:
                error(f"Failed to parse input file [magenta]{input}[/magenta] as [magenta]json[/magenta]: {e}.")

        elif content_format == InputFormat.TEXT:
            input_data = input_path.read_text()
            tracked_run.input = input_data

            return tracked_run

        else:
            error(f"Unsupported content format [magenta]{content_format.value}[/magenta] for file input.")

    # If the input is a directory, we give the path directly to the run method.
    # Internally, the files will be tarred and uploaded.
    if input_path.is_dir():
        tracked_run.input_dir_path = input

        return tracked_run

    error(f"Input path [magenta]{input}[/magenta] does not exist.")


def resolve_output(
    tracked_run: TrackedRun,
    output: str,
    content_format: InputFormat,
) -> TrackedRun:
    """
    Resolves the output for the tracked run.

    Parameters
    ----------
    tracked_run : TrackedRun
        The tracked run to set the output for.
    output : str
        The output file or directory path.
    content_format : InputFormat
        The content format of the output (json or text).

    Returns
    -------
    TrackedRun
        The tracked run with the resolved output.
    """

    output_path = Path(output)
    if output_path.is_file():
        if content_format == InputFormat.JSON:
            try:
                with output_path.open("r") as f:
                    output_data = json.load(f)

                tracked_run.output = output_data

                return tracked_run

            except json.JSONDecodeError as e:
                error(f"Failed to parse output file [magenta]{output}[/magenta] as [magenta]json[/magenta]: {e}.")

        elif content_format == InputFormat.TEXT:
            output_data = output_path.read_text()
            tracked_run.output = output_data

            return tracked_run

        else:
            error(f"Unsupported content type [magenta]{content_format.value}[/magenta] for file output.")

    # If the output is a directory, we give the path directly to the run method.
    # Internally, the files will be downloaded and extracted.
    if output_path.is_dir():
        tracked_run.output_dir_path = output

        return tracked_run

    error(f"Output path [magenta]{output}[/magenta] does not exist.")
