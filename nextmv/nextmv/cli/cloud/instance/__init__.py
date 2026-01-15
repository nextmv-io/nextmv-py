"""
This module defines the cloud instance command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.instance.create import app as create_app
from nextmv.cli.cloud.instance.delete import app as delete_app
from nextmv.cli.cloud.instance.exists import app as exists_app
from nextmv.cli.cloud.instance.get import app as get_app
from nextmv.cli.cloud.instance.list import app as list_app
from nextmv.cli.cloud.instance.update import app as update_app

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
    Create and manage Nextmv Cloud application instances.

    An application instance is a representation of a version and optional
    configuration (options/parameters). Instances are the mechanism by which a
    run is made. When you make a new run, the app determines which instance to
    use and then uses the executable code associated to the version for the
    run.
    """
    pass
