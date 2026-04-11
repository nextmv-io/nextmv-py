"""Cloud input-set command tree for the Nextmv CLI.

``list``, ``get``, and ``delete`` are thin wrappers around the actions in
``nextmv.cli.actions.input_set``. ``create`` and ``update`` route through
``_workflows.py`` because they parse a ``--managed-inputs`` JSON flag and
(for create) RFC 3339 time range flags.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.input_set import (
    delete_input_set,
    get_input_set,
    list_input_sets,
)
from nextmv.cli.cloud.input_set._workflows import (
    run_create_input_set,
    run_update_input_set,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud input sets.

    An input set is a collection of inputs from associated runs that can be
    reused across multiple experiments. Input sets allow you to test different
    configurations of your decision model using the same set of inputs for
    consistent comparison.
    """
    pass


LIST_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "List all input sets of application [magenta]hare-app[/magenta].",
        "nextmv cloud input-set list --app-id hare-app",
    ),
    (
        "List all input sets and save the information to a file.",
        "nextmv cloud input-set list --app-id hare-app --output input_sets.json",
    ),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the input set [magenta]hare-input-set[/magenta] from application [magenta]hare-app[/magenta].",
        "nextmv cloud input-set get --app-id hare-app --input-set-id hare-input-set",
    ),
    (
        "Get an input set and save the information to a file.",
        "nextmv cloud input-set get --app-id hare-app --input-set-id hare-input-set \\\n"
        "    --output input_set.json",
    ),
)

CREATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Create an input set for application [magenta]hare-app[/magenta] from runs.",
        "nextmv cloud input-set create --app-id hare-app \\\n"
        '    --name "Hare Input Set" --run-ids run-1 --run-ids run-2',
    ),
    (
        "Create an input set with a specific ID.",
        "nextmv cloud input-set create --app-id hare-app \\\n"
        '    --input-set-id hare-input-set --name "Hare Input Set" --run-ids run-1',
    ),
    (
        "Create an input set using existing managed inputs.",
        "nextmv cloud input-set create --app-id hare-app \\\n"
        '    --name "Hare Input Set" \\\n'
        "    --managed-inputs '[{\"id\": \"hare-input-1\", \"name\": \"hare input\", "
        "\"description\": \"hare description\"}]'",
    ),
    (
        "Create an input set from runs using a specific instance and time range.",
        "nextmv cloud input-set create --app-id hare-app \\\n"
        '    --name "Hare Input Set" --instance-id hare-instance \\\n'
        '    --start-time "2024-01-01T00:00:00Z" --end-time "2024-01-31T23:59:59Z"',
    ),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Update an input set's name.",
        "nextmv cloud input-set update --app-id hare-app \\\n"
        '    --input-set-id hare-input-set --name "New Name"',
    ),
    (
        "Update an input set's managed inputs.",
        "nextmv cloud input-set update --app-id hare-app --input-set-id hare-input-set \\\n"
        "    --managed-inputs '[{\"id\": \"hare-input-1\", \"name\": \"hare input\", "
        "\"description\": \"hare description\"}]'",
    ),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Delete the input set [magenta]hare-input-set[/magenta] from application [magenta]hare-app[/magenta].",
        "nextmv cloud input-set delete --app-id hare-app --input-set-id hare-input-set",
    ),
    (
        "Delete the input set without the confirmation prompt.",
        "nextmv cloud input-set delete --app-id hare-app --input-set-id hare-input-set --yes",
    ),
)


list = cli.command(  # noqa: A001
    app,
    list_input_sets,
    name="list",
    progress="Listing input sets...",
    output_flag=True,
    saved_noun="Input sets list information",
    examples=LIST_EXAMPLES,
)

get = cli.command(
    app,
    get_input_set,
    name="get",
    progress="Getting input set...",
    output_flag=True,
    saved_noun="Input set information",
    examples=GET_EXAMPLES,
)

create = cli.command(
    app,
    run_create_input_set,
    name="create",
    handles_own_output=True,
    examples=CREATE_EXAMPLES,
)

update = cli.command(
    app,
    run_update_input_set,
    name="update",
    handles_own_output=True,
    examples=UPDATE_EXAMPLES,
)

delete = cli.command(
    app,
    delete_input_set,
    name="delete",
    progress="Deleting input set...",
    delete_confirm=cli.DeleteConfirmation(
        confirm=(
            "Are you sure you want to delete input set "
            "[magenta]{input_set_id}[/magenta] from application "
            "[magenta]{app_id}[/magenta]? This action cannot be undone."
        ),
        decline="Input set [magenta]{input_set_id}[/magenta] will not be deleted.",
        succeeded=(
            "Input set [magenta]{input_set_id}[/magenta] deleted successfully "
            "from application [magenta]{app_id}[/magenta]."
        ),
    ),
    examples=DELETE_EXAMPLES,
)
