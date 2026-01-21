"""
This module defines the cloud acceptance command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.acceptance.create import app as create_app
from nextmv.cli.cloud.acceptance.delete import app as delete_app
from nextmv.cli.cloud.acceptance.get import app as get_app
from nextmv.cli.cloud.acceptance.list import app as list_app
from nextmv.cli.cloud.acceptance.update import app as update_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(create_app)
app.add_typer(delete_app)
app.add_typer(get_app)
app.add_typer(list_app)
app.add_typer(update_app)


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud acceptance tests.
    """
    pass
