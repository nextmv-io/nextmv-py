"""Cloud account command tree for the Nextmv CLI.

``get`` and ``delete`` wrap thin actions from ``nextmv.cli.actions.account``.
``create`` and ``update`` route through ``_workflows.py`` for admin email
parsing and ``--output`` file saves respectively.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.account import delete_account, get_account
from nextmv.cli.cloud.account._workflows import run_create_account, run_update_account

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Manage your Nextmv Cloud account (organization).

    Please contact Nextmv support for assistance configuring SSO for your
    organization. You may use ``nextmv cloud sso`` to manage the SSO
    configuration for your organization.
    """
    pass


GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the account with the ID [magenta]bunny-logistics[/magenta].",
        "nextmv cloud account get --account-id bunny-logistics",
    ),
    (
        "Get an account and save the information to a file.",
        "nextmv cloud account get --account-id cottontail-couriers --output account.json",
    ),
)

CREATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Create an account named [magenta]Bunny Logistics[/magenta] with a single administrator.",
        'nextmv cloud account create --name "Bunny Logistics" \\\n'
        "    --admins peter.rabbit@carrotexpress.com",
    ),
    (
        "Create an account with multiple administrators by repeating the flag.",
        'nextmv cloud account create --name "Hare Delivery Co" \\\n'
        "    --admins bugs@acme.com --admins roger@toontown.com",
    ),
    (
        "Create an account with comma-separated administrators.",
        'nextmv cloud account create --name "Whiskers Warehouse" \\\n'
        '    --admins "thumper@forestmail.com,flopsy@warren.io"',
    ),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Update an account's name.",
        "nextmv cloud account update --account-id hare-delivery \\\n"
        '    --name "Hare Delivery Co"',
    ),
    (
        "Update an account and save the updated information to a file.",
        "nextmv cloud account update --account-id cottontail-couriers \\\n"
        '    --name "Cottontail Express" --output updated_account.json',
    ),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Delete an account by ID.",
        "nextmv cloud account delete --account-id bunnies-account",
    ),
    (
        "Delete an account without the confirmation prompt.",
        "nextmv cloud account delete --account-id bunnies-account --yes",
    ),
)


get = cli.command(
    app,
    get_account,
    name="get",
    progress="Getting account...",
    output_flag=True,
    saved_noun="Account information",
    examples=GET_EXAMPLES,
)

create = cli.command(
    app,
    run_create_account,
    name="create",
    handles_own_output=True,
    examples=CREATE_EXAMPLES,
)

update = cli.command(
    app,
    run_update_account,
    name="update",
    handles_own_output=True,
    examples=UPDATE_EXAMPLES,
)

delete = cli.command(
    app,
    delete_account,
    name="delete",
    progress="Deleting account...",
    delete_confirm=cli.DeleteConfirmation(
        confirm=(
            "Are you sure you want to delete account "
            "[magenta]{account_id}[/magenta]? This action cannot be undone."
        ),
        decline="Account [magenta]{account_id}[/magenta] will not be deleted.",
        succeeded="Account [magenta]{account_id}[/magenta] has been deleted.",
    ),
    examples=DELETE_EXAMPLES,
)
