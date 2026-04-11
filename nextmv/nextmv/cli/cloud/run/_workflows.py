"""CLI-only workflows for the cloud run domain.

Run commands support polling (``--wait``, ``--tail``), file saves with
content-format-aware handling (JSON/text → file, multi-file/archive →
directory), inline metric/stat/asset JSON files, and stdin input. These
concerns don't fit the framework's default ``emit()``/``on_success``
flow, so they live in workflow functions that opt into
``handles_own_output=True``.
"""

import json
import sys
import tarfile
from pathlib import Path
from typing import Annotated, Any

import rich
import typer

from nextmv.cli.actions.run import (
    run_input as action_run_input,
)
from nextmv.cli.actions.run import submit_run
from nextmv.cli.framework.options import AppIdRequiredOption, RunIdOption
from nextmv.cli.message import enum_values, error, in_progress, print_json, success, warning
from nextmv.cloud import Application, Client
from nextmv.input import InputFormat
from nextmv.output import OutputFormat
from nextmv.polling import PollingOptions, default_polling_options
from nextmv.run import (
    Format,
    FormatInput,
    RunConfiguration,
    RunQueuing,
    RunType,
    RunTypeConfiguration,
    TrackedRun,
    TrackedRunStatus,
)

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _build_run_config(
    run_type: RunType,
    priority: int,
    no_queuing: bool,
    execution_class: str | None = None,
    content_format: InputFormat | None = None,
    secret_collection_id: str | None = None,
    integration_id: str | None = None,
    definition_id: str | None = None,
) -> RunConfiguration:
    """Build a ``RunConfiguration`` from CLI flag values."""
    config = RunConfiguration(
        run_type=RunTypeConfiguration(run_type=RunType(run_type)),
        queuing=RunQueuing(priority=priority, disabled=no_queuing),
    )
    if execution_class is not None:
        config.execution_class = execution_class
    if content_format is not None:
        config.format = Format(
            format_input=FormatInput(input_type=InputFormat(content_format)),
        )
    if secret_collection_id is not None:
        config.secrets_collection_id = secret_collection_id
    if integration_id is not None:
        config.integration_id = integration_id
    if definition_id is not None:
        config.run_type.definition_id = definition_id

    return config


def _build_run_options(options: list[str] | None) -> dict[str, str] | None:
    """Parse ``key=value`` option flags into a dict.

    Options may be provided by repeating the flag or by separating with
    commas inside a single flag, or both.
    """
    if options is None:
        return None

    run_options: dict[str, str] = {}
    for opt in options:
        sub_opts = opt.split(",")
        for sub_opt in sub_opts:
            key_value = sub_opt.split("=", 1)
            if len(key_value) != 2:
                error(f"Invalid option format: {sub_opt}. Expected format is [magenta]key=value[/magenta].")
            key, value = key_value
            run_options[key] = value
    return run_options


def _resolve_input_kwarg(
    stdin: str | None,
    input: str | None,
    managed_input_id: str | None,
    cloud_app: Application,
) -> dict[str, Any]:
    """Resolve the input source into a kwarg for ``submit_run``."""
    if stdin is not None:
        try:
            input_data = json.loads(stdin)
        except json.JSONDecodeError:
            input_data = stdin
        return {"input": input_data}

    if managed_input_id is not None and managed_input_id != "":
        return {"managed_input_id": managed_input_id}

    input_path = Path(input)

    if input_path.is_file():
        upload_url = cloud_app.upload_url()
        if tarfile.is_tarfile(input_path):
            cloud_app.upload_data(data=None, upload_url=upload_url, tar_file=input_path)
        else:
            input_data = input_path.read_text()
            cloud_app.upload_data(data=input_data, upload_url=upload_url)
        return {"upload_id": upload_url.upload_id}

    if input_path.is_dir():
        return {"input_dir_path": input}

    error(f"Input path [magenta]{input}[/magenta] does not exist.")


