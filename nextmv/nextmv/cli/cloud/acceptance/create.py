"""
This module defines the cloud acceptance create command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import enum_values, error, in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.acceptance_test import Comparison, Metric, MetricToleranceType, MetricType, StatisticType
from nextmv.polling import default_polling_options

# Set up subcommand application.
app = typer.Typer()


@app.command(
    # AVOID USING THE HELP PARAMETER WITH TYPER COMMAND DECORATOR. For
    # consistency, commands should be documented using docstrings. We were
    # forced to use help here to work around f-string limitations in
    # docstrings.
    help=f"""
    Create a new Nextmv Cloud acceptance test.

    The acceptance test is based on a batch experiment. If the batch experiment
    with the same ID already exists, it will be reused. Otherwise, you must
    provide the --input-set-id option to create a new batch experiment.

    Use the --wait flag to wait for the acceptance test to complete, polling
    for results. Using the --output flag will also activate waiting, and allows
    you to specify a destination file for the results.

    [bold][underline]Metrics[/underline][/bold]

    Metrics are provided as [magenta]json[/magenta] objects using the
    --metrics flag. Each metric defines how to compare the
    candidate and baseline instances.

    You can provide metrics in three ways:
    - A single metric as a [magenta]json[/magenta] object.
    - Multiple metrics by repeating the --metrics flag.
    - Multiple metrics as a [magenta]json[/magenta] array in a single --metrics flag.

    Each metric must have the following fields:
    - [magenta]field[/magenta]: Field of the metric to measure (e.g., "solution.objective").
    - [magenta]metric_type[/magenta]: Type of metric comparison. Allowed values: {enum_values(MetricType)}.
    - [magenta]params[/magenta]: Parameters of the metric comparison.
        - [magenta]operator[/magenta]: Comparison operator. Allowed values: {enum_values(Comparison)}.
        - [magenta]tolerance[/magenta]: Tolerance for the comparison.
            - [magenta]type[/magenta]: Type of tolerance. Allowed values: {enum_values(MetricToleranceType)}.
            - [magenta]value[/magenta]: Tolerance value (numeric).
    - [magenta]statistic[/magenta]: Statistical method. Allowed values: {enum_values(StatisticType)}.

    Object format:
    [dim]{{
        "field": "field",
        "metric_type": "type",
        "params": {{
            "operator": "op",
            "tolerance": {{
                "type": "tol_type",
                "value": tol_value
            }}
        }},
        "statistic": "statistic"
    }}[/dim]

    [bold][underline]Examples[/underline][/bold]

    - Create an acceptance test with a single metric.
        $ [dim]METRIC='{{
            "field": "solution.objective",
            "metric_type": "direct-comparison",
            "params": {{
                "operator": "lt",
                "tolerance": {{"type": "relative", "value": 0.05}}
            }},
            "statistic": "mean"
        }}'
        nextmv cloud acceptance create --app-id hare-app --acceptance-test-id test-123 \\
            --candidate-instance-id candidate-123 --baseline-instance-id baseline-456 \\
            --metrics "$METRIC" --input-set-id input-set-123[/dim]

    - Create with multiple metrics by repeating the flag.
        $ [dim]METRIC1='{{
            "field": "solution.objective",
            "metric_type": "direct-comparison",
            "params": {{
                "operator": "lt",
                "tolerance": {{"type": "relative", "value": 0.05}}
            }},
            "statistic": "mean"
        }}'
        METRIC2='{{
            "field": "statistics.run.duration",
            "metric_type": "direct-comparison",
            "params": {{
                "operator": "le",
                "tolerance": {{"type": "absolute", "value": 1.0}}
            }},
            "statistic": "p95"
        }}'
        nextmv cloud acceptance create --app-id hare-app --acceptance-test-id test-123 \\
            --candidate-instance-id candidate-123 --baseline-instance-id baseline-456 \\
            --metrics "$METRIC1" --metrics "$METRIC2" --input-set-id input-set-123[/dim]

    - Create with multiple metrics in a single [magenta]json[/magenta] array.
        $ [dim]METRICS='[
            {{
                "field": "solution.objective",
                "metric_type": "direct-comparison",
                "params": {{
                    "operator": "lt",
                    "tolerance": {{"type": "relative", "value": 0.05}}
                }},
                "statistic": "mean"
            }},
            {{
                "field": "statistics.run.duration",
                "metric_type": "direct-comparison",
                "params": {{
                    "operator": "le",
                    "tolerance": {{"type": "absolute", "value": 1.0}}
                }},
                "statistic": "p95"
            }}
        ]'
        nextmv cloud acceptance create --app-id hare-app --acceptance-test-id test-123 \\
            --candidate-instance-id candidate-123 --baseline-instance-id baseline-456 \\
            --metrics "$METRICS" --input-set-id input-set-123[/dim]

    - Create an acceptance test and wait for it to complete.
        $ [dim]METRIC='{{
            "field": "solution.objective",
            "metric_type": "direct-comparison",
            "params": {{
                "operator": "lt",
                "tolerance": {{"type": "relative", "value": 0.05}}
            }},
            "statistic": "mean"
        }}'
        nextmv cloud acceptance create --app-id hare-app --acceptance-test-id test-123 \\
            --candidate-instance-id candidate-123 --baseline-instance-id baseline-456 \\
            --metrics "$METRIC" --input-set-id input-set-123 --wait[/dim]

    - Create an acceptance test and save the results to a file, waiting for completion.
        $ [dim]METRIC='{{
            "field": "solution.objective",
            "metric_type": "direct-comparison",
            "params": {{
                "operator": "lt",
                "tolerance": {{"type": "relative", "value": 0.05}}
            }},
            "statistic": "mean"
        }}'
        nextmv cloud acceptance create --app-id hare-app --acceptance-test-id test-123 \\
            --candidate-instance-id candidate-123 --baseline-instance-id baseline-456 \\
            --metrics "$METRIC" --input-set-id input-set-123 --output results.json[/dim]
    """
)
def create(
    app_id: AppIDOption,
    # Options for acceptance test configuration.
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
            help="Metrics to use for the acceptance test. Data should be valid [magenta]json[/magenta]. "
            "Pass multiple metrics by repeating the flag, or providing a list of objects. "
            "See command help for details on metric formatting.",
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
            help="ID of the input set to use for the underlying batch experiment. "
            "Required if the batch experiment does not exist yet.",
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
            help="Wait for the acceptance test to complete. Results are printed to [magenta]stdout[/magenta]. "
            "Specify output location with --output.",
            rich_help_panel="Output control",
        ),
    ] = False,
    profile: ProfileOption = None,
) -> None:
    cloud_app = build_app(app_id=app_id, profile=profile)

    # Build the metrics list from the CLI options
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

    # If we don't need to poll at all we are done.
    if not wait and (output is None or output == ""):
        print_json({"acceptance_test_id": acceptance_id})

        return

    success(f"Acceptance test [magenta]{acceptance_id}[/magenta] created.")

    # Build the polling options.
    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    in_progress(msg="Getting acceptance test results...")
    acceptance_test = cloud_app.acceptance_test_with_polling(
        acceptance_test_id=acceptance_id,
        polling_options=polling_options,
    )
    acceptance_test_dict = acceptance_test.to_dict()

    # Handle output
    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(acceptance_test_dict, f, indent=2)

        success(msg=f"Acceptance test results saved to [magenta]{output}[/magenta].")

        return

    print_json(acceptance_test_dict)


def build_metrics(metrics: list[str]) -> list[Metric]:
    """
    Builds the metrics list from the CLI option(s).

    Parameters
    ----------
    metrics : list[str]
        List of metrics provided via the CLI.

    Returns
    -------
    list[Metric]
        The built metrics list.
    """
    metrics_list = []

    for metric_str in metrics:
        try:
            metric_data = json.loads(metric_str)

            # Handle the case where the value is a list of metrics.
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

                    metric = Metric(**item)
                    metrics_list.append(metric)

            # Handle the case where the value is a single metric.
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

                metric = Metric(**metric_data)
                metrics_list.append(metric)

            else:
                error(
                    f"Invalid metric format: [magenta]{metric_str}[/magenta]. "
                    "Expected [magenta]json[/magenta] object or array."
                )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            error(f"Invalid metric format: [magenta]{metric_str}[/magenta]. Error: {e}")

    if not metrics_list:
        error(
            "No valid metrics were provided. Please specify at least one metric with "
            "[magenta]field[/magenta], [magenta]metric_type[/magenta], "
            "[magenta]params[/magenta], and [magenta]statistic[/magenta] fields."
        )

    return metrics_list
