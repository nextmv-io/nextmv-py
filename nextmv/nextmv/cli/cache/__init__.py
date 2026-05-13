"""
This module defines the cache command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cache.delete import app as delete_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(delete_app)


@app.callback()
def callback() -> None:
    """
    Manage the cache used for Nextmv operations.
    """
    pass
