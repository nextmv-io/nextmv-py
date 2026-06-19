"""
This module defines the cache delete command for the Nextmv CLI.
"""

import typer

from nextmv.cache import clear_cache, format_bytes
from nextmv.cli.message import confirmation, info, success
from nextmv.cli.options import DebugOption, YesOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(yes: YesOption = False, _: DebugOption = False) -> None:
    """
    Deletes the Nextmv cache and resets it to an empty state.

    This action is permanent and cannot be undone. Use the --yes flag to skip
    the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the Nextmv cache.

        $ [dim]nextmv cache delete[/dim]

    - Delete the Nextmv cache without confirmation prompt.

        $ [dim]nextmv cache delete --yes[/dim]
    """

    deps, bytes_deleted = clear_cache()
    if deps == 0 and bytes_deleted == 0:
        info("Nothing to delete: cache is already empty.")
        return

    if not yes:
        confirm = confirmation(
            "Are you sure you want to delete the Nextmv cache? This action cannot be undone.",
        )

        if not confirm:
            info("The Nextmv cache will not be deleted.")
            return

    size_str = format_bytes(bytes_deleted)
    dep_label = "dependency" if deps == 1 else "dependencies"
    success(f"Deleted [magenta]{deps}[/magenta] {dep_label} ([magenta]{size_str}[/magenta]) from the cache.")
