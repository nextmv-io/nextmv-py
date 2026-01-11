"""
This module defines the cloud run command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.run.cancel import app as cancel_app
from nextmv.cli.cloud.run.create import app as create_app
from nextmv.cli.cloud.run.get import app as get_app
from nextmv.cli.cloud.run.logs import app as logs_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(cancel_app)
app.add_typer(create_app)
app.add_typer(get_app)
app.add_typer(logs_app)


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud application runs.
    """
    pass
