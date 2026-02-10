"""
This module defines the cloud marketplace command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.marketplace.app import app as app_app
from nextmv.cli.cloud.marketplace.subscription import app as subscription_app
from nextmv.cli.cloud.marketplace.version import app as version_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(app_app, name="app")
app.add_typer(subscription_app, name="subscription")
app.add_typer(version_app, name="version")


@app.callback()
def callback() -> None:
    """
    Interact with the Nextmv Marketplace.

    The Nextmv Marketplace is a platform where users can discover,
    subscribe to, and run decision applications for various use cases.
    """
    pass
