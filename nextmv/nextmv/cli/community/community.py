"""
This module defines the community command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.community.clone import app as clone_app
from nextmv.cli.community.list import app as list_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(list_app)
app.add_typer(clone_app)


@app.callback()
def callback() -> None:
    """
    Interact with community apps, which are pre-built decision models.

    Community apps are maintained in the following GitHub repository:
    [link=https://github.com/nextmv-io/community-apps][bold]nextmv-io/community-apps[/bold][/link].
    """
    pass
