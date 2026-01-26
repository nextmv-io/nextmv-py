"""
This module defines the cloud app list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_client
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import ProfileOption
from nextmv.cloud.application import list_applications

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
    profile: ProfileOption = None,
) -> None:
    """
    List all Nextmv Cloud applications.

    [bold][underline]Examples[/underline][/bold]

    - List all applications.
        $ [dim]nextmv cloud app list[/dim]

    - List all applications using the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud app list --profile hare[/dim]

    - List all applications and save the information to an [magenta]apps.json[/magenta] file.
        $ [dim]nextmv cloud app list --output apps.json[/dim]
    """

    client = build_client(profile)
    in_progress(msg="Listing applications...")

    cloud_apps = list_applications(client)
    cloud_apps_dicts = [app.to_dict() for app in cloud_apps]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(cloud_apps_dicts, f, indent=2)

        success(msg=f"Application list information saved to [magenta]{output}[/magenta].")

        return

    print_json(cloud_apps_dicts)
