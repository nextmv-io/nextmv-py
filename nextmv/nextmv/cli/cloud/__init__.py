"""
This module defines the cloud command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.app import app as app_app
from nextmv.cli.cloud.instance import app as instance_app
from nextmv.cli.cloud.run import app as run_app
from nextmv.cli.cloud.upload import app as upload_app
from nextmv.cli.cloud.version import app as version_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(app_app, name="app")
app.add_typer(instance_app, name="instance")
app.add_typer(run_app, name="run")
app.add_typer(upload_app, name="upload")
app.add_typer(version_app, name="version")


@app.callback()
def callback() -> None:
    """
    Interact with Nextmv Cloud, a platform for deploying and managing decision models.
    """
    pass
