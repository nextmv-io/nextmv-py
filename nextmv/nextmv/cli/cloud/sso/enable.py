"""
This module defines the cloud sso enable command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_sso_config
from nextmv.cli.message import confirmation, info, success
from nextmv.cli.options import DebugOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def enable(
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Agree to enable confirmation prompt. Useful for non-interactive sessions.",
        ),
    ] = False,
    _: DebugOption = False,
    profile: ProfileOption = None,
) -> None:
    """
    Enables the SSO configuration.

    Use the --yes flag to skip the confirmation prompt. Use the [code]nextmv
    cloud sso disable[/code] command to disable SSO.

    [bold][underline]Examples[/underline][/bold]

    - Enable the SSO configuration.
        $ [dim]nextmv cloud sso enable[/dim]

    - Enable the SSO configuration without confirmation prompt.
        $ [dim]nextmv cloud sso enable --yes[/dim]
    """

    if not yes:
        confirm = confirmation(
            "Are you sure you want to enable the sso configuration?.",
        )

        if not confirm:
            info("SSO configuration will not be enabled.")
            return

    sso_config = build_sso_config(profile)
    sso_config.enable()
    success("SSO configuration has been enabled.")
