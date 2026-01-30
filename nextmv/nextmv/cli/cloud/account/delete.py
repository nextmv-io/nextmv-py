"""
This module defines the cloud account delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_account
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import info, success
from nextmv.cli.options import AccountIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    account_id: AccountIDOption,
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
    Deletes an account within your SSO-enabled organization.

    You must have the [magenta]administrator[/magenta] role on that account in order to delete it.

    This action is permanent and cannot be undone. Use the --yes
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the account with the ID [magenta]bunnies-account[/magenta].
        $ [dim]nextmv cloud account delete --account-id bunnies-account[/dim]

    - Delete the account without confirmation prompt.
        $ [dim]nextmv cloud account delete --account-id bunnies-account --yes[/dim]
    """

    if not yes:
        confirm = get_confirmation(
            f"Are you sure you want to delete account [magenta]{account_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(f"Account [magenta]{account_id}[/magenta] will not be deleted.")
            return

    cloud_account = build_account(account_id=account_id, profile=profile)
    cloud_account.delete()
    success(f"Account [magenta]{account_id}[/magenta] has been deleted.")
