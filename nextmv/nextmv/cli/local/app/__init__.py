"""
This module defines the local app command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.local.app.delete import app as delete_app
from nextmv.cli.local.app.get import app as get_app
from nextmv.cli.local.app.list import app as list_app
from nextmv.cli.local.app.register import app as register_app
from nextmv.cli.local.app.registered import app as registered_app
from nextmv.cli.local.app.sync import app as sync_app
from nextmv.cli.local.app.update import app as update_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(delete_app)
app.add_typer(get_app)
app.add_typer(list_app)
app.add_typer(register_app)
app.add_typer(registered_app)
app.add_typer(sync_app)
app.add_typer(update_app)


@app.callback()
def callback() -> None:
    """
    Manage and sync local Nextmv applications.

    A Nextmv application is an entity that contains a decision model as
    executable code. An application can make a run by taking an input,
    executing the decision model, and producing an output.
    """
    pass
