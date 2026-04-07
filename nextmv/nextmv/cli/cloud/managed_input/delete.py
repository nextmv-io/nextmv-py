"""
This module defines the cloud managed-input delete command for the Nextmv CLI.
"""

import typer

from nextmv.cli.actions.managed_input import delete_managed_input as _delete_managed_input
from nextmv.cli.message import confirmation, info, success
from nextmv.cli.options import AppIDOption, ManagedInputIDOption, ProfileOption, YesOption
from nextmv.cloud.client import Client

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    managed_input_id: ManagedInputIDOption,
    yes: YesOption = False,
    profile: ProfileOption = None,
) -> None:
    """
    Deletes a Nextmv Cloud application managed input.

    This action is permanent and cannot be undone. Use the --yes
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the managed input with the ID [magenta]inp_123456789[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud managed-input delete --app-id hare-app \
            --managed-input-id inp_123456789[/dim]

    - Delete the managed input without confirmation prompt.
        $ [dim]nextmv cloud managed-input delete --app-id hare-app --managed-input-id inp_123456789 --yes[/dim]
    """

    if not yes:
        confirm = confirmation(
            f"Are you sure you want to delete managed input [magenta]{managed_input_id}[/magenta] "
            f"from application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(f"Managed input [magenta]{managed_input_id}[/magenta] will not be deleted.")
            return

    client = Client(profile=profile)
    _delete_managed_input(client, app_id=app_id, managed_input_id=managed_input_id)
    success(
        f"Managed input [magenta]{managed_input_id}[/magenta] deleted successfully "
        f"from application [magenta]{app_id}[/magenta]."
    )
