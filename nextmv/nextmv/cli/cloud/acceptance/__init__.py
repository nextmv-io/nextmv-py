"""Cloud acceptance command tree for the Nextmv CLI.

``list`` and ``delete`` wrap the thin actions in
``nextmv.cli.actions.acceptance``. ``get``, ``create``, and ``update``
route through ``_workflows.py`` because they handle polling/waiting,
JSON parsing of metric definitions, and ``--output`` file saves.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.acceptance import (
    delete_acceptance_test,
    list_acceptance_tests,
)
from nextmv.cli.cloud.acceptance._workflows import (
    run_create_acceptance_test,
    run_get_acceptance_test,
    run_update_acceptance_test,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud acceptance tests.
    """
    pass


LIST_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "List all acceptance tests of application [magenta]hare-app[/magenta].",
        "nextmv cloud acceptance list --app-id hare-app",
    ),
    (
        "List all acceptance tests and save the information to a file.",
        "nextmv cloud acceptance list --app-id hare-app --output acceptance_tests.json",
    ),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get an acceptance test by ID.",
        "nextmv cloud acceptance get --app-id hare-app --acceptance-test-id test-123",
    ),
    (
        "Get an acceptance test and wait for it to complete.",
        "nextmv cloud acceptance get --app-id hare-app --acceptance-test-id test-123 --wait",
    ),
    (
        "Get an acceptance test and save the results to a file.",
        "nextmv cloud acceptance get --app-id hare-app \\\n"
        "    --acceptance-test-id test-123 --output results.json",
    ),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Update the name of an acceptance test.",
        "nextmv cloud acceptance update --app-id hare-app \\\n"
        '    --acceptance-test-id test-123 --name "Updated Test Name"',
    ),
    (
        "Update name and description.",
        "nextmv cloud acceptance update --app-id hare-app --acceptance-test-id test-123 \\\n"
        '    --name "New Name" --description "New description"',
    ),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Delete an acceptance test.",
        "nextmv cloud acceptance delete --app-id hare-app --acceptance-test-id test-123",
    ),
    (
        "Delete without the confirmation prompt.",
        "nextmv cloud acceptance delete --app-id hare-app --acceptance-test-id test-123 --yes",
    ),
)


list = cli.command(  # noqa: A001
    app,
    list_acceptance_tests,
    name="list",
    progress="Listing acceptance tests...",
    output_flag=True,
    saved_noun="Acceptance tests list information",
    examples=LIST_EXAMPLES,
)

get = cli.command(
    app,
    run_get_acceptance_test,
    name="get",
    handles_own_output=True,
    examples=GET_EXAMPLES,
)

# `create` takes many flags including repeatable JSON metrics and
# optional polling. The create workflow is inherently interactive.
create = cli.command(
    app,
    run_create_acceptance_test,
    name="create",
    handles_own_output=True,
)

update = cli.command(
    app,
    run_update_acceptance_test,
    name="update",
    handles_own_output=True,
    examples=UPDATE_EXAMPLES,
)

delete = cli.command(
    app,
    delete_acceptance_test,
    name="delete",
    progress="Deleting acceptance test...",
    delete_confirm=cli.DeleteConfirmation(
        confirm=(
            "Are you sure you want to delete acceptance test "
            "[magenta]{acceptance_test_id}[/magenta] from application "
            "[magenta]{app_id}[/magenta]? This action cannot be undone."
        ),
        decline="Acceptance test [magenta]{acceptance_test_id}[/magenta] will not be deleted.",
        succeeded=(
            "Acceptance test [magenta]{acceptance_test_id}[/magenta] deleted successfully "
            "from application [magenta]{app_id}[/magenta]."
        ),
    ),
    examples=DELETE_EXAMPLES,
)
