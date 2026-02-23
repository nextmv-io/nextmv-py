"""
This module defines the cloud sso delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_sso_config
from nextmv.cli.message import confirmation, info, success
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

    You must have the [magenta]administrator[/magenta] role on the organization
    in order to delete it. Use the --yes flag to skip the confirmation prompt.
    You can create a new SSO configuration again with [code]nextmv cloud sso create[/code].

    [bold][underline]Examples[/underline][/bold]

    - Delete the SSO configuration.
        $ [dim]nextmv cloud sso delete[/dim]

    - Delete the SSO configuration without confirmation prompt.
        $ [dim]nextmv cloud sso delete --yes[/dim]
    """

    if not yes:
        confirm = confirmation(
            "Are you sure you want to delete the sso configuration? "
            "You can create it again with [code]nextmv cloud sso create[/code].",
        )

        if not confirm:
            info("SSO configuration will not be deleted.")
            return

    sso_config = build_sso_config(profile)
    sso_config.delete()
    success("SSO configuration has been deleted. You can create it again with [code]nextmv cloud sso create[/code].")
