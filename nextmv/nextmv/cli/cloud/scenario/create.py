"""
This module defines the cloud scenario create command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import error, in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.scenario import Scenario
from nextmv.polling import default_polling_options

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    app_id: AppIDOption,
    # Options for scenario test configuration.
    scenarios: Annotated[
        list[str],
        typer.Option(
            "--scenarios",
            "-s",
            help="Scenarios to use for the test. Data should be valid [magenta]json[/magenta]. "
            "Pass multiple scenarios by repeating the flag, or providing a list of objects. "
            "See command help for details on scenario formatting.",
            metavar="SCENARIOS",
            rich_help_panel="Scenario test configuration",
        ),
    ],
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Description of the scenario test.",
            metavar="DESCRIPTION",
            rich_help_panel="Scenario test configuration",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Name of the scenario test. If not provided, the ID will be used as the name.",
            metavar="NAME",
            rich_help_panel="Scenario test configuration",
        ),
    ] = None,
    repetitions: Annotated[
        int | None,
        typer.Option(
            "--repetitions",
            "-r",
            help="Number of times the scenario test is [italic]repeated[/italic]. "
            "0 repetitions = 1 execution, 1 repetition = 2 executions, etc.",
            metavar="REPETITIONS",
            rich_help_panel="Scenario test configuration",
        ),
    ] = 0,
    scenario_test_id: Annotated[
        str | None,
        typer.Option(
            "--scenario-test-id",
            "-i",
            help="ID for the scenario test. Will be generated if not provided.",
            envvar="NEXTMV_SCENARIO_TEST_ID",
            metavar="SCENARIO_TEST_ID",
            rich_help_panel="Scenario test configuration",
        ),
    ] = None,
    # Options for controlling output.
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Waits for the test to complete and saves the results to this location.",
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
            help="Wait for the scenario test to complete. Results are printed to [magenta]stdout[/magenta]. "
            "Specify output location with --output.",
            rich_help_panel="Output control",
        ),
    ] = False,
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Cloud scenario test.

    A scenario test allows you to run multiple scenarios with different inputs,
    instances/versions, and configurations in a single test.

    Use the --wait flag to wait for the scenario test to complete,
    polling for results. Using the --output flag will also
    activate waiting, and allows you to specify a destination file for the
    results.

    [bold][underline]Scenarios[/underline][/bold]

    Scenarios are provided as [magenta]json[/magenta] objects using the
    --scenarios flag. Each scenario defines the configuration for a scenario
    test execution.

    You can provide scenarios in three ways:
    - A single scenario as a [magenta]json[/magenta] object.
    - Multiple scenarios by repeating the --scenarios flag.
    - Multiple scenarios as a [magenta]json[/magenta] array in a single --scenarios flag.

    Each scenario must have the following fields:
    - [magenta]instance_id[/magenta]: ID of the instance to use for this scenario (required).
    - [magenta]scenario_input[/magenta]: Object containing the scenario input (required), with:
        - [magenta]scenario_input_type[/magenta]: Type of the scenario input (required).
        - [magenta]scenario_input_data[/magenta]: Data for the scenario input (required).
    - [magenta]scenario_id[/magenta]: ID of the scenario (optional). The
      default value will be set as [magenta]scenario-<index>[/magenta] if not set.
    - [magenta]configuration[/magenta]: An array of configuration objects
      (optional). Use this attribute to configure variation of options for the scenario. Each scenario
      configuration object requires:
        - [magenta]name[/magenta]: Name of the configuration option.
        - [magenta]values[/magenta]: List of values for the configuration option.

    Example object format:
    [dim]{
        "instance_id": "bunny-hopper-v2",
        "scenario_input": {
            "scenario_input_type": "input_set",
            "scenario_input_data": {
                "input_id": "meadow-input-a1",
                "input_set_id": "spring-gardens"
            }
        },
        "configuration": [
            {
                "name": "speed",
                "values": ["optimized", "balanced", "safe"]
            }
        ]
    }[/dim]

    [bold][underline]Examples[/underline][/bold]

    - Create a scenario test with a single scenario.
        $ [dim]SCENARIO='{
            "instance_id": "warren-planner-v1",
            "scenario_input": {
                "scenario_input_type": "input_set",
                "scenario_input_data": {
                    "input_id": "carrot-patch-a",
                    "input_set_id": "spring-gardens"
                }
            }
        }'
        nextmv cloud scenario create --app-id hare-app --name "Spring Meadow Routes" --scenarios "$SCENARIO"[/dim]

    - Create with multiple scenarios by repeating the flag.
        $ [dim]SCENARIO1='{
            "instance_id": "hop-optimizer",
            "scenario_input": {
                "scenario_input_type": "input_set",
                "scenario_input_data": {
                    "input_id": "lettuce-field-1",
                    "input_set_id": "veggie-gardens"
                }
            }
        }'
        SCENARIO2='{
            "instance_id": "hop-optimizer",
            "scenario_input": {
                "scenario_input_type": "input_set",
                "scenario_input_data": {
                    "input_id": "lettuce-field-2",
                    "input_set_id": "veggie-gardens"
                }
            }
        }'
        nextmv cloud scenario create --app-id hare-app --name "Lettuce Delivery Optimization" \\
            --scenarios "$SCENARIO1" --scenarios "$SCENARIO2"[/dim]

    - Create with multiple scenarios in a single [magenta]json[/magenta] array.
        $ [dim]SCENARIOS='[
            {
                "instance_id": "burrow-builder",
                "scenario_input": {
                    "scenario_input_type": "input_set",
                    "scenario_input_data": {
                        "input_id": "warren-zone-a",
                        "input_set_id": "burrow-sites"
                    }
                }
            },
            {
                "instance_id": "tunnel-planner-v3",
                "scenario_input": {
                    "scenario_input_type": "input_set",
                    "scenario_input_data": {
                        "input_id": "warren-zone-b",
                        "input_set_id": "burrow-sites"
                    }
                }
            }
        ]'
        nextmv cloud scenario create --app-id hare-app --name "Warren Construction Plans" \\
            --scenarios "$SCENARIOS"[/dim]

    - Create a scenario test and wait for it to complete.
        $ [dim]SCENARIO='{
            "instance_id": "foraging-route",
            "scenario_input": {
                "scenario_input_type": "input_set",
                "scenario_input_data": {
                    "input_id": "carrot-harvest",
                    "input_set_id": "harvest-season"
                }
            }
        }'
        nextmv cloud scenario create --app-id hare-app --name "Autumn Carrot Collection" --scenarios "$SCENARIO" \\
            --wait[/dim]

    - Create a scenario test and save the results to a file, waiting for completion.
        $ [dim]SCENARIO='{
            "instance_id": "safe-hopper",
            "scenario_input": {
                "scenario_input_type": "input_set",
                "scenario_input_data": {
                    "input_id": "predator-zones",
                    "input_set_id": "danger-zones"
                }
            }
        }'
        nextmv cloud scenario create --app-id hare-app --name "Fox Avoidance Routes" --scenarios "$SCENARIO" \\
            --output bunny-safety-results.json[/dim]

    - Create a scenario test with configuration options.
        $ [dim]SCENARIO='{
            "instance_id": "hop-optimizer",
            "scenario_input": {
                "scenario_input_type": "input_set",
                "scenario_input_data": {
                    "input_id": "garden-route-1",
                    "input_set_id": "garden-paths"
                }
            },
            "configuration": [
                {
                    "name": "speed",
                    "values": ["fast", "careful"]
                }
            ]
        }'
        nextmv cloud scenario create --app-id hare-app --name "Speed Analysis" --scenarios "$SCENARIO"[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)

    # Build the scenario list from the CLI options
    scenario_list = build_scenarios(scenarios)

    scenario_id = cloud_app.new_scenario_test(
        scenarios=scenario_list,
        id=scenario_test_id,
        name=name,
        description=description,
        repetitions=repetitions,
    )

    # If we don't need to poll at all we are done.
    if not wait and (output is None or output == ""):
        print_json({"scenario_test_id": scenario_id})

        return

    success(f"Scenario test [magenta]{scenario_id}[/magenta] created.")

    # Build the polling options.
    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    in_progress(msg="Getting scenario test results...")
    scenario_test = cloud_app.scenario_test_with_polling(
        scenario_test_id=scenario_id,
        polling_options=polling_options,
    )
    scenario_test_dict = scenario_test.to_dict()

    # Handle output
    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(scenario_test_dict, f, indent=2)

        success(msg=f"Scenario test output saved to [magenta]{output}[/magenta].")

        return

    print_json(scenario_test_dict)


def build_scenarios(scenarios: list[str]) -> list[Scenario]:
    """
    Build a list of Scenario objects from CLI JSON input.

    Parameters
    ----------
    scenarios : list[str]
        List of scenario JSON strings provided via the CLI. Each string can be
        a single scenario object or a list of scenario objects.

    Returns
    -------
    list[Scenario]
        The built list of Scenario objects.
    """

    scenario_list = []

    for scenario_str in scenarios:
        try:
            scenario_data = json.loads(scenario_str)

            # Handle the case where the value is a list of scenarios.
            if isinstance(scenario_data, list):
                scenario_list.extend(_process_scenario_list(scenario_data, scenario_str))

            # Handle the case where the value is a single scenario.
            elif isinstance(scenario_data, dict):
                scenario_list.append(_process_single_scenario(scenario_data, scenario_str))

            else:
                error(
                    f"Invalid scenario format: [magenta]{scenario_str}[/magenta]. "
                    "Expected [magenta]json[/magenta] object or array."
                )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            error(f"Invalid scenario format: [magenta]{scenario_str}[/magenta]. Error: {e}")

    return scenario_list


def _process_scenario_list(scenario_data: list, scenario_str: str) -> list[Scenario]:
    """
    Process a list of scenario dictionaries into Scenario objects.

    Parameters
    ----------
    scenario_data : list
        List of scenario dictionaries.
    scenario_str : str
        Original string for error messages.

    Returns
    -------
    list[Scenario]
        List of processed Scenario objects.
    """

    processed_scenarios = []
    for ix, item in enumerate(scenario_data):
        _validate_scenario_fields(item, scenario_str, ix)
        scenario = Scenario.from_dict(item)
        processed_scenarios.append(scenario)

    return processed_scenarios


def _process_single_scenario(scenario_data: dict, scenario_str: str) -> "Scenario":
    """
    Process a single scenario dictionary into a Scenario object.

    Parameters
    ----------
    scenario_data : dict
        Scenario dictionary.
    scenario_str : str
        Original string for error messages.

    Returns
    -------
    Scenario
        Processed Scenario object.
    """

    _validate_scenario_fields(scenario_data, scenario_str)

    return Scenario.from_dict(scenario_data)


def _validate_scenario_fields(scenario_data: dict, scenario_str: str, index: int | None = None) -> None:
    """
    Validate that required fields are present in a scenario dictionary.

    Parameters
    ----------
    scenario_data : dict
        Scenario dictionary to validate.
    scenario_str : str
        Original string for error messages.
    index : int | None
        Index in array if validating array element (for error reporting).
    """
    location = f"at index [magenta]{index}[/magenta] in " if index is not None else "in "

    if scenario_data.get("instance_id") is None:
        error(
            f"Invalid scenario format {location}"
            f"[magenta]{scenario_str}[/magenta]. Each scenario must have an "
            "[magenta]instance_id[/magenta] field."
        )

    scenario_input = scenario_data.get("scenario_input")
    if scenario_input is None:
        error(
            f"Invalid scenario format {location}"
            f"[magenta]{scenario_str}[/magenta]. Each scenario must have a "
            "[magenta]scenario_input[/magenta] field."
        )

    if scenario_input.get("scenario_input_type") is None:
        error(
            f"Invalid scenario format {location}"
            f"[magenta]{scenario_str}[/magenta]. Each [magenta]scenario_input[/magenta] must have a "
            "[magenta]scenario_input_type[/magenta] field."
        )

    if scenario_input.get("scenario_input_data") is None:
        error(
            f"Invalid scenario format {location}"
            f"[magenta]{scenario_str}[/magenta]. Each [magenta]scenario_input[/magenta] must have a "
            "[magenta]scenario_input_data[/magenta] field."
        )
