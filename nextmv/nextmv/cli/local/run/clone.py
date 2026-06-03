"""
This module defines the local run clone command for the Nextmv CLI.
"""

import sys
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_local_app
from nextmv.cli.local.run.create import build_run_options, resolve_input_kwarg
from nextmv.cli.local.run.get import handle_outputs
from nextmv.cli.local.run.logs import handle_logs
from nextmv.cli.message import enum_values, parse_content_format, print_json, success
from nextmv.cli.options import DebugOption, LocalAppIDOption, LocalAppSrcOption
from nextmv.content_format import ContentFormat
from nextmv.input import InputFormat
from nextmv.polling import default_polling_options
from nextmv.run import Format, FormatInput, RunConfiguration

# Set up subcommand application.
app = typer.Typer()


@app.command()
def clone(
    cloned_run_id: Annotated[
        str,
        typer.Option(
            "--cloned-run-id",
            "-r",
            help="The original Nextmv run ID that you want to clone.",
            envvar="NEXTMV_CLONED_RUN_ID",
            metavar="CLONED_RUN_ID",
        ),
    ],
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
    Clone an existing local application run.

    All information of the original (cloned) run will be reused. You may
    override any information you wish, such as the input, content format, or
    options, for example. All the options for creating the new run work the
    same way as in the [code]nextmv local run create[/code] command. You may
    inspect the documentation of that command for more details on what each
    option does.

    [bold][underline]Examples[/underline][/bold]

    - Clone run [magenta]run-123[/magenta] from an app in the current directory.
        $ [dim]nextmv local run clone --cloned-run-id run-123[/dim]

    - Clone a [magenta]json[/magenta] input via [magenta]stdin[/magenta], from an [magenta]input.json[/magenta] file,
      and create a run for an app in the current directory.
        $ [dim]cat input.json | nextmv local run clone --cloned-run-id run-123[/dim]

    - Clone a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      create a run for an app with ID [magenta]hare-app[/magenta].
        $ [dim]nextmv local run clone --cloned-run-id run-123 --app-id hare-app --input input.json[/dim]

    - Clone a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      create a run for an app at path [magenta]./my-app[/magenta].
      Wait for the run to complete and print the result to [magenta]stdout[/magenta].
        $ [dim]nextmv local run clone --cloned-run-id run-123 --app-src ./my-app --input input.json --wait[/dim]

    - Clone a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      create a run for an app at path [magenta]./my-app[/magenta].
      Tail the run's logs, streaming to [magenta]stderr[/magenta].
        $ [dim]nextmv local run clone --cloned-run-id run-123 --app-src ./my-app --input input.json --tail[/dim]

    - Clone a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      create a run for an app with ID [magenta]hare-app[/magenta].
      Wait for the run to complete and write the result to an [magenta]output.json[/magenta] file.
        $ [dim]nextmv local run clone --cloned-run-id run-123 --app-id hare-app --input input.json \\
            --output output.json[/dim]

    - Clone a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      create a run for an app with ID [magenta]hare-app[/magenta].
      Wait for the run to complete, and write the logs to a [magenta]logs.log[/magenta] file.
        $ [dim]nextmv local run clone --cloned-run-id run-123 --app-id hare-app --input input.json --logs logs.log[/dim]

    - Clone a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and create a run for an app at
      path [magenta]./my-app[/magenta]. Wait for the run to complete. Tail the run's logs, streaming to
      [magenta]stderr[/magenta]. Write the logs to a [magenta]logs.log[/magenta] file. Write the result to an
      [magenta]output.json[/magenta] file.
        $ [dim]nextmv local run clone --cloned-run-id run-123 --app-src ./my-app --input input.json --tail \\
            --logs logs.log --output output.json[/dim]

    - Clone a [magenta]multi-file[/magenta] input from an [magenta]inputs[/magenta] directory, and
      create a run for an app at path [magenta]./my-app[/magenta].
        $ [dim]nextmv local run clone --cloned-run-id run-123 --app-src ./my-app --input inputs \\
            --content-format multi-file[/dim]

    - Clone a [magenta]multi-file[/magenta] input from an [magenta]inputs[/magenta] directory, and
      create a run for an app with ID [magenta]hare-app[/magenta].
      Wait for the run to complete and save the result files to an [magenta]outputs[/magenta] directory.
        $ [dim]nextmv local run clone --cloned-run-id run-123 --app-id hare-app --input inputs --output outputs[/dim]

    - Clone a run with custom options for an app at path [magenta]./my-app[/magenta].
        $ [dim]nextmv local run clone --cloned-run-id run-123 --app-src ./my-app --input input.json \\
            --options duration=10s --options verbose=true[/dim]
    """

    content_format = parse_content_format(content_format)
    stdin = sys.stdin.read().strip() if sys.stdin.isatty() is False else None

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
    run_id = local_app.clone_run(
        **input_kwarg,
        cloned_run_id=cloned_run_id,
        name=name,
        description=description,
        options=run_options,
        configuration=config,
    )

    # If we don't need to poll at all we are done.
    if not wait and not tail and output is None and logs is None:
        print_json({"run_id": run_id})

        return

    success(f"Run [magenta]{run_id}[/magenta] cloned from original run [magenta]{cloned_run_id}[/magenta].")

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
