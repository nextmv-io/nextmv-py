"""
This module defines the cloud command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.run import app as run_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(run_app, name="run")


@app.callback()
def callback() -> None:
    """
    Interact with Nextmv Cloud, a platform for deploying and managing decision models.
    """
    pass
