"""CLI-only workflows for the cloud batch domain.

Batch experiment commands support waiting for results (polling), saving
output to a file, parsing repeatable JSON run definitions plus a JSON
option sets dict, and a separate metadata retrieval path. These
concerns don't fit the framework's default ``emit()`` flow, so they
live in workflow functions that opt into ``handles_own_output=True``.
"""

import json
from pathlib import Path
from typing import Annotated

import typer

from nextmv.cli.actions.batch import (
    batch_metadata,
    create_batch,
    get_batch,
    update_batch,
)
from nextmv.cli.framework.options import AppIdRequiredOption, BatchExperimentIdOption
from nextmv.cli.message import error, in_progress, print_json, success
from nextmv.cloud import Application
from nextmv.cloud.batch_experiment import BatchExperimentRun
from nextmv.cloud.client import Client
from nextmv.polling import default_polling_options


def build_option_sets(option_sets: str | None) -> dict[str, dict[str, str]] | None:
    """Parse the CLI ``--option-sets`` JSON string into a dict.

    The value must be a JSON object whose keys are option set IDs and
    whose values are dicts of string key/value option pairs. Invalid
    payloads exit via ``error()``.
    """
    if option_sets is None:
        return None

    try:
        option_sets_data = json.loads(option_sets)
    except json.JSONDecodeError as e:
        error(f"Invalid option sets format: [magenta]{option_sets}[/magenta]. Error: {e}")
        return None

    if not isinstance(option_sets_data, dict):
        error(
            f"Invalid option sets format: [magenta]{option_sets}[/magenta]. "
            "Expected [magenta]json[/magenta] object."
        )

    for key, value in option_sets_data.items():
        if not isinstance(value, dict):
            error(
                f"Invalid option sets format: [magenta]{option_sets}[/magenta]. "
                f"Each option set must be a [magenta]json[/magenta] object. "
                f"Key [magenta]{key}[/magenta] has invalid value."
            )

    return option_sets_data


def build_runs(runs: list[str] | None) -> list[BatchExperimentRun] | None:
    """Parse a list of CLI ``--runs`` JSON strings into run dataclasses.

    Each string may be a single JSON object or a JSON array of
    objects. Required fields (``input_id`` plus one of
    ``instance_id`` / ``version_id``) are validated here so errors
    surface before the SDK call.
    """
    if runs is None:
        return None

    runs_list: list[BatchExperimentRun] = []

    for run_str in runs:
        try:
            run_data = json.loads(run_str)

            if isinstance(run_data, list):
                for ix, item in enumerate(run_data):
                    _validate_run_fields(item, run_str, ix)
                    runs_list.append(BatchExperimentRun(**item))
            elif isinstance(run_data, dict):
                _validate_run_fields(run_data, run_str)
                runs_list.append(BatchExperimentRun(**run_data))
            else:
                error(
                    f"Invalid run format: [magenta]{run_str}[/magenta]. "
                    "Expected [magenta]json[/magenta] object or array."
                )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            error(f"Invalid run format: [magenta]{run_str}[/magenta]. Error: {e}")

    return runs_list if runs_list else None


def _validate_run_fields(run_data: dict, run_str: str, index: int | None = None) -> None:
    """Validate that required fields are present in a run dict."""
    location = f"at index [magenta]{index}[/magenta] in " if index is not None else "in "

    if run_data.get("input_id") is None:
        error(
            f"Invalid run format {location}"
            f"[magenta]{run_str}[/magenta]. Each run must have an "
            "[magenta]input_id[/magenta] field."
        )

    if run_data.get("instance_id") is None and run_data.get("version_id") is None:
        error(
            f"Invalid run format {location}"
            f"[magenta]{run_str}[/magenta]. Each run must have either an "
            "[magenta]instance_id[/magenta] or [magenta]version_id[/magenta] field."
        )


def _save_or_print(data: dict | list, output: str | None, saved_noun: str) -> None:
    """Write ``data`` as JSON to ``output`` or print it to stdout."""
    if output is not None and output != "":
        Path(output).write_text(json.dumps(data, indent=2))
        success(f"{saved_noun} saved to [magenta]{output}[/magenta].")
        return
    print_json(data)


