"""
This module defines the manifest command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.manifest.init import app as init_app
from nextmv.cli.manifest.validate import app as validate_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(init_app)
app.add_typer(validate_app)


@app.callback()
def callback() -> None:
    """
    Manage [magenta]app.yaml[/magenta] (app manifest/config) files.
    """
    pass
