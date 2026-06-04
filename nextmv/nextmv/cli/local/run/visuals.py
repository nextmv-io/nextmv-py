"""
This module defines the local run metadata command for the Nextmv CLI.
"""

import typer

from nextmv.cli.configuration.config import build_local_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import DebugOption, LocalAppIDOption, LocalAppSrcOption, RunIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def visuals(
    run_id: RunIDOption,
    app_id: LocalAppIDOption = None,
    app_src: LocalAppSrcOption = ".",
    _: DebugOption = False,
) -> None:
    """
    Get the visuals of a Nextmv local application run.

    You may identify the app by using --app-src, or --app-id if it has been
    registered. If the app is not already registered, this command will
    register it.

    [bold][underline]Examples[/underline][/bold]

    - Get the visuals of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Visuals are opened in a web browser.
        $ [dim]nextmv local run visuals --app-id hare-app --run-id burrow-123[/dim]

    - Get the visuals of a run with ID [magenta]burrow-123[/magenta], belonging to an app with source path
      [magenta]./my-app[/magenta].
        $ [dim]nextmv local run visuals --app-src ./my-app --run-id burrow-123[/dim]
    """

    local_app = build_local_app(app_src, app_id)
    in_progress(msg="Getting run visuals...")
    run_visuals = local_app.run_visuals(run_id)
    success(msg="Run visuals opened in web browser, here are the local URLs of the visual files:")
    print_json(run_visuals)
