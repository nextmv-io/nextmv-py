"""
This module defines the local run create command for the Nextmv CLI.
"""

import json
import sys
from pathlib import Path
from typing import Annotated, Any

import typer

from nextmv.cli.configuration.config import build_local_app
from nextmv.cli.local.run.get import handle_outputs
from nextmv.cli.local.run.logs import handle_logs
from nextmv.cli.message import enum_values, error, parse_content_format, print_json, success
from nextmv.cli.options import DebugOption, LocalAppIDOption, LocalAppSrcOption
from nextmv.content_format import ContentFormat
from nextmv.input import InputFormat
from nextmv.polling import default_polling_options
from nextmv.run import Format, FormatInput, RunConfiguration

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    app_id: LocalAppIDOption = None,
    app_src: LocalAppSrcOption = ".",
    # Options for controlling input.
    input: Annotated[
        str | None,
        typer.Option(
            "--input",
            "-i",
            help="The input path to use. File or directory depending on content format. "
            "Uses [magenta]stdin[/magenta] if not defined. "
            "Can be a [magenta].tar.gz[/magenta] file for multi-file content format.",
            metavar="INPUT_PATH",
            rich_help_panel="Input control",
        ),
    ] = None,
    # Options for controlling output.
    logs: Annotated[
        str | None,
        typer.Option(
            "--logs",
            "-l",
            help="Waits for the run to complete and saves the logs to this location.",
            metavar="LOGS_PATH",
            rich_help_panel="Output control",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-u",
            help="Waits for the run to complete and save the output to this location. "
            "A file or directory will be created depending on content format. ",
            metavar="OUTPUT_PATH",
            rich_help_panel="Output control",
        ),
    ] = None,
    tail: Annotated[
        bool,
        typer.Option(
            "--tail",
            "-t",
            help="Tail the logs until the run completes. Logs are streamed to [magenta]stderr[/magenta]. "
            "Specify log output location with --logs.",
            rich_help_panel="Output control",
        ),
    ] = False,
    wait: Annotated[
        bool,
        typer.Option(
            "--wait",
            "-w",
            help="Wait for the run to complete. Run result is printed to [magenta]stdout[/magenta] for "
            "[magenta]json[/magenta], to a dir for [magenta]multi-file[/magenta]. "
            "Specify output location with --output.",
            rich_help_panel="Output control",
        ),
    ] = False,
    # Options for run configuration.
    content_format: Annotated[
        InputFormat | None,  # Keep deprecated type for backwards compatibility, translated in the code.
        typer.Option(
            "--content-format",
            "-c",
            help=f"The content format of the run to create. Allowed values are: {enum_values(ContentFormat)}.",
            metavar="CONTENT_FORMAT",
            rich_help_panel="Run configuration",
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            help="An optional description for the new run.",
            metavar="DESCRIPTION",
            rich_help_panel="Run configuration",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="An optional name for the new run.",
            metavar="NAME",
            rich_help_panel="Run configuration",
        ),
    ] = None,
    options: Annotated[
        list[str] | None,
        typer.Option(
            "--options",
            "-o",
            help="Options passed to the run. Format: [magenta]key=value[/magenta]. "
            "Pass multiple options by repeating the flag, or separating with commas.",
            metavar="KEY=VALUE",
            rich_help_panel="Run configuration",
        ),
    ] = None,
    timeout: Annotated[
        int,
        typer.Option(
            help="The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.",
            metavar="TIMEOUT_SECONDS",
            rich_help_panel="Run configuration",
        ),
    ] = -1,
    _: DebugOption = False,
) -> None:
    """
    Create a new local application run.

    You may identify the app by using --app-src, or --app-id if it has been
    registered. If the app is not already registered, this command will
    register it. Input for the run should be given through
    [magenta]stdin[/magenta] or the --input flag. When using the --input flag,
    the value can be one of the following:

    - [yellow]<FILE_PATH>[/yellow]: path to a [magenta]file[/magenta] containing
      the input data. Use with the [magenta]json[/magenta] content format.
    - [yellow]<DIR_PATH>[/yellow]: path to a [magenta]directory[/magenta]
      containing the input data files. Use with the
      [magenta]multi-file[/magenta] content format.

    The CLI determines how to send the input to the application based on the
    value.

    Use the --wait flag to wait for the run to complete, polling for results.
    Using the --output flag will also activate waiting, and allows you to
    specify a destination (file or dir) for the output, depending on the
    content type.

    Use the --tail flag to stream logs to [magenta]stderr[/magenta] until the
    run completes. Using the --logs flag will also activate waiting, and allows
    you to specify a file to write the logs to.

    [bold][underline]Examples[/underline][/bold]

    - Read a [magenta]json[/magenta] input via [magenta]stdin[/magenta], from an [magenta]input.json[/magenta] file,
      and create a run for an app at the current directory.
        $ [dim]cat input.json | nextmv local run create[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      create a run for an app with ID [magenta]hare-app[/magenta].
        $ [dim]nextmv local run create --app-id hare-app --input input.json[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      create a run for an app at path [magenta]./my-app[/magenta].
      Wait for the run to complete and print the result to [magenta]stdout[/magenta].
        $ [dim]nextmv local run create --app-src ./my-app --input input.json --wait[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      create a run for an app at path [magenta]./my-app[/magenta].
      Tail the run's logs, streaming to [magenta]stderr[/magenta].
        $ [dim]nextmv local run create --app-src ./my-app --input input.json --tail[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      create a run for an app with ID [magenta]hare-app[/magenta].
      Wait for the run to complete and write the result to an [magenta]output.json[/magenta] file.
        $ [dim]nextmv local run create --app-id hare-app --input input.json --output output.json[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      create a run for an app with ID [magenta]hare-app[/magenta].
      Wait for the run to complete, and write the logs to a [magenta]logs.log[/magenta] file.
        $ [dim]nextmv local run create --app-id hare-app --input input.json --logs logs.log[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and create a run for an app at
      path [magenta]./my-app[/magenta]. Wait for the run to complete. Tail the run's logs, streaming to
      [magenta]stderr[/magenta]. Write the logs to a [magenta]logs.log[/magenta] file. Write the result to an
      [magenta]output.json[/magenta] file.
        $ [dim]nextmv local run create --app-src ./my-app --input input.json --tail --logs logs.log \\
            --output output.json[/dim]

    - Read a [magenta]multi-file[/magenta] input from an [magenta]inputs[/magenta] directory, and
      create a run for an app at path [magenta]./my-app[/magenta].
        $ [dim]nextmv local run create --app-src ./my-app --input inputs --content-format multi-file[/dim]

    - Read a [magenta]multi-file[/magenta] input from an [magenta]inputs[/magenta] directory, and
      create a run for an app with ID [magenta]hare-app[/magenta].
      Wait for the run to complete and save the result files to an [magenta]outputs[/magenta] directory.
        $ [dim]nextmv local run create --app-id hare-app --input inputs --output outputs[/dim]

    - Create a run with custom options for an app at path [magenta]./my-app[/magenta].
        $ [dim]nextmv local run create --app-src ./my-app --input input.json \\
            --options duration=10s --options verbose=true[/dim]
    """

    content_format = parse_content_format(content_format)

    # Validate that input is provided.
    stdin = sys.stdin.read().strip() if sys.stdin.isatty() is False else None
    if stdin is None and (input is None or input == ""):
        error("Input data must be provided via the --input flag or [magenta]stdin[/magenta].")

    # Instantiate the basic requirements to start a new run.
    local_app = build_local_app(app_src, app_id)
    config = None
    if content_format is not None:
        config = RunConfiguration()
        config.format = Format(
            format_input=FormatInput(
                input_type=content_format,
            ),
        )
    run_options = build_run_options(options)

    # Start the run before deciding if we should poll or not.
    input_kwarg = resolve_input_kwarg(stdin=stdin, input=input)
    run_id = local_app.new_run(
        **input_kwarg,
        name=name,
        description=description,
        options=run_options,
        configuration=config,
    )

    # If we don't need to poll at all we are done.
    if not wait and not tail and output is None and logs is None:
        print_json({"run_id": run_id})

        return

    success(f"Run [magenta]{run_id}[/magenta] created.")

    # Build the polling options.
    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    # Handle what happens after the run is created for logging and result
    # retrieval.
    handle_logs(
        local_app=local_app,
        run_id=run_id,
        tail=tail,
        logs=logs,
        polling_options=polling_options,
        file_output=True,
    )
    handle_outputs(
        local_app=local_app,
        run_id=run_id,
        wait=wait,
        output=output,
        polling_options=polling_options,
        skip_wait_check=False,
    )


