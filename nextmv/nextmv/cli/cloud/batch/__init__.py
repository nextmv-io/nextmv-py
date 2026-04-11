"""Cloud batch command tree for the Nextmv CLI.

``list`` and ``delete`` wrap the thin actions in
``nextmv.cli.actions.batch``. ``get``, ``metadata``, ``create``, and
``update`` route through ``_workflows.py`` because they handle polling,
JSON parsing of runs/option sets, ``--output`` file saves, and a
separate metadata retrieval path.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.batch import (
    delete_batch,
    list_batches,
)
from nextmv.cli.cloud.batch._workflows import (
    run_create_batch,
    run_get_batch,
    run_get_batch_metadata,
    run_update_batch,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud batch experiments.
    """
    pass


LIST_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "List all batch experiments for application [magenta]hare-app[/magenta].",
        "nextmv cloud batch list --app-id hare-app",
    ),
    (
        "List all batch experiments and save to a file.",
        "nextmv cloud batch list --app-id hare-app --output experiments.json",
    ),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the batch experiment with ID [magenta]carrot-optimization[/magenta] "
        "from application [magenta]hare-app[/magenta].",
        "nextmv cloud batch get --app-id hare-app --batch-experiment-id carrot-optimization",
    ),
    (
        "Get a batch experiment and wait for it to complete.",
        "nextmv cloud batch get --app-id hare-app --batch-experiment-id bunny-hop-test --wait",
    ),
    (
        "Get a batch experiment and save the results to a file.",
        "nextmv cloud batch get --app-id hare-app --batch-experiment-id warren-planning \\\n"
        "    --output results.json",
    ),
)

METADATA_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get metadata for a batch experiment.",
        "nextmv cloud batch metadata --app-id hare-app --batch-experiment-id carrot-optimization",
    ),
    (
        "Get metadata and save it to a file.",
        "nextmv cloud batch metadata --app-id hare-app \\\n"
        "    --batch-experiment-id carrot-optimization --output metadata.json",
    ),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Update the name of a batch experiment.",
        "nextmv cloud batch update --app-id hare-app \\\n"
        '    --batch-experiment-id carrot-feast --name "Spring Carrot Harvest"',
    ),
    (
        "Update both name and description and save the result.",
        "nextmv cloud batch update --app-id hare-app --batch-experiment-id lettuce-delivery \\\n"
        '    --name "Warren Lettuce Express" --description "Fast lettuce delivery" \\\n'
        "    --output updated-batch.json",
    ),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Delete a batch experiment.",
        "nextmv cloud batch delete --app-id hare-app --batch-experiment-id hop-analysis",
    ),
    (
        "Delete without the confirmation prompt.",
        "nextmv cloud batch delete --app-id hare-app --batch-experiment-id carrot-routes --yes",
    ),
)


list = cli.command(  # noqa: A001
    app,
    list_batches,
    name="list",
    progress="Listing batch experiments...",
    output_flag=True,
    saved_noun="Batch experiments list",
    examples=LIST_EXAMPLES,
)

get = cli.command(
    app,
    run_get_batch,
    name="get",
    handles_own_output=True,
    examples=GET_EXAMPLES,
)

metadata = cli.command(
    app,
    run_get_batch_metadata,
    name="metadata",
    handles_own_output=True,
    examples=METADATA_EXAMPLES,
)

create = cli.command(
    app,
    run_create_batch,
    name="create",
    handles_own_output=True,
)

update = cli.command(
    app,
    run_update_batch,
    name="update",
    handles_own_output=True,
    examples=UPDATE_EXAMPLES,
)

delete = cli.command(
    app,
    delete_batch,
    name="delete",
    progress="Deleting batch experiment...",
    delete_confirm=cli.DeleteConfirmation(
        confirm=(
            "Are you sure you want to delete batch experiment "
            "[magenta]{batch_experiment_id}[/magenta] from application "
            "[magenta]{app_id}[/magenta]? This action cannot be undone."
        ),
        decline="Batch experiment [magenta]{batch_experiment_id}[/magenta] will not be deleted.",
        succeeded=(
            "Batch experiment [magenta]{batch_experiment_id}[/magenta] deleted successfully "
            "from application [magenta]{app_id}[/magenta]."
        ),
    ),
    examples=DELETE_EXAMPLES,
)
