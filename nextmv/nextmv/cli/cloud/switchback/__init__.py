"""Cloud switchback command tree for the Nextmv CLI.

``list``, ``start``, and ``delete`` wrap the thin actions in
``nextmv.cli.actions.switchback``. ``get``, ``metadata``, ``create``,
``update``, and ``stop`` route through ``_workflows.py`` because they
handle ``--output`` file saves, inline comparison/duration flags that
compose into a single SDK create call, the separate metadata retrieval
path, and the ``--intent`` enum for the stop flow.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.switchback import (
    delete_switchback_test,
    list_switchback_tests,
    start_switchback_test,
)
from nextmv.cli.cloud.switchback._workflows import (
    run_create_switchback_test,
    run_get_switchback_metadata,
    run_get_switchback_test,
    run_stop_switchback_test,
    run_update_switchback_test,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud switchback tests.
    """
    pass


LIST_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "List all switchback tests for application [magenta]hare-app[/magenta].",
        "nextmv cloud switchback list --app-id hare-app",
    ),
    (
        "List all switchback tests and save to a file.",
        "nextmv cloud switchback list --app-id hare-app --output tests.json",
    ),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the switchback test with ID [magenta]carrot-optimization[/magenta] "
        "from application [magenta]hare-app[/magenta].",
        "nextmv cloud switchback get --app-id hare-app --switchback-test-id carrot-optimization",
    ),
    (
        "Get a switchback test and save the results to a file.",
        "nextmv cloud switchback get --app-id hare-app \\\n"
        "    --switchback-test-id lettuce-routes --output results.json",
    ),
)

METADATA_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get metadata for a switchback test.",
        "nextmv cloud switchback metadata --app-id hare-app --switchback-test-id bunny-warren",
    ),
    (
        "Get metadata and save it to a file.",
        "nextmv cloud switchback metadata --app-id hare-app \\\n"
        "    --switchback-test-id bunny-warren --output metadata.json",
    ),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Update the name of a switchback test.",
        "nextmv cloud switchback update --app-id hare-app \\\n"
        '    --switchback-test-id carrot-feast --name "Spring Carrot Harvest"',
    ),
    (
        "Update both name and description and save the result.",
        "nextmv cloud switchback update --app-id hare-app --switchback-test-id lettuce-delivery \\\n"
        '    --name "Warren Lettuce Express" --description "Fast lettuce delivery" \\\n'
        "    --output updated-switchback-test.json",
    ),
)

START_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Start the switchback test with ID [magenta]hop-analysis[/magenta].",
        "nextmv cloud switchback start --app-id hare-app --switchback-test-id hop-analysis",
    ),
)

STOP_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Stop a running switchback test and mark it as canceled.",
        "nextmv cloud switchback stop --app-id hare-app --switchback-test-id hop-analysis --intent cancel",
    ),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Delete a switchback test.",
        "nextmv cloud switchback delete --app-id hare-app --switchback-test-id hop-analysis",
    ),
    (
        "Delete without the confirmation prompt.",
        "nextmv cloud switchback delete --app-id hare-app --switchback-test-id carrot-routes --yes",
    ),
)


list = cli.command(  # noqa: A001
    app,
    list_switchback_tests,
    name="list",
    progress="Listing switchback tests...",
    output_flag=True,
    saved_noun="Switchback tests list",
    examples=LIST_EXAMPLES,
)

get = cli.command(
    app,
    run_get_switchback_test,
    name="get",
    handles_own_output=True,
    examples=GET_EXAMPLES,
)

metadata = cli.command(
    app,
    run_get_switchback_metadata,
    name="metadata",
    handles_own_output=True,
    examples=METADATA_EXAMPLES,
)

create = cli.command(
    app,
    run_create_switchback_test,
    name="create",
    handles_own_output=True,
)

update = cli.command(
    app,
    run_update_switchback_test,
    name="update",
    handles_own_output=True,
    examples=UPDATE_EXAMPLES,
)

start = cli.command(
    app,
    start_switchback_test,
    name="start",
    progress="Starting switchback test...",
    on_success=(
        "Switchback test [magenta]{switchback_test_id}[/magenta] started successfully "
        "in application [magenta]{app_id}[/magenta]."
    ),
    examples=START_EXAMPLES,
)

stop = cli.command(
    app,
    run_stop_switchback_test,
    name="stop",
    handles_own_output=True,
    examples=STOP_EXAMPLES,
)

delete = cli.command(
    app,
    delete_switchback_test,
    name="delete",
    progress="Deleting switchback test...",
    delete_confirm=cli.DeleteConfirmation(
        confirm=(
            "Are you sure you want to delete switchback test "
            "[magenta]{switchback_test_id}[/magenta] from application "
            "[magenta]{app_id}[/magenta]? This action cannot be undone."
        ),
        decline="Switchback test [magenta]{switchback_test_id}[/magenta] will not be deleted.",
        succeeded=(
            "Switchback test [magenta]{switchback_test_id}[/magenta] deleted successfully "
            "from application [magenta]{app_id}[/magenta]."
        ),
    ),
    examples=DELETE_EXAMPLES,
)