def run_get_batch(
    client: Client,
    app_id: AppIdRequiredOption,
    batch_experiment_id: BatchExperimentIdOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Waits for the batch experiment to complete and saves the results to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    timeout: Annotated[
        int,
        typer.Option(
            help="The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.",
            metavar="TIMEOUT_SECONDS",
        ),
    ] = -1,
    wait: Annotated[
        bool,
        typer.Option(
            "--wait",
            "-w",
            help=(
                "Wait for the batch experiment to complete. Results are printed to [magenta]stdout[/magenta]. "
                "Specify output location with --output."
            ),
        ),
    ] = False,
) -> None:
    """Get a Nextmv Cloud batch experiment, including its runs.

    Use the ``--wait`` flag to wait for the batch experiment to
    complete, polling for results. Using ``--output`` will also
    activate waiting, and allows you to specify a destination file for
    the results.
    """

    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    should_wait = wait or (output is not None and output != "")

    in_progress(msg="Getting batch experiment...")
    if should_wait:
        cloud_app = Application(client=client, id=app_id)
        batch_experiment_dict = cloud_app.batch_experiment_with_polling(
            batch_id=batch_experiment_id,
            polling_options=polling_options,
        ).to_dict()
    else:
        batch_experiment_dict = get_batch(
            client, app_id=app_id, batch_experiment_id=batch_experiment_id
        )

    _save_or_print(batch_experiment_dict, output, "Batch experiment results")


