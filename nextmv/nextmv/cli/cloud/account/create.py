"""
This module defines the cloud account create command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_client
from nextmv.cli.message import in_progress, print_json
from nextmv.cli.options import ProfileOption
from nextmv.cloud.account import Account

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    admins: Annotated[
        list[str],
        typer.Option(
            "--admins",
            "-a",
            help="Email addresses of the administrators for the account. "
            "Pass multiple emails by repeating the flag, or separating with commas.",
            metavar="ADMINS",
        ),
    ],
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="A name for the account.",
            metavar="NAME",
        ),
    ],
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Cloud account in your organization.

    To create managed accounts, SSO must be configured for your organization.
    Please contact [link=https://www.nextmv.io/contact][bold]Nextmv support[/bold][/link] for assistance.

    At least one administrator email address must be provided. Multiple
    administrators can be specified by repeating the --admins flag or by
    separating email addresses with commas.

    [bold][underline]Examples[/underline][/bold]

    - Create an account named [magenta]Bunny Logistics[/magenta] with a single administrator.
        $ [dim]nextmv cloud account create --name "Bunny Logistics" \\
            --admins peter.rabbit@carrotexpress.com[/dim]

    - Create an account named [magenta]Hare Delivery Co[/magenta] with multiple administrators.
        $ [dim]nextmv cloud account create --name "Hare Delivery Co" \\
            --admins bugs@acme.com --admins roger@toontown.com[/dim]

    - Create an account using the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud account create --name "Cottontail Couriers" \\
            --admins fluffy@hopmail.com --profile hare[/dim]

    - Create an account with comma-separated administrators.
        $ [dim]nextmv cloud account create --name "Whiskers Warehouse" \\
            --admins "thumper@forestmail.com,flopsy@warren.io"[/dim]
    """

    cloud_client = build_client(profile)
    in_progress(msg="Creating account...")

    admin_list = []
    for admin in admins:
        # It is possible to pass multiple emails separated by commas. The
        # default way though is to use the flag multiple times to specify
        # different options.
        sub_admins = admin.split(",")
        for sub_admin in sub_admins:
            admin_list.append(sub_admin.strip())

    account = Account.new(client=cloud_client, name=name, admins=admin_list)
    print_json(account.to_dict())
