"""CLI-only workflows for the cloud scenario domain.

Scenario test commands support waiting for results (polling), saving
output to a file, parsing repeatable JSON scenario definitions, and a
separate metadata retrieval path. These concerns don't fit the
framework's default ``emit()`` flow, so they live in workflow functions
that opt into ``handles_own_output=True``.
"""

import json
from pathlib import Path
from typing import Annotated

import typer

from nextmv.cli.actions.scenario import (
    create_scenario_test,
    get_scenario_test,
    update_scenario_test,
)
from nextmv.cli.framework.options import AppIdRequiredOption, ScenarioTestIdOption
from nextmv.cli.message import error, in_progress, print_json, success
from nextmv.cloud import Application
from nextmv.cloud.client import Client
from nextmv.polling import default_polling_options


def build_scenario_dicts(scenarios: list[str]) -> list[dict]:
    """Parse CLI JSON strings into a list of scenario dicts.

    Each string may be a single JSON object or a JSON array. Required
    fields (``instance_id``, ``scenario_input`` with its inner
    ``scenario_input_type`` and ``scenario_input_data``) are validated
    here so errors surface before the SDK call.
    """

    scenario_list: list[dict] = []

    for scenario_str in scenarios:
        try:
            scenario_data = json.loads(scenario_str)

            if isinstance(scenario_data, list):
                for ix, item in enumerate(scenario_data):
                    _validate_scenario_fields(item, scenario_str, ix)
                    scenario_list.append(item)
            elif isinstance(scenario_data, dict):
                _validate_scenario_fields(scenario_data, scenario_str)
                scenario_list.append(scenario_data)
            else:
                error(
                    f"Invalid scenario format: [magenta]{scenario_str}[/magenta]. "
                    "Expected [magenta]json[/magenta] object or array."
                )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            error(f"Invalid scenario format: [magenta]{scenario_str}[/magenta]. Error: {e}")

    return scenario_list


def _validate_scenario_fields(
    scenario_data: dict,
    scenario_str: str,
    index: int | None = None,
) -> None:
    """Validate that required fields are present in a scenario dict."""
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


def _save_or_print(data: dict | list, output: str | None, saved_noun: str) -> None:
    """Write ``data`` as JSON to ``output`` or print it to stdout."""
    if output is not None and output != "":
        Path(output).write_text(json.dumps(data, indent=2))
        success(f"{saved_noun} saved to [magenta]{output}[/magenta].")
        return
    print_json(data)


def run_get_scenario_test(
    client: Client,
    app_id: AppIdRequiredOption,
    scenario_test_id: ScenarioTestIdOption,
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
            help=(
                "Wait for the scenario test to complete. Results are printed to [magenta]stdout[/magenta]. "
                "Specify output location with --output."
            ),
        ),
    ] = False,
) -> None:
    """Get a Nextmv Cloud scenario test, including its runs.

    Use the ``--wait`` flag to wait for the scenario test to complete,
    polling for results. Using ``--output`` will also activate waiting,
    and allows you to specify a destination file for the results.
    """

    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    should_wait = wait or (output is not None and output != "")

    in_progress(msg="Getting scenario test...")
    if should_wait:
        cloud_app = Application(client=client, id=app_id)
        scenario_test_dict = cloud_app.scenario_test_with_polling(
            scenario_test_id=scenario_test_id,
            polling_options=polling_options,
        ).to_dict()
    else:
        scenario_test_dict = get_scenario_test(
            client, app_id=app_id, scenario_test_id=scenario_test_id
        )

    _save_or_print(scenario_test_dict, output, "Scenario test results")


