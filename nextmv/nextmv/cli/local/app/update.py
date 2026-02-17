"""
This module defines the local app update command for the Nextmv CLI.
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
def update(
    description: Annotated[
        str,
        typer.Option(
            "--description",
            "-d",
            help="A new description for the application.",
            metavar="DESCRIPTION",
        ),
    ],
    app_id: LocalAppIDOption = None,
    app_src: LocalAppSrcOption = ".",
    new_app_id: Annotated[
        str | None,
        typer.Option(
            "--new-app-id",
            "-n",
            help="A new ID for the local Nextmv application.",
            metavar="NEW_APP_ID",
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
) -> None:
    """
    Update a registered local Nextmv application.

    You may identify the app by using --app-src, or --app-id if it has been
    registered. If the app is not already registered, this command will
    register it. You can update the app's ID through the --new-app-id option.

    [bold][underline]Examples[/underline][/bold]

    - Update the application with the ID [magenta]hare-app[/magenta].
        $ [dim]nextmv local app update --app-id hare-app --description "New description"[/dim]

    - Update the application with the ID [magenta]hare-app[/magenta] and save the information to an
      [magenta]app.json[/magenta] file.
        $ [dim]nextmv local app update --app-id hare-app --description "New description" --output app.json[/dim]

    - Update the ID of the application located at [magenta]./my-app[/magenta] to [magenta]hare-app[/magenta].
        $ [dim]nextmv local app update --app-src ./my-app --new-app-id hare-app --description "New description"[/dim]
    """

    in_progress(msg="Updating application...")
    local_app = build_local_app(app_src, app_id)
    local_app.update(app_id=new_app_id, description=description)
    app_dict = local_app.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(app_dict, f, indent=2)

        success(msg=f"Application information saved to [magenta]{output}[/magenta].")

        return

    print_json(app_dict)
