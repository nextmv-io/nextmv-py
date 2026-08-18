"""
This module defines the cloud run clone command for the Nextmv CLI.
"""

import sys
from typing import Annotated

import typer

from nextmv.cli.cloud.run.create import build_run_options, resolve_input_kwarg
from nextmv.cli.cloud.run.get import handle_outputs
from nextmv.cli.cloud.run.logs import handle_logs
from nextmv.cli.configuration.config import build_cloud_app
from nextmv.cli.message import enum_values, parse_content_format, print_json, success
from nextmv.cli.options import AppIDOption, DebugOption, ProfileOption
from nextmv.content_format import ContentFormat
from nextmv.input import InputFormat
from nextmv.polling import default_polling_options
from nextmv.run import Format, FormatInput, RunConfiguration, RunQueuing, RunType, RunTypeConfiguration

# Set up subcommand application.
app = typer.Typer()


@app.command()
def clone(
    app_id: AppIDOption,
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
            help="The definition ID to use for the run. Required for certain run types like ensemble runs.",
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
        int | None,
        typer.Option(
            "--priority",
            help="The priority of the run. Priority is between 1 and 9, with 1 being the highest priority.",
            metavar="PRIORITY",
            rich_help_panel="Run configuration",
        ),
    ] = None,
    run_type: Annotated[
        RunType | None,
        typer.Option(
            "--run-type",
            help=f"The type of run to create. Allowed values are: {enum_values(RunType)}.",
            metavar="RUN_TYPE",
            rich_help_panel="Run configuration",
        ),
    ] = None,
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
    Clone an existing Nextmv Cloud application run.

    All information of the original (cloned) run will be reused. You may
    override any information you wish, such as the input, content format, or
    instance, for example. All the options for creating the new run work the
    same way as in the [code]nextmv cloud run create[/code] command. You may
    inspect the documentation of that command for more details on what each
    option does.

    [bold][underline]Examples[/underline][/bold]

    - Clone run [magenta]run-123[/magenta] from app [magenta]hare-app[/magenta],
      reusing the original run's input.

        $ [dim]nextmv cloud run clone --app-id hare-app --cloned-run-id run-123[/dim]

    - Clone run [magenta]run-123[/magenta] from app [magenta]hare-app[/magenta],
      overriding the input with a [magenta]json[/magenta] file via [magenta]stdin[/magenta].
        $ [dim]cat input.json | nextmv cloud run clone --app-id hare-app --cloned-run-id run-123[/dim]

    - Clone run [magenta]run-123[/magenta] from app [magenta]hare-app[/magenta],
      overriding the input with an [magenta]input.json[/magenta] file.

        $ [dim]nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --input input.json[/dim]

    - Clone run [magenta]run-123[/magenta] from app [magenta]hare-app[/magenta].
      Wait for the run to complete and print the result to [magenta]stdout[/magenta].

        $ [dim]nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --wait[/dim]

    - Clone run [magenta]run-123[/magenta] from app [magenta]hare-app[/magenta].
      Tail the run's logs, streaming to [magenta]stderr[/magenta].

        $ [dim]nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --tail[/dim]

    - Clone run [magenta]run-123[/magenta] from app [magenta]hare-app[/magenta].
      Wait for the run to complete and write the result to an [magenta]output.json[/magenta] file.

        $ [dim]nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --output output.json[/dim]

    - Clone run [magenta]run-123[/magenta] from app [magenta]hare-app[/magenta].
      Wait for the run to complete, and write the logs to a [magenta]logs.log[/magenta] file.

        $ [dim]nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --logs logs.log[/dim]

    - Clone run [magenta]run-123[/magenta] from app [magenta]hare-app[/magenta]. Wait for the run to complete. Tail
      the run's logs, streaming to [magenta]stderr[/magenta]. Write the logs to a [magenta]logs.log[/magenta] file.
      Write the result to an [magenta]output.json[/magenta] file.

        $ [dim]nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --tail --logs logs.log \\
            --output output.json [/dim]

    - Clone run [magenta]run-123[/magenta] from app [magenta]hare-app[/magenta], overriding the input with a
      [magenta]multi-file[/magenta] directory, using the [magenta]default[/magenta] instance.

        $ [dim]nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --input inputs \\
            --instance-id default[/dim]

    - Clone run [magenta]run-123[/magenta] from app [magenta]hare-app[/magenta], overriding the input with a
      [magenta]multi-file[/magenta] directory, using the [magenta]burrow[/magenta] instance.
      Wait for the run to complete and download the result files to an [magenta]outputs[/magenta] directory.

        $ [dim]nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --input inputs --instance-id burrow \\
            --output outputs[/dim]

    - Clone run [magenta]run-123[/magenta] from app [magenta]hare-app[/magenta], overriding the input with a
      [magenta]Nextmv managed[/magenta] input with ID [magenta]carrot-input[/magenta].
      Wait for the run to complete and download the result files to an [magenta]outputs[/magenta] directory.

        $ [dim]nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --managed-input-id carrot-input \\
            --output outputs[/dim]
    """

    content_format = parse_content_format(content_format)
    stdin = sys.stdin.read().strip() if sys.stdin.isatty() is False else None

    # Instantiate the basic requirements to start a new run.
    cloud_app, _ = build_cloud_app(app_id=app_id, profile=profile)
    config = _build_run_config(
        no_queuing=no_queuing,
        run_type=run_type,
        priority=priority,
        execution_class=execution_class,
        content_format=content_format,
        secret_collection_id=secret_collection_id,
        integration_id=integration_id,
        definition_id=definition_id,
    )
    run_options = build_run_options(options)

    # Start the run before deciding if we should poll or not.
    input_kwarg = resolve_input_kwarg(
        stdin=stdin,
        input=input,
        managed_input_id=managed_input_id,
        cloud_app=cloud_app,
    )
    run_id = cloud_app.clone_run(
        **input_kwarg,
        cloned_run_id=cloned_run_id,
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

    success(f"Run [magenta]{run_id}[/magenta] cloned from original run [magenta]{cloned_run_id}[/magenta].")

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


def _build_run_config(
    no_queuing: bool,
    run_type: RunType | None = None,
    priority: int | None = None,
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
    no_queuing : bool
        Whether to disable queuing for the run.
    run_type : RunType | None
        The type of run to create.
    priority : int | None
        The priority of the run.
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

    config = RunConfiguration(
        queuing=RunQueuing(
            disabled=no_queuing,
        ),
    )

    if run_type is not None:
        config.run_type = RunTypeConfiguration(run_type=RunType(run_type))
    if priority is not None:
        config.queuing.priority = priority
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

    return config
