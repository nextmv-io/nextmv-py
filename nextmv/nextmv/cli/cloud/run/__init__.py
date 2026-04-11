"""Cloud run command tree for the Nextmv CLI.

Simple commands (``cancel``, ``delete``) wrap thin actions in
``nextmv.cli.actions.run`` via ``cli.command()``. Commands that need
content-format-aware output handling, polling, stdin input, or
complex configuration (``list``, ``metadata``, ``get``, ``input``,
``logs``, ``create``, ``track``) route through ``_workflows.py``
because they opt into ``handles_own_output=True``.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.run import cancel_run, delete_run
from nextmv.cli.cloud.run._workflows import (
    run_create_run,
    run_get_input,
    run_get_logs,
    run_get_run,
    run_list_runs,
    run_metadata_workflow,
    run_track_run,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud application runs.

    A run represents the execution of a decision model within a Nextmv Cloud
    application. Each run takes an input, processes it using the decision model,
    and produces an output.
    """
    pass


# ---------------------------------------------------------------------------
# Rich example blocks
# ---------------------------------------------------------------------------

CANCEL_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Cancel the run with ID [magenta]burrow-123[/magenta] belonging to an app with ID [magenta]hare-app[/magenta].",
        "nextmv cloud run cancel --app-id hare-app --run-id burrow-123",
    ),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Delete the run with ID [magenta]burrow-123[/magenta] belonging to an app with ID [magenta]hare-app[/magenta].",
        "nextmv cloud run delete --app-id hare-app --run-id burrow-123",
    ),
    (
        "Delete the run without confirmation prompt.",
        "nextmv cloud run delete --app-id hare-app --run-id burrow-123 --yes",
    ),
)

LIST_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the list of runs for an app with ID [magenta]hare-app[/magenta]. "
        "List is printed to [magenta]stdout[/magenta].",
        "nextmv cloud run list --app-id hare-app",
    ),
    (
        "Get the list of runs for an app and save to a [magenta]runs.json[/magenta] file.",
        "nextmv cloud run list --app-id hare-app --output runs.json",
    ),
    (
        "Get the list of [magenta]queued[/magenta] runs for an app.",
        "nextmv cloud run list --app-id hare-app --status queued",
    ),
)

METADATA_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the metadata of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID "
        "[magenta]hare-app[/magenta].",
        "nextmv cloud run metadata --app-id hare-app --run-id burrow-123",
    ),
    (
        "Get the metadata of a run and save it to a [magenta]metadata.json[/magenta] file.",
        "nextmv cloud run metadata --app-id hare-app --run-id burrow-123 --output metadata.json",
    ),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the results of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID "
        "[magenta]hare-app[/magenta].",
        "nextmv cloud run get --app-id hare-app --run-id burrow-123",
    ),
    (
        "Get the results of a run. Wait for the run to complete if necessary.",
        "nextmv cloud run get --app-id hare-app --run-id burrow-123 --wait",
    ),
    (
        "Get the results of a [magenta]json[/magenta] run. Save the results to a [magenta]results.json[/magenta] file.",
        "nextmv cloud run get --app-id hare-app --run-id burrow-123 --output results.json",
    ),
    (
        "Get the results of a [magenta]multi-file[/magenta] run. "
        "Save the results to the [magenta]results[/magenta] dir.",
        "nextmv cloud run get --app-id hare-app --run-id burrow-123 --output results",
    ),
)

INPUT_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the input of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID "
        "[magenta]hare-app[/magenta]. Input is printed to [magenta]stdout[/magenta].",
        "nextmv cloud run input --app-id hare-app --run-id burrow-123",
    ),
    (
        "Save the input to a [magenta]input.json[/magenta] file.",
        "nextmv cloud run input --app-id hare-app --run-id burrow-123 --output input.json",
    ),
)

LOGS_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the logs of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID "
        "[magenta]hare-app[/magenta]. Logs are printed to [magenta]stderr[/magenta].",
        "nextmv cloud run logs --app-id hare-app --run-id burrow-123",
    ),
    (
        "Tail the logs until the run completes.",
        "nextmv cloud run logs --app-id hare-app --run-id burrow-123 --tail",
    ),
    (
        "Save the logs to a [magenta]logs.log[/magenta] file.",
        "nextmv cloud run logs --app-id hare-app --run-id burrow-123 --output logs.log",
    ),
)

CREATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Read a [magenta]json[/magenta] input via [magenta]stdin[/magenta], and submit a run to an app with ID "
        "[magenta]hare-app[/magenta], using the [magenta]latest[/magenta] instance.",
        "cat input.json | nextmv cloud run create --app-id hare-app",
    ),
    (
        "Read a [magenta]json[/magenta] input from an [magenta]input.json[/magenta] file.",
        "nextmv cloud run create --app-id hare-app --input input.json",
    ),
    (
        "Read a [magenta]json[/magenta] input, wait for the run, and print the result to stdout.",
        "nextmv cloud run create --app-id hare-app --input input.json --wait",
    ),
    (
        "Submit a run and write the result to a file.",
        "nextmv cloud run create --app-id hare-app --input input.json --output output.json",
    ),
    (
        "Submit a run and tail the logs.",
        "nextmv cloud run create --app-id hare-app --input input.json --tail",
    ),
    (
        "Submit a [magenta]multi-file[/magenta] run from an [magenta]inputs[/magenta] directory.",
        "nextmv cloud run create --app-id hare-app --input inputs --instance-id default",
    ),
    (
        "Use a [magenta]Nextmv managed[/magenta] input by ID.",
        "nextmv cloud run create --app-id hare-app --managed-input-id carrot-input --output outputs",
    ),
)

TRACK_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Track a [magenta]successful[/magenta] [magenta]json[/magenta] run via [magenta]stdin[/magenta] input.",
        "cat input.json | nextmv cloud run track --app-id hare-app --status succeeded",
    ),
    (
        "Track a successful run from an [magenta]input.json[/magenta] file with output from an "
        "[magenta]output.json[/magenta] file.",
        "nextmv cloud run track --app-id hare-app --status succeeded --input input.json \\\n"
        "    --output output.json",
    ),
    (
        "Track a successful run including logs, assets, and metrics.",
        "nextmv cloud run track --app-id hare-app --status succeeded --input input.json \\\n"
        "    --output output.json --logs logs.log --assets assets.json --metrics metrics.json",
    ),
    (
        "Track a failed run with an error message.",
        "nextmv cloud run track --app-id hare-app --status failed --input input.json \\\n"
        '    --error-msg "Solver timed out"',
    ),
)


# ---------------------------------------------------------------------------
# Command registration
# ---------------------------------------------------------------------------

cancel = cli.command(
    app,
    cancel_run,
    name="cancel",
    progress="Canceling run...",
    on_success="Run [magenta]{run_id}[/magenta] canceled.",
    examples=CANCEL_EXAMPLES,
)

delete = cli.command(
    app,
    delete_run,
    name="delete",
    progress="Deleting run...",
    delete_confirm=cli.DeleteConfirmation(
        confirm=(
            "Are you sure you want to delete run [magenta]{run_id}[/magenta] from "
            "application [magenta]{app_id}[/magenta]? This action cannot be undone."
        ),
        decline=(
            "Run [magenta]{run_id}[/magenta] from application [magenta]{app_id}[/magenta] will not be deleted."
        ),
        succeeded=(
            "Run [magenta]{run_id}[/magenta] from application [magenta]{app_id}[/magenta] deleted successfully."
        ),
    ),
    examples=DELETE_EXAMPLES,
)

list = cli.command(  # noqa: A001
    app,
    run_list_runs,
    name="list",
    handles_own_output=True,
    examples=LIST_EXAMPLES,
)

metadata = cli.command(
    app,
    run_metadata_workflow,
    name="metadata",
    handles_own_output=True,
    examples=METADATA_EXAMPLES,
)

get = cli.command(
    app,
    run_get_run,
    name="get",
    handles_own_output=True,
    examples=GET_EXAMPLES,
)

input = cli.command(  # noqa: A001
    app,
    run_get_input,
    name="input",
    handles_own_output=True,
    examples=INPUT_EXAMPLES,
)

logs = cli.command(
    app,
    run_get_logs,
    name="logs",
    handles_own_output=True,
    examples=LOGS_EXAMPLES,
)

create = cli.command(
    app,
    run_create_run,
    name="create",
    handles_own_output=True,
    examples=CREATE_EXAMPLES,
)

track = cli.command(
    app,
    run_track_run,
    name="track",
    handles_own_output=True,
    examples=TRACK_EXAMPLES,
)
