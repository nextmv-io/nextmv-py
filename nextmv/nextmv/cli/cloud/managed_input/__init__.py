"""Cloud managed-input command tree for the Nextmv CLI.

``list``, ``get``, and ``delete`` are thin wrappers around the actions in
``nextmv.cli.actions.managed_input``. ``create`` and ``update`` route
through ``_workflows.py`` because they need CLI-specific shaping
(``--content-format`` Format object, ``--output`` file save, etc).
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.managed_input import (
    delete_managed_input,
    get_managed_input,
    list_managed_inputs,
)
from nextmv.cli.cloud.managed_input._workflows import (
    run_create_managed_input,
    run_update_managed_input,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create and handle managed inputs for Nextmv Cloud applications.

    A managed input is a stored input that can be referenced and used across
    runs and experiments. Managed inputs help organize and reuse test cases
    and datasets within your application.
    """
    pass


LIST_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "List all managed inputs of application [magenta]hare-app[/magenta].",
        "nextmv cloud managed-input list --app-id hare-app",
    ),
    (
        "List all managed inputs and save the information to a file.",
        "nextmv cloud managed-input list --app-id hare-app --output managed_inputs.json",
    ),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the managed input [magenta]inp_123[/magenta] from application [magenta]hare-app[/magenta].",
        "nextmv cloud managed-input get --app-id hare-app --managed-input-id inp_123",
    ),
    (
        "Get a managed input and save the information to a file.",
        "nextmv cloud managed-input get --app-id hare-app --managed-input-id inp_123 \\\n"
        "    --output managed_input.json",
    ),
)

CREATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Create a managed input from an upload.",
        'nextmv cloud managed-input create --app-id hare-app --name "Test Input 1" \\\n'
        "    --upload-id upl_123456789",
    ),
    (
        "Create a managed input from a run.",
        'nextmv cloud managed-input create --app-id hare-app --name "Baseline Run" \\\n'
        "    --run-id run_123456789",
    ),
    (
        "Create a managed input with a specific ID and description.",
        'nextmv cloud managed-input create --app-id hare-app --name "Test Input" \\\n'
        '    --managed-input-id inp_custom --description "Test case for validation" \\\n'
        "    --upload-id upl_123456789",
    ),
    (
        "Create a managed input with a CSV content format.",
        'nextmv cloud managed-input create --app-id hare-app --name "CSV Input" \\\n'
        "    --upload-id upl_123456789 --content-format csv",
    ),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Update a managed input's name.",
        "nextmv cloud managed-input update --app-id hare-app --managed-input-id inp_123 \\\n"
        '    --name "Updated Test Input"',
    ),
    (
        "Update name and description.",
        "nextmv cloud managed-input update --app-id hare-app --managed-input-id inp_123 \\\n"
        '    --name "Updated Test Input" --description "Updated test case for validation"',
    ),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Delete a managed input.",
        "nextmv cloud managed-input delete --app-id hare-app --managed-input-id inp_123",
    ),
    (
        "Delete a managed input without the confirmation prompt.",
        "nextmv cloud managed-input delete --app-id hare-app --managed-input-id inp_123 --yes",
    ),
)


list = cli.command(  # noqa: A001
    app,
    list_managed_inputs,
    name="list",
    progress="Listing managed inputs...",
    output_flag=True,
    saved_noun="Managed inputs list information",
    examples=LIST_EXAMPLES,
)

get = cli.command(
    app,
    get_managed_input,
    name="get",
    progress="Getting managed input...",
    output_flag=True,
    saved_noun="Managed input information",
    examples=GET_EXAMPLES,
)

create = cli.command(
    app,
    run_create_managed_input,
    name="create",
    handles_own_output=True,
    examples=CREATE_EXAMPLES,
)

update = cli.command(
    app,
    run_update_managed_input,
    name="update",
    handles_own_output=True,
    examples=UPDATE_EXAMPLES,
)

delete = cli.command(
    app,
    delete_managed_input,
    name="delete",
    progress="Deleting managed input...",
    delete_confirm=cli.DeleteConfirmation(
        confirm=(
            "Are you sure you want to delete managed input "
            "[magenta]{managed_input_id}[/magenta] from application "
            "[magenta]{app_id}[/magenta]? This action cannot be undone."
        ),
        decline="Managed input [magenta]{managed_input_id}[/magenta] will not be deleted.",
        succeeded=(
            "Managed input [magenta]{managed_input_id}[/magenta] deleted successfully "
            "from application [magenta]{app_id}[/magenta]."
        ),
    ),
    examples=DELETE_EXAMPLES,
)
