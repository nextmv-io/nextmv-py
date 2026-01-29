"""
This module defines the cloud run logs command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.options import AppIDOption, RunIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def logs(
    app_id: AppIDOption,
    run_id: RunIDOption,
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
) -> None:
    """
    Get the logs of a Nextmv Cloud application run.

    By default, the logs are fetched and printed to [magenta]stderr[/magenta].
    Use the --tail flag to stream logs to [magenta]stderr[/magenta] until the
    run completes. Using the --output flag will also activate waiting, and
    allows you to specify a file to write the logs to.

    [bold][underline]Examples[/underline][/bold]

    - Get the logs of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Logs are printed to [magenta]stderr[/magenta].
        $ [dim]nextmv cloud run logs --app-id hare-app --run-id burrow-123[/dim]

    - Get the logs of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Tail the logs until the run completes.
        $ [dim]nextmv cloud run logs --app-id hare-app --run-id burrow-123 --tail[/dim]

    - Get the logs of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Save the logs to a [magenta]logs.log[/magenta] file.
        $ [dim]nextmv cloud run logs --app-id hare-app --run-id burrow-123 --output logs.log[/dim]

    - Get the logs of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Tail the logs and save them to a [magenta]logs.log[/magenta] file.
        $ [dim]nextmv cloud run logs --app-id hare-app --run-id burrow-123 --tail --output logs.log[/dim]

    - Get the logs of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Use the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud run logs --app-id hare-app --run-id burrow-123 --profile hare[/dim]
    """

    # TODO: replace copied code with actual logic / connect to actual logic
