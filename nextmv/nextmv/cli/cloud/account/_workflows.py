"""CLI-only workflows for the cloud account domain.

The ``create`` command accepts repeatable ``--admins`` flags that also
support comma-separated emails; the ``update`` command prints a success
message and optionally writes the updated account information to a file.
"""

import json
from pathlib import Path
from typing import Annotated

import typer

from nextmv.cli.actions.account import create_account, update_account
from nextmv.cli.framework.options import AccountIdOption, NameOption
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cloud.client import Client


def _parse_admins(admins: list[str]) -> list[str]:
    """Flatten a list of ``--admins`` values, splitting any comma-separated
    entries and stripping whitespace."""
    result: list[str] = []
    for admin in admins:
        for email in admin.split(","):
            email = email.strip()
            if email:
                result.append(email)
    return result


def run_create_account(
    client: Client,
    name: NameOption,
    admins: Annotated[
        list[str],
        typer.Option(
            "--admins",
            "-a",
            help=(
                "Email addresses of the administrators for the account. "
                "Pass multiple emails by repeating the flag, or separating with commas."
            ),
            metavar="ADMINS",
        ),
    ],
) -> None:
    """Create a new Nextmv Cloud account in your organization.

    To create managed accounts, SSO must be configured for your
    organization. Please contact Nextmv support for assistance. You may
    use ``nextmv cloud sso`` to manage the SSO configuration for your
    organization.

    At least one administrator email address must be provided. Multiple
    administrators can be specified by repeating the ``--admins`` flag or
    by separating email addresses with commas.
    """

    in_progress(msg="Creating account...")
    admin_list = _parse_admins(admins)
    account_dict = create_account(client, name=name, admins=admin_list)
    print_json(account_dict)


def run_update_account(
    client: Client,
    account_id: AccountIdOption,
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="A new name for the account.",
            metavar="NAME",
        ),
    ],
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated account information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Update information of a Nextmv Cloud account.

    This command allows you to update the name of an existing account.
    """

    in_progress(msg="Updating account...")
    updated_dict = update_account(client, account_id=account_id, name=name)
    success(f"Account [magenta]{account_id}[/magenta] updated successfully.")

    if output is not None and output != "":
        Path(output).write_text(json.dumps(updated_dict, indent=2))
        success(f"Updated account information saved to [magenta]{output}[/magenta].")
        return

    print_json(updated_dict)
