"""
This module defines the community clone command for the Nextmv CLI.
"""

import json
import sys
import tarfile
from pathlib import Path
from typing import Annotated, Any

import rich
import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.error import error
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.application import Application
from nextmv.input import InputFormat
from nextmv.output import OutputFormat
from nextmv.polling import DEFAULT_POLLING_OPTIONS
from nextmv.run import Format, FormatInput, RunConfiguration, RunQueuing, RunResult, RunType, RunTypeConfiguration

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    app_id: AppIDOption,
    content_type: Annotated[
        InputFormat | None,
        typer.Option(
            "--content-type",
            "-c",
            help="The content type of the run to create. Allowed values are: "
            f"{[v.value for v in InputFormat.__members__.values()]}",
            metavar="CONTENT_TYPE",
        ),
    ] = None,
    definition_id: Annotated[
        str | None,
        typer.Option(
            "--definition-id",
            "-d",
            help="The definition ID to use for the run. Required for certain run types like ensemble runs.",
            metavar="DEFINITION_ID",
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            help="An optional description for the new run.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    execution_class: Annotated[
        str | None,
        typer.Option(
            "--execution-class",
            "-e",
            help="The execution class to use for the run, if applicable.",
            metavar="EXECUTION_CLASS",
        ),
    ] = None,
    input: Annotated[
        str | None,
        typer.Option(
            "--input",
            "-i",
            help="The input location to use. File or directory depending on content type. "
            "Uses [magenta]stdin[/magenta] if not defined.",
            metavar="INPUT_DATA",
        ),
    ] = None,
    instance_id: Annotated[
        str | None,
        typer.Option(
            help="The instance ID to use for the run.",
            metavar="INSTANCE_ID",
        ),
    ] = "latest",
    integration_id: Annotated[
        str | None,
        typer.Option(
            help="The integration ID to use for the run, if applicable.",
            metavar="INTEGRATION_ID",
        ),
    ] = None,
    logs: Annotated[
        str | None,
        typer.Option(
            "--logs",
            "-l",
            help="The location to stream the logs to. They will also be streamed to [magenta]stdout[/magenta]. "
            "Activates [code]--wait[/code] if not set.",
            metavar="LOGS_OUTPUT",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="An optional name for the new run.",
            metavar="NAME",
        ),
    ] = None,
    no_queuing: Annotated[
        bool,
        typer.Option(
            "--no-queuing",
            help="Do not queue run. Default is [magenta]False[/magenta], "
            "meaning the run [italic]will[/italic] be queued.",
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
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-u",
            help="The output location to use. A file or directory will be created depending on content type."
            "Activates [code]--wait[/code] if not set.",
            metavar="OUTPUT_DATA",
        ),
    ] = None,
    priority: Annotated[
        int,
        typer.Option(
            help="The priority of the run. Priority is between 1 and 10, with 1 being the highest priority.",
            metavar="PRIORITY",
        ),
    ] = 6,
    run_type: Annotated[
        RunType,
        typer.Option(
            "--run-type",
            "-r",
            help=f"The type of run to create. Allowed values are: {[v.value for v in RunType.__members__.values()]}",
            metavar="RUN_TYPE",
        ),
    ] = RunType.STANDARD,
    secret_collection_id: Annotated[
        str | None,
        typer.Option(
            "--secret-collection-id",
            "-s",
            help="The secret collection ID to use for the run, if applicable.",
            metavar="SECRET_COLLECTION_ID",
        ),
    ] = None,
    timeout: Annotated[
        int,
        typer.Option(
            "--timeout",
            "-t",
            help="The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.",
            metavar="TIMEOUT_SECONDS",
        ),
    ] = -1,
    wait: Annotated[
        bool,
        typer.Option(
            "--wait",
            "-w",
            help="Wait for the run to complete. Activates polling for the result and log streaming. "
            "Run result is printed to [magenta]stdout[/magenta] for [magenta]json[/magenta], "
            "to a directory for [magenta]multi-file[/magenta]. Logs are streamed to [magenta]stdout[/magenta].",
        ),
    ] = False,
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Cloud application run.

    An application run executes against a specific instance. An instance
    represents the combination of executable code and configuration. You can
    specify the instance with the [code]--instance-id[/code] flag. These are
    the possible values for this flag:

    - [green]latest[/green]: uses the special [magenta]latest[/magenta]
      instance of the application. This corresponds to the latest pushed
      executable.
    - [green]default[/green]: if the application has a [italic]default[/italic]
      instance configured, then it uses that instance. Setting the flag's value
      to [code]''[/code] (empty string) has the same effect.
    - [green]<INSTANCE_ID>[/green]: uses the instance with the given ID.
    """

    stdin = sys.stdin.read().strip() if sys.stdin.isatty() is False else None
    if stdin is None and input is None:
        error("Input data must be provided via the [code]--input[/code] flag or [magenta]stdin[/magenta].")

    cloud_app = build_app(app_id, profile)
    config = build_config(
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

    # Decide which method to use based on whether polling is needed.
    should_poll = wait or output is not None or logs is not None
    method = cloud_app.new_run
    kwargs = {
        "instance_id": instance_id,
        "name": name,
        "description": description,
        "configuration": config,
    }
    if should_poll:
        method = cloud_app.new_run_with_result
        kwargs["run_options"] = run_options
        kwargs["polling_options"] = polling_options
    else:
        kwargs["options"] = run_options

    # Resolve input (stdin, file, directory).
    kwargs = resolve_input(
        kwargs=kwargs,
        stdin=stdin,
        input=input,
        cloud_app=cloud_app,
    )

    # Actually create the run and resolve the result based on polling, output
    # specification, etc.
    result = method(**kwargs)
    resolve_result(
        should_poll=should_poll,
        result=result,
        output=output,
        cloud_app=cloud_app,
    )


def build_config(
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


def resolve_input(
    kwargs: dict[str, Any],
    stdin: str | None,
    input: str | None,
    cloud_app: Application,
) -> dict[str, Any]:
    """
    Resolves the input for the run creation. It handles stdin, file, and
    directory inputs. It uploads the input to the cloud application if needed.

    Parameters
    ----------
    kwargs : dict[str, Any]
        The existing keyword arguments for the run creation.
    stdin : str | None
        The stdin input data, if provided.
    input : str | None
        The input path, if provided.
    cloud_app : Application
        The cloud application instance.

    Returns
    -------
    dict[str, Any]
        The updated keyword arguments with the resolved input.
    """

    if stdin is not None:
        # Handle the case where stdin is provided as JSON for a JSON app.
        try:
            input_data = json.loads(stdin)
        except json.JSONDecodeError:
            input_data = stdin

        kwargs["input"] = input_data

        return kwargs

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

        kwargs["upload_id"] = upload_url.upload_id

        return kwargs

    # If the input is a directory, we give the path directly to the run method.
    # Internally, the files will be tarred and uploaded.
    if input_path.is_dir():
        kwargs["input_dir_path"] = input
        return kwargs

    error(f"Input path [magenta]{input}[/magenta] does not exist.")


def resolve_result(
    should_poll: bool,
    result: RunResult | str,
    output: str | None,
    cloud_app: Application,
) -> None:
    # Validate the combination of result type and polling.
    if (should_poll and not isinstance(result, RunResult)) or (not should_poll and not isinstance(result, str)):
        error(f"Unexpected result type ({type(result)}) and should_poll ({should_poll}) combination from run creation.")

    # We handle the non-polling case first, which is simply returning the run
    # ID.
    if not should_poll and isinstance(result, str):
        rich.print({"run_id": result})

        return

    # At this point, we know that we waited for the result and the type is a
    # RunResult.
    content_type = result.metadata.format.format_output.output_type

    # Handle the case where output is embedded directly in the result: json and
    # text.
    if content_type in {OutputFormat.JSON, OutputFormat.TEXT}:
        # If no output is specified, we print to stdout. Otherwise, we write
        # to the specified output file.
        if output is None:
            rich.print(result.to_dict())
        else:
            with open(output, "w") as f:
                json.dump(result.to_dict(), f, indent=2)
                rich.print(f":white_check_mark: Run output written to [magenta]{output}[/magenta].")

        return

    # Finally, we know that the output is multi-file or csv-archive, which
    # means we need to handle the output directory.
    run_id = result.id
    if output is None or output == "":
        output = run_id

    _ = cloud_app.run_result(run_id=run_id, output_dir_path=output)
    rich.print(f":white_check_mark: Run outputs downloaded to [magenta]{output}[/magenta]. Here is the metadata:")
    result_dict = result.to_dict()
    del result_dict["output"]
    rich.print(result_dict)
