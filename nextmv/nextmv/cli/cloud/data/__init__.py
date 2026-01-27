"""
This module defines the cloud data command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.data.upload import app as upload_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(upload_app)


@app.callback()
def callback() -> None:
    """
    Upload data for Nextmv Cloud application components.

    When data is too large (exceeds [magenta]5 MiB[/magenta]), or you are
    working with the [magenta]multi-file[/magenta] content format, you can use
    this command to upload information to Nextmv Cloud. Requires a pre-signed
    upload URL, which can be obtained using the [code]nextmv cloud upload
    create[/code] command. Use the [magenta].upload_url[/magenta] field from the
    command output.
    """
    pass
