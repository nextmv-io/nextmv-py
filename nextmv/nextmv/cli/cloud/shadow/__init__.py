"""Cloud shadow command tree for the Nextmv CLI.

``list``, ``start``, and ``delete`` wrap the thin actions in
``nextmv.cli.actions.shadow``. ``get``, ``metadata``, ``create``,
``update``, and ``stop`` route through ``_workflows.py`` because they
handle JSON comparisons parsing, SDK start/termination dataclass
construction, ``--output`` file saves, a separate metadata retrieval
path, and the ``--intent`` enum for the stop flow.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.shadow import (
    delete_shadow_test,
    list_shadow_tests,
    start_shadow_test,
)
from nextmv.cli.cloud.shadow._workflows import (
    run_create_shadow_test,
    run_get_shadow_metadata,
    run_get_shadow_test,
    run_stop_shadow_test,
    run_update_shadow_test,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud shadow tests.
    """
    pass


LIST_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "List all shadow tests for application [magenta]hare-app[/magenta].",
        "nextmv cloud shadow list --app-id hare-app",
    ),
    (
        "List all shadow tests and save to a file.",
        "nextmv cloud shadow list --app-id hare-app --output tests.json",
    ),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the shadow test with ID [magenta]carrot-optimization[/magenta] "
        "from application [magenta]hare-app[/magenta].",
        "nextmv cloud shadow get --app-id hare-app --shadow-test-id carrot-optimization",
    ),
    (
        "Get a shadow test and save the results to a file.",
        "nextmv cloud shadow get --app-id hare-app \\\n"
        "    --shadow-test-id lettuce-routes --output results.json",
    ),
)

METADATA_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get metadata for a shadow test.",
        "nextmv cloud shadow metadata --app-id hare-app --shadow-test-id bunny-warren",
    ),
    (
        "Get metadata and save it to a file.",
        "nextmv cloud shadow metadata --app-id hare-app \\\n"
        "    --shadow-test-id bunny-warren --output metadata.json",
    ),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Update the name of a shadow test.",
        "nextmv cloud shadow update --app-id hare-app \\\n"
        '    --shadow-test-id carrot-feast --name "Spring Carrot Harvest"',
    ),
    (
        "Update both name and description and save the result.",
        "nextmv cloud shadow update --app-id hare-app --shadow-test-id lettuce-delivery \\\n"
        '    --name "Warren Lettuce Express" --description "Fast lettuce delivery" \\\n'
        "    --output updated-shadow-test.json",
    ),
)

START_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Start the shadow test with ID [magenta]hop-analysis[/magenta].",
        "nextmv cloud shadow start --app-id hare-app --shadow-test-id hop-analysis",
    ),
)

STOP_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Stop a running shadow test and mark it as canceled.",
        "nextmv cloud shadow stop --app-id hare-app --shadow-test-id hop-analysis --intent cancel",
    ),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Delete a shadow test.",
        "nextmv cloud shadow delete --app-id hare-app --shadow-test-id hop-analysis",
    ),
    (
        "Delete without the confirmation prompt.",
        "nextmv cloud shadow delete --app-id hare-app --shadow-test-id carrot-routes --yes",
    ),
)


list = cli.command(  # noqa: A001
    app,
    list_shadow_tests,
    name="list",
    progress="Listing shadow tests...",
    output_flag=True,
    saved_noun="Shadow tests list",
    examples=LIST_EXAMPLES,
)

get = cli.command(
    app,
    run_get_shadow_test,
    name="get",
    handles_own_output=True,
    examples=GET_EXAMPLES,
)

metadata = cli.command(
    app,
    run_get_shadow_metadata,
    name="metadata",
    handles_own_output=True,
    examples=METADATA_EXAMPLES,
)

create = cli.command(
    app,
    run_create_shadow_test,
    name="create",
    handles_own_output=True,
)

update = cli.command(
    app,
    run_update_shadow_test,
    name="update",
    handles_own_output=True,
    examples=UPDATE_EXAMPLES,
)

start = cli.command(
    app,
    start_shadow_test,
    name="start",
    progress="Starting shadow test...",
    on_success=(
        "Shadow test [magenta]{shadow_test_id}[/magenta] started successfully "
        "in application [magenta]{app_id}[/magenta]."
    ),
    examples=START_EXAMPLES,
)

stop = cli.command(
    app,
    run_stop_shadow_test,
    name="stop",
    handles_own_output=True,
    examples=STOP_EXAMPLES,
)

delete = cli.command(
    app,
    delete_shadow_test,
    name="delete",
    progress="Deleting shadow test...",
    delete_confirm=cli.DeleteConfirmation(
        confirm=(
            "Are you sure you want to delete shadow test "
            "[magenta]{shadow_test_id}[/magenta] from application "
            "[magenta]{app_id}[/magenta]? This action cannot be undone."
        ),
        decline="Shadow test [magenta]{shadow_test_id}[/magenta] will not be deleted.",
        succeeded=(
            "Shadow test [magenta]{shadow_test_id}[/magenta] deleted successfully "
            "from application [magenta]{app_id}[/magenta]."
        ),
    ),
    examples=DELETE_EXAMPLES,
)
