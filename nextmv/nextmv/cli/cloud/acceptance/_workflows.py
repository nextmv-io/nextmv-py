"""CLI-only workflows for the cloud acceptance domain.

Acceptance test commands support waiting for results (polling), saving
output to a file, and passing complex metric definitions as repeatable
JSON flags. These concerns don't fit the framework's default
``emit()``/``on_success`` flow, so they live in workflow functions that
opt into ``handles_own_output=True``.
"""

import json
from pathlib import Path
from typing import Annotated

import typer

from nextmv.cli.actions.acceptance import (
    get_acceptance_test,
    update_acceptance_test,
)
from nextmv.cli.framework.options import AcceptanceTestIdOption, AppIdRequiredOption
from nextmv.cli.message import error, in_progress, print_json, success
from nextmv.cloud import Application
from nextmv.cloud.acceptance_test import Metric
from nextmv.cloud.client import Client
from nextmv.polling import default_polling_options


def build_metrics(metrics: list[str]) -> list[Metric]:
    """Parse a list of JSON strings into SDK ``Metric`` instances.

    Each input string may be a single JSON object or a JSON array. Each
    metric must have ``field``, ``metric_type``, ``params``, and
    ``statistic`` fields. Invalid inputs exit via ``error()``.
    """
    metrics_list: list[Metric] = []

    for metric_str in metrics:
        try:
            metric_data = json.loads(metric_str)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            error(f"Invalid metric format: [magenta]{metric_str}[/magenta]. Error: {e}")
            continue

        if isinstance(metric_data, list):
            for ix, item in enumerate(metric_data):
                if (
                    item.get("field") is None
                    or item.get("metric_type") is None
                    or item.get("params") is None
                    or item.get("statistic") is None
                ):
                    error(
                        f"Invalid metric format at index [magenta]{ix}[/magenta] in "
                        f"[magenta]{metric_str}[/magenta]. Each metric must have "
                        "[magenta]field[/magenta], [magenta]metric_type[/magenta], "
                        "[magenta]params[/magenta], and [magenta]statistic[/magenta] fields."
                    )
                metrics_list.append(Metric(**item))
        elif isinstance(metric_data, dict):
            if (
                metric_data.get("field") is None
                or metric_data.get("metric_type") is None
                or metric_data.get("params") is None
                or metric_data.get("statistic") is None
            ):
                error(
                    f"Invalid metric format in [magenta]{metric_str}[/magenta]. "
                    "Each metric must have [magenta]field[/magenta], [magenta]metric_type[/magenta], "
                    "[magenta]params[/magenta], and [magenta]statistic[/magenta] fields."
                )
            metrics_list.append(Metric(**metric_data))
        else:
            error(
                f"Invalid metric format: [magenta]{metric_str}[/magenta]. "
                "Expected [magenta]json[/magenta] object or array."
            )

    if not metrics_list:
        error(
            "No valid metrics were provided. Please specify at least one metric with "
            "[magenta]field[/magenta], [magenta]metric_type[/magenta], "
            "[magenta]params[/magenta], and [magenta]statistic[/magenta] fields."
        )

    return metrics_list


def _save_or_print(data: dict, output: str | None, saved_noun: str) -> None:
    """Write ``data`` as JSON to ``output`` or print it to stdout."""
    if output is not None and output != "":
        Path(output).write_text(json.dumps(data, indent=2))
        success(f"{saved_noun} saved to [magenta]{output}[/magenta].")
        return
    print_json(data)


def run_get_acceptance_test(
    client: Client,
    app_id: AppIdRequiredOption,
    acceptance_test_id: AcceptanceTestIdOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Waits for the acceptance test to complete and saves the results to this location.",
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
                "Wait for the acceptance test to complete. Results are printed to [magenta]stdout[/magenta]. "
                "Specify output location with --output."
            ),
        ),
    ] = False,
) -> None:
    """Get a Nextmv Cloud acceptance test.

    Use the ``--wait`` flag to wait for the acceptance test to complete,
    polling for results. Using ``--output`` will also activate waiting,
    and allows you to specify a destination file for the results.
    """

    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    should_wait = wait or (output is not None and output != "")

    in_progress(msg="Getting acceptance test...")
    if should_wait:
        cloud_app = Application(client=client, id=app_id)
        acceptance_test_dict = cloud_app.acceptance_test_with_polling(
            acceptance_test_id=acceptance_test_id,
            polling_options=polling_options,
        ).to_dict()
    else:
        acceptance_test_dict = get_acceptance_test(
            client, app_id=app_id, acceptance_test_id=acceptance_test_id
        )

    _save_or_print(acceptance_test_dict, output, "Acceptance test results")


