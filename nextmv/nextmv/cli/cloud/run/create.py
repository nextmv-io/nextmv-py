"""
This module defines the community clone command for the Nextmv CLI.
"""

from typing import Annotated

import rich
import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.error import error
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.input import InputFormat
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
            help="The location to stream the logs to (in addition to the terminal). "
            "Activates tailing if not set. Automatically names file if defined without filename.",
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
            help="The output location to use. File or directory depending on content type. "
            "Activates polling if not set. Uses [magenta]stdout[/magenta] or a generated filename if not specified.",
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
    should_poll = output is not None or logs is not None
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

    result = method(**kwargs)
    if should_poll and isinstance(result, RunResult):
        unserialized_res = result.to_dict()
    elif not should_poll and isinstance(result, str):
        unserialized_res = {"run_id": result}
    else:
        error("Unexpected result type received from run creation.")

    rich.print(unserialized_res)


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
