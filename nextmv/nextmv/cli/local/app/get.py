"""
This module defines the cloud app get command for the Nextmv CLI.
"""

import json
import os
from typing import Annotated

import typer

from nextmv.cli.message import in_progress, print_json, success, warning
from nextmv.cli.options import AppIDOption
from nextmv.local.registry import Registry

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    app_id: AppIDOption,
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
    Get a local Nextmv application.

    This command is useful to get the attributes of an existing local Nextmv
    application by its ID.

    [bold][underline]Examples[/underline][/bold]

    - Get the application with the ID [magenta]hare-app[/magenta].
        $ [dim]nextmv local app get --app-id hare-app[/dim]

    - Get the application with the ID [magenta]hare-app[/magenta] and save the information to an
      [magenta]app.json[/magenta] file.
        $ [dim]nextmv local app get --app-id hare-app --output app.json[/dim]
    """

    registry = Registry.from_yaml()
    in_progress(msg="Getting application...")

    app_entry = next((app for app in registry.apps if app.app_id == app_id), None)

    if app_entry is None:
        typer.echo(f"Application with ID '{app_id}' not found.")
        raise typer.Exit(code=1)
    elif not os.path.exists(app_entry.src):
        warning(f"Application with ID '{app_id}' found in registry but path does not exist.")

    app_dict = app_entry.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(app_dict, f, indent=2)
        success(msg=f"Application information saved to [magenta]{output}[/magenta].")

        return

    print_json(app_dict)
