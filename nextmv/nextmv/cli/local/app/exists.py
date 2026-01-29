"""
This module defines the cloud app exists command for the Nextmv CLI.
"""

import typer

from nextmv.cli.message import in_progress, print_json
from nextmv.cli.options import AppIDOption
from nextmv.local.registry import read_local_registry

# Set up subcommand application.
app = typer.Typer()


@app.command()
def exists(
    app_id: AppIDOption,
) -> None:
    """
    Check if a local Nextmv application exists.

    This command is useful in scripting applications to verify the existence of
    a local application by its ID.

    [bold][underline]Examples[/underline][/bold]

    - Check if the application with the ID [magenta]hare-app[/magenta] exists.
        $ [dim]nextmv local app exists --app-id hare-app[/dim]
    """

    registry = read_local_registry()
    in_progress(msg="Checking if application exists...")

    ok = any(app.app_id == app_id for app in registry.apps)
    print_json({"exists": ok})
