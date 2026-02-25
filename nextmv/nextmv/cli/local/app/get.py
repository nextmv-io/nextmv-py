"""
This module defines the local app get command for the Nextmv CLI.
"""

import json
import os
from typing import Annotated

import typer

from nextmv.cli.message import in_progress, print_json, success, warning
from nextmv.cli.options import LocalAppIDOption, LocalAppSrcOption
from nextmv.local.application import Application
from nextmv.local.registry import Registry

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

    You may identify the app by using --app-src or --app-id.

    [bold][underline]Examples[/underline][/bold]

    - Get the application with the ID [magenta]hare-app[/magenta].
        $ [dim]nextmv local app get --app-id hare-app[/dim]

    - Get the application with the ID [magenta]hare-app[/magenta] and save the information to an
      [magenta]app.json[/magenta] file.
        $ [dim]nextmv local app get --app-id hare-app --output app.json[/dim]
    """

    if (app_id is None or app_id == "") and (app_src is None or app_src == ""):
        app_src = "."

    if app_src is not None and app_src != "":
        app_src = os.path.abspath(app_src)

    in_progress(msg="Getting registered application...")

    reg = Registry.from_yaml()
    entry = reg.entry(app_id=app_id, src=app_src)
    if entry is None:
        warning(
            f"Could not find a local registry entry for app ID [magenta]{app_id}[/magenta] and "
            f"source [magenta]{app_src}[/magenta]. Register with [code]nextmv local app register[/code]."
        )
        return

    local_app = Application.from_registry(src=app_src, app_id=app_id)
    app_dict = local_app.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(app_dict, f, indent=2)

        success(msg=f"Registered application information saved to [magenta]{output}[/magenta].")

        return

    print_json(app_dict)
