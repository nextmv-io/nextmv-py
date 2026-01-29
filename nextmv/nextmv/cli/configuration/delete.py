"""
This module defines the configuration delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import load_config, save_config
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import error, info, success

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    profile: Annotated[  # Similar to nextmv.cli.options.ProfileOption but with different help text.
        str,
        typer.Option(
            "--profile",
            "-p",
            help="Profile name to delete.",
            envvar="NEXTMV_PROFILE",
            metavar="PROFILE_NAME",
        ),
    ],
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Agree to deletion confirmation prompt. Useful for non-interactive sessions.",
        ),
    ] = False,
) -> None:
    """
    Delete a profile from the configuration.

    Use the --yes flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete a profile named [magenta]hare[/magenta].
        $ [dim]nextmv configuration delete --profile hare[/dim]

    - Delete a profile named [magenta]hare[/magenta] without confirmation prompt.
        $ [dim]nextmv configuration delete --profile hare --yes[/dim]
    """
    config = load_config()
    if profile not in config:
        error(f"Profile [magenta]{profile}[/magenta] does not exist.")

    if not yes:
        confirm = get_confirmation(
            f"Are you sure you want to delete profile [magenta]{profile}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(f"Profile [magenta]{profile}[/magenta] will not be deleted.")
            return

    del config[profile]
    save_config(config)

    success(f"Profile [magenta]{profile}[/magenta] deleted successfully.")
