"""CLI-only workflows for the cloud ensemble domain.

Ensemble commands accept repeatable JSON ``--run-groups`` and
``--rules`` flags for create, and the update command has a precondition
check plus an ``--output`` file save. These concerns don't fit the
framework's default ``emit()`` flow, so they live in workflow functions
that opt into ``handles_own_output=True``.
"""

import json
from pathlib import Path
from typing import Annotated

import typer

from nextmv.cli.actions.ensemble import create_ensemble, update_ensemble
from nextmv.cli.framework.options import (
    AppIdRequiredOption,
    EnsembleDefinitionIdOption,
)
from nextmv.cli.message import enum_values, error, in_progress, print_json, success
from nextmv.cloud.client import Client
from nextmv.cloud.ensemble import RuleObjective, RuleToleranceType


def build_run_group_dicts(run_groups: list[str]) -> list[dict]:
    """Parse CLI JSON strings into a list of run group dicts.

    Each string may be a single JSON object or a JSON array. Each run
    group must have ``id`` and ``instance_id`` fields.
    """

    run_groups_list: list[dict] = []

    for run_group_str in run_groups:
        try:
            run_group_data = json.loads(run_group_str)

            if isinstance(run_group_data, list):
                for ix, item in enumerate(run_group_data):
                    if item.get("id") is None or item.get("instance_id") is None:
                        error(
                            f"Invalid run group format at index [magenta]{ix}[/magenta] in "
                            f"[magenta]{run_group_str}[/magenta]. Each run group must have "
                            "[magenta]id[/magenta] and [magenta]instance_id[/magenta] fields."
                        )
                    run_groups_list.append(item)
            elif isinstance(run_group_data, dict):
                if run_group_data.get("id") is None or run_group_data.get("instance_id") is None:
                    error(
                        f"Invalid run group format in [magenta]{run_group_str}[/magenta]. "
                        "Each run group must have [magenta]id[/magenta] and [magenta]instance_id[/magenta] fields."
                    )
                run_groups_list.append(run_group_data)
            else:
                error(
                    f"Invalid run group format: [magenta]{run_group_str}[/magenta]. "
                    "Expected [magenta]json[/magenta] object or array."
                )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            error(f"Invalid run group format: [magenta]{run_group_str}[/magenta]. Error: {e}")

    return run_groups_list


def build_rule_dicts(rules: list[str]) -> list[dict]:
    """Parse CLI JSON strings into a list of evaluation rule dicts.

    Each string may be a single JSON object or a JSON array. Each rule
    is validated for required fields before being passed to the action
    layer.
    """

    rules_list: list[dict] = []

    for rule_str in rules:
        try:
            rule_data = json.loads(rule_str)

            if isinstance(rule_data, list):
                for ix, item in enumerate(rule_data):
                    _validate_rule_data(item, rule_str, ix)
                    rules_list.append(item)
            elif isinstance(rule_data, dict):
                _validate_rule_data(rule_data, rule_str)
                rules_list.append(rule_data)
            else:
                error(
                    f"Invalid rule format: [magenta]{rule_str}[/magenta]. "
                    "Expected [magenta]json[/magenta] object or array."
                )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            error(f"Invalid rule format: [magenta]{rule_str}[/magenta]. Error: {e}")

    return rules_list


def _validate_rule_data(data: dict, rule_str: str, index: int | None = None) -> None:
    """Validate that rule data contains all required fields."""
    required_fields = ["id", "statistics_path", "objective", "tolerance", "index"]
    missing_fields = [field for field in required_fields if data.get(field) is None]

    if missing_fields:
        index_msg = f" at index [magenta]{index}[/magenta]" if index is not None else ""
        error(
            f"Invalid rule format{index_msg} in [magenta]{rule_str}[/magenta]. "
            f"Missing required fields: [magenta]{', '.join(missing_fields)}[/magenta]."
        )

    tolerance = data.get("tolerance")
    if not isinstance(tolerance, dict) or tolerance.get("value") is None or tolerance.get("type") is None:
        index_msg = f" at index [magenta]{index}[/magenta]" if index is not None else ""
        error(
            f"Invalid tolerance format{index_msg} in [magenta]{rule_str}[/magenta]. "
            "Tolerance must have [magenta]value[/magenta] and [magenta]type[/magenta] fields."
        )


def _save_or_print(data: dict, output: str | None, saved_noun: str) -> None:
    """Write ``data`` as JSON to ``output`` or print it to stdout."""
    if output is not None and output != "":
        Path(output).write_text(json.dumps(data, indent=2))
        success(f"{saved_noun} saved to [magenta]{output}[/magenta].")
        return
    print_json(data)