def run_get_scenario_metadata(
    client: Client,
    app_id: AppIdRequiredOption,
    scenario_test_id: ScenarioTestIdOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the scenario test metadata to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Get metadata for a Nextmv Cloud scenario test.

    Retrieves metadata only (status, creation date, and other high-level
    information) without the full per-run details. This is a faster
    alternative to the ``get`` command when full run details are not
    needed.
    """

    cloud_app = Application(client=client, id=app_id)
    in_progress(msg="Getting scenario test metadata...")
    scenario_metadata_dict = cloud_app.scenario_test_metadata(
        scenario_test_id=scenario_test_id,
    ).to_dict()
    _save_or_print(scenario_metadata_dict, output, "Scenario test metadata")


_CREATE_HELP = """
Create a new Nextmv Cloud scenario test.

A scenario test runs multiple scenarios with different inputs,
instances/versions, and configurations in a single test.

Use the --wait flag to wait for the scenario test to complete, polling
for results. Using the --output flag will also activate waiting, and
allows you to specify a destination file for the results.

Scenarios are provided as [magenta]json[/magenta] objects using the --scenarios flag.
Each scenario defines the configuration for a scenario test execution.

You can provide scenarios in three ways:

* A single scenario as a [magenta]json[/magenta] object.
* Multiple scenarios by repeating the --scenarios flag.
* Multiple scenarios as a [magenta]json[/magenta] array in a single --scenarios flag.

Each scenario must have an [magenta]instance_id[/magenta] and a
[magenta]scenario_input[/magenta] object with
[magenta]scenario_input_type[/magenta] and
[magenta]scenario_input_data[/magenta] fields. An optional
[magenta]scenario_id[/magenta] and [magenta]configuration[/magenta] list
can also be provided.
"""


def run_create_scenario_test(
    client: Client,
    app_id: AppIdRequiredOption,
    scenarios: Annotated[
        list[str],
        typer.Option(
            "--scenarios",
            "-s",
            help=(
                "Scenarios to use for the test. Data should be valid [magenta]json[/magenta]. "
                "Pass multiple scenarios by repeating the flag, or providing a list of objects. "
                "See command help for details on scenario formatting."
            ),
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
        int,
        typer.Option(
            "--repetitions",
            "-r",
            help=(
                "Number of times the scenario test is [italic]repeated[/italic]. "
                "0 repetitions = 1 execution, 1 repetition = 2 executions, etc."
            ),
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
            help=(
                "Wait for the scenario test to complete. Results are printed to [magenta]stdout[/magenta]. "
                "Specify output location with --output."
            ),
            rich_help_panel="Output control",
        ),
    ] = False,
) -> None:
    # Full help text attached via __doc__ below because it contains
    # multi-line Rich formatting that doesn't play well with Typer's
    # docstring handling of f-string-style content.
    scenario_dicts = build_scenario_dicts(scenarios)

    scenario_id = create_scenario_test(
        client,
        app_id=app_id,
        scenarios=scenario_dicts,
        scenario_test_id=scenario_test_id,
        name=name,
        description=description,
        repetitions=repetitions,
    )

    if not wait and (output is None or output == ""):
        print_json({"scenario_test_id": scenario_id})
        return

    success(f"Scenario test [magenta]{scenario_id}[/magenta] created.")

    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    cloud_app = Application(client=client, id=app_id)
    in_progress(msg="Getting scenario test results...")
    scenario_test_dict = cloud_app.scenario_test_with_polling(
        scenario_test_id=scenario_id,
        polling_options=polling_options,
    ).to_dict()

    _save_or_print(scenario_test_dict, output, "Scenario test results")


run_create_scenario_test.__doc__ = _CREATE_HELP


def run_update_scenario_test(
    client: Client,
    app_id: AppIdRequiredOption,
    scenario_test_id: ScenarioTestIdOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Updated description of the scenario test.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Updated name of the scenario test.",
            metavar="NAME",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated scenario test information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Update a Nextmv Cloud scenario test.

    Update the name and/or description of a scenario test. Any fields
    not specified will remain unchanged.
    """

    in_progress(msg="Updating scenario test...")
    scenario_info_dict = update_scenario_test(
        client,
        app_id=app_id,
        scenario_test_id=scenario_test_id,
        name=name,
        description=description,
    )
    success(
        f"Scenario test [magenta]{scenario_test_id}[/magenta] updated successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
    _save_or_print(scenario_info_dict, output, "Updated scenario test information")
