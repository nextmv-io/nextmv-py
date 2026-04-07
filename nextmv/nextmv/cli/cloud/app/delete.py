"""
This module defines the cloud app delete command for the Nextmv CLI.
"""

import typer

from nextmv.cli.actions.app import delete_app as _delete_app
from nextmv.cli.message import confirmation, info, success
from nextmv.cli.options import AppIDOption, ProfileOption, YesOption
from nextmv.cloud.client import Client

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    yes: YesOption = False,
    profile: ProfileOption = None,
) -> None:
    """
    Deletes a Nextmv Cloud application.

    This action is permanent and cannot be undone. Use the --yes
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the application with the ID [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud app delete --app-id hare-app[/dim]

    - Delete the application with the ID [magenta]hare-app[/magenta] without confirmation prompt.
        $ [dim]nextmv cloud app delete --app-id hare-app --yes[/dim]
    """

    if not yes:
        confirm = confirmation(
            f"Are you sure you want to delete application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(f"Application [magenta]{app_id}[/magenta] will not be deleted.")
            return

    client = Client(profile=profile)
    _delete_app(client, app_id=app_id)
    success(f"Application [magenta]{app_id}[/magenta] deleted successfully.")
