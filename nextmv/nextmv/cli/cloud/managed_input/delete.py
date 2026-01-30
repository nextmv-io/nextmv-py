"""
This module defines the cloud managed-input delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import info, success
from nextmv.cli.options import AppIDOption, ManagedInputIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    managed_input_id: ManagedInputIDOption,
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
        confirm = get_confirmation(
            f"Are you sure you want to delete managed input [magenta]{managed_input_id}[/magenta] "
            f"from application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(f"Managed input [magenta]{managed_input_id}[/magenta] will not be deleted.")
            return

    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.delete_managed_input(managed_input_id=managed_input_id)
    success(
        f"Managed input [magenta]{managed_input_id}[/magenta] deleted successfully "
        f"from application [magenta]{app_id}[/magenta]."
    )
