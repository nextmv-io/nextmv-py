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

    print(__version__)
