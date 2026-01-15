"""
This module defines the cloud version command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.version.create import app as create_app
from nextmv.cli.cloud.version.delete import app as delete_app
from nextmv.cli.cloud.version.exists import app as exists_app
from nextmv.cli.cloud.version.get import app as get_app
from nextmv.cli.cloud.version.list import app as list_app
from nextmv.cli.cloud.version.update import app as update_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(create_app)
app.add_typer(delete_app)
app.add_typer(exists_app)
app.add_typer(get_app)
app.add_typer(list_app)
app.add_typer(update_app)


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud application versions.

    A version represents a snapshot of an application's code at a specific
    point in time. Versions are used to track changes to the decision model.
    You can think of versions as Git tags for your Nextmv Cloud applications.
    """
    pass
