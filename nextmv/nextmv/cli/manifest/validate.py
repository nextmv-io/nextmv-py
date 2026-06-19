"""
This module defines the manifest validate command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.message import error, success
from nextmv.cli.options import DebugOption
from nextmv.manifest import MANIFEST_FILE_NAME, Manifest

# Set up subcommand application.
app = typer.Typer()


@app.command()
def validate(
    dirpath: Annotated[
        str,
        typer.Option(
            "--dirpath",
            "-d",
            help="The directory path where the manifest file is located. Defaults to the current directory.",
            metavar="DIRPATH",
        ),
    ] = ".",
    _: DebugOption = False,
) -> None:
    """
    Validate an [magenta]app.yaml[/magenta] (app manifest) file.

    Loads the [magenta]app.yaml[/magenta] manifest from the given directory and
    validates it. If no directory is provided, the current directory is used.

    [bold][underline]Examples[/underline][/bold]

    - Validate the manifest in the current directory.

        $ [dim]nextmv manifest validate[/dim]

    - Validate the manifest in the [magenta]./my-app[/magenta] directory.

        $ [dim]nextmv manifest validate --dirpath ./my-app[/dim]
    """

    try:
        Manifest.from_yaml(dirpath)
    except FileNotFoundError:
        error(
            f"Manifest file [magenta]{MANIFEST_FILE_NAME}[/magenta] not found in path [magenta]{dirpath}[/magenta], "
            "please check the path and try again."
        )
    except Exception as e:
        error(f"Manifest validation failed: {e}")

    success(f"Manifest [magenta]{MANIFEST_FILE_NAME}[/magenta] in [magenta]{dirpath}[/magenta] is valid.")
