"""
This module defines the cloud sso disable command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_sso_config
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import info, success
from nextmv.cli.options import ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def disable(
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Agree to disable confirmation prompt. Useful for non-interactive sessions.",
        ),
    ] = False,
    profile: ProfileOption = None,
) -> None:
    """
    Disables the SSO configuration.

    Use the --yes flag to skip the confirmation prompt. Use the [code]nextmv
    cloud sso enable[/code] command to re-enable SSO.

    [bold][underline]Examples[/underline][/bold]

    - Disable the SSO configuration.
        $ [dim]nextmv cloud sso disable[/dim]

    - Disable the SSO configuration without confirmation prompt.
        $ [dim]nextmv cloud sso disable --yes[/dim]
    """

    if not yes:
        confirm = get_confirmation(
            "Are you sure you want to disable the sso configuration?.",
        )

        if not confirm:
            info("SSO configuration will not be disabled.")
            return

    sso_config = build_sso_config(profile)
    sso_config.disable()
    success("SSO configuration has been disabled.")
