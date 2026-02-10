"""
This module defines the cloud app list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.message import print_json, success
from nextmv.local.registry import Registry

# Set up subcommand application.
app = typer.Typer()


@app.command()
def list(
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the app list information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """
    List all local Nextmv applications.

    [bold][underline]Examples[/underline][/bold]

    - List all applications.
        $ [dim]nextmv local app list[/dim]

    - List all applications and save the information to an [magenta]apps.json[/magenta] file.
        $ [dim]nextmv local app list --output apps.json[/dim]
    """

    registry = Registry.from_yaml()
    apps_dicts = [app.to_dict() for app in registry.apps]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(apps_dicts, f, indent=2)

        success(msg=f"Application list information saved to [magenta]{output}[/magenta].")

        return

    print_json(apps_dicts)
