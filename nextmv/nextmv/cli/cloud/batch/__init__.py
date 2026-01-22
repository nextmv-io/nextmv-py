"""
This module defines the cloud batch command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.batch.create import app as create_app
from nextmv.cli.cloud.batch.delete import app as delete_app
from nextmv.cli.cloud.batch.get import app as get_app
from nextmv.cli.cloud.batch.list import app as list_app
from nextmv.cli.cloud.batch.metadata import app as metadata_app
from nextmv.cli.cloud.batch.update import app as update_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(create_app)
app.add_typer(delete_app)
app.add_typer(get_app)
app.add_typer(list_app)
app.add_typer(metadata_app)
app.add_typer(update_app)


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud batch experiments.
    """
    pass
