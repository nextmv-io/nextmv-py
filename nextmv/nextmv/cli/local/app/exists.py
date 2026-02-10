"""
This module defines the cloud app exists command for the Nextmv CLI.
"""

import typer

from nextmv.cli.message import in_progress, print_json
from nextmv.cli.options import LocalAppIDOption, LocalAppSrcOption
from nextmv.local.application import Application

# Set up subcommand application.
app = typer.Typer()


@app.command()
def exists(
    app_id: LocalAppIDOption = None,
    app_src: LocalAppSrcOption = None,
) -> None:
    """
    Check if a local Nextmv application exists.

    You may identify the app by using either --app-id or --app-src. This
    command is useful in scripting applications to verify the existence of a
    local application.

    [bold][underline]Examples[/underline][/bold]

    - Check if the application with the ID [magenta]hare-app[/magenta] exists.
        $ [dim]nextmv local app exists --app-id hare-app[/dim]

    - Check if the application with source path [magenta]./hare-app/[/magenta] exists.
        $ [dim]nextmv local app exists --app-src ./hare-app/[/dim
    """

    in_progress(msg="Checking if application exists...")
    app = Application(src=app_src, app_id=app_id)
    ok = app.exists()
    print_json({"exists": ok})
