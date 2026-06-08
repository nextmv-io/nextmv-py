"""
This module defines the cache get command for the Nextmv CLI.
"""

import typer

from nextmv.cache import get_cache
from nextmv.cli.message import print_json, success
from nextmv.cli.options import DebugOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(_: DebugOption = False) -> None:
    """
    Gets general information about the Nextmv cache.

    [bold][underline]Examples[/underline][/bold]

    - Get cache information.
        $ [dim]nextmv cache get[/dim]
    """

    info = get_cache()
    success("Cache information retrieved successfully.")
    print_json(info)