def run_get_batch_metadata(
    client: Client,
    app_id: AppIdRequiredOption,
    batch_experiment_id: BatchExperimentIdOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the batch experiment metadata to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Get metadata for a Nextmv Cloud batch experiment.

    Retrieves metadata only (status, run counts, timing) without the
    full per-run details. This is a faster alternative to the ``get``
    command when per-run results are not needed.
    """

    in_progress(msg="Getting batch experiment metadata...")
    batch_metadata_dict = batch_metadata(
        client, app_id=app_id, batch_experiment_id=batch_experiment_id
    )
    _save_or_print(batch_metadata_dict, output, "Batch experiment metadata")


_CREATE_HELP = """
Create a new Nextmv Cloud batch experiment.

A batch experiment executes multiple runs across different inputs and/or
configurations. Each run is defined by a combination of input,
instance or version, and optional configuration options.

Use the --wait flag to wait for the batch experiment to complete, polling
for results. Using the --output flag will also activate waiting, and
allows you to specify a destination file for the results.

[bold][underline]Runs[/underline][/bold]

Runs are provided as [magenta]json[/magenta] objects using the --runs flag.
Each run defines what input, instance/version, and configuration to use.

You can provide runs in three ways:

* A single run as a [magenta]json[/magenta] object.
* Multiple runs by repeating the --runs flag.
* Multiple runs as a [magenta]json[/magenta] array in a single --runs flag.

Each run must have [magenta]input_id[/magenta] and either
[magenta]instance_id[/magenta] or [magenta]version_id[/magenta]. Optional
fields include [magenta]option_set[/magenta], [magenta]input_set_id[/magenta],
[magenta]scenario_id[/magenta], and [magenta]repetition[/magenta].

[bold][underline]Option Sets[/underline][/bold]

Option sets are provided as a [magenta]json[/magenta] object using the
--option-sets flag. The keys are option set IDs and the values are
dictionaries of string key-value option pairs.
"""


def run_create_batch(
    client: Client,
    app_id: AppIdRequiredOption,
    batch_experiment_id: Annotated[
        str | None,
        typer.Option(
            "--batch-experiment-id",
            "-b",
            help="ID for the batch experiment. Will be generated if not provided.",
            envvar="NEXTMV_BATCH_EXPERIMENT_ID",
            metavar="BATCH_EXPERIMENT_ID",
            rich_help_panel="Batch experiment configuration",
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Description of the batch experiment.",
            metavar="DESCRIPTION",
            rich_help_panel="Batch experiment configuration",
        ),
    ] = None,
    input_set_id: Annotated[
        str | None,
        typer.Option(
            "--input-set-id",
            "-i",
            help="ID of the input set to use for the batch experiment.",
            metavar="INPUT_SET_ID",
            rich_help_panel="Batch experiment configuration",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Name of the batch experiment. If not provided, the ID will be used as the name.",
            metavar="NAME",
            rich_help_panel="Batch experiment configuration",
        ),
    ] = None,
    option_sets: Annotated[
        str | None,
        typer.Option(
            "--option-sets",
            help=(
                "Option sets to use for the batch experiment. Data should be valid "
                "[magenta]json[/magenta]. See command help for details on option sets formatting."
            ),
            metavar="OPTION_SETS",
            rich_help_panel="Batch experiment configuration",
        ),
    ] = None,
    runs: Annotated[
        list[str] | None,
        typer.Option(
            "--runs",
            "-r",
            help=(
                "Runs to execute for the batch experiment. Data should be valid "
                "[magenta]json[/magenta]. Pass multiple runs by repeating the flag, "
                "or providing a list of objects. See command help for details on run formatting."
            ),
            metavar="RUNS",
            rich_help_panel="Batch experiment configuration",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Waits for the experiment to complete and saves the results to this location.",
            metavar="OUTPUT_PATH",
            rich_help_panel="Output control",
        ),
    ] = None,
    timeout: Annotated[
        int,
        typer.Option(
            help="The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.",
            metavar="TIMEOUT_SECONDS",
            rich_help_panel="Output control",
        ),
    ] = -1,
    wait: Annotated[
        bool,
        typer.Option(
            "--wait",
            "-w",
            help=(
                "Wait for the batch experiment to complete. Results are printed to [magenta]stdout[/magenta]. "
                "Specify output location with --output."
            ),
            rich_help_panel="Output control",
        ),
    ] = False,
) -> None:
    # Full help text attached via __doc__ below because it contains
    # multi-line Rich formatting that doesn't play well with Typer's
    # docstring handling of f-string-style content.
    runs_list = build_runs(runs)
    option_sets_dict = build_option_sets(option_sets)

    # create_batch accepts the list of BatchExperimentRun dataclasses
    # directly — BatchExperimentRun inherits from dict-compatible types
    # or the SDK accepts dict | BatchExperimentRun — we pass the parsed
    # run objects through.
    batch_id = create_batch(
        client,
        app_id=app_id,
        input_set_id=input_set_id,
        name=name,
        description=description,
        option_sets=option_sets_dict,
        runs=runs_list,
    )

    if not wait and (output is None or output == ""):
        print_json({"batch_experiment_id": batch_id})
        return

    success(f"Batch experiment [magenta]{batch_id}[/magenta] created.")

    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    cloud_app = Application(client=client, id=app_id)
    in_progress(msg="Getting batch experiment results...")
    batch_experiment_dict = cloud_app.batch_experiment_with_polling(
        batch_id=batch_id,
        polling_options=polling_options,
    ).to_dict()

    _save_or_print(batch_experiment_dict, output, "Batch experiment results")


run_create_batch.__doc__ = _CREATE_HELP


def run_update_batch(
    client: Client,
    app_id: AppIdRequiredOption,
    batch_experiment_id: BatchExperimentIdOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Updated description of the batch experiment.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Updated name of the batch experiment.",
            metavar="NAME",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated batch experiment information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Update a Nextmv Cloud batch experiment.

    Update the name and/or description of a batch experiment. Any
    fields not specified will remain unchanged.
    """

    in_progress(msg="Updating batch experiment...")
    batch_experiment_dict = update_batch(
        client,
        app_id=app_id,
        batch_experiment_id=batch_experiment_id,
        name=name,
        description=description,
    )
    success(
        f"Batch experiment [magenta]{batch_experiment_id}[/magenta] updated successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
    _save_or_print(batch_experiment_dict, output, "Updated batch experiment information")
