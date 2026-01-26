"""
This module defines the cloud batch create command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import error, in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.batch_experiment import BatchExperimentRun
from nextmv.polling import default_polling_options

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    app_id: AppIDOption,
    # Options for batch experiment configuration.
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
            help="Option sets to use for the batch experiment. Data should be valid [magenta]json[/magenta]. "
            "See command help for details on option sets formatting.",
            metavar="OPTION_SETS",
            rich_help_panel="Batch experiment configuration",
        ),
    ] = None,
    runs: Annotated[
        list[str] | None,
        typer.Option(
            "--runs",
            "-r",
            help="Runs to execute for the batch experiment. Data should be valid [magenta]json[/magenta]. "
            "Pass multiple runs by repeating the flag, or providing a list of objects. "
            "See command help for details on run formatting.",
            metavar="RUNS",
            rich_help_panel="Batch experiment configuration",
        ),
    ] = None,
    # Options for controlling output.
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
            help="Wait for the batch experiment to complete. Results are printed to [magenta]stdout[/magenta]. "
            "Specify output location with --output.",
            rich_help_panel="Output control",
        ),
    ] = False,
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Cloud batch experiment.

    A batch experiment executes multiple runs across different inputs and/or
    configurations. Each run is defined by a combination of input, instance or
    version, and optional configuration options.

    Use the --wait flag to wait for the batch experiment to complete, polling
    for results. Using the --output flag will also activate waiting, and allows
    you to specify a destination file for the results.

    [bold][underline]Runs[/underline][/bold]

    Runs are provided as [magenta]json[/magenta] objects using the --runs flag.
    Each run defines what input, instance/version, and configuration to use.

    You can provide runs in three ways:
    - A single run as a [magenta]json[/magenta] object.
    - Multiple runs by repeating the --runs flag.
    - Multiple runs as a [magenta]json[/magenta] array in a single --runs flag.

    Each run must have the following fields:
    - [magenta]input_id[/magenta]: ID of the input to use for this run
      (required). If a managed input is used, this should be the ID of the
      managed input. If [magenta]input_set_id[/magenta] is provided for the run,
      this should be the ID of an input within that input set.
    - [magenta]instance_id[/magenta] OR [magenta]version_id[/magenta]: Either an instance ID or
      version ID must be provided (at least one required).
    - [magenta]option_set[/magenta]: ID of the option set to use (optional).
      Make sure to define the option sets using the --option-sets flag.
    - [magenta]input_set_id[/magenta]: ID of the input set (optional).
    - [magenta]scenario_id[/magenta]: Scenario ID if part of a scenario test (optional).
    - [magenta]repetition[/magenta]: Repetition number (optional).

    Object format:
    [dim]{
        "input_id": "meadow-input-a1",
        "instance_id": "bunny-hopper-v2",
        "option_set": "speed-optimized",
        "input_set_id": "spring-gardens"
    }[/dim]

    [bold][underline]Option Sets[/underline][/bold]

    Option sets are provided as a [magenta]json[/magenta] object using the
    --option-sets flag. Option sets define named collections of
    runtime options that can be referenced by runs.

    The option sets object is a dictionary where keys are option set IDs and
    values are dictionaries of string key-value pairs representing the options.

    Object format:
    [dim]{
        "speed-optimized": {"timeout": "30", "algorithm": "fast"},
        "quality-focused": {"timeout": "300", "algorithm": "thorough"}
    }[/dim]

    [bold][underline]Examples[/underline][/bold]

    - Create a batch experiment with a single run.
        $ [dim]RUN='{
            "input_id": "carrot-patch-a",
            "instance_id": "warren-planner-v1"
        }'
        nextmv cloud batch create --app-id hare-app --batch-experiment-id bunny-hop-test \\
            --name "Spring Meadow Routes" --input-set-id spring-gardens --runs "$RUN"[/dim]

    - Create with multiple runs by repeating the flag.
        $ [dim]RUN1='{
            "input_id": "lettuce-field-1",
            "instance_id": "hop-optimizer"
        }'
        RUN2='{
            "input_id": "lettuce-field-2",
            "instance_id": "hop-optimizer"
        }'
        nextmv cloud batch create --app-id hare-app --batch-experiment-id lettuce-routes \\
            --name "Lettuce Delivery Optimization" --input-set-id veggie-gardens \\
            --runs "$RUN1" --runs "$RUN2"[/dim]

    - Create with multiple runs in a single [magenta]json[/magenta] array.
        $ [dim]RUNS='[
            {
                "input_id": "warren-zone-a",
                "instance_id": "burrow-builder"
            },
            {
                "input_id": "warren-zone-b",
                "version_id": "tunnel-planner-v3"
            }
        ]'
        nextmv cloud batch create --app-id hare-app --batch-experiment-id warren-expansion \\
            --name "Warren Construction Plans" --input-set-id burrow-sites --runs "$RUNS"[/dim]

    - Create a batch experiment and wait for it to complete.
        $ [dim]RUN='{
            "input_id": "carrot-harvest",
            "instance_id": "foraging-route"
        }'
        nextmv cloud batch create --app-id hare-app --batch-experiment-id harvest-time \\
            --name "Autumn Carrot Collection" --input-set-id harvest-season \\
            --runs "$RUN" --wait[/dim]

    - Create a batch experiment and save the results to a file, waiting for completion.
        $ [dim]RUN='{
            "input_id": "predator-zones",
            "instance_id": "safe-hopper"
        }'
        nextmv cloud batch create --app-id hare-app --batch-experiment-id safety-analysis \\
            --name "Fox Avoidance Routes" --input-set-id danger-zones \\
            --runs "$RUN" --output bunny-safety-results.json[/dim]

    - Create a batch experiment with option sets.
        $ [dim]RUN1='{
            "input_id": "garden-route-1",
            "instance_id": "hop-optimizer",
            "option_set": "fast-hops"
        }'
        RUN2='{
            "input_id": "garden-route-1",
            "instance_id": "hop-optimizer",
            "option_set": "careful-hops"
        }'
        OPTION_SETS='{
            "fast-hops": {"max_speed": "10", "caution_level": "low"},
            "careful-hops": {"max_speed": "5", "caution_level": "high"}
        }'
        nextmv cloud batch create --app-id hare-app --batch-experiment-id hop-comparison \\
            --name "Speed vs Safety Analysis" --input-set-id garden-paths \\
            --runs "$RUN1" --runs "$RUN2" --option-sets "$OPTION_SETS"[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)

    # Build the runs list from the CLI options
    runs_list = build_runs(runs)

    # Build the option sets from the CLI options
    option_sets_dict = build_option_sets(option_sets)

    batch_id = cloud_app.new_batch_experiment(
        id=batch_experiment_id,
        name=name,
        runs=runs_list,
        description=description,
        input_set_id=input_set_id,
        option_sets=option_sets_dict,
    )

    # If we don't need to poll at all we are done.
    if not wait and (output is None or output == ""):
        print_json({"batch_experiment_id": batch_id})

        return

    success(f"Batch experiment [magenta]{batch_id}[/magenta] created.")

    # Build the polling options.
    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    in_progress(msg="Getting batch experiment results...")
    batch_experiment = cloud_app.batch_experiment_with_polling(
        batch_id=batch_id,
        polling_options=polling_options,
    )
    batch_experiment_dict = batch_experiment.to_dict()

    # Handle output
    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(batch_experiment_dict, f, indent=2)

        success(msg=f"Batch experiment results saved to [magenta]{output}[/magenta].")
        return

    print_json(batch_experiment_dict)


def build_option_sets(option_sets: str | None) -> dict[str, dict[str, str]] | None:
    """
    Builds the option sets dictionary from the CLI option.

    Parameters
    ----------
    option_sets : str | None
        Option sets JSON string provided via the CLI.

    Returns
    -------
    dict[str, dict[str, str]] | None
        The built option sets dictionary, or None if not provided.
    """
    if option_sets is None:
        return None

    try:
        option_sets_data = json.loads(option_sets)

        if not isinstance(option_sets_data, dict):
            error(
                f"Invalid option sets format: [magenta]{option_sets}[/magenta]. "
                "Expected [magenta]json[/magenta] object."
            )

        # Validate structure
        for key, value in option_sets_data.items():
            if not isinstance(value, dict):
                error(
                    f"Invalid option sets format: [magenta]{option_sets}[/magenta]. "
                    f"Each option set must be a [magenta]json[/magenta] object. "
                    f"Key [magenta]{key}[/magenta] has invalid value."
                )

        return option_sets_data

    except json.JSONDecodeError as e:
        error(f"Invalid option sets format: [magenta]{option_sets}[/magenta]. Error: {e}")


def build_runs(runs: list[str] | None) -> list[BatchExperimentRun] | None:
    """
    Builds the runs list from the CLI option(s).

    Parameters
    ----------
    runs : list[str] | None
        List of runs provided via the CLI.

    Returns
    -------
    list[BatchExperimentRun] | None
        The built runs list, or None if no runs provided.
    """
    if runs is None:
        return None

    runs_list = []

    for run_str in runs:
        try:
            run_data = json.loads(run_str)

            # Handle the case where the value is a list of runs.
            if isinstance(run_data, list):
                runs_list.extend(_process_run_list(run_data, run_str))

            # Handle the case where the value is a single run.
            elif isinstance(run_data, dict):
                runs_list.append(_process_single_run(run_data, run_str))

            else:
                error(
                    f"Invalid run format: [magenta]{run_str}[/magenta]. "
                    "Expected [magenta]json[/magenta] object or array."
                )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            error(f"Invalid run format: [magenta]{run_str}[/magenta]. Error: {e}")

    return runs_list if runs_list else None


def _process_run_list(run_data: list, run_str: str) -> list[BatchExperimentRun]:
    """
    Process a list of run objects.

    Parameters
    ----------
    run_data : list
        List of run dictionaries.
    run_str : str
        Original string for error messages.

    Returns
    -------
    list[BatchExperimentRun]
        List of processed runs.
    """
    processed_runs = []
    for ix, item in enumerate(run_data):
        _validate_run_fields(item, run_str, ix)
        run = BatchExperimentRun(**item)
        processed_runs.append(run)
    return processed_runs


def _process_single_run(run_data: dict, run_str: str) -> BatchExperimentRun:
    """
    Process a single run object.

    Parameters
    ----------
    run_data : dict
        Run dictionary.
    run_str : str
        Original string for error messages.

    Returns
    -------
    BatchExperimentRun
        Processed run.
    """
    _validate_run_fields(run_data, run_str)
    return BatchExperimentRun(**run_data)


def _validate_run_fields(run_data: dict, run_str: str, index: int | None = None) -> None:
    """
    Validate that required run fields are present.

    Parameters
    ----------
    run_data : dict
        Run dictionary to validate.
    run_str : str
        Original string for error messages.
    index : int | None
        Index in array if validating array element.
    """
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
