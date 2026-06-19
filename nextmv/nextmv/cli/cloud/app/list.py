"""
This module defines the cloud app list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import DebugOption, NoPaginationOption, ProfileOption
from nextmv.cloud.application import list_applications
from nextmv.cloud.client import Client

# Set up subcommand application.
app = typer.Typer()


@app.command()
def list(
    no_pagination: NoPaginationOption = False,
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
    profile: ProfileOption = None,
) -> None:
    """
    List all Nextmv Cloud applications.

    By default this command paginates the list of applications, which means
    multiple API calls may be made to retrieve all applications. You may use the
    --no-pagination option to disable pagination.

    [bold][underline]Examples[/underline][/bold]

    - List all applications.

        $ [dim]nextmv cloud app list[/dim]

    - List all applications using the profile named [magenta]hare[/magenta].

        $ [dim]nextmv cloud app list --profile hare[/dim]

    - List all applications and save the information to an [magenta]apps.json[/magenta] file.

        $ [dim]nextmv cloud app list --output apps.json[/dim]

    - List all applications without pagination.

        $ [dim]nextmv cloud app list --no-pagination[/dim]
    """

    client = Client(profile=profile)
    in_progress(msg="Listing applications...")

    cloud_apps = list_applications(client, no_pagination)
    cloud_apps_dicts = [cloud_app.to_dict() for cloud_app in cloud_apps]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(cloud_apps_dicts, f, indent=2)

        success(msg=f"Application list information saved to [magenta]{output}[/magenta].")

        return

    print_json(cloud_apps_dicts)
