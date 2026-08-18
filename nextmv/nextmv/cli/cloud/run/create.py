"""
This module defines the cloud run create command for the Nextmv CLI.
"""

import json
import sys
import tarfile
from pathlib import Path
from typing import Annotated, Any

import typer

from nextmv.cli.cloud.run.get import handle_outputs
from nextmv.cli.cloud.run.logs import handle_logs
from nextmv.cli.configuration.config import build_cloud_app
from nextmv.cli.message import enum_values, error, parse_content_format, print_json, success
from nextmv.cli.options import AppIDOption, DebugOption, ProfileOption
from nextmv.cloud.application import Application
from nextmv.content_format import ContentFormat
from nextmv.input import InputFormat
from nextmv.polling import default_polling_options
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
            help="The input path to use. File or directory depending on content format. "
            "Uses [magenta]stdin[/magenta] if not defined. "
            "Can be a [magenta].tar.gz[/magenta] file for multi-file content format.",
            metavar="INPUT_PATH",
            rich_help_panel="Input control",
        ),
    ] = None,
    managed_input_id: Annotated[
        str | None,
        typer.Option(
            "--managed-input-id",
            "-m",
            help="The Nextmv Cloud managed input ID to use as the input for the run.",
            envvar="NEXTMV_MANAGED_INPUT_ID",
            metavar="MANAGED_INPUT_ID",
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
    definition_id: Annotated[
        str | None,
        typer.Option(
            "--definition-id",
            "-d",
            help="The definition ID to use for the run. Setting it converts the run into an ensemble run.",
            metavar="DEFINITION_ID",
            rich_help_panel="Run configuration",
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
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
            "--instance-id",
            help="The instance ID to use for the run.",
            metavar="INSTANCE_ID",
            rich_help_panel="Run configuration",
        ),
    ] = None,
    integration_id: Annotated[
        str | None,
        typer.Option(
            "--integration-id",
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
            "--no-queuing/--yes-queuing",
            help="Whether to queue when running. "
            "Default is [magenta]False[/magenta], meaning the run [italic]will[/italic] be queued.",
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
            "--priority",
            help="The priority of the run. Priority is between 1 and 9, with 1 being the highest priority.",
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
            "--timeout",
            help="The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.",
            metavar="TIMEOUT_SECONDS",
            rich_help_panel="Run configuration",
        ),
    ] = -1,
    _: DebugOption = False,
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Cloud application run.

    Input for the run should be given through [magenta]stdin[/magenta], the --input flag,
    or a Nextmv managed input by passing its ID into the --managed-input-id flag.
    When using the --input flag, the value can be one of the following:

    - [yellow]<FILE_PATH>[/yellow]: path to a [magenta]file[/magenta] containing
      the input data. Use with the [magenta]json[/magenta] content format.
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

    - [yellow]unspecified[/yellow]: Run against the default instance of the
      application. When an application is created, the default instance is [magenta]latest[/magenta].
    - [yellow]latest[/yellow]: uses the special [magenta]latest[/magenta]
      instance of the application. This corresponds to the latest pushed
      executable.
    - [yellow]<INSTANCE_ID>[/yellow]: uses the instance with the given ID.

    [bold][underline]Examples[/underline][/bold]

    - Read a [magenta]json[/magenta] input via [magenta]stdin[/magenta], from an [magenta]input.json[/magenta] file,
      and submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
        $ [dim]cat input.json | nextmv cloud run create --app-id hare-app[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.

        $ [dim]nextmv cloud run create --app-id hare-app --input input.json[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
      Wait for the run to complete and print the result to [magenta]stdout[/magenta].

        $ [dim]nextmv cloud run create --app-id hare-app --input input.json --wait[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
      Tail the run's logs, streaming to [magenta]stderr[/magenta].

        $ [dim]nextmv cloud run create --app-id hare-app --input input.json --tail[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
      Wait for the run to complete and write the result to an [magenta]output.json[/magenta] file.

        $ [dim]nextmv cloud run create --app-id hare-app --input input.json --output output.json[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
      Wait for the run to complete, and write the logs to a [magenta]logs.log[/magenta] file.

        $ [dim]nextmv cloud run create --app-id hare-app --input input.json --logs logs.log[/dim]

    - Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file, and submit a run to an app with
      ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance. Wait for the run to complete. Tail
      the run's logs, streaming to [magenta]stderr[/magenta]. Write the logs to a [magenta]logs.log[/magenta] file.
      Write the result to an [magenta]output.json[/magenta] file.

        $ [dim]nextmv cloud run create --app-id hare-app --input input.json --tail --logs logs.log \\
            --output output.json [/dim]

    - Read a [magenta]multi-file[/magenta] input from an [magenta]inputs[/magenta] directory, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]default[/magenta] instance.

        $ [dim]nextmv cloud run create --app-id hare-app --input inputs --instance-id default[/dim]

    - Read a [magenta]multi-file[/magenta] input from an [magenta]inputs[/magenta] directory, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]default[/magenta] instance.
      Wait for the run to complete, and save the results to the default location (a directory named after the run ID).

        $ [dim]nextmv cloud run create --app-id hare-app --input inputs --instance-id default --wait[/dim]

    - Read a [magenta]multi-file[/magenta] input from an [magenta]inputs[/magenta] directory, and
      submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]burrow[/magenta] instance.
      Wait for the run to complete and download the result files to an [magenta]outputs[/magenta] directory.

        $ [dim]nextmv cloud run create --app-id hare-app --input inputs --instance-id burrow --output outputs[/dim]

    - Set the run to use a [magenta]Nextmv managed[/magenta] input with ID [magenta]carrot-input[/magenta],
      and submit a run to an app with ID [magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.
      Wait for the run to complete and download the result files to an [magenta]outputs[/magenta] directory.

        $ [dim]nextmv cloud run create --app-id hare-app --managed-input-id carrot-input --output outputs[/dim]
    """

    content_format = parse_content_format(content_format)

    # Validate that input is provided.
    stdin = sys.stdin.read().strip() if sys.stdin.isatty() is False else None
    if stdin is None and (input is None or input == "") and (managed_input_id is None or managed_input_id == ""):
        error("Input data must be provided via the --input or --managed-input-id flags, or [magenta]stdin[/magenta].")

    # Instantiate the basic requirements to start a new run.
    cloud_app, _ = build_cloud_app(app_id=app_id, profile=profile)
    config = build_run_config(
        run_type=run_type,
        priority=priority,
        no_queuing=no_queuing,
        execution_class=execution_class,
        content_format=content_format,
        secret_collection_id=secret_collection_id,
        integration_id=integration_id,
        definition_id=definition_id,
    )
    run_options = build_run_options(options)
    config = _resolve_ensemble_content_format(config=config, stdin=stdin, input=input)

    # Start the run before deciding if we should poll or not.
    input_kwarg = resolve_input_kwarg(
        stdin=stdin,
        input=input,
        managed_input_id=managed_input_id,
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
        print_json({"run_id": run_id})

        return

    success(f"Run [magenta]{run_id}[/magenta] created.")

    # Build the polling options.
    polling_options = default_polling_options()
    polling_options.max_duration = timeout

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
    execution_class: str | None = None,
    content_format: ContentFormat | None = None,
    secret_collection_id: str | None = None,
    integration_id: str | None = None,
    definition_id: str | None = None,
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
    content_format : ContentFormat | None
        The content format of the run to create, if applicable.
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

    if run_type == RunType.ENSEMBLE and not definition_id:
        error(
            f"--run-type set to [magenta]{RunType.ENSEMBLE.value}[/magenta] and --definition-id not set. "
            "A definition ID must be provided for ensemble runs.",
        )

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
    if content_format is not None:
        config.format = Format(
            format_input=FormatInput(
                input_type=content_format,
            ),
        )
    if secret_collection_id is not None:
        config.secrets_collection_id = secret_collection_id
    if integration_id is not None:
        config.integration_id = integration_id
    if definition_id is not None:
        config.run_type.definition_id = definition_id
        config.run_type.run_type = RunType.ENSEMBLE

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


def resolve_input_kwarg(
    stdin: str | None,
    input: str | None,
    managed_input_id: str | None,
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

    # It is possible to not provide any input when we are cloning a run.
    if stdin is None and input is None and managed_input_id is None:
        return {}

    if stdin:
        # Handle the case where stdin is provided as JSON for a JSON app.
        try:
            input_data = json.loads(stdin)
        except json.JSONDecodeError:
            input_data = stdin

        return {"input": input_data}

    if managed_input_id is not None and managed_input_id != "":
        return {"managed_input_id": managed_input_id}

    input_path = Path(input)

    # If the input is a file, we need to determine if it is a tar file or
    # a regular file and upload it accordingly. If it is a regular file, we
    # need to read its content.
    if input_path.is_file():
        upload_url = cloud_app.upload_url()
        if tarfile.is_tarfile(input_path):
            cloud_app.upload_data(data=None, upload_url=upload_url, tar_file=input_path)
        else:
            input_data = input_path.read_text()
            cloud_app.upload_data(data=input_data, upload_url=upload_url)

        return {"upload_id": upload_url.upload_id}

    # If the input is a directory, we give the path directly to the run method.
    # Internally, the files will be tarred and uploaded.
    if input_path.is_dir():
        return {"input_dir_path": input}

    error(f"Input path [magenta]{input}[/magenta] does not exist.")


def _resolve_ensemble_content_format(
    config: RunConfiguration,
    stdin: str | None,
    input: str | None,
) -> RunConfiguration:
    """
    Sets the run type to ensemble in the run configuration if the content
    format is not explicitly set and the run type is ensemble. This is needed
    to trigger the auto-detection of the content format for ensemble runs,
    which is based on the input provided. If the content format is explicitly
    set, we assume the user knows what they are doing and we do not override
    it.

    Parameters
    ----------
    config : RunConfiguration
        The run configuration to update.
    stdin : str | None
        The stdin input data, if provided.
    input : str | None
        The input path, if provided.

    Returns
    -------
    RunConfiguration
        The updated run configuration with the inferred content format.
    """

    # If we are not dealing with an ensemble run or the content format is
    # explicitly set, we do not need to do anything.
    if config.run_type.run_type != RunType.ENSEMBLE or (
        config.format is not None and config.format.format_input is not None
    ):
        return config

    # When cloning a run, there is no input to infer the content format from.
    # In that case, we do not modify the config.
    if stdin is None and input is None:
        return config

    # Infer the appropriate content format based on the input provided.
    content_format = ContentFormat.JSON
    if stdin is not None:
        try:
            json.loads(stdin)
        except json.JSONDecodeError:
            content_format = InputFormat.TEXT

    if input is not None:
        input_path = Path(input)
        if input_path.is_dir() or (input_path.is_file() and tarfile.is_tarfile(input_path)):
            content_format = ContentFormat.MULTI_FILE
        elif not input_path.is_file():
            error(f"Input path [magenta]{input}[/magenta] does not exist.")

    # Set the appropriate content format in the config to trigger the correct
    # handling of the input for ensemble runs.
    if config.format is None:
        config.format = Format(format_input=FormatInput(input_type=content_format))
    else:
        config.format.format_input = FormatInput(input_type=content_format)

    return config
