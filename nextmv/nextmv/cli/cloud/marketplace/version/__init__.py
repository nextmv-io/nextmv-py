"""
This module defines the cloud marketplace version command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.marketplace.version.create import app as create_app
from nextmv.cli.cloud.marketplace.version.get import app as get_app
from nextmv.cli.cloud.marketplace.version.list import app as list_app
from nextmv.cli.cloud.marketplace.version.update import app as update_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(create_app)
app.add_typer(get_app)
app.add_typer(list_app)
app.add_typer(update_app)


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Marketplace application versions.
    """
    pass
