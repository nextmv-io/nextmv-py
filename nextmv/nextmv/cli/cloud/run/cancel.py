"""
This module defines the cloud run cancel command for the Nextmv CLI.
"""

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import success
from nextmv.cli.options import AppIDOption, ProfileOption, RunIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def cancel(
    app_id: AppIDOption,
    run_id: RunIDOption,
    profile: ProfileOption = None,
) -> None:
    """
    Cancel a queued/running Nextmv Cloud application run.

    [bold][underline]Examples[/underline][/bold]

    - Cancel the run with ID [magenta]burrow-123[/magenta] belonging to an app with ID [magenta]hare-app[/magenta].
        $ [green]nextmv cloud run cancel --app-id hare-app --run-id burrow-123[/green]

    - Cancel the run with ID [magenta]burrow-123[/magenta] belonging to an app with ID [magenta]hare-app[/magenta].
      Use the profile named [magenta]hare[/magenta].
        $ [green]nextmv cloud run cancel --app-id hare-app --run-id burrow-123 --profile hare[/green]
    """

    cloud_app = build_app(app_id, profile)
    cloud_app.cancel_run(run_id)
    success(f"Run [magenta]{run_id}[/magenta] canceled.")
