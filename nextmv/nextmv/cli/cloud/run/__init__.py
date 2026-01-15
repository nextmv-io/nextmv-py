"""
This module defines the cloud run command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.run.cancel import app as cancel_app
from nextmv.cli.cloud.run.create import app as create_app
from nextmv.cli.cloud.run.get import app as get_app
from nextmv.cli.cloud.run.input import app as input_app
from nextmv.cli.cloud.run.list import app as list_app
from nextmv.cli.cloud.run.logs import app as logs_app
from nextmv.cli.cloud.run.metadata import app as metadata_app
from nextmv.cli.cloud.run.track import app as track_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(cancel_app)
app.add_typer(create_app)
app.add_typer(get_app)
app.add_typer(input_app)
app.add_typer(list_app)
app.add_typer(logs_app)
app.add_typer(metadata_app)
app.add_typer(track_app)


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud application runs.

    A run represents the execution of a decision model within a Nextmv Cloud
    application. Each run takes an input, processes it using the decision model,
    and produces an output.
    """
    pass
