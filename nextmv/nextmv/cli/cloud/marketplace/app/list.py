"""
This module defines the cloud marketplace app list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import DebugOption, ProfileOption
from nextmv.cloud.client import Client
from nextmv.cloud.marketplace import list_marketplace_applications

# Set up subcommand application.
app = typer.Typer()


@app.command()
def list(
    partner_id: Annotated[
        str | None,
        typer.Option(
            "--partner-id",
            "-n",
            help="Only the apps belonging to this partner will be listed. If not provided, all apps are listed.",
            envvar="NEXTMV_MARKETPLACE_PARTNER_ID",
            metavar="PARTNER_ID",
        ),
    ] = None,
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
    List all Nextmv Marketplace applications.

    By default, this command lists all marketplace applications. Use the
    --partner-id flag to filter applications belonging to a specific partner.

    [bold][underline]Examples[/underline][/bold]

    - List all marketplace applications.
        $ [dim]nextmv cloud marketplace app list[/dim]

    - List all applications for a specific partner.
        $ [dim]nextmv cloud marketplace app list --partner-id my-partner[/dim]

    - List all applications using the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud marketplace app list --profile hare[/dim]

    - List all applications and save the information to an [magenta]apps.json[/magenta] file.
        $ [dim]nextmv cloud marketplace app list --output apps.json[/dim]
    """

    client = Client(profile=profile)
    in_progress(msg="Listing applications...")

    mkt_apps = list_marketplace_applications(client, partner_id)
    mkt_apps_dicts = [mkt_app.to_dict() for mkt_app in mkt_apps]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(mkt_apps_dicts, f, indent=2)

        success(msg=f"Application list information saved to [magenta]{output}[/magenta].")

        return

    print_json(mkt_apps_dicts)
