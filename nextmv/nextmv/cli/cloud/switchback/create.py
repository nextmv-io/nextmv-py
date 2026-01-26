"""
This module defines the cloud switchback create command for the Nextmv CLI.
"""

from datetime import datetime
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.switchback import TestComparisonSingle

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    app_id: AppIDOption,
    baseline_instance_id: Annotated[
        str,
        typer.Option(
            "--baseline-instance-id",
            "-b",
            help="ID of the baseline instance for the switchback test.",
            metavar="BASELINE_INSTANCE_ID",
        ),
    ],
    candidate_instance_id: Annotated[
        str,
        typer.Option(
            "--candidate-instance-id",
            "-c",
            help="ID of the candidate instance for the switchback test.",
            metavar="CANDIDATE_INSTANCE_ID",
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
        ),
    ],
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Description of the switchback test.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Name of the switchback test. If not provided, the ID will be used as the name.",
            metavar="NAME",
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
        ),
    ] = None,
    start: Annotated[
        datetime | None,
        typer.Option(
            "--start",
            "-r",
            formats=["%Y-%m-%dT%H:%M:%S%z"],
            help="Scheduled time for switchback test start in [magenta]RFC 3339[/magenta] format. "
            "Object format: [dim]'2024-01-01T00:00:00Z'[/dim]",
            metavar="START",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Cloud switchback test in draft mode.

    The test will alternate between the --baseline-instance-id and
    --candidate-instance-id over specified time intervals.

    You may specify the --start option to make the switchback test start at a
    specific time. Alternatively, you may use the [code]nextmv cloud switchback
    start[/code] command to start the test.

    Use the [code]nextmv cloud switchback stop[/code] command to stop the test.

    [bold][underline]Examples[/underline][/bold]

    - Create a switchback test alternating between two bunny instances.
        $ [dim]nextmv cloud switchback create --app-id hare-app --switchback-test-id bunny-switch-hop \\
            --name "Bunny Switch Hop" --baseline-instance-id fluffy-bunny-baseline \\
            --candidate-instance-id speedy-cottontail --unit-duration-minutes 15 --units 10[/dim]

    - Create a switchback test with a scheduled start time.
        $ [dim]nextmv cloud switchback create --app-id hare-app --switchback-test-id sunrise-switch \\
            --name "Sunrise Switch Test" --baseline-instance-id wise-old-rabbit \\
            --candidate-instance-id burrow-master --unit-duration-minutes 30 --units 8 \\
            --start '2026-01-23T10:00:00Z'[/dim]

    - Create a switchback test with a description.
        $ [dim]nextmv cloud switchback create --app-id hare-app --switchback-test-id carrot-switch \\
            --name "Carrot Switch" --baseline-instance-id fluffy-bunny-baseline \\
            --candidate-instance-id hopping-candidate-ears --unit-duration-minutes 20 --units 12 \\
            --description "Which bunny hops best for carrots?"[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)

    in_progress(msg="Creating switchback test in draft mode...")
    switchback_test = cloud_app.new_switchback_test(
        comparison=TestComparisonSingle(
            baseline_instance_id=baseline_instance_id,
            candidate_instance_id=candidate_instance_id,
        ),
        unit_duration_minutes=unit_duration_minutes,
        units=units,
        switchback_test_id=switchback_test_id,
        name=name,
        description=description,
        start=start,
    )

    print_json(switchback_test.to_dict())
