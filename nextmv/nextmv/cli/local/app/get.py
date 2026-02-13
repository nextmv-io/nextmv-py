"""
This module defines the cloud app get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_local_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import LocalAppIDOption, LocalAppSrcOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    app_id: LocalAppIDOption = None,
    app_src: LocalAppSrcOption = ".",
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the app information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """
    Get a registered local Nextmv application.

    You may identify the app by using --app-src, or --app-id if it has been
    registered.

    [bold][underline]Examples[/underline][/bold]

    - Get the application with the ID [magenta]hare-app[/magenta].
        $ [dim]nextmv local app get --app-id hare-app[/dim]

    - Get the application with the ID [magenta]hare-app[/magenta] and save the information to an
      [magenta]app.json[/magenta] file.
        $ [dim]nextmv local app get --app-id hare-app --output app.json[/dim]
    """

    in_progress(msg="Getting application...")
    local_app = build_local_app(app_src, app_id)
    app_dict = local_app.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(app_dict, f, indent=2)

        success(msg=f"Application information saved to [magenta]{output}[/magenta].")

        return

    print_json(app_dict)
