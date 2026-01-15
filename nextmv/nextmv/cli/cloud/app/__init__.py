"""
This module defines the cloud app command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.app.create import app as create_app
from nextmv.cli.cloud.app.delete import app as delete_app
from nextmv.cli.cloud.app.exists import app as exists_app
from nextmv.cli.cloud.app.get import app as get_app
from nextmv.cli.cloud.app.list import app as list_app
from nextmv.cli.cloud.app.push import app as push_app
from nextmv.cli.cloud.app.update import app as update_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(create_app)
app.add_typer(delete_app)
app.add_typer(exists_app)
app.add_typer(get_app)
app.add_typer(list_app)
app.add_typer(push_app)
app.add_typer(update_app)


@app.callback()
def callback() -> None:
    """
    Create, manage, and push Nextmv Cloud applications.

    A Nextmv application is an entity that contains a decision model as
    executable code. An application can make a run by taking an input,
    executing the decision model, and producing an output.
    """
    pass
