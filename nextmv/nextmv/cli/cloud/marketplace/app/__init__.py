"""
This module defines the cloud marketplace app command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.marketplace.app.create import app as create_app
from nextmv.cli.cloud.marketplace.app.get import app as get_app
from nextmv.cli.cloud.marketplace.app.list import app as list_app
from nextmv.cli.cloud.marketplace.app.update import app as update_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(create_app)
app.add_typer(get_app)
app.add_typer(list_app)
app.add_typer(update_app)


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Marketplace applications.

    Unlike the [code]nextmv cloud app[/code] command set, this one can be used
    to manage Marketplace applications instances explicitly.
    """
    pass
