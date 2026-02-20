"""
This module defines the local command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.local.app import app as app_app
from nextmv.cli.local.manifest import app as manifest_app
from nextmv.cli.local.run import app as run_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(app_app, name="app")
app.add_typer(manifest_app, name="manifest")
app.add_typer(run_app, name="run")


@app.callback()
def callback() -> None:
    """
    Interact with local Nextmv apps and make runs.
    """
    pass
