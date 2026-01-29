"""
This module defines the cloud app push command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.options import ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def sync(
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
    Sync local Nextmv applications to the Nextmv Cloud.

    [bold][underline]Examples[/underline][/bold]

    - Sync local applications to the Nextmv Cloud.
        $ [dim]nextmv local app sync[/dim]

    - Sync local applications using the profile named [magenta]hare[/magenta].
        $ [dim]nextmv local app sync --profile hare[/dim]
    """

    # TODO: replace copied code with actual logic / connect to actual logic
