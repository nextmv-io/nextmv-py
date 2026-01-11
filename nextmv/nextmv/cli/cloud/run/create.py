"""
This module defines the cloud run create command for the Nextmv CLI.
"""

import json
import sys
import tarfile
from pathlib import Path
from typing import Annotated, Any

import rich
import typer

from nextmv.cli.cloud.run.get import handle_outputs
from nextmv.cli.cloud.run.logs import handle_logs
from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import error, success
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.application import Application
from nextmv.input import InputFormat
from nextmv.polling import DEFAULT_POLLING_OPTIONS
from nextmv.run import Format, FormatInput, RunConfiguration, RunQueuing, RunType, RunTypeConfiguration

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
            help="The input location to use. File or directory depending on content type. "
            "Uses [magenta]stdin[/magenta] if not defined.",
            metavar="INPUT_LOCATION",
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
            metavar="LOGS_LOCATION",
            rich_help_panel="Output control",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-u",
            help="Waits for the run to complete and save the output to this location. "
            "A file or directory will be created depending on content type. ",
            metavar="OUTPUT_LOCATION",
            rich_help_panel="Output control",
        ),
    ] = None,
    tail: Annotated[
        bool,
        typer.Option(
            "--tail",
            "-t",
            help="Tail the logs until the run completes. Logs are streamed to [magenta]stderr[/magenta]. "
            "Specify log output location with [code]--logs[/code].",
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
            "Specify output location with [code]--output[/code].",
            rich_help_panel="Output control",
        ),
    ] = False,
    # Options for run configuration.
    content_type: Annotated[
        InputFormat | None,
        typer.Option(
            "--content-type",
            "-c",
            help="The content type of the run to create. Allowed values are: "
            f"{[v.value for v in InputFormat.__members__.values()]}",
            metavar="CONTENT_TYPE",
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
        list[str],
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
            help=f"The type of run to create. Allowed values are: {[v.value for v in RunType.__members__.values()]}",
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
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Cloud application run.

    Input for the run should be given through [magenta]stdin[/magenta] or the
    [code]--input[/code] flag.

    Use the [code]--wait[/code] flag to wait for the run to complete, polling
    for results. Using the [code]--output[/code] flag will also activate
    waiting, and allows you to specify a destination (file or dir) for the
    output, depending on the content type.

    Use the [code]--tail[/code] flag to stream logs to
    [magenta]stderr[/magenta] until the run completes. Using the
    [code]--logs[/code] flag will also activate waiting, and allows you to
    specify a file to write the logs to.

    An application run executes against a specific instance. An instance
    represents the combination of executable code and configuration. You can
    specify the instance with the [code]--instance-id[/code] flag. These are
    the possible values for this flag:

    - [green]latest[/green]: uses the special [magenta]latest[/magenta]
      instance of the application. This corresponds to the latest pushed
      executable. This is the default behavior.
    - [green]default[/green]: if the application has a [italic]default[/italic]
      instance configured, then it uses that instance. Setting the flag's value
      to [code]''[/code] (empty string) has the same effect.
    - [green]<INSTANCE_ID>[/green]: uses the instance with the given ID.

    [bold][underline]Examples[/underline][/bold]

    - Read a [magenta]json[/magenta] input via [magenta]stdin[/magenta], from an [magenta]input.json[/magenta] file,
      and submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
        $ [green]cat input.json | nextmv cloud run create --app-id hare-app[/green]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
        $ [green]nextmv cloud run create --app-id hare-app --input input.json[/green]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
      Wait for the run to complete and print the result to [magenta]stdout[/magenta].
        $ [green]nextmv cloud run create --app-id hare-app --input input.json --wait[/green]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
      Tail the run's logs, streaming to [magenta]stderr[/magenta].
        $ [green]nextmv cloud run create --app-id hare-app --input input.json --tail[/green]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
      Wait for the run to complete and write the result to an [magenta]output.json[/magenta] file.
        $ [green]nextmv cloud run create --app-id hare-app --input input.json --output output.json[/green]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
      Wait for the run to complete, and write the logs to a [magenta]logs.log[/magenta] file.
        $ [green]nextmv cloud run create --app-id hare-app --input input.json --logs logs.log[/green]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and submit a run to an app with
      ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance. Wait for the run to complete. Tail
      the run's logs, streaming to [magenta]stderr[/magenta]. Write the logs to a [magenta]logs.log[/magenta] file.
      Write the result to an [magenta]output.json[/magenta] file.
        $ [green]nextmv cloud run create --app-id hare-app --input input.json --tail --logs logs.log \\
            --output output.json [/green]

    - Read a [magenta]multi-file[/magenta] input from an [magenta]inputs[/magenta] directory, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]default[/magenta] instance.
        $ [green]nextmv cloud run create --app-id hare-app --input inputs --instance-id default[/green]

    - Read a [magenta]multi-file[/magenta] input from an [magenta]inputs[/magenta] directory, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]default[/magenta] instance.
      Wait for the run to complete, and save the results to the default location (a directory named after the run ID).
        $ [green]nextmv cloud run create --app-id hare-app --input inputs --instance-id default --wait[/green]

    - Read a [magenta]multi-file[/magenta] input from an [magenta]inputs[/magenta] directory, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]burrow[/magenta] instance.
      Wait for the run to complete and download the result files to an [magenta]outputs[/magenta] directory.
        $ [green]nextmv cloud run create --app-id hare-app --input inputs --instance-id burrow --output outputs[/green]
    """

    # Validate that input is provided.
    stdin = sys.stdin.read().strip() if sys.stdin.isatty() is False else None
    if stdin is None and input is None:
        error("Input data must be provided via the [code]--input[/code] flag or [magenta]stdin[/magenta].")

    # Instantiate the basic requirements to start a new run.
    cloud_app = build_app(app_id, profile)
    config = build_run_config(
        run_type=run_type,
        priority=priority,
        no_queuing=no_queuing,
        execution_class=execution_class,
        content_type=content_type,
        secret_collection_id=secret_collection_id,
        integration_id=integration_id,
        definition_id=definition_id,
    )
    run_options = build_run_options(options)

    # Build the polling options.
    polling_options = DEFAULT_POLLING_OPTIONS
    polling_options.max_duration = timeout

    # Handles the default instance.
    if instance_id == "default":
        instance_id = ""

    # Start the run before deciding if we should poll or not.
    input_kwarg = resolve_input_kwarg(
        stdin=stdin,
        input=input,
        cloud_app=cloud_app,
    )
    run_id = cloud_app.new_run(
        **input_kwarg,
        instance_id=instance_id,
        name=name,
        description=description,
        options=run_options,
        configuration=config,
    )

    # If we don't need to poll at all we are done.
    if not wait and not tail and output is None and logs is None:
        rich.print({"run_id": run_id})

        return

    success(f"Run [magenta]{run_id}[/magenta] created.")

    # Handle what happens after the run is created for logging and result
    # retrieval.
    handle_logs(
        cloud_app=cloud_app,
        run_id=run_id,
        tail=tail,
        logs=logs,
        polling_options=polling_options,
        file_output=True,
    )
    handle_outputs(
        cloud_app=cloud_app,
        run_id=run_id,
        wait=wait,
        output=output,
        polling_options=polling_options,
        skip_wait_check=False,
    )


def build_run_config(
    run_type: RunType,
    priority: int,
    no_queuing: bool,
    execution_class: str | None,
    content_type: InputFormat | None,
    secret_collection_id: str | None,
    integration_id: str | None,
    definition_id: str | None,
) -> RunConfiguration:
    """
    Builds the run configuration for the new run.

    Parameters
    ----------
    run_type : RunType
        The type of run to create.
    priority : int
        The priority of the run.
    no_queuing : bool
        Whether to disable queuing for the run.
    execution_class : str | None
        The execution class to use for the run, if applicable.
    content_type : InputFormat | None
        The content type of the run to create, if applicable.
    secret_collection_id : str | None
        The secret collection ID to use for the run, if applicable.
    integration_id : str | None
        The integration ID to use for the run, if applicable.
    definition_id : str | None
        The definition ID to use for the run, if applicable.

    Returns
    -------
    RunConfiguration
        The built run configuration.
    """

    config = RunConfiguration(
        run_type=RunTypeConfiguration(
            run_type=RunType(run_type),
        ),
        queuing=RunQueuing(
            priority=priority,
            disabled=no_queuing,
        ),
    )
    if execution_class is not None:
        config.execution_class = execution_class
    if content_type is not None:
        config.format = Format(
            format_input=FormatInput(
                input_type=InputFormat(content_type),
            ),
        )
    if secret_collection_id is not None:
        config.secrets_collection_id = secret_collection_id
    if integration_id is not None:
        config.integration_id = integration_id
    if definition_id is not None:
        config.run_type.definition_id = definition_id

    return config


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

    run_options = {}
    for opt in options or []:
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


def resolve_input_kwarg(
    stdin: str | None,
    input: str | None,
    cloud_app: Application,
) -> dict[str, Any]:
    """
    Gets the keyword argument related to the input that is needed for the run
    creation. It handles stdin, file, and directory inputs. It uploads the
    input to the cloud application if needed.

    Parameters
    ----------
    stdin : str | None
        The stdin input data, if provided.
    input : str | None
        The input path, if provided.
    cloud_app : Application
        The cloud application instance.

    Returns
    -------
    dict[str, Any]
        The keyword argument with the resolved input.
    """

    if stdin is not None:
        # Handle the case where stdin is provided as JSON for a JSON app.
        try:
            input_data = json.loads(stdin)
        except json.JSONDecodeError:
            input_data = stdin

        return {"input": input_data}

    input_path = Path(input)

    # If the input is a file, we need to determine if it is a tar file or
    # a regular file and upload it accordingly. If it is a regular file, we
    # need to read its content.
    if input_path.is_file():
        upload_url = cloud_app.upload_url()
        if tarfile.is_tarfile(input_path):
            cloud_app.upload_large_input(input=None, upload_url=upload_url, tar_file=input_path)
        else:
            input_data = input_path.read_text()
            cloud_app.upload_large_input(input=input_data, upload_url=upload_url)

        return {"upload_id": upload_url.upload_id}

    # If the input is a directory, we give the path directly to the run method.
    # Internally, the files will be tarred and uploaded.
    if input_path.is_dir():
        return {"input_dir_path": input}

    error(f"Input path [magenta]{input}[/magenta] does not exist.")
