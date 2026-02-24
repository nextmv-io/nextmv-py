"""
This module defines the cloud sso delete domain command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_sso_config
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import in_progress, info, success
from nextmv.cli.options import ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Agree to deletion confirmation prompt. Useful for non-interactive sessions.",
        ),
    ] = False,
    domain: Annotated[
        str | None,
        typer.Option(
            "--domain",
            "-d",
            help="The domain to delete from the SSO configuration.",
            metavar="DOMAIN",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Delete a mapped domain from a Nextmv Cloud SSO configuration.

    Mapped domains redirect additional domains to your IDP for federated authentication.
    This command deletes a domain from an existing SSO configuration.

    You can use the command [code] nextmv cloud sso get[/code] command to view all
    mapped domains in your SSO configuration.

    [bold][underline]Examples[/underline][/bold]

    - Delete a mapped domain from the SSO configuration.
        $ [dim]nextmv cloud sso domain delete --domain "example.com"[/dim]
    """

    if not yes:
        confirm = get_confirmation(
            f"Are you sure you want to delete the [magenta]{domain}[/magenta] domain? "
            "You must contact Nextmv support to re-add it.",
        )

        if not confirm:
            info("SSO mapped domain will not be deleted.")
            return

    sso_config = build_sso_config(profile)
    in_progress(msg="Deleting SSO mapped domain from configuration...")
    sso_config.delete_domain(domain=domain)
    success("SSO mapped domain deleted successfully.")
