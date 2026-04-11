"""CLI-only workflows for the cloud shadow domain.

Shadow test commands save output to a file, parse JSON comparison
definitions, construct SDK start/termination event dataclasses from
plain values, and include a separate metadata retrieval path. These
concerns don't fit the framework's default ``emit()`` flow, so they
live in workflow functions that opt into ``handles_own_output=True``.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer

from nextmv.cli.actions.shadow import (
    create_shadow_test,
    get_shadow_test,
    shadow_test_metadata,
    stop_shadow_test,
    update_shadow_test,
)
from nextmv.cli.framework.options import AppIdRequiredOption, ShadowTestIdOption
from nextmv.cli.message import enum_values, error, in_progress, print_json, success
from nextmv.cloud.client import Client
from nextmv.cloud.shadow import StartEvents, StopIntent, TerminationEvents


def _save_or_print(data: dict | list, output: str | None, saved_noun: str) -> None:
    """Write ``data`` as JSON to ``output`` or print it to stdout."""
    if output is not None and output != "":
        Path(output).write_text(json.dumps(data, indent=2))
        success(f"{saved_noun} saved to [magenta]{output}[/magenta].")
        return
    print_json(data)


def run_get_shadow_test(
    client: Client,
    app_id: AppIdRequiredOption,
    shadow_test_id: ShadowTestIdOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the shadow test results to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Get a Nextmv Cloud shadow test, including its runs.

    Returns the full test dict. Use ``--output`` to save the results
    to a file instead of printing them to stdout.
    """

    in_progress(msg="Getting shadow test...")
    shadow_test_dict = get_shadow_test(
        client, app_id=app_id, shadow_test_id=shadow_test_id
    )
    _save_or_print(shadow_test_dict, output, "Shadow test output")