def build_run_options(options: list[str] | None) -> dict[str, str]:
    """
    Builds the run options for the new run. One can pass options by either
    using the flag multiple times or by separating with commas in the same
    flag. A combination of both is also possible.

    Parameters
    ----------
    options : list[str] | None
        The list of run options as strings.

    Returns
    -------
    dict[str, str]
        The built run options.
    """

    if options is None:
        return None

    run_options = {}
    for opt in options:
        # It is possible to pass multiple options separated by commas. The
        # default way though is to use the flag multiple times to specify
        # different options.
        sub_opts = opt.split(",")
        for sub_opt in sub_opts:
            key_value = sub_opt.split("=", 1)
            if len(key_value) != 2:
                error(f"Invalid option format: {sub_opt}. Expected format is [magenta]key=value[/magenta].")

            key, value = key_value
            run_options[key] = value

    return run_options


def resolve_input_kwarg(stdin: str | None, input: str | None) -> dict[str, Any]:
    """
    Gets the keyword argument related to the input that is needed for the run
    creation. It handles stdin, file, and directory inputs.

    Parameters
    ----------
    stdin : str | None
        The stdin input data, if provided.
    input : str | None
        The input path, if provided.

    Returns
    -------
    dict[str, Any]
        The keyword argument with the resolved input.
    """

    # It is possible to not provide any input when we are cloning a run.
    if stdin is None and input is None:
        return {}

    if stdin:
        # Handle the case where stdin is provided as JSON for a JSON app.
        try:
            input_data = json.loads(stdin)
        except json.JSONDecodeError:
            input_data = stdin

        return {"input": input_data}

    input_path = Path(input)

    # If the input is a file, we read the content and pass it directly.
    if input_path.is_file():
        try:
            data = json.loads(input_path.read_text())
            return {"input": data}
        except json.JSONDecodeError:
            data = input_path.read_text()
            return {"input": data}

    # If the input is a directory, we give the path directly to the run method.
    # Internally, the files will be handled.
    if input_path.is_dir():
        return {"input_dir_path": input}

    error(f"Input path [magenta]{input}[/magenta] does not exist.")
