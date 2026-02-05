"""
This module defines the cloud sso command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.sso.create import app as create_app
from nextmv.cli.cloud.sso.delete import app as delete_app
from nextmv.cli.cloud.sso.disable import app as disable_app
from nextmv.cli.cloud.sso.enable import app as enable_app
from nextmv.cli.cloud.sso.get import app as get_app
from nextmv.cli.cloud.sso.update import app as update_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(create_app)
app.add_typer(delete_app)
app.add_typer(disable_app)
app.add_typer(enable_app)
app.add_typer(get_app)
app.add_typer(update_app)


@app.callback()
def callback() -> None:
    """
    Manage SSO for your Nextmv Cloud organization (account).

    Please contact [link=https://www.nextmv.io/contact][bold]Nextmv support[/bold][/link]
    for assistance configuring SSO for your organization.
    """
    pass
