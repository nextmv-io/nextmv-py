"""
This module defines the cloud app get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.message import error, in_progress, print_json, success
from nextmv.cli.options import LocalAppIDOption, LocalAppSrcOption
from nextmv.local.application import Application

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    app_id: LocalAppIDOption = None,
    app_src: LocalAppSrcOption = None,
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

    if (app_id is None or app_id == "") and (app_src is None or app_src == ""):
        error("Either --app-id or --app-src must be provided to identify the application.")

    in_progress(msg="Getting application...")
    app = Application.from_registry(src=app_src, app_id=app_id)
    app_dict = app.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(app_dict, f, indent=2)

        success(msg=f"Application information saved to [magenta]{output}[/magenta].")

        return

    print_json(app_dict)
