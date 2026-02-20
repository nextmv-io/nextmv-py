"""
This module defines the local manifest command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.local.manifest.init import app as init_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(init_app)


@app.callback()
def callback() -> None:
    """
    Manage Nextmv app manifest files.
    """
    pass
