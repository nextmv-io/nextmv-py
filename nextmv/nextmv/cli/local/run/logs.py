"""
This module defines the local run logs command for the Nextmv CLI.
"""

import sys
from pathlib import Path
from typing import Annotated

import rich
import typer

from nextmv import local
from nextmv.cli.message import in_progress, success
from nextmv.cli.options import LocalAppIDOption, LocalAppSrcOption, RunIDOption

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
) -> None:
    """
    Get the logs of a local application run.

    You may identify the app by using --app-src, or --app-id if it has been
    registered. By default, the logs are fetched and printed to
    [magenta]stderr[/magenta]. Use the --output flag to save the logs to a
    file.

    [bold][underline]Examples[/underline][/bold]

    - Get the logs of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Logs are printed to [magenta]stderr[/magenta].
        $ [dim]nextmv local run logs --app-id hare-app --run-id burrow-123[/dim]

    - Get the logs of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Save the logs to a [magenta]logs.log[/magenta] file.
        $ [dim]nextmv local run logs --app-id hare-app --run-id burrow-123 --output logs.log[/dim]

    - Get the logs of a run with ID [magenta]burrow-123[/magenta], belonging to an app with source path
      [magenta]./my-app[/magenta].
        $ [dim]nextmv local run logs --app-src ./my-app --run-id burrow-123[/dim]
    """

    local_app = local.Application.from_registry(src=app_src, app_id=app_id)
    in_progress(msg="Getting run logs...")
    run_logs = local_app.run_logs(run_id=run_id)

    if output is not None and output != "":
        Path(output).write_text(run_logs)
        success(f"Run logs written to [magenta]{output}[/magenta].")

        return

    rich.print(run_logs, file=sys.stderr)
