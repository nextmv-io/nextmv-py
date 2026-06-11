"""
Subcommands for authenticating with Nextmv (PKCE flow, logout).
"""

import typer

from nextmv.cli.auth.login import app as login_app
from nextmv.cli.auth.logout import app as logout_app

app = typer.Typer()
app.add_typer(login_app)
app.add_typer(logout_app)


@app.callback()
def callback() -> None:
    """Authenticate and manage login sessions."""
    pass
