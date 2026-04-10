"""
This module defines the cloud version delete command for the Nextmv CLI.
"""

import typer

from nextmv.cli.actions.version import delete_version as _delete_version
from nextmv.cli.message import confirmation, info, success
from nextmv.cli.options import AppIDOption, ProfileOption, VersionIDOption, YesOption
from nextmv.cloud.client import Client

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    version_id: VersionIDOption,
    yes: YesOption = False,
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
        confirm = confirmation(
            f"Are you sure you want to delete version [magenta]{version_id}[/magenta] "
            f"from application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(f"Version [magenta]{version_id}[/magenta] will not be deleted.")
            return

    client = Client(profile=profile)
    _delete_version(client, app_id=app_id, version_id=version_id)
    success(
        f"Version [magenta]{version_id}[/magenta] deleted successfully from application [magenta]{app_id}[/magenta]."
    )
