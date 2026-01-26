"""
This module defines the cloud scenario get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption, ScenarioTestIDOption
from nextmv.polling import default_polling_options

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    app_id: AppIDOption,
    scenario_test_id: ScenarioTestIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Waits for the scenario test to complete and saves the results to this location.",
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
            help="Wait for the scenario test to complete. Results are printed to [magenta]stdout[/magenta]. "
            "Specify output location with --output.",
        ),
    ] = False,
    profile: ProfileOption = None,
) -> None:
    """
    Get a Nextmv Cloud scenario test, including its runs.

    Use the --wait flag to wait for the scenario test to
    complete, polling for results. Using the --output flag will
    also activate waiting, and allows you to specify a destination file for the
    results.

    [bold][underline]Examples[/underline][/bold]

    - Get the scenario test with ID [magenta]carrot-optimization[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud scenario get --app-id hare-app --scenario-test-id carrot-optimization[/dim]

    - Get the scenario test and wait for it to complete if necessary.
        $ [dim]nextmv cloud scenario get --app-id hare-app --scenario-test-id bunny-hop-test --wait[/dim]

    - Get the scenario test and save the results to a file.
        $ [dim]nextmv cloud scenario get --app-id hare-app --scenario-test-id warren-planning \\
            --output results.json[/dim]

    - Get the scenario test using a specific profile.
        $ [dim]nextmv cloud scenario get --app-id hare-app --scenario-test-id lettuce-routes --profile prod[/dim]
    """
    cloud_app = build_app(app_id=app_id, profile=profile)

    # Build the polling options.
    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    # Determine if we should wait
    should_wait = wait or (output is not None and output != "")

    in_progress(msg="Getting scenario test...")
    if should_wait:
        scenario_test = cloud_app.scenario_test_with_polling(
            scenario_test_id=scenario_test_id,
            polling_options=polling_options,
        )
    else:
        scenario_test = cloud_app.scenario_test(scenario_test_id=scenario_test_id)

    scenario_test_dict = scenario_test.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(scenario_test_dict, f, indent=2)

        success(msg=f"Scenario test results saved to [magenta]{output}[/magenta].")

        return

    print_json(scenario_test_dict)
