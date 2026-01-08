"""
This module defines the version command for the Nextmv CLI.
"""

import typer

from nextmv.__about__ import __version__

# Set up subcommand application.
app = typer.Typer()


@app.command()
def version() -> None:
    """
    Show the current version of the Nextmv CLI.
    """

    version_callback(True)


def version_callback(value: bool):
    """
    Callback function to display the version.

    Parameters
    ----------
    value : bool
        If True, print the version and exit.
    """
    if value:
        print(__version__)
        raise typer.Exit()
