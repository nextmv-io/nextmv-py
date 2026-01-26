"""
This module defines the cloud switchback command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.switchback.create import app as create_app
from nextmv.cli.cloud.switchback.delete import app as delete_app
from nextmv.cli.cloud.switchback.get import app as get_app
from nextmv.cli.cloud.switchback.list import app as list_app
from nextmv.cli.cloud.switchback.metadata import app as metadata_app
from nextmv.cli.cloud.switchback.start import app as start_app
from nextmv.cli.cloud.switchback.stop import app as stop_app
from nextmv.cli.cloud.switchback.update import app as update_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(create_app)
app.add_typer(delete_app)
app.add_typer(get_app)
app.add_typer(list_app)
app.add_typer(metadata_app)
app.add_typer(start_app)
app.add_typer(stop_app)
app.add_typer(update_app)


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud switchback tests.
    """
    pass
