"""
This module defines the cloud sso delete command for the Nextmv CLI.
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
def delete(
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Agree to deletion confirmation prompt. Useful for non-interactive sessions.",
        ),
    ] = False,
    profile: ProfileOption = None,
) -> None:
    """
    Deletes the SSO configuration.

    You must have the [magenta]administrator[/magenta] role on the organization in order to delete it.

    This action is permanent and cannot be undone. Use the --yes
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the SSO configuration.
        $ [dim]nextmv cloud sso delete[/dim]

    - Delete the SSO configuration without confirmation prompt.
        $ [dim]nextmv cloud sso delete --yes[/dim]
    """

    if not yes:
        confirm = get_confirmation(
            "Are you sure you want to delete the sso configuration? This action cannot be undone.",
        )

        if not confirm:
            info("SSO configuration will not be deleted.")
            return

    sso_config = build_sso_config(profile)
    sso_config.delete()
    success("SSO configuration has been deleted.")
