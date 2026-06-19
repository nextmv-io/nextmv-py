"""
This module defines the local app list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import DebugOption
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
    _: DebugOption = False,
) -> None:
    """
    List all local registered Nextmv applications.

    [bold][underline]Examples[/underline][/bold]

    - List all registered applications.

        $ [dim]nextmv local app list[/dim]

    - List all registered applications and save the information to an [magenta]apps.json[/magenta] file.

        $ [dim]nextmv local app list --output apps.json[/dim]
    """

    in_progress(msg="Listing registered applications...")
    registry = Registry.from_yaml()
    entries_dicts = [entry.to_dict() for entry in registry.list_entries()]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(entries_dicts, f, indent=2)

        success(msg=f"Registered application list information saved to [magenta]{output}[/magenta].")

        return

    print_json(entries_dicts)
