"""
This module defines the cloud ensemble command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.ensemble.create import app as create_app
from nextmv.cli.cloud.ensemble.delete import app as delete_app
from nextmv.cli.cloud.ensemble.get import app as get_app
from nextmv.cli.cloud.ensemble.list import app as list_app
from nextmv.cli.cloud.ensemble.update import app as update_app

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
    Create and manage Nextmv Cloud ensemble definitions.

    An ensemble definition defines how to coordinate and execute multiple child
    runs for an application, and how to determine the optimal result from those
    runs. You can configure run groups to specify which instances to run on and
    with what options, as well as evaluation rules to determine the best result
    based on specified metrics.
    """
    pass
