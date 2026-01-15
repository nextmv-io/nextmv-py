"""
This module defines the cloud upload command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.upload.create import app as create_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(create_app)


@app.callback()
def callback() -> None:
    """
    Create temporary upload URLs for Nextmv Cloud applications.

    When data is too large, or you are working with multiple files, you can use
    upload URLs to upload data directly to Nextmv Cloud storage.
    """
    pass
