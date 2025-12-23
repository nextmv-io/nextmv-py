"""
This module defines the configuration command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.configuration.create import app as create_app
from nextmv.cli.configuration.delete import app as delete_app
from nextmv.cli.configuration.list import app as list_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(create_app)
app.add_typer(delete_app)
app.add_typer(list_app)


@app.callback()
def callback() -> None:
    """
    Configure the CLI and manage profiles.
    """
    pass