_CREATE_HELP = f"""
Create a new Nextmv Cloud ensemble definition.

An ensemble definition coordinates the execution of multiple child runs
for an application and determines the optimal result from those runs.
Each ensemble definition contains run groups and evaluation rules.

[bold][underline]Run Groups[/underline][/bold]

Run groups are provided as [magenta]json[/magenta] objects using the
--run-groups flag. Each run group specifies how child runs are executed.

You can provide run groups in three ways:

* A single run group as a [magenta]json[/magenta] object.
* Multiple run groups by repeating the --run-groups flag.
* Multiple run groups as a [magenta]json[/magenta] array in a single --run-groups flag.

Each run group must have [magenta]id[/magenta] and [magenta]instance_id[/magenta]
fields. Optional fields include [magenta]options[/magenta] (a JSON object of
string key-value pairs) and [magenta]repetitions[/magenta] (an integer).

[bold][underline]Evaluation Rules[/underline][/bold]

Evaluation rules are provided as [magenta]json[/magenta] objects using the
--rules flag. Each rule determines how to evaluate and select the best
result from the child runs.

Each rule must have [magenta]id[/magenta], [magenta]statistics_path[/magenta]
(e.g., [magenta]$.result.value[/magenta]), [magenta]objective[/magenta]
(allowed values: {enum_values(RuleObjective)}),
[magenta]tolerance[/magenta] (an object with [magenta]value[/magenta] and
[magenta]type[/magenta] — allowed types: {enum_values(RuleToleranceType)}),
and [magenta]index[/magenta] (evaluation order).
"""


def run_create_ensemble(
    client: Client,
    app_id: AppIdRequiredOption,
    run_groups: Annotated[
        list[str],
        typer.Option(
            "--run-groups",
            "-r",
            help=(
                "Run groups to configure for the ensemble. Data should be valid [magenta]json[/magenta]. "
                "Pass multiple run groups by repeating the flag, or providing a list of objects. "
                "See command help for details on run group formatting."
            ),
            metavar="RUN_GROUPS",
            rich_help_panel="Ensemble configuration",
        ),
    ],
    rules: Annotated[
        list[str],
        typer.Option(
            "--rules",
            "-u",
            help=(
                "Evaluation rules to configure for the ensemble. Data should be valid [magenta]json[/magenta]. "
                "Pass multiple rules by repeating the flag, or providing a list of objects. "
                "See command help for details on rule formatting."
            ),
            metavar="RULES",
            rich_help_panel="Ensemble configuration",
        ),
    ],
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="An optional description for the ensemble definition.",
            metavar="DESCRIPTION",
            rich_help_panel="Ensemble configuration",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="A name for the ensemble definition.",
            metavar="NAME",
            rich_help_panel="Ensemble configuration",
        ),
    ] = None,
    ensemble_definition_id: Annotated[
        str | None,
        typer.Option(
            "--ensemble-definition-id",
            "-e",
            help=(
                "The ID to assign to the new ensemble definition. If not provided, "
                "a random ID will be generated."
            ),
            envvar="NEXTMV_ENSEMBLE_DEFINITION_ID",
            metavar="ENSEMBLE_DEFINITION_ID",
            rich_help_panel="Ensemble configuration",
        ),
    ] = None,
) -> None:
    # Full help attached via __doc__ below because it uses enum_values()
    # interpolation that typer can't parse in a real docstring.
    in_progress(msg="Creating ensemble definition...")

    run_groups_dicts = build_run_group_dicts(run_groups)
    rules_dicts = build_rule_dicts(rules)

    ensemble_definition_dict = create_ensemble(
        client,
        app_id=app_id,
        run_groups=run_groups_dicts,
        rules=rules_dicts,
        ensemble_definition_id=ensemble_definition_id,
        name=name,
        description=description,
    )
    print_json(ensemble_definition_dict)


run_create_ensemble.__doc__ = _CREATE_HELP


def run_update_ensemble(
    client: Client,
    app_id: AppIdRequiredOption,
    ensemble_definition_id: EnsembleDefinitionIdOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="A new description for the ensemble definition.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="A new name for the ensemble definition.",
            metavar="NAME",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated ensemble definition information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Update a Nextmv Cloud ensemble definition.

    Update the name and/or description of an existing ensemble
    definition. To modify run groups or evaluation rules, you need to
    delete and recreate the ensemble definition.
    """

    if name is None and description is None:
        error("Provide at least one option to update: --name or --description.")

    in_progress(msg="Updating ensemble definition...")
    ensemble_definition_dict = update_ensemble(
        client,
        app_id=app_id,
        ensemble_definition_id=ensemble_definition_id,
        name=name,
        description=description,
    )
    success(
        f"Ensemble definition [magenta]{ensemble_definition_id}[/magenta] updated successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
    _save_or_print(ensemble_definition_dict, output, "Updated ensemble definition information")
