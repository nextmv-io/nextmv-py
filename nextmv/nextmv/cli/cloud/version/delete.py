"""
This module defines the cloud version delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import info, success
from nextmv.cli.options import AppIDOption, ProfileOption, VersionIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    version_id: VersionIDOption,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Agree to deletion confirmation prompt. Useful for non-interactive sessions.",
        ),
    ] = False,
    profile: ProfileOption = None,
) -> None:
    """
    Deletes a Nextmv Cloud application version.

    This action is permanent and cannot be undone. Use the --yes
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the version with the ID [magenta]v1[/magenta] from application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud version delete --app-id hare-app --version-id v1[/dim]

    - Delete the version without confirmation prompt.
        $ [dim]nextmv cloud version delete --app-id hare-app --version-id v1 --yes[/dim]
    """

    if not yes:
        confirm = get_confirmation(
            f"Are you sure you want to delete version [magenta]{version_id}[/magenta] "
            f"from application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(msg=f"Version [magenta]{version_id}[/magenta] will not be deleted.", emoji=":bulb:")
            return

    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.delete_version(version_id=version_id)
    success(
        f"Version [magenta]{version_id}[/magenta] deleted successfully from application [magenta]{app_id}[/magenta]."
    )
