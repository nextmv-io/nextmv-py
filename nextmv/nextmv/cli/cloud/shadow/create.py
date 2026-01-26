"""
This module defines the cloud shadow create command for the Nextmv CLI.
"""

import json
from datetime import datetime
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import error, in_progress, print_json
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.shadow import StartEvents, TerminationEvents

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    app_id: AppIDOption,
    comparisons: Annotated[
        str,
        typer.Option(
            "--comparisons",
            "-c",
            help="Object mapping baseline instance IDs to a list of comparison instance IDs. "
            "Data should be valid [magenta]json[/magenta]. "
            "Object format: [dim]{'baseline_id1': ['comparison_id1', 'comparison_id2'], 'baseline_id2': ...}[/dim]",
            metavar="COMPARISONS",
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
        ),
    ],
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Description of the shadow test.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Name of the shadow test. If not provided, the ID will be used as the name.",
            metavar="NAME",
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
        ),
    ] = None,
    start_time: Annotated[
        datetime | None,
        typer.Option(
            "--start-time",
            "-r",
            formats=["%Y-%m-%dT%H:%M:%S%z"],
            help="Scheduled time for shadow test start in [magenta]RFC 3339[/magenta] format. "
            "Object format: [dim]'2024-01-01T00:00:00Z'[/dim]",
            metavar="START_TIME",
        ),
    ] = None,
    termination_time: Annotated[
        datetime | None,
        typer.Option(
            "--termination-time",
            "-t",
            help="Scheduled time for shadow test end in [magenta]RFC 3339[/magenta] format. "
            "Object format: [dim]'2024-01-01T00:00:00Z'[/dim]",
            formats=["%Y-%m-%dT%H:%M:%S%z"],
            metavar="TERMINATION_TIME",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
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

    The --termination-maximum-runs option is required and provides control over
    when the shadow test should terminate, after said number of runs.
    Alternatively, you may specify the --termination-time option or use the
    [code]nextmv cloud shadow stop[/code] command to stop the test.

    [bold][underline]Examples[/underline][/bold]

    - Create a shadow test with a baseline and two candidate instances.
        $ [dim]COMPARISONS='{
            "fluffy-bunny-baseline": [
                "hopping-candidate-ears",
                "speedy-cottontail"
            ]
        }'
        nextmv cloud shadow create --app-id hare-app --shadow-test-id bunny-hop-shadow --name "Bunny Hop Showdown" \\
            --comparisons "$COMPARISONS" --termination-maximum-runs 100[/dim]

    - Create a shadow test with multiple baselines and candidates.
        $ [dim]COMPARISONS='{
            "fluffy-bunny-baseline": [
                "hopping-candidate-ears"
            ],
            "wise-old-rabbit": [
                "burrow-master"
            ]
        }'
        nextmv cloud shadow create --app-id hare-app --shadow-test-id warren-race --name "Warren Race Test" \\
            --comparisons "$COMPARISONS" --termination-maximum-runs 50[/dim]

    - Create a shadow test with a scheduled start and termination time.
        $ [dim]COMPARISONS='{
            "fluffy-bunny-baseline": [
                "hopping-candidate-ears"
            ]
        }'
        nextmv cloud shadow create --app-id hare-app --shadow-test-id sunrise-hop --name "Sunrise Hop Test" \\
            --comparisons "$COMPARISONS" --start-time '2026-01-23T10:00:00Z' \\
            --termination-time '2026-01-23T18:00:00Z' --termination-maximum-runs 20[/dim]

    - Create a shadow test with a description.
        $ [dim]COMPARISONS='{
            "fluffy-bunny-baseline": [
                "hopping-candidate-ears"
            ]
        }'
        nextmv cloud shadow create --app-id hare-app --shadow-test-id carrot-compare --name "Carrot Comparison" \\
            --description "Testing cool bunnies" --comparisons "$COMPARISONS" --termination-maximum-runs 10[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)

    try:
        comparisons_dict = json.loads(comparisons)
    except json.JSONDecodeError as e:
        error(f"Invalid comparisons format: [magenta]{comparisons}[/magenta]. Error: {e}")

    in_progress(msg="Creating shadow test in draft mode...")
    shadow_test = cloud_app.new_shadow_test(
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

    print_json(shadow_test.to_dict())
