"""
This module defines the cloud run create command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.message import enum_values
from nextmv.cli.options import AppIDOption
from nextmv.input import InputFormat
from nextmv.run import RunType

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    app_id: AppIDOption,
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
        InputFormat | None,
        typer.Option(
            "--content-format",
            "-c",
            help=f"The content format of the run to create. Allowed values are: {enum_values(InputFormat)}.",
            metavar="CONTENT_FORMAT",
            rich_help_panel="Run configuration",
        ),
    ] = None,
    definition_id: Annotated[
        str | None,
        typer.Option(
            "--definition-id",
            "-d",
            help="The definition ID to use for the run. Required for certain run types like ensemble runs.",
            metavar="DEFINITION_ID",
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
    execution_class: Annotated[
        str | None,
        typer.Option(
            "--execution-class",
            "-e",
            help="The execution class to use for the run, if applicable.",
            metavar="EXECUTION_CLASS",
            rich_help_panel="Run configuration",
        ),
    ] = None,
    instance_id: Annotated[
        str | None,
        typer.Option(
            help="The instance ID to use for the run.",
            metavar="INSTANCE_ID",
            rich_help_panel="Run configuration",
        ),
    ] = "latest",
    integration_id: Annotated[
        str | None,
        typer.Option(
            help="The integration ID to use for the run, if applicable.",
            metavar="INTEGRATION_ID",
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
    no_queuing: Annotated[
        bool,
        typer.Option(
            "--no-queuing",
            help="Do not queue run. Default is [magenta]False[/magenta], "
            "meaning the run [italic]will[/italic] be queued.",
            rich_help_panel="Run configuration",
        ),
    ] = False,
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
    priority: Annotated[
        int,
        typer.Option(
            help="The priority of the run. Priority is between 1 and 10, with 1 being the highest priority.",
            metavar="PRIORITY",
            rich_help_panel="Run configuration",
        ),
    ] = 6,
    run_type: Annotated[
        RunType,
        typer.Option(
            "--run-type",
            "-r",
            help=f"The type of run to create. Allowed values are: {enum_values(RunType)}.",
            metavar="RUN_TYPE",
            rich_help_panel="Run configuration",
        ),
    ] = RunType.STANDARD,
    secret_collection_id: Annotated[
        str | None,
        typer.Option(
            "--secret-collection-id",
            "-s",
            help="The secret collection ID to use for the run, if applicable.",
            metavar="SECRET_COLLECTION_ID",
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
) -> None:
    """
    Create a new Nextmv Local application run.

    Input for the run should be given through [magenta]stdin[/magenta] or the
    --input flag. When using the --input flag, the value can be one of the
    following:

    - [yellow]<FILE_PATH>[/yellow]: path to a [magenta]file[/magenta] containing
      the input data. Use with the [magenta]json[/magenta], and
      [magenta]text[/magenta] content formats.
    - [yellow]<DIR_PATH>[/yellow]: path to a [magenta]directory[/magenta]
      containing the input data files. Use with the
      [magenta]multi-file[/magenta] content format.
    - [yellow]<.tar.gz PATH>[/yellow]: path to a [magenta].tar.gz[/magenta] file
      containing tarred input data files. Use with the
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

    An application run executes against a specific instance. An instance
    represents the combination of executable code and configuration. You can
    specify the instance with the --instance-id flag. These are the possible
    values for this flag:

    - [yellow]latest[/yellow]: uses the special [magenta]latest[/magenta]
      instance of the application. This corresponds to the latest pushed
      executable. This is the default behavior.
    - [yellow]default[/yellow]: if the application has a [italic]default[/italic]
      instance configured, then it uses that instance. Setting the flag's value
      to [magenta]''[/magenta] (empty string) has the same effect.
    - [yellow]<INSTANCE_ID>[/yellow]: uses the instance with the given ID.

    [bold][underline]Examples[/underline][/bold]

    - Read a [magenta]json[/magenta] input via [magenta]stdin[/magenta], from an [magenta]input.json[/magenta] file,
      and submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
        $ [dim]cat input.json | nextmv local run create --app-id hare-app[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
        $ [dim]nextmv local run create --app-id hare-app --input input.json[/dim]
    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
      Wait for the run to complete and print the result to [magenta]stdout[/magenta].
        $ [dim]nextmv local run create --app-id hare-app --input input.json --wait[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
      Tail the run's logs, streaming to [magenta]stderr[/magenta].
        $ [dim]nextmv local run create --app-id hare-app --input input.json --tail[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
      Wait for the run to complete and write the result to an [magenta]output.json[/magenta] file.
        $ [dim]nextmv local run create --app-id hare-app --input input.json --output output.json[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
      Wait for the run to complete, and write the logs to a [magenta]logs.log[/magenta] file.
        $ [dim]nextmv local run create --app-id hare-app --input input.json --logs logs.log[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and submit a run to an app with
      ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance. Wait for the run to complete. Tail
      the run's logs, streaming to [magenta]stderr[/magenta]. Write the logs to a [magenta]logs.log[/magenta] file.
      Write the result to an [magenta]output.json[/magenta] file.
        $ [dim]nextmv local run create --app-id hare-app --input input.json --tail --logs logs.log \\
            --output output.json [/dim]

    - Read a [magenta]multi-file[/magenta] input from an [magenta]inputs[/magenta] directory, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]default[/magenta] instance.
        $ [dim]nextmv local run create --app-id hare-app --input inputs --instance-id default[/dim]

    - Read a [magenta]multi-file[/magenta] input from an [magenta]inputs[/magenta] directory, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]default[/magenta] instance.
      Wait for the run to complete, and save the results to the default location (a directory named after the run ID).
        $ [dim]nextmv local run create --app-id hare-app --input inputs --instance-id default --wait[/dim]

    - Read a [magenta]multi-file[/magenta] input from an [magenta]inputs[/magenta] directory, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]burrow[/magenta] instance.
      Wait for the run to complete and download the result files to an [magenta]outputs[/magenta] directory.
        $ [dim]nextmv local run create --app-id hare-app --input inputs --instance-id burrow --output outputs[/dim]
    """

    # TODO: replace copied code with actual logic / connect to actual logic
