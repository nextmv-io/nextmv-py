"""Cloud scenario command tree for the Nextmv CLI.

``list`` and ``delete`` wrap the thin actions in
``nextmv.cli.actions.scenario``. ``get``, ``metadata``, ``create``, and
``update`` route through ``_workflows.py`` because they handle polling,
JSON scenario parsing, ``--output`` file saves, and a separate metadata
retrieval path.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.scenario import (
    delete_scenario_test,
    list_scenario_tests,
)
from nextmv.cli.cloud.scenario._workflows import (
    run_create_scenario_test,
    run_get_scenario_metadata,
    run_get_scenario_test,
    run_update_scenario_test,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud scenario tests.
    """
    pass


LIST_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "List all scenario tests for application [magenta]hare-app[/magenta].",
        "nextmv cloud scenario list --app-id hare-app",
    ),
    (
        "List all scenario tests and save to a file.",
        "nextmv cloud scenario list --app-id hare-app --output scenario_tests.json",
    ),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get a scenario test by ID.",
        "nextmv cloud scenario get --app-id hare-app --scenario-test-id test-123",
    ),
    (
        "Get a scenario test and wait for it to complete.",
        "nextmv cloud scenario get --app-id hare-app --scenario-test-id test-123 --wait",
    ),
    (
        "Get a scenario test and save the results to a file.",
        "nextmv cloud scenario get --app-id hare-app \\\n"
        "    --scenario-test-id test-123 --output results.json",
    ),
)

METADATA_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get metadata for a scenario test.",
        "nextmv cloud scenario metadata --app-id hare-app --scenario-test-id test-123",
    ),
    (
        "Get metadata and save it to a file.",
        "nextmv cloud scenario metadata --app-id hare-app \\\n"
        "    --scenario-test-id test-123 --output metadata.json",
    ),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Update the name of a scenario test.",
        "nextmv cloud scenario update --app-id hare-app \\\n"
        '    --scenario-test-id test-123 --name "Updated Test Name"',
    ),
    (
        "Update name and description.",
        "nextmv cloud scenario update --app-id hare-app --scenario-test-id test-123 \\\n"
        '    --name "New Name" --description "New description"',
    ),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Delete a scenario test.",
        "nextmv cloud scenario delete --app-id hare-app --scenario-test-id test-123",
    ),
    (
        "Delete without the confirmation prompt.",
        "nextmv cloud scenario delete --app-id hare-app --scenario-test-id test-123 --yes",
    ),
)


list = cli.command(  # noqa: A001
    app,
    list_scenario_tests,
    name="list",
    progress="Listing scenario tests...",
    output_flag=True,
    saved_noun="Scenario tests list information",
    examples=LIST_EXAMPLES,
)

get = cli.command(
    app,
    run_get_scenario_test,
    name="get",
    handles_own_output=True,
    examples=GET_EXAMPLES,
)

metadata = cli.command(
    app,
    run_get_scenario_metadata,
    name="metadata",
    handles_own_output=True,
    examples=METADATA_EXAMPLES,
)

create = cli.command(
    app,
    run_create_scenario_test,
    name="create",
    handles_own_output=True,
)

update = cli.command(
    app,
    run_update_scenario_test,
    name="update",
    handles_own_output=True,
    examples=UPDATE_EXAMPLES,
)

delete = cli.command(
    app,
    delete_scenario_test,
    name="delete",
    progress="Deleting scenario test...",
    delete_confirm=cli.DeleteConfirmation(
        confirm=(
            "Are you sure you want to delete scenario test "
            "[magenta]{scenario_test_id}[/magenta] from application "
            "[magenta]{app_id}[/magenta]? This action cannot be undone."
        ),
        decline="Scenario test [magenta]{scenario_test_id}[/magenta] will not be deleted.",
        succeeded=(
            "Scenario test [magenta]{scenario_test_id}[/magenta] deleted successfully "
            "from application [magenta]{app_id}[/magenta]."
        ),
    ),
    examples=DELETE_EXAMPLES,
)
