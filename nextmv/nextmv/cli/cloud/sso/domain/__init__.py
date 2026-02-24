"""
This module defines the cloud sso command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.sso.domain.delete import app as delete_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(delete_app)


@app.callback()
def callback() -> None:
    """
    Manage SSO mapped domains for your Nextmv Cloud organization (account).

    Please contact [link=https://www.nextmv.io/contact][bold]Nextmv support[/bold][/link]
    for assistance configuring SSO for your organization.
    """
    pass
