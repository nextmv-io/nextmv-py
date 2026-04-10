"""
This module defines the cloud sso domain delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.actions.sso import delete_domain as _delete_domain
from nextmv.cli.message import confirmation, in_progress, info, success
from nextmv.cli.options import ProfileOption, YesOption
from nextmv.cloud.client import Client

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    domain: Annotated[
        str,
        typer.Option(
            "--domain",
            "-d",
            help="The domain to delete from the SSO configuration.",
            metavar="DOMAIN",
        ),
    ],
    yes: YesOption = False,
    profile: ProfileOption = None,
) -> None:
    """
    Delete a mapped domain from a Nextmv Cloud SSO configuration.


    This action will prevent users from the deleted domain from accessing your
    account using SSO. Use the --yes flag to skip the confirmation prompt.

    You can use the [code]nextmv cloud sso get[/code] command to view all
    mapped domains in your SSO configuration.

    [bold][underline]Examples[/underline][/bold]

    - Delete a mapped domain from the SSO configuration.
        $ [dim]nextmv cloud sso domain delete --domain "example.com"[/dim]
    """

    if not yes:
        confirm = confirmation(
            f"Are you sure you want to delete the [magenta]{domain}[/magenta] domain? "
            "You must contact Nextmv support to re-add it.",
        )

        if not confirm:
            info("SSO mapped domain will not be deleted.")
            return

    client = Client(profile=profile)
    in_progress(msg="Deleting SSO mapped domain from configuration...")
    _delete_domain(client, domain=domain)
    success("SSO mapped domain deleted successfully.")
