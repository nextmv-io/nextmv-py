"""
This module defines the cloud secrets command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.secrets.create import app as create_app
from nextmv.cli.cloud.secrets.delete import app as delete_app
from nextmv.cli.cloud.secrets.get import app as get_app
from nextmv.cli.cloud.secrets.list import app as list_app
from nextmv.cli.cloud.secrets.update import app as update_app

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
    Create and manage Nextmv Cloud secrets collections.

    A secret collection defines one or more secrets used by your optimization
    model during execution. You can reference a secret collection either in an
    application instance configuration, or directly when starting a run. The
    platform then injects the secrets into the container during the
    optimization run as environment variables and files.
    """
    pass