def _handle_outputs(
    cloud_app: Application,
    run_id: str,
    wait: bool,
    output: str | None,
    polling_options: PollingOptions,
    skip_wait_check: bool = False,
) -> None:
    """Retrieve a run's output, handling content-format-aware saving."""
    if not wait and (output is None or output == "") and not skip_wait_check:
        return

    run_info = cloud_app.run_metadata(run_id=run_id)
    content_format = run_info.metadata.format.format_output.output_type

    kwargs: dict[str, Any] = {"run_id": run_id}
    output_dir: str | None = None
    if content_format not in {OutputFormat.JSON, OutputFormat.TEXT}:
        output_dir = f"{run_id}-output" if output is None or output == "" else output
        kwargs["output_dir_path"] = output_dir

    in_progress(msg="Getting run results...")
    wait = wait or (output is not None and output != "")
    if wait:
        kwargs["polling_options"] = polling_options
        run_result_obj = cloud_app.run_result_with_polling(**kwargs)
    else:
        run_result_obj = cloud_app.run_result(**kwargs)

    if content_format in {OutputFormat.JSON, OutputFormat.TEXT}:
        if output is None or output == "":
            print_json(run_result_obj.to_dict())
        else:
            with open(output, "w") as f:
                json.dump(run_result_obj.to_dict(), f, indent=2)
            success(f"Run output written to [magenta]{output}[/magenta].")
        return

    result_dict = run_result_obj.to_dict()
    if "output" in result_dict:
        del result_dict["output"]

    success(f"Run outputs saved to [magenta]{output_dir}[/magenta]. Here is the metadata.")
    print_json(result_dict)


def _handle_logs(
    cloud_app: Application,
    run_id: str,
    tail: bool,
    logs: str | None,
    polling_options: PollingOptions,
    file_output: bool,
) -> None:
    """Retrieve a run's logs, with optional tailing and file persistence."""
    log_content: str
    if tail:
        in_progress(msg="Tailing logs...")
        fetched_logs = cloud_app.run_logs_with_polling(
            run_id=run_id,
            polling_options=polling_options,
            verbose=True,
            rich_print=True,
        )
        if logs is None:
            return
        log_content = "".join(log_entry.log for log_entry in fetched_logs)
    elif logs is not None and logs != "" and file_output:
        in_progress(msg="Getting run logs...")
        cloud_app.run_result_with_polling(run_id=run_id, polling_options=polling_options)
        fetched_logs = cloud_app.run_logs(run_id=run_id)
        log_content = fetched_logs.log
    elif not file_output:
        in_progress(msg="Getting run logs...")
        fetched_logs = cloud_app.run_logs(run_id=run_id)
        rich.print(fetched_logs.log, file=sys.stderr)
        return
    else:
        return

    Path(logs).write_text(log_content)
    success(f"Run logs written to [magenta]{logs}[/magenta].")


# ---------------------------------------------------------------------------
# list — save or print runs
# ---------------------------------------------------------------------------