def run_get_shadow_metadata(
    client: Client,
    app_id: AppIdRequiredOption,
    shadow_test_id: ShadowTestIdOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the shadow test metadata to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Get metadata for a Nextmv Cloud shadow test.

    Retrieves metadata only (status, run counts, timing) without the
    full per-run details. This is a faster alternative to the ``get``
    command when per-run results are not needed.
    """

    in_progress(msg="Getting shadow test metadata...")
    shadow_metadata_dict = shadow_test_metadata(
        client, app_id=app_id, shadow_test_id=shadow_test_id
    )
    _save_or_print(shadow_metadata_dict, output, "Shadow test metadata")


_CREATE_HELP = """
Create a new Nextmv Cloud shadow test in draft mode.

Use the --comparisons option to define how to set up instance comparisons.
The value should be valid [magenta]json[/magenta]. The keys of the
comparisons object are the baseline instance IDs, and the values are the
candidate lists of instance IDs to compare against the respective baseline.

Here is an example comparisons object:
[dim]{
    "baseline-instance-1": ["candidate-instance-1", "candidate-instance-2"],
    "baseline-instance-2": ["candidate-instance-3"]
}[/dim]

You may specify the --start-time option to make the shadow test start at a
specific time. Alternatively, you may use the [code]nextmv cloud shadow
start[/code] command to start the test.

The --termination-maximum-runs option is required and provides control
over when the shadow test should terminate, after said number of runs.
Alternatively, you may specify the --termination-time option or use the
[code]nextmv cloud shadow stop[/code] command to stop the test.
"""


def run_create_shadow_test(
    client: Client,
    app_id: AppIdRequiredOption,
    comparisons: Annotated[
        str,
        typer.Option(
            "--comparisons",
            "-c",
            help=(
                "Object mapping baseline instance IDs to a list of comparison "
                "instance IDs. Data should be valid [magenta]json[/magenta]. "
                "Object format: [dim]{'baseline_id1': ['comparison_id1', 'comparison_id2']}[/dim]"
            ),
            metavar="COMPARISONS",
            rich_help_panel="Shadow test configuration",
        ),
    ],
    termination_maximum_runs: Annotated[
        int,
        typer.Option(
            "--termination-maximum-runs",
            "-m",
            help="Maximum number of runs for the shadow test termination condition.",
            metavar="TERMINATION_MAXIMUM_RUNS",
            min=1,
            max=300,
            rich_help_panel="Shadow test configuration",
        ),
    ],
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Description of the shadow test.",
            metavar="DESCRIPTION",
            rich_help_panel="Shadow test configuration",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Name of the shadow test. If not provided, the ID will be used as the name.",
            metavar="NAME",
            rich_help_panel="Shadow test configuration",
        ),
    ] = None,
    shadow_test_id: Annotated[
        str | None,
        typer.Option(
            "--shadow-test-id",
            "-s",
            help="ID for the shadow test. Will be generated if not provided.",
            envvar="NEXTMV_SHADOW_TEST_ID",
            metavar="SHADOW_TEST_ID",
            rich_help_panel="Shadow test configuration",
        ),
    ] = None,
    start_time: Annotated[
        datetime | None,
        typer.Option(
            "--start-time",
            "-r",
            formats=["%Y-%m-%dT%H:%M:%S%z"],
            help=(
                "Scheduled time for shadow test start in [magenta]RFC 3339[/magenta] format. "
                "Object format: [dim]'2024-01-01T00:00:00Z'[/dim]"
            ),
            metavar="START_TIME",
            rich_help_panel="Shadow test configuration",
        ),
    ] = None,
    termination_time: Annotated[
        datetime | None,
        typer.Option(
            "--termination-time",
            "-t",
            formats=["%Y-%m-%dT%H:%M:%S%z"],
            help=(
                "Scheduled time for shadow test end in [magenta]RFC 3339[/magenta] format. "
                "Object format: [dim]'2024-01-01T00:00:00Z'[/dim]"
            ),
            metavar="TERMINATION_TIME",
            rich_help_panel="Shadow test configuration",
        ),
    ] = None,
) -> None:
    # Full help text attached via __doc__ below because it contains
    # multi-line Rich formatting that doesn't play well with Typer's
    # docstring handling of f-string-style content.
    try:
        comparisons_dict = json.loads(comparisons)
    except json.JSONDecodeError as e:
        error(f"Invalid comparisons format: [magenta]{comparisons}[/magenta]. Error: {e}")
        return

    in_progress(msg="Creating shadow test in draft mode...")
    shadow_test_dict = create_shadow_test(
        client,
        app_id=app_id,
        comparisons=comparisons_dict,
        termination_events=TerminationEvents(
            maximum_runs=termination_maximum_runs,
            time=termination_time,
        ),
        shadow_test_id=shadow_test_id,
        name=name,
        description=description,
        start_events=StartEvents(time=start_time) if start_time is not None else None,
    )
    print_json(shadow_test_dict)


run_create_shadow_test.__doc__ = _CREATE_HELP


def run_update_shadow_test(
    client: Client,
    app_id: AppIdRequiredOption,
    shadow_test_id: ShadowTestIdOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Updated description of the shadow test.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Updated name of the shadow test.",
            metavar="NAME",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated shadow test information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Update a Nextmv Cloud shadow test.

    Update the name and/or description of a shadow test. Any fields
    not specified will remain unchanged.
    """

    in_progress(msg="Updating shadow test...")
    shadow_test_dict = update_shadow_test(
        client,
        app_id=app_id,
        shadow_test_id=shadow_test_id,
        name=name,
        description=description,
    )
    success(
        f"Shadow test [magenta]{shadow_test_id}[/magenta] updated successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
    _save_or_print(shadow_test_dict, output, "Updated shadow test information")


def run_stop_shadow_test(
    client: Client,
    app_id: AppIdRequiredOption,
    shadow_test_id: ShadowTestIdOption,
    intent: Annotated[
        StopIntent,
        typer.Option(
            "--intent",
            "-i",
            help=f"Intent for stopping the shadow test. Allowed values are: {enum_values(StopIntent)}.",
            metavar="INTENT",
        ),
    ],
) -> None:
    """Stop a running Nextmv Cloud shadow test.

    Before stopping a shadow test, it must be in a started state.
    Experiments in a [magenta]draft[/magenta] state, that haven't
    started, can be deleted with the [code]nextmv cloud shadow delete[/code]
    command.
    """

    in_progress(msg="Stopping shadow test...")
    stop_shadow_test(
        client, app_id=app_id, shadow_test_id=shadow_test_id, intent=intent.value
    )
    success(
        f"Shadow test [magenta]{shadow_test_id}[/magenta] stopped successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
