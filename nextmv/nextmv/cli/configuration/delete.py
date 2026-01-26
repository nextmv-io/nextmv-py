"""
This module defines the configuration delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer
from rich.prompt import Confirm

from nextmv.cli.configuration.config import load_config, save_config
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
    Delete a profile from the configuration. Use the --yes
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete a profile named [magenta]hare[/magenta].
        $ [green]nextmv configuration delete --profile hare[/green]

    - Delete a profile named [magenta]hare[/magenta] without confirmation prompt.
        $ [green]nextmv configuration delete --profile hare --yes[/green]
    """
    config = load_config()
    if profile not in config:
        error(f"Profile [magenta]{profile}[/magenta] does not exist.")

    if not yes:
        confirm = Confirm.ask(
            f"Are you sure you want to delete profile [magenta]{profile}[/magenta]? This action cannot be undone.",
            default=False,
        )

        if not confirm:
            info(msg=f"Profile [magenta]{profile}[/magenta] will not be deleted.", emoji=":bulb:")
            return

    del config[profile]
    save_config(config)

    success(f"Profile [magenta]{profile}[/magenta] deleted successfully.")
