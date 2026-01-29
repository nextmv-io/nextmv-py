"""
This module defines the local app delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import info, success
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.local.application import Application
from nextmv.local.registry import delete_registry_entry, read_local_registry

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Agree to deletion confirmation prompt. Useful for non-interactive sessions.",
        ),
    ] = False,
    profile: ProfileOption = None,
) -> None:
    """
    Deletes a local Nextmv application.

    This action is permanent and cannot be undone. Use the --yes
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the application with the ID [magenta]hare-app[/magenta].
        $ [dim]nextmv local app delete --app-id hare-app[/dim]

    - Delete the application with the ID [magenta]hare-app[/magenta] without confirmation prompt.
        $ [dim]nextmv local app delete --app-id hare-app --yes[/dim]
    """

    if not yes:
        confirm = get_confirmation(
            f"Are you sure you want to delete application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(msg=f"Application [magenta]{app_id}[/magenta] will not be deleted.", emoji=":bulb:")
            return

    # Find app in registry.
    registry = read_local_registry()
    app_entry = next((app for app in registry.apps if app.app_id == app_id), None)
    if app_entry is None:
        typer.echo(f"Application with ID '{app_id}' not found.")
        raise typer.Exit(code=1)
    app = Application(src=app_entry.path)

    # Make sure the app exists before attempting to delete.
    if not app.exists():
        typer.echo(f"Application with ID '{app_id}' not found at path '{app_entry.path}'.")
        raise typer.Exit(code=1)

    # Delete the app.
    app.delete()
    delete_registry_entry(app_id)
    success(f"Application [magenta]{app_id}[/magenta] deleted successfully.")
