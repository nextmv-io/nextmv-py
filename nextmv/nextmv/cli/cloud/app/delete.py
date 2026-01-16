"""
This module defines the cloud app delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer
from rich.prompt import Confirm

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import info, success
from nextmv.cli.options import AppIDOption, ProfileOption

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
    Deletes a Nextmv Cloud application.

    This action is permanent and cannot be undone. Use the [code]--yes[/code]
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the application with the ID [magenta]hare-app[/magenta].
        $ [green]nextmv cloud app delete --app-id hare-app[/green]

    - Delete the application with the ID [magenta]hare-app[/magenta] without confirmation prompt.
        $ [green]nextmv cloud app delete --app-id hare-app --yes[/green]
    """

    if not yes:
        confirm = Confirm.ask(
            f"Are you sure you want to delete application [magenta]{app_id}[/magenta]? This action cannot be undone.",
            default=False,
        )

        if not confirm:
            info(msg=f"Application [magenta]{app_id}[/magenta] will not be deleted.", emoji=":bulb:")
            return

    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.delete()
    success(f"Application [magenta]{app_id}[/magenta] deleted successfully.")
