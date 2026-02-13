"""
This module defines the local app delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_local_app
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import info, success
from nextmv.cli.options import LocalAppIDOption, LocalAppSrcOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: LocalAppIDOption = None,
    app_src: LocalAppSrcOption = ".",
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Agree to deletion confirmation prompt. Useful for non-interactive sessions.",
        ),
    ] = False,
) -> None:
    """
    Deletes a local Nextmv application.

    You may identify the app by using --app-src, or --app-id if it has been
    registered. This action is permanent and cannot be undone. Use the --yes
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the application with the ID [magenta]hare-app[/magenta].
        $ [dim]nextmv local app delete --app-id hare-app[/dim]

    - Delete the application with the ID [magenta]hare-app[/magenta] without confirmation prompt.
        $ [dim]nextmv local app delete --app-id hare-app --yes[/dim]
    """

    if not yes:
        if app_id is not None and app_id != "":
            msg = f"Are you sure you want to delete application [magenta]{app_id}[/magenta]?"
        elif app_src is not None and app_src != "":
            msg = f"Are you sure you want to delete application with source [magenta]{app_src}[/magenta]?"

        confirm = get_confirmation(f"{msg} This action cannot be undone.")

        if not confirm:
            if app_id is not None and app_id != "":
                info(f"Application [magenta]{app_id}[/magenta] will not be deleted.")
            elif app_src is not None and app_src != "":
                info(f"Application with source [magenta]{app_src}[/magenta] will not be deleted.")

            return

    local_app = build_local_app(app_src, app_id)
    local_app.delete()

    success(f"Application with source [magenta]{local_app.src}[/magenta] deleted successfully.")
