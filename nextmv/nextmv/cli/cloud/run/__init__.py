"""
This module defines the cloud run command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.run.create import app as create_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(create_app)


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud application runs.
    """
    pass
