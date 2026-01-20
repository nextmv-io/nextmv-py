"""
This module defines the cloud managed-input command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.managed_input.create import app as create_app
from nextmv.cli.cloud.managed_input.delete import app as delete_app
from nextmv.cli.cloud.managed_input.get import app as get_app
from nextmv.cli.cloud.managed_input.list import app as list_app
from nextmv.cli.cloud.managed_input.update import app as update_app

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
    Create and handle managed inputs for Nextmv Cloud applications.

    A managed input is a stored input that can be referenced and used across
    runs and experiments. Managed inputs help organize and reuse test cases
    and datasets within your application.
    """
    pass