_CREATE_HELP = """
Create a new Nextmv Cloud acceptance test.

The acceptance test is based on a batch experiment. If the batch experiment
with the same ID already exists, it will be reused. Otherwise, you must
provide the --input-set-id option to create a new batch experiment.

Use the --wait flag to wait for the acceptance test to complete, polling
for results. Using the --output flag will also activate waiting, and allows
you to specify a destination file for the results.

Metrics are provided as [magenta]json[/magenta] objects using the --metrics flag.
Each metric defines how to compare the candidate and baseline instances.

You can provide metrics in three ways:

* A single metric as a [magenta]json[/magenta] object.
* Multiple metrics by repeating the --metrics flag.
* Multiple metrics as a [magenta]json[/magenta] array in a single --metrics flag.

Each metric must have [magenta]field[/magenta], [magenta]metric_type[/magenta],
[magenta]params[/magenta], and [magenta]statistic[/magenta] fields.
"""


def run_create_acceptance_test(
    client: Client,
    app_id: AppIdRequiredOption,
    acceptance_test_id: Annotated[
        str,
        typer.Option(
            "--acceptance-test-id",
            "-t",
            help="ID for the acceptance test.",
            envvar="NEXTMV_ACCEPTANCE_TEST_ID",
            metavar="ACCEPTANCE_TEST_ID",
            rich_help_panel="Acceptance test configuration",
        ),
    ],
    baseline_instance_id: Annotated[
        str,
        typer.Option(
            "--baseline-instance-id",
            "-b",
            help="ID of the baseline instance to compare against.",
            metavar="BASELINE_INSTANCE_ID",
            rich_help_panel="Acceptance test configuration",
        ),
    ],
    candidate_instance_id: Annotated[
        str,
        typer.Option(
            "--candidate-instance-id",
            "-c",
            help="ID of the candidate instance to test.",
            metavar="CANDIDATE_INSTANCE_ID",
            rich_help_panel="Acceptance test configuration",
        ),
    ],
    metrics: Annotated[
        list[str],
        typer.Option(
            "--metrics",
            "-m",
            help=(
                "Metrics to use for the acceptance test. Data should be valid [magenta]json[/magenta]. "
                "Pass multiple metrics by repeating the flag, or providing a list of objects. "
                "See command help for details on metric formatting."
            ),
            metavar="METRICS",
            rich_help_panel="Acceptance test configuration",
        ),
    ],
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Description of the acceptance test.",
            metavar="DESCRIPTION",
            rich_help_panel="Acceptance test configuration",
        ),
    ] = None,
    input_set_id: Annotated[
        str | None,
        typer.Option(
            "--input-set-id",
            "-i",
            help=(
                "ID of the input set to use for the underlying batch experiment. "
                "Required if the batch experiment does not exist yet."
            ),
            metavar="INPUT_SET_ID",
            rich_help_panel="Acceptance test configuration",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Name of the acceptance test. If not provided, the ID will be used as the name.",
            metavar="NAME",
            rich_help_panel="Acceptance test configuration",
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
                "Wait for the acceptance test to complete. Results are printed to [magenta]stdout[/magenta]. "
                "Specify output location with --output."
            ),
            rich_help_panel="Output control",
        ),
    ] = False,
) -> None:
    # Full docstring is provided via the typer command help attribute so
    # it can include multi-line example blocks. Typer reads __doc__ or the
    # command-level help attribute; we use the latter below via cli.command
    # by setting help_extra=... No — we use this docstring below.
    cloud_app = Application(client=client, id=app_id)

    metrics_list = build_metrics(metrics)

    new_test = cloud_app.new_acceptance_test(
        candidate_instance_id=candidate_instance_id,
        baseline_instance_id=baseline_instance_id,
        id=acceptance_test_id,
        metrics=metrics_list,
        name=name,
        input_set_id=input_set_id,
        description=description,
    )
    acceptance_id = new_test.id

    if not wait and (output is None or output == ""):
        print_json({"acceptance_test_id": acceptance_id})
        return

    success(f"Acceptance test [magenta]{acceptance_id}[/magenta] created.")

    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    in_progress(msg="Getting acceptance test results...")
    acceptance_test_dict = cloud_app.acceptance_test_with_polling(
        acceptance_test_id=acceptance_id,
        polling_options=polling_options,
    ).to_dict()

    _save_or_print(acceptance_test_dict, output, "Acceptance test results")


run_create_acceptance_test.__doc__ = _CREATE_HELP


def run_update_acceptance_test(
    client: Client,
    app_id: AppIdRequiredOption,
    acceptance_test_id: AcceptanceTestIdOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Updated description of the acceptance test.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Updated name of the acceptance test.",
            metavar="NAME",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated acceptance test information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Update a Nextmv Cloud acceptance test.

    Update the name and/or description of an acceptance test. Any fields
    not specified will remain unchanged.
    """

    in_progress(msg="Updating acceptance test...")
    acceptance_test_dict = update_acceptance_test(
        client,
        app_id=app_id,
        acceptance_test_id=acceptance_test_id,
        name=name,
        description=description,
    )
    success(
        f"Acceptance test [magenta]{acceptance_test_id}[/magenta] updated successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
    _save_or_print(acceptance_test_dict, output, "Updated acceptance test information")
