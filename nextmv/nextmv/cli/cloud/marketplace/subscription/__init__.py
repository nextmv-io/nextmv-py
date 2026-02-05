"""
This module defines the cloud marketplace subscription command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.marketplace.subscription.create import app as create_app
from nextmv.cli.cloud.marketplace.subscription.delete import app as delete_app
from nextmv.cli.cloud.marketplace.subscription.get import app as get_app
from nextmv.cli.cloud.marketplace.subscription.list import app as list_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(create_app)
app.add_typer(delete_app)
app.add_typer(get_app)
app.add_typer(list_app)


@app.callback()
def callback() -> None:
    """
    Manage Nextmv Marketplace subscriptions.

    These commands allow you to view and manage your subscriptions to
    Marketplace applications.
    """
    pass
