"""
This module defines the local app registered command for the Nextmv CLI.
"""

import typer

from nextmv.cli.message import in_progress, print_json
from nextmv.cli.options import LocalAppIDOption, LocalAppSrcOption
from nextmv.local.registry import Registry

# Set up subcommand application.
app = typer.Typer()


@app.command()
def registered(
    app_id: LocalAppIDOption = None,
    app_src: LocalAppSrcOption = ".",
) -> None:
    """
    Check if a Nextmv application is registered locally.

    You may identify the app by using --app-src or --app-id. This command is
    useful in scripting applications to verify the existence of a local
    application.

    [bold][underline]Examples[/underline][/bold]

    - Check if the application with the ID [magenta]hare-app[/magenta] is registered.
        $ [dim]nextmv local app registered --app-id hare-app[/dim]

    - Check if the application with source path [magenta]./hare-app/[/magenta] is registered.
        $ [dim]nextmv local app registered --app-src ./hare-app/[/dim]
    """

    in_progress(msg="Checking if application is registered...")
    reg = Registry.from_yaml()
    entry = reg.entry(app_id=app_id, src=app_src)
    ok = entry is not None
    print_json({"registered": ok})
