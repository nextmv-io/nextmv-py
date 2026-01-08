"""
This module defines the community clone command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.cloud.run.create import handle_logging, handle_results
from nextmv.cli.configuration.config import build_app
from nextmv.cli.options import AppIDOption, ProfileOption, RunIDOption
from nextmv.polling import DEFAULT_POLLING_OPTIONS

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    app_id: AppIDOption,
    run_id: RunIDOption,
    logs: Annotated[
        str | None,
        typer.Option(
            "--logs",
            "-l",
            help="The location to stream the logs to. They will also be streamed to [magenta]stdout[/magenta]. "
            "Activates [code]--tail[/code] if not set.",
            metavar="LOGS_OUTPUT",
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
    tail: Annotated[
        bool,
        typer.Option(
            "--tail",
            "-t",
            help="Tail the logs until the run completes. Logs are streamed to [magenta]stdout[/magenta]. "
            "Activates [code]--wait[/code] if not set.",
        ),
    ] = False,
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
            help="Wait for the run to complete. Activates polling for the result. "
            "Run result is printed to [magenta]stdout[/magenta] for [magenta]json[/magenta], "
            "to a directory for [magenta]multi-file[/magenta].",
        ),
    ] = False,
    profile: ProfileOption = None,
) -> None:
    """
    Get the result of a Nextmv Cloud application run.

    Use the [code]--wait[/code] flag to wait for the run to complete, polling
    for results. Using the [code]--output[/code] flag will also activate
    waiting, and allows you to specify a destination (file or dir) for the
    output, depending on the content type.

    Use the [code]--tail[/code] flag to stream logs to
    [magenta]stdout[/magenta] until the run completes, polling for results.
    Using the [code]--logs[/code] flag will also activate tailing, and allows
    you to specify a file to write the logs to.
    """

    cloud_app = build_app(app_id, profile)

    # Build the polling options.
    polling_options = DEFAULT_POLLING_OPTIONS
    polling_options.max_duration = timeout

    handle_logging(
        tail=tail,
        logs=logs,
        cloud_app=cloud_app,
        run_id=run_id,
        polling_options=polling_options,
    )
    handle_results(
        output=output,
        cloud_app=cloud_app,
        run_id=run_id,
        polling_options=polling_options,
    )
