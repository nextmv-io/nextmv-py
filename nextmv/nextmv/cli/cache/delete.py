"""
This module defines the cache delete command for the Nextmv CLI.
"""

import typer

from nextmv.cache import clear_cache, format_bytes
from nextmv.cli.message import info, success

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete() -> None:
    """
    Deletes the Nextmv cache and resets it to an empty state.

    [bold][underline]Examples[/underline][/bold]

    - Delete the Nextmv cache.
        $ [dim]nextmv cache delete[/dim]
    """

    deps, bytes_deleted = clear_cache()
    if deps == 0 and bytes_deleted == 0:
        info("Nothing to delete: cache is already empty.")
        return

    size_str = format_bytes(bytes_deleted)
    dep_label = "dependency" if deps == 1 else "dependencies"
    success(f"Deleted [magenta]{deps}[/magenta] {dep_label} ([magenta]{size_str}[/magenta]) from the cache.")
