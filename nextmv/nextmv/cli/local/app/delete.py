"""
This module defines the local app delete command for the Nextmv CLI.
"""

import os

import typer

from nextmv.cli.message import confirmation, info, success, warning
from nextmv.cli.options import DebugOption, LocalAppIDOption, LocalAppSrcOption, YesOption
from nextmv.local.registry import Registry

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: LocalAppIDOption = None,
    app_src: LocalAppSrcOption = None,
    yes: YesOption = False,
    _: DebugOption = False,
) -> None:
    """
    Deletes a Nextmv application from the local registry.

    You may identify the app by using --app-src or --app-id. This action is
    permanent and cannot be undone. Use the --yes flag to skip the confirmation
    prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the application with the ID [magenta]hare-app[/magenta].

        $ [dim]nextmv local app delete --app-id hare-app[/dim]

    - Delete the application with the ID [magenta]hare-app[/magenta] without confirmation prompt.

        $ [dim]nextmv local app delete --app-id hare-app --yes[/dim]
    """

    if (app_id is None or app_id == "") and (app_src is None or app_src == ""):
        app_src = "."

    if app_src is not None and app_src != "":
        app_src = os.path.abspath(app_src)

    if not yes:
        if app_id is not None and app_id != "":
            msg = f"Are you sure you want to delete application [magenta]{app_id}[/magenta]?"
        elif app_src is not None and app_src != "":
            msg = f"Are you sure you want to delete application with source [magenta]{app_src}[/magenta]?"

        confirm = confirmation(f"{msg} This action cannot be undone.")

        if not confirm:
            if app_id is not None and app_id != "":
                info(f"Application [magenta]{app_id}[/magenta] will not be deleted.")
            elif app_src is not None and app_src != "":
                info(f"Application with source [magenta]{app_src}[/magenta] will not be deleted.")

            return

    reg = Registry.from_yaml()
    entry = reg.entry(app_id=app_id, src=app_src)
    if entry is None:
        warning(
            f"Could not find a local registry entry for app ID [magenta]{app_id}[/magenta] and "
            f"source [magenta]{app_src}[/magenta]."
        )
        return

    reg.delete_entry(app_id=app_id, src=app_src)
    success("Application deleted successfully from the local registry.")
