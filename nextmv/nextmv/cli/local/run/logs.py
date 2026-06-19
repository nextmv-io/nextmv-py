"""
This module defines the local run logs command for the Nextmv CLI.
"""

import sys
from pathlib import Path
from typing import Annotated

import rich
import typer

from nextmv.cli.configuration.config import build_local_app
from nextmv.cli.message import in_progress, success
from nextmv.cli.options import DebugOption, LocalAppIDOption, LocalAppSrcOption, RunIDOption
from nextmv.local.application import Application
from nextmv.polling import PollingOptions, default_polling_options

# Set up subcommand application.
app = typer.Typer()


@app.command()
def logs(
    run_id: RunIDOption,
    app_id: LocalAppIDOption = None,
    app_src: LocalAppSrcOption = ".",
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
            help="Tail the logs until the run completes. Logs are streamed to [magenta]stderr[/magenta]. "
            "Specify log output location with --output.",
        ),
    ] = False,
    timeout: Annotated[
        int,
        typer.Option(
            help="The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.",
            metavar="TIMEOUT_SECONDS",
        ),
    ] = -1,
    _: DebugOption = False,
) -> None:
    """
    Get the logs of a local application run.

    You may identify the app by using --app-src, or --app-id if it has been
    registered. If the app is not already registered, this command will
    register it.

    By default, the logs are fetched and printed to [magenta]stderr[/magenta].
    Use the --tail flag to stream logs to [magenta]stderr[/magenta] until the
    run completes. Using the --output flag will also activate waiting, and
    allows you to specify a file to write the logs to.

    [bold][underline]Examples[/underline][/bold]

    - Get the logs of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Logs are printed to [magenta]stderr[/magenta].

        $ [dim]nextmv local run logs --app-id hare-app --run-id burrow-123[/dim]

    - Get the logs of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Tail the logs until the run completes.

        $ [dim]nextmv local run logs --app-id hare-app --run-id burrow-123 --tail[/dim]

    - Get the logs of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Save the logs to a [magenta]logs.log[/magenta] file.

        $ [dim]nextmv local run logs --app-id hare-app --run-id burrow-123 --output logs.log[/dim]

    - Get the logs of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Tail the logs and save them to a [magenta]logs.log[/magenta] file.

        $ [dim]nextmv local run logs --app-id hare-app --run-id burrow-123 --tail --output logs.log[/dim]

    - Get the logs of a run with ID [magenta]burrow-123[/magenta], belonging to an app with source path
      [magenta]./my-app[/magenta].

        $ [dim]nextmv local run logs --app-src ./my-app --run-id burrow-123[/dim]

    - Get the logs of a run with ID [magenta]burrow-123[/magenta], belonging to an app with source path
      [magenta]./my-app[/magenta]. Set a timeout of [magenta]60[/magenta] seconds.

        $ [dim]nextmv local run logs --app-src ./my-app --run-id burrow-123 --timeout 60[/dim]
    """

    local_app = build_local_app(app_src, app_id)

    # Build the polling options.
    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    handle_logs(
        local_app=local_app,
        run_id=run_id,
        tail=tail,
        logs=output,
        polling_options=polling_options,
        file_output=output is not None,
    )


def handle_logs(
    local_app: Application,
    run_id: str,
    tail: bool,
    logs: str | None,
    polling_options: PollingOptions,
    file_output: bool,
) -> None:
    """
    Handle retrieving and outputting logs from a run.

    When `tail` is True, logs are streamed in real-time to stderr as the run
    executes. When `logs` is specified (without tailing), the function waits
    for the run to complete and then fetches all logs at once. When neither
    `tail` is True nor `file_output` is set, logs are fetched immediately and
    printed to stderr without waiting for the run to complete. In all cases
    where `tail` is True or `logs` is specified, if a `logs` file path is
    provided, the logs are persisted to that file.

    Parameters
    ----------
    local_app : Application
        The local application instance used to interact with the Nextmv Local
        API.
    run_id : str
        The unique identifier of the run to retrieve logs for.
    tail : bool
        If True, streams logs in real-time to stderr as the run executes.
    logs : str | None
        The file path where logs should be written. If None, logs are only
        displayed to stderr (when tailing) and not persisted to a file.
    polling_options : PollingOptions
        Configuration options for polling behavior, including timeout and
        interval settings.
    file_output : bool
        Indicates whether logs should be written to a file. If False, logs are
        only printed to stderr, no matter the status of the run.
    """

    if tail:
        in_progress(msg="Tailing logs...")
        fetched_logs = local_app.run_logs_with_polling(
            run_id=run_id,
            polling_options=polling_options,
            verbose=True,
            rich_print=True,
        )
        if logs is None:
            return

        log_content = "\n".join(log_entry for log_entry in fetched_logs)
    elif logs is not None and logs != "" and file_output:
        in_progress(msg="Getting run logs...")
        local_app.run_result_with_polling(run_id=run_id, polling_options=polling_options)
        run_logs = local_app.run_logs(run_id=run_id)
        log_content = run_logs
    elif not file_output:
        in_progress(msg="Getting run logs...")
        run_logs = local_app.run_logs(run_id=run_id)
        rich.print(run_logs, file=sys.stderr)
        return
    else:
        return

    Path(logs).write_text(log_content)
    success(f"Run logs written to [magenta]{logs}[/magenta].")
