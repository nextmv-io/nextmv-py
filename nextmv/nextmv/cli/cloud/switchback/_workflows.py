"""CLI-only workflows for the cloud switchback domain.

Switchback test commands save output to a file, take a handful of
comparison/duration flags that compose into a single SDK create call,
and include a separate metadata retrieval path. These concerns don't
fit the framework's default ``emit()`` flow, so they live in workflow
functions that opt into ``handles_own_output=True``.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer

from nextmv.cli.actions.switchback import (
    create_switchback_test,
    get_switchback_test,
    stop_switchback_test,
    switchback_test_metadata,
    update_switchback_test,
)
from nextmv.cli.framework.options import AppIdRequiredOption, SwitchbackTestIdOption
from nextmv.cli.message import enum_values, in_progress, print_json, success
from nextmv.cloud.client import Client
from nextmv.cloud.shadow import StopIntent


def _save_or_print(data: dict | list, output: str | None, saved_noun: str) -> None:
    """Write ``data`` as JSON to ``output`` or print it to stdout."""
    if output is not None and output != "":
        Path(output).write_text(json.dumps(data, indent=2))
        success(f"{saved_noun} saved to [magenta]{output}[/magenta].")
        return
    print_json(data)


def run_get_switchback_test(
    client: Client,
    app_id: AppIdRequiredOption,
    switchback_test_id: SwitchbackTestIdOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the switchback test results to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Get a Nextmv Cloud switchback test, including its runs.

    Returns the full test dict. Use ``--output`` to save the results
    to a file instead of printing them to stdout.
    """

    in_progress(msg="Getting switchback test...")
    switchback_test_dict = get_switchback_test(
        client, app_id=app_id, switchback_test_id=switchback_test_id
    )
    _save_or_print(switchback_test_dict, output, "Switchback test output")


def run_get_switchback_metadata(
    client: Client,
    app_id: AppIdRequiredOption,
    switchback_test_id: SwitchbackTestIdOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the switchback test metadata to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Get metadata for a Nextmv Cloud switchback test.

    Retrieves metadata only (status, unit counts, timing) without the
    full per-unit details. This is a faster alternative to the ``get``
    command when per-unit results are not needed.
    """

    in_progress(msg="Getting switchback test metadata...")
    switchback_metadata_dict = switchback_test_metadata(
        client, app_id=app_id, switchback_test_id=switchback_test_id
    )
    _save_or_print(switchback_metadata_dict, output, "Switchback test metadata")


def run_create_switchback_test(
    client: Client,
    app_id: AppIdRequiredOption,
    baseline_instance_id: Annotated[
        str,
        typer.Option(
            "--baseline-instance-id",
            "-b",
            help="ID of the baseline instance for the switchback test.",
            metavar="BASELINE_INSTANCE_ID",
            rich_help_panel="Switchback test configuration",
        ),
    ],
    candidate_instance_id: Annotated[
        str,
        typer.Option(
            "--candidate-instance-id",
            "-c",
            help="ID of the candidate instance for the switchback test.",
            metavar="CANDIDATE_INSTANCE_ID",
            rich_help_panel="Switchback test configuration",
        ),
    ],
    unit_duration_minutes: Annotated[
        float,
        typer.Option(
            "--unit-duration-minutes",
            "-u",
            help="Duration of each interval in minutes.",
            metavar="UNIT_DURATION_MINUTES",
            min=1,
            max=10080,
            rich_help_panel="Switchback test configuration",
        ),
    ],
    units: Annotated[
        int,
        typer.Option(
            "--units",
            "-t",
            help="Total number of intervals in the switchback test.",
            metavar="UNITS",
            min=1,
            max=1000,
            rich_help_panel="Switchback test configuration",
        ),
    ],
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Description of the switchback test.",
            metavar="DESCRIPTION",
            rich_help_panel="Switchback test configuration",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Name of the switchback test. If not provided, the ID will be used as the name.",
            metavar="NAME",
            rich_help_panel="Switchback test configuration",
        ),
    ] = None,
    switchback_test_id: Annotated[
        str | None,
        typer.Option(
            "--switchback-test-id",
            "-s",
            help="ID for the switchback test. Will be generated if not provided.",
            envvar="NEXTMV_SWITCHBACK_TEST_ID",
            metavar="SWITCHBACK_TEST_ID",
            rich_help_panel="Switchback test configuration",
        ),
    ] = None,
    start: Annotated[
        datetime | None,
        typer.Option(
            "--start",
            "-r",
            formats=["%Y-%m-%dT%H:%M:%S%z"],
            help=(
                "Scheduled time for switchback test start in [magenta]RFC 3339[/magenta] format. "
                "Object format: [dim]'2024-01-01T00:00:00Z'[/dim]"
            ),
            metavar="START",
            rich_help_panel="Switchback test configuration",
        ),
    ] = None,
) -> None:
    """Create a new Nextmv Cloud switchback test in draft mode.

    The test will alternate between the --baseline-instance-id and
    --candidate-instance-id over specified time intervals.

    You may specify the --start option to make the switchback test
    start at a specific time. Alternatively, you may use the
    [code]nextmv cloud switchback start[/code] command to start the
    test.

    Use the [code]nextmv cloud switchback stop[/code] command to stop
    the test.
    """

    in_progress(msg="Creating switchback test in draft mode...")
    switchback_test_dict = create_switchback_test(
        client,
        app_id=app_id,
        baseline_instance_id=baseline_instance_id,
        candidate_instance_id=candidate_instance_id,
        unit_duration_minutes=unit_duration_minutes,
        units=units,
        switchback_test_id=switchback_test_id,
        name=name,
        description=description,
        start=start,
    )
    print_json(switchback_test_dict)


def run_update_switchback_test(
    client: Client,
    app_id: AppIdRequiredOption,
    switchback_test_id: SwitchbackTestIdOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Updated description of the switchback test.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Updated name of the switchback test.",
            metavar="NAME",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated switchback test information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Update a Nextmv Cloud switchback test.

    Update the name and/or description of a switchback test. Any
    fields not specified will remain unchanged.
    """

    in_progress(msg="Updating switchback test...")
    switchback_test_dict = update_switchback_test(
        client,
        app_id=app_id,
        switchback_test_id=switchback_test_id,
        name=name,
        description=description,
    )
    success(
        f"Switchback test [magenta]{switchback_test_id}[/magenta] updated successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
    _save_or_print(switchback_test_dict, output, "Updated switchback test information")


def run_stop_switchback_test(
    client: Client,
    app_id: AppIdRequiredOption,
    switchback_test_id: SwitchbackTestIdOption,
    intent: Annotated[
        StopIntent,
        typer.Option(
            "--intent",
            "-i",
            help=f"Intent for stopping the switchback test. Allowed values are: {enum_values(StopIntent)}.",
            metavar="INTENT",
        ),
    ],
) -> None:
    """Stop a running Nextmv Cloud switchback test.

    Before stopping a switchback test, it must be in a started state.
    Experiments in a [magenta]draft[/magenta] state, that haven't
    started, can be deleted with the [code]nextmv cloud switchback delete[/code]
    command.
    """

    in_progress(msg="Stopping switchback test...")
    stop_switchback_test(
        client,
        app_id=app_id,
        switchback_test_id=switchback_test_id,
        intent=intent.value,
    )
    success(
        f"Switchback test [magenta]{switchback_test_id}[/magenta] stopped successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
