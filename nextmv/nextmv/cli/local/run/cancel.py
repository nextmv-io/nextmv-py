"""
This module defines the local run cancel command for the Nextmv CLI.
"""

import typer

from nextmv.cli.options import AppIDOption, RunIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def cancel(
    app_id: AppIDOption,
    run_id: RunIDOption,
) -> None:
    """
    Cancel a queued/running Nextmv Local application run.

    [bold][underline]Examples[/underline][/bold]

    - Cancel the run with ID [magenta]burrow-123[/magenta] belonging to an app with ID [magenta]hare-app[/magenta].
        $ [dim]nextmv local run cancel --app-id hare-app --run-id burrow-123[/dim]

    - Cancel the run with ID [magenta]burrow-123[/magenta] belonging to an app with ID [magenta]hare-app[/magenta].
      Use the profile named [magenta]hare[/magenta].
        $ [dim]nextmv local run cancel --app-id hare-app --run-id burrow-123 --profile hare[/dim]
    """

    # TODO: replace copied code with actual logic / connect to actual logic
