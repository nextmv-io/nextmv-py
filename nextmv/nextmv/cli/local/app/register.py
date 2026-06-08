"""
This module defines the local app register command for the Nextmv CLI.
"""

import json
import os
from typing import Annotated

import typer

from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import DebugOption, LocalAppIDOption, LocalAppSrcOption
from nextmv.local.registry import Registry

# Set up subcommand application.
app = typer.Typer()


@app.command()
def register(
    app_id: LocalAppIDOption = None,
    app_src: LocalAppSrcOption = None,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="An optional description for the application.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the app information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    _: DebugOption = False,
) -> None:
    """
    Register a local Nextmv application.

    After an application is registered, you may use the resulting app ID to
    interact with the application from different locations on your machine
    without needing to specify the source path. You may also use the app ID to
    refer to the application in other Nextmv CLI commands. If an app ID is not
    provided, the CLI will generate one for you. The source path must be a
    local path on your machine that contains a Nextmv application manifest
    file ([magenta]app.yaml[/magenta]).

    [bold][underline]Examples[/underline][/bold]

    - Register a local application with the source path [magenta]./my-app[/magenta].
        $ [dim]nextmv local app register --app-src ./my-app[/dim]

    - Register a local application with the source path [magenta]./my-app[/magenta] and save the
      information to an [magenta]app.json[/magenta] file.
        $ [dim]nextmv local app register --app-src ./my-app --output app.json[/dim]
    """

    if (app_id is None or app_id == "") and (app_src is None or app_src == ""):
        app_src = "."

    if app_src is not None and app_src != "":
        app_src = os.path.abspath(app_src)

    registry = Registry.from_yaml()
    in_progress(msg="Registering application...")
    entry = registry.register(src=app_src, app_id=app_id, description=description)
    success(f"Successfully registered application with source [magenta]{entry.src}[/magenta].")
    entry_dict = entry.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(entry_dict, f, indent=2)

        success(msg=f"Registry information saved to [magenta]{output}[/magenta].")

        return

    print_json(entry_dict)
