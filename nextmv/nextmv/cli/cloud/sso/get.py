"""
This module defines the cloud sso get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import ProfileOption
from nextmv.cloud.client import Client
from nextmv.cloud.sso import SSOConfiguration

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the SSO configuration information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get the information of a Nextmv Cloud SSO configuration.

    This command is useful to get the attributes of an existing Nextmv Cloud
    SSO configuration.

    [bold][underline]Examples[/underline][/bold]

    - Get the SSO configuration.
        $ [dim]nextmv cloud sso get[/dim]

    - Get the SSO configuration and save the information to an [magenta]sso_config.json[/magenta] file.
        $ [dim]nextmv cloud sso get --output sso_config.json[/dim]
    """

    client = Client(profile=profile)
    in_progress(msg="Getting SSO configuration...")

    sso_config = SSOConfiguration.get(client)
    sso_config_dict = sso_config.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(sso_config_dict, f, indent=2)

        success(msg=f"SSO configuration information saved to [magenta]{output}[/magenta].")

        return

    print_json(sso_config_dict)
