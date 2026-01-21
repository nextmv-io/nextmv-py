"""
This module defines the cloud ensemble create command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import enum_values, error, in_progress, print_json
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.ensemble import EvaluationRule, RuleObjective, RuleTolerance, RuleToleranceType, RunGroup

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    app_id: AppIDOption,
    run_groups: Annotated[
        list[str],
        typer.Option(
            "--run-groups",
            "-r",
            help="Run groups to configure for the ensemble. Data should be valid [magenta]json[/magenta]. "
            "Pass multiple run groups by repeating the flag, or providing a list of objects. "
            "Object format: [magenta]{'id': id, 'instance_id': instance_id, "
            "'options': options, 'repetitions': repetitions}[/magenta]. "
            "The [magenta]options[/magenta] and [magenta]repetitions[/magenta] fields are optional.",
            metavar="RUN_GROUPS",
        ),
    ],
    rules: Annotated[
        list[str],
        typer.Option(
            "--rules",
            "-u",
            help="Evaluation rules to configure for the ensemble. Data should be valid [magenta]json[/magenta]. "
            "Pass multiple rules by repeating the flag, or providing a list of objects. "
            "Allowed values for [magenta]objective[/magenta] are: "
            f"{enum_values(RuleObjective)}. "
            "Allowed values for [magenta]tolerance.type[/magenta] are: "
            f"{enum_values(RuleToleranceType)}. "
            "Object format: [magenta]{'id': id, 'statistics_path': path, 'objective': objective, "
            "'tolerance': {'value': value, 'type': type}, 'index': index}[/magenta].",
            metavar="RULES",
        ),
    ],
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="An optional description for the ensemble definition.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="A name for the ensemble definition.",
            metavar="NAME",
        ),
    ] = None,
    ensemble_definition_id: Annotated[
        str | None,
        typer.Option(
            "--ensemble-definition-id",
            "-e",
            help="The ID to assign to the new ensemble definition. If not provided, a random ID will be generated.",
            envvar="NEXTMV_ENSEMBLE_DEFINITION_ID",
            metavar="ENSEMBLE_DEFINITION_ID",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Cloud ensemble definition.

    An ensemble definition coordinates the execution of multiple child runs for
    an application and determines the optimal result from those runs. Each
    ensemble definition contains run groups and evaluation rules.

    [bold]Run Groups[/bold] specify how child runs are executed:
    - [magenta]id[/magenta]: Unique identifier for the run group.
    - [magenta]instance_id[/magenta]: The instance to execute runs on.
    - [magenta]options[/magenta] (optional): Runtime options/parameters. Options should be provded as a
        [magenta]json[/magenta] object, with [magenta]string[/magenta] key-value pairs.
    - [magenta]repetitions[/magenta] (optional): Number of times to repeat the run.

    [bold]Evaluation Rules[/bold] determine the best result:
    - [magenta]id[/magenta]: Unique identifier for the rule.
    - [magenta]statistics_path[/magenta]: JSONPath to the metric (e.g., [magenta]$.result.value[/magenta]).
    - [magenta]objective[/magenta]: Either [magenta]maximize[/magenta] or [magenta]minimize[/magenta].
    - [magenta]tolerance[/magenta]: Object with [magenta]value[/magenta] (float) and [magenta]type[/magenta]
      ([magenta]absolute[/magenta] or [magenta]relative[/magenta]).
    - [magenta]index[/magenta]: Evaluation order (lower indices evaluated first).

    You can provide run groups and rules in three ways:
    - A single object as [magenta]json[/magenta].
    - Multiple objects by repeating the flag.
    - Multiple objects as a [magenta]json[/magenta] array in a single flag.

    [bold][underline]Examples[/underline][/bold]

    - Create an ensemble definition with a single run group and rule.
        $ [green]RUN_GROUP='{
            "id": "rg1",
            "instance_id": "inst-123"
        }'
        RULE='{
            "id": "rule1",
            "statistics_path": "$.result.value",
            "objective": "minimize",
            "tolerance": {"value": 0.1, "type": "relative"},
            "index": 0
        }'
        nextmv cloud ensemble create --app-id hare-app --run-groups "$RUN_GROUP" --rules "$RULE"[/green]

    - Create with multiple run groups by repeating the flag.
        $ [green]RUN_GROUP_1='{
            "id": "rg1",
            "instance_id": "inst-123"
        }'
        RUN_GROUP_2='{
            "id": "rg2",
            "instance_id": "inst-456",
            "options": {"param": "value"}
        }'
        RULE='{
            "id": "rule1",
            "statistics_path": "$.result.value",
            "objective": "minimize",
            "tolerance": {"value": 0.1, "type": "relative"},
            "index": 0
        }'
        nextmv cloud ensemble create --app-id hare-app --run-groups "$RUN_GROUP_1" --run-groups "$RUN_GROUP_2" \\
            --rules "$RULE"[/green]

    - Create with multiple items in a single JSON array.
        $ [green]RUN_GROUPS='[
            {"id": "rg1", "instance_id": "inst-123"},
            {"id": "rg2", "instance_id": "inst-456"}
        ]'
        RULES='[{
            "id": "rule1",
            "statistics_path": "$.result.value",
            "objective": "minimize",
            "tolerance": {"value": 0.1, "type": "relative"},
            "index": 0
        }]'
        nextmv cloud ensemble create --app-id hare-app --run-groups "$RUN_GROUPS" --rules "$RULES"[/green]

    - Create with custom ID, name, and description.
        $ [green]RUN_GROUP='{
            "id": "rg1",
            "instance_id": "inst-123"
        }'
        RULE='{
            "id": "rule1",
            "statistics_path": "$.result.value",
            "objective": "minimize",
            "tolerance": {"value": 0.1, "type": "relative"},
            "index": 0
        }'
        nextmv cloud ensemble create --app-id hare-app \\
            --ensemble-definition-id prod-ensemble --name "Production Ensemble" \\
            --description "Production ensemble with multiple solvers" \\
            --run-groups "$RUN_GROUP" --rules "$RULE"[/green]

    - Create with run group repetitions.
        $ [green]RUN_GROUP='{
            "id": "rg1",
            "instance_id": "inst-123",
            "repetitions": 5
        }'
        RULE='{
            "id": "rule1",
            "statistics_path": "$.result.value",
            "objective": "minimize",
            "tolerance": {"value": 0.1, "type": "relative"},
            "index": 0
        }'
        nextmv cloud ensemble create --app-id hare-app --run-groups "$RUN_GROUP" --rules "$RULE"[/green]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Creating ensemble definition...")

    # Build the run groups and rules lists from the CLI options
    run_groups_list = build_run_groups(run_groups)
    rules_list = build_rules(rules)

    ensemble_definition = cloud_app.new_ensemble_definition(
        run_groups=run_groups_list,
        rules=rules_list,
        id=ensemble_definition_id,
        name=name,
        description=description,
    )
    print_json(ensemble_definition.to_dict())


def build_run_groups(run_groups: list[str]) -> list[RunGroup]:
    """
    Builds the run groups list from the CLI option(s).

    Parameters
    ----------
    run_groups : list[str]
        List of run groups provided via the CLI.

    Returns
    -------
    list[RunGroup]
        The built run groups list.
    """
    import json

    run_groups_list = []

    for run_group_str in run_groups:
        try:
            run_group_data = json.loads(run_group_str)

            # Handle the case where the value is a list of run groups.
            if isinstance(run_group_data, list):
                for ix, item in enumerate(run_group_data):
                    if item.get("id") is None or item.get("instance_id") is None:
                        error(
                            f"Invalid run group format at index [magenta]{ix}[/magenta] in "
                            f"[magenta]{run_group_str}[/magenta]. Each run group must have "
                            "[magenta]id[/magenta] and [magenta]instance_id[/magenta] fields."
                        )

                    run_group = RunGroup(
                        id=item["id"],
                        instance_id=item["instance_id"],
                        options=item.get("options"),
                        repetitions=item.get("repetitions"),
                    )
                    run_groups_list.append(run_group)

            # Handle the case where the value is a single run group.
            elif isinstance(run_group_data, dict):
                if run_group_data.get("id") is None or run_group_data.get("instance_id") is None:
                    error(
                        f"Invalid run group format in [magenta]{run_group_str}[/magenta]. "
                        "Each run group must have [magenta]id[/magenta] and [magenta]instance_id[/magenta] fields."
                    )

                run_group = RunGroup(
                    id=run_group_data["id"],
                    instance_id=run_group_data["instance_id"],
                    options=run_group_data.get("options"),
                    repetitions=run_group_data.get("repetitions"),
                )
                run_groups_list.append(run_group)

            else:
                error(
                    f"Invalid run group format: [magenta]{run_group_str}[/magenta]. "
                    "Expected [magenta]json[/magenta] object or array."
                )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            error(f"Invalid run group format: [magenta]{run_group_str}[/magenta]. Error: {e}")

    return run_groups_list


def build_rules(rules: list[str]) -> list[EvaluationRule]:
    """
    Builds the rules list from the CLI option(s).

    Parameters
    ----------
    rules : list[str]
        List of rules provided via the CLI.

    Returns
    -------
    list[EvaluationRule]
        The built rules list.
    """
    import json

    rules_list = []

    for rule_str in rules:
        try:
            rule_data = json.loads(rule_str)

            # Handle the case where the value is a list of rules.
            if isinstance(rule_data, list):
                for ix, item in enumerate(rule_data):
                    validate_rule_data(item, rule_str, ix)
                    rule = create_evaluation_rule(item)
                    rules_list.append(rule)

            # Handle the case where the value is a single rule.
            elif isinstance(rule_data, dict):
                validate_rule_data(rule_data, rule_str)
                rule = create_evaluation_rule(rule_data)
                rules_list.append(rule)

            else:
                error(
                    f"Invalid rule format: [magenta]{rule_str}[/magenta]. "
                    "Expected [magenta]json[/magenta] object or array."
                )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            error(f"Invalid rule format: [magenta]{rule_str}[/magenta]. Error: {e}")

    return rules_list


def validate_rule_data(data: dict, rule_str: str, index: int | None = None) -> None:
    """
    Validates that rule data contains all required fields.

    Parameters
    ----------
    data : dict
        The rule data to validate.
    rule_str : str
        The original rule string for error messages.
    index : int | None
        The index if this is part of a list, for error messages.
    """
    required_fields = ["id", "statistics_path", "objective", "tolerance", "index"]
    missing_fields = [field for field in required_fields if data.get(field) is None]

    if missing_fields:
        index_msg = f" at index [magenta]{index}[/magenta]" if index is not None else ""
        error(
            f"Invalid rule format{index_msg} in [magenta]{rule_str}[/magenta]. "
            f"Missing required fields: [magenta]{', '.join(missing_fields)}[/magenta]."
        )

    # Validate tolerance structure
    tolerance = data.get("tolerance")
    if not isinstance(tolerance, dict) or tolerance.get("value") is None or tolerance.get("type") is None:
        index_msg = f" at index [magenta]{index}[/magenta]" if index is not None else ""
        error(
            f"Invalid tolerance format{index_msg} in [magenta]{rule_str}[/magenta]. "
            "Tolerance must have [magenta]value[/magenta] and [magenta]type[/magenta] fields."
        )


def create_evaluation_rule(data: dict) -> EvaluationRule:
    """
    Creates an EvaluationRule from validated data.

    Parameters
    ----------
    data : dict
        The validated rule data.

    Returns
    -------
    EvaluationRule
        The created evaluation rule.
    """
    tolerance_data = data["tolerance"]
    tolerance = RuleTolerance(
        value=float(tolerance_data["value"]),
        type=RuleToleranceType(tolerance_data["type"]),
    )

    return EvaluationRule(
        id=data["id"],
        statistics_path=data["statistics_path"],
        objective=RuleObjective(data["objective"]),
        tolerance=tolerance,
        index=int(data["index"]),
    )