def run_list_runs(
    client: Client,
    app_id: AppIdRequiredOption,
    status: Annotated[
        str | None,
        typer.Option(
            "--status",
            "-s",
            help="Filter runs by status. Allowed values: queued, running, succeeded, failed, canceled.",
            metavar="STATUS",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the list of runs to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Get the list of runs for a Nextmv Cloud application.

    By default, the list of runs is fetched and printed to ``stdout``.
    Use the ``--output`` flag to save the list to a file. You can use
    the optional ``--status`` flag to filter runs by their status.
    """
    from nextmv.cli.actions.run import list_runs

    in_progress(msg="Listing app runs...")
    runs_dicts = list_runs(client, app_id=app_id, status=status)

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(runs_dicts, f, indent=2)
        success(msg=f"Run list saved to [magenta]{output}[/magenta].")
        return

    print_json(runs_dicts)


# ---------------------------------------------------------------------------
# metadata — save or print
# ---------------------------------------------------------------------------


def run_metadata_workflow(
    client: Client,
    app_id: AppIdRequiredOption,
    run_id: RunIdOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the metadata to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Get the metadata of a Nextmv Cloud application run.

    By default, the metadata is fetched and printed to ``stdout``. Use
    the ``--output`` flag to save the metadata to a file.
    """
    from nextmv.cli.actions.run import run_metadata

    in_progress(msg="Getting run metadata...")
    info_dict = run_metadata(client, app_id=app_id, run_id=run_id)

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(info_dict, f, indent=2)
        success(msg=f"Run metadata saved to [magenta]{output}[/magenta].")
        return

    print_json(info_dict)


# ---------------------------------------------------------------------------
# get — output retrieval with --wait polling
# ---------------------------------------------------------------------------


def run_get_run(
    client: Client,
    app_id: AppIdRequiredOption,
    run_id: RunIdOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help=(
                "Waits for the run to complete and save the output to this location. "
                "A file or directory will be created depending on content format."
            ),
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    timeout: Annotated[
        int,
        typer.Option(
            help="The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.",
            metavar="TIMEOUT_SECONDS",
        ),
    ] = -1,
    wait: Annotated[
        bool,
        typer.Option(
            "--wait",
            "-w",
            help=(
                "Wait for the run to complete. Run result is printed to [magenta]stdout[/magenta] for "
                "[magenta]json[/magenta], to a dir for [magenta]multi-file[/magenta]. "
                "Specify output location with --output."
            ),
        ),
    ] = False,
) -> None:
    """Get the result (output) of a Nextmv Cloud application run.

    Use the ``--wait`` flag to wait for the run to complete, polling for
    results. Using the ``--output`` flag will also activate waiting, and
    allows you to specify a destination (file or dir) for the output,
    depending on the content type.
    """
    cloud_app = Application(client=client, id=app_id)

    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    _handle_outputs(
        cloud_app=cloud_app,
        run_id=run_id,
        wait=wait,
        output=output,
        polling_options=polling_options,
        skip_wait_check=True,
    )


# ---------------------------------------------------------------------------
# input — save or print run input
# ---------------------------------------------------------------------------


def run_get_input(
    client: Client,
    app_id: AppIdRequiredOption,
    run_id: RunIdOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the input to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Get the input of a Nextmv Cloud application run.

    By default, the input is fetched and printed to ``stdout``. Use the
    ``--output`` flag to save the input to a file (or directory for
    multi-file content formats).
    """
    cloud_app = Application(client=client, id=app_id)
    in_progress(msg="Getting run input...")

    run_info = cloud_app.run_metadata(run_id)

    if run_info.metadata.format.format_input.input_type not in {OutputFormat.JSON, OutputFormat.TEXT}:
        output = f"{run_id}-input" if output is None or output == "" else output
        action_run_input(client, app_id=app_id, run_id=run_id, output_dir_path=output)
        success(msg=f"Run input saved to [magenta]{output}[/magenta].")
        return

    fetched_input = action_run_input(client, app_id=app_id, run_id=run_id)

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(fetched_input, f, indent=2)
        success(msg=f"Run input saved to [magenta]{output}[/magenta].")
        return

    print_json(data=fetched_input)


# ---------------------------------------------------------------------------
# logs — tail, save, or print
# ---------------------------------------------------------------------------


def run_get_logs(
    client: Client,
    app_id: AppIdRequiredOption,
    run_id: RunIdOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Waits for the run to complete and saves the logs to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    tail: Annotated[
        bool,
        typer.Option(
            "--tail",
            "-t",
            help=(
                "Tail the logs until the run completes. Logs are streamed to [magenta]stderr[/magenta]. "
                "Specify log output location with --output."
            ),
        ),
    ] = False,
    timeout: Annotated[
        int,
        typer.Option(
            help="The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.",
            metavar="TIMEOUT_SECONDS",
        ),
    ] = -1,
) -> None:
    """Get the logs of a Nextmv Cloud application run.

    By default, the logs are fetched and printed to ``stderr``. Use the
    ``--tail`` flag to stream logs to ``stderr`` until the run
    completes. Using the ``--output`` flag will also activate waiting,
    and allows you to specify a file to write the logs to.
    """
    cloud_app = Application(client=client, id=app_id)

    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    _handle_logs(
        cloud_app=cloud_app,
        run_id=run_id,
        tail=tail,
        logs=output,
        polling_options=polling_options,
        file_output=output is not None,
    )


# ---------------------------------------------------------------------------
# create — submit a run with many options
# ---------------------------------------------------------------------------


_CREATE_CONTENT_FORMAT_HELP = (
    f"The content format of the run to create. Allowed values are: {enum_values(InputFormat)}."
)
_CREATE_RUN_TYPE_HELP = f"The type of run to create. Allowed values are: {enum_values(RunType)}."


def run_create_run(
    client: Client,
    app_id: AppIdRequiredOption,
    # Input control
    input: Annotated[
        str | None,
        typer.Option(
            "--input",
            "-i",
            help=(
                "The input path to use. File or directory depending on content format. "
                "Uses [magenta]stdin[/magenta] if not defined. "
                "Can be a [magenta].tar.gz[/magenta] file for multi-file content format."
            ),
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
    # Output control
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
            help=(
                "Waits for the run to complete and save the output to this location. "
                "A file or directory will be created depending on content format."
            ),
            metavar="OUTPUT_PATH",
            rich_help_panel="Output control",
        ),
    ] = None,
    tail: Annotated[
        bool,
        typer.Option(
            "--tail",
            "-t",
            help=(
                "Tail the logs until the run completes. Logs are streamed to [magenta]stderr[/magenta]. "
                "Specify log output location with --logs."
            ),
            rich_help_panel="Output control",
        ),
    ] = False,
    wait: Annotated[
        bool,
        typer.Option(
            "--wait",
            "-w",
            help=(
                "Wait for the run to complete. Run result is printed to [magenta]stdout[/magenta] for "
                "[magenta]json[/magenta], to a dir for [magenta]multi-file[/magenta]. "
                "Specify output location with --output."
            ),
            rich_help_panel="Output control",
        ),
    ] = False,
    # Run configuration
    content_format: Annotated[
        InputFormat | None,
        typer.Option(
            "--content-format",
            "-c",
            help=_CREATE_CONTENT_FORMAT_HELP,
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
    ] = None,
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
            help=(
                "Do not queue run. Default is [magenta]False[/magenta], "
                "meaning the run [italic]will[/italic] be queued."
            ),
            rich_help_panel="Run configuration",
        ),
    ] = False,
    options: Annotated[
        list[str] | None,
        typer.Option(
            "--options",
            "-o",
            help=(
                "Options passed to the run. Format: [magenta]key=value[/magenta]. "
                "Pass multiple options by repeating the flag, or separating with commas."
            ),
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
            help=_CREATE_RUN_TYPE_HELP,
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
    """Create a new Nextmv Cloud application run.

    Input for the run should be given through ``stdin``, the ``--input``
    flag, or a Nextmv managed input via ``--managed-input-id``.

    Use ``--wait`` to wait for the run to complete, or ``--output`` to
    save the result to a file/directory (which also activates waiting).
    Use ``--tail`` to stream logs to ``stderr``, or ``--logs`` to save
    them to a file.
    """
    stdin = sys.stdin.read().strip() if sys.stdin.isatty() is False else None
    if stdin is None and (input is None or input == "") and (managed_input_id is None or managed_input_id == ""):
        error("Input data must be provided via the --input or --managed-input-id flags, or [magenta]stdin[/magenta].")

    cloud_app = Application(client=client, id=app_id)
    config = _build_run_config(
        run_type=run_type,
        priority=priority,
        no_queuing=no_queuing,
        execution_class=execution_class,
        content_format=content_format,
        secret_collection_id=secret_collection_id,
        integration_id=integration_id,
        definition_id=definition_id,
    )
    run_options = _build_run_options(options)

    input_kwarg = _resolve_input_kwarg(
        stdin=stdin,
        input=input,
        managed_input_id=managed_input_id,
        cloud_app=cloud_app,
    )
    run_id = submit_run(
        client,
        app_id=app_id,
        **input_kwarg,
        instance_id=instance_id,
        name=name,
        description=description,
        options=run_options,
        configuration=config,
    )

    if not wait and not tail and output is None and logs is None:
        print_json({"run_id": run_id})
        return

    success(f"Run [magenta]{run_id}[/magenta] created.")

    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    _handle_logs(
        cloud_app=cloud_app,
        run_id=run_id,
        tail=tail,
        logs=logs,
        polling_options=polling_options,
        file_output=True,
    )
    _handle_outputs(
        cloud_app=cloud_app,
        run_id=run_id,
        wait=wait,
        output=output,
        polling_options=polling_options,
        skip_wait_check=False,
    )


# ---------------------------------------------------------------------------
# track — track an external run
# ---------------------------------------------------------------------------


_TRACK_CONTENT_FORMAT_HELP = (
    f"The content format of the run to track. Allowed values are: {enum_values(InputFormat)}."
)
_TRACK_STATUS_HELP = f"Status of the tracked run. Allowed values are: {enum_values(TrackedRunStatus)}."


def _resolve_tracked_input(
    tracked_run: TrackedRun,
    stdin: str | None,
    input: str | None,
    content_format: InputFormat,
) -> TrackedRun:
    if stdin is not None:
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

    input_path = Path(input)
    if input_path.is_file():
        if content_format == InputFormat.JSON:
            try:
                with input_path.open("r") as f:
                    tracked_run.input = json.load(f)
                return tracked_run
            except json.JSONDecodeError as e:
                error(f"Failed to parse input file [magenta]{input}[/magenta] as [magenta]json[/magenta]: {e}.")
        elif content_format == InputFormat.TEXT:
            tracked_run.input = input_path.read_text()
            return tracked_run
        else:
            error(f"Unsupported content format [magenta]{content_format.value}[/magenta] for file input.")

    if input_path.is_dir():
        tracked_run.input_dir_path = input
        return tracked_run

    error(f"Input path [magenta]{input}[/magenta] does not exist.")


def _resolve_tracked_output(
    tracked_run: TrackedRun,
    output: str,
    content_format: InputFormat,
) -> TrackedRun:
    output_path = Path(output)
    if output_path.is_file():
        if content_format == InputFormat.JSON:
            try:
                with output_path.open("r") as f:
                    tracked_run.output = json.load(f)
                return tracked_run
            except json.JSONDecodeError as e:
                error(f"Failed to parse output file [magenta]{output}[/magenta] as [magenta]json[/magenta]: {e}.")
        elif content_format == InputFormat.TEXT:
            tracked_run.output = output_path.read_text()
            return tracked_run
        else:
            error(f"Unsupported content type [magenta]{content_format.value}[/magenta] for file output.")

    if output_path.is_dir():
        tracked_run.output_dir_path = output
        return tracked_run

    error(f"Output path [magenta]{output}[/magenta] does not exist.")


def _build_tracked_run(
    status: TrackedRunStatus,
    duration: int,
    error_msg: str | None,
    name: str | None,
    description: str | None,
    stdin: str | None,
    input: str | None,
    content_format: InputFormat,
    output: str,
    assets: str | None,
    logs: str | None,
    statistics: str | None,
    metrics: str | None,
) -> TrackedRun:
    tracked_run = TrackedRun(
        status=TrackedRunStatus(status),
        duration=duration,
        error=error_msg,
        name=name,
        description=description,
    )
    tracked_run = _resolve_tracked_input(
        tracked_run=tracked_run,
        stdin=stdin,
        input=input,
        content_format=content_format,
    )
    tracked_run = _resolve_tracked_output(
        tracked_run=tracked_run,
        output=output,
        content_format=content_format,
    )

    if assets is not None and assets != "":
        try:
            with open(assets) as f:
                tracked_run.assets = json.load(f)
        except json.JSONDecodeError as e:
            error(f"Failed to parse assets file [magenta]{assets}[/magenta] as [magenta]json[/magenta]: {e}.")

    if logs is not None and logs != "":
        try:
            tracked_run.logs = Path(logs).read_text()
        except Exception as e:
            error(f"Failed to read logs file [magenta]{logs}[/magenta]: {e}.")

    if statistics is not None and statistics != "":
        try:
            with open(statistics) as f:
                tracked_run.statistics = json.load(f)
        except json.JSONDecodeError as e:
            error(f"Failed to parse statistics file [magenta]{statistics}[/magenta] as [magenta]json[/magenta]: {e}.")

    if metrics is not None and metrics != "":
        try:
            with open(metrics) as f:
                tracked_run.metrics = json.load(f)
        except json.JSONDecodeError as e:
            error(f"Failed to parse metrics file [magenta]{metrics}[/magenta] as [magenta]json[/magenta]: {e}.")

    return tracked_run


def run_track_run(
    client: Client,
    app_id: AppIdRequiredOption,
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
            help=_TRACK_STATUS_HELP,
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
            help=_TRACK_CONTENT_FORMAT_HELP,
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
            help=(
                "The input of the run being tracked. File or directory depending on content format. "
                "Uses [magenta]stdin[/magenta] if not defined."
            ),
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
            help=(
                "[red](deprecated) Use --metrics instead.[/red] The statistics of the run being tracked. "
                "A [magenta]json[/magenta] file to read the statistics from."
            ),
            metavar="STATISTICS_PATH",
            rich_help_panel="Tracked run configuration",
        ),
    ] = None,
    metrics: Annotated[
        str | None,
        typer.Option(
            help="The metrics of the run being tracked. A [magenta]json[/magenta] file to read the metrics from.",
            metavar="METRICS_PATH",
            rich_help_panel="Tracked run configuration",
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
) -> None:
    """Track an external run as a Nextmv Cloud application run.

    Run logs, assets, and metrics can be provided via files using the
    ``--logs``, ``--assets``, and ``--metrics`` options respectively.
    """
    if statistics:
        warning("The --statistics option is deprecated, use --metrics instead.")
    stdin = sys.stdin.read().strip() if sys.stdin.isatty() is False else None
    if stdin is None and (input is None or input == ""):
        error("Input data must be provided via the --input flag or [magenta]stdin[/magenta].")

    cloud_app = Application(client=client, id=app_id)
    config = _build_run_config(
        run_type=RunType.EXTERNAL,
        priority=6,
        no_queuing=False,
        content_format=content_format,
    )

    if instance_id == "default":
        instance_id = ""

    tracked_run = _build_tracked_run(
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
        metrics=metrics,
    )

    in_progress(msg="Tracking run...")
    run_id = cloud_app.track_run(
        tracked_run=tracked_run,
        instance_id=instance_id,
        configuration=config,
    )

    print_json({"run_id": run_id})


