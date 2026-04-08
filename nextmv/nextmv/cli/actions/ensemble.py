"""Core ensemble actions.

Pure functions that wrap SDK calls. No CLI or MCP concerns.
"""

from typing import Any

from nextmv.cloud import Application, Client
from nextmv.cloud.ensemble import (
    EvaluationRule,
    RuleObjective,
    RuleTolerance,
    RuleToleranceType,
    RunGroup,
)
from nextmv.run import RunConfiguration, RunType, RunTypeConfiguration


def parse_evaluation_rule(r: dict[str, Any], index: int) -> EvaluationRule:
    """Parse a single evaluation rule dict into an EvaluationRule.

    Raises ValueError on invalid input (instead of returning an error string).
    """

    # Normalize the tolerance field: the LLM may pass a bare
    # float (shorthand for a relative tolerance) or a full dict.
    raw_tol = r.get("tolerance")
    if isinstance(raw_tol, dict):
        tol = RuleTolerance(
            value=raw_tol["value"],
            type=RuleToleranceType(raw_tol.get("type", "relative")),
        )
    else:
        # Bare number — treat as relative tolerance.
        tol = RuleTolerance(
            value=float(raw_tol) if raw_tol is not None else 0.0,
            type=RuleToleranceType.RELATIVE,
        )

    # Normalise objective shorthand: the LLM may send "min"/"max"
    # instead of the full "minimize"/"maximize".
    raw_obj = r["objective"]
    obj_map = {"min": "minimize", "max": "maximize"}
    mapped = obj_map.get(raw_obj, raw_obj)
    valid_objectives = {o.value for o in RuleObjective}
    if mapped not in valid_objectives:
        raise ValueError(
            f"rules[{index}] has unknown objective '{raw_obj}'; "
            f"use one of: {sorted(valid_objectives)} "
            f"(or shorthand 'min'/'max')."
        )
    objective = RuleObjective(mapped)

    try:
        rule_id = r["id"]
        statistics_path = r["statistics_path"]
    except KeyError as exc:
        raise KeyError(f"rules[{index}] is missing required field {exc}") from exc

    return EvaluationRule(
        id=rule_id,
        statistics_path=statistics_path,
        objective=objective,
        tolerance=tol,
        index=r.get("index", 0),
    )


def list_ensembles(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all ensemble definitions for an application."""
    app = Application(client=client, id=app_id)
    ensembles = app.list_ensemble_definitions()
    return [e.to_dict() for e in ensembles]


def get_ensemble(client: Client, app_id: str, ensemble_id: str) -> dict[str, Any]:
    """Get details of an ensemble definition."""
    app = Application(client=client, id=app_id)
    ensemble = app.ensemble_definition(ensemble_definition_id=ensemble_id)
    return ensemble.to_dict()


def create_ensemble(
    client: Client,
    app_id: str,
    run_groups: list[dict[str, Any]],
    rules: list[dict[str, Any]],
    ensemble_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Create an ensemble definition. Returns the ensemble dict."""
    app = Application(client=client, id=app_id)

    run_group_objs = []
    for i, rg in enumerate(run_groups):
        try:
            run_group_objs.append(RunGroup.from_dict(rg))
        except Exception as exc:
            raise ValueError(f"run_groups[{i}] is invalid: {exc}") from exc
    rule_objs = [parse_evaluation_rule(r, i) for i, r in enumerate(rules)]

    ensemble = app.new_ensemble_definition(
        run_groups=run_group_objs,
        rules=rule_objs,
        id=ensemble_id,
        name=name,
        description=description,
    )
    return ensemble.to_dict()


def delete_ensemble(client: Client, app_id: str, ensemble_id: str) -> None:
    """Delete an ensemble definition."""
    app = Application(client=client, id=app_id)
    app.delete_ensemble_definition(ensemble_definition_id=ensemble_id)


def build_ensemble_run_config(
    ensemble_id: str,
    content_format: str | None = None,
) -> RunConfiguration:
    """Build a RunConfiguration for an ensemble run."""
    from nextmv.cli.actions.config import build_run_configuration

    config = build_run_configuration(content_format) or RunConfiguration()
    config.run_type = RunTypeConfiguration(
        run_type=RunType.ENSEMBLE,
        definition_id=ensemble_id,
    )
    return config


def ensemble_run_with_result(
    client: Client,
    app_id: str,
    ensemble_id: str,
    input: dict[str, Any] | None = None,
    input_dir_path: str | None = None,
    content_format: str | None = None,
    run_options: dict[str, str] | None = None,
    managed_input_id: str | None = None,
    polling_options: Any = None,
) -> dict[str, Any]:
    """Submit an ensemble run and wait for the result. Returns result dict."""
    from nextmv.polling import default_polling_options

    app = Application(client=client, id=app_id)
    config = build_ensemble_run_config(ensemble_id, content_format)
    result = app.new_run_with_result(
        input=input,
        input_dir_path=input_dir_path,
        configuration=config,
        run_options=run_options or {},
        polling_options=polling_options or default_polling_options(),
        managed_input_id=managed_input_id,
    )
    return result.to_dict()


def ensemble_run_submit(
    client: Client,
    app_id: str,
    ensemble_id: str,
    input: dict[str, Any] | None = None,
    input_dir_path: str | None = None,
    content_format: str | None = None,
    run_options: dict[str, str] | None = None,
    managed_input_id: str | None = None,
) -> str:
    """Submit an ensemble run without waiting. Returns the run ID."""
    app = Application(client=client, id=app_id)
    config = build_ensemble_run_config(ensemble_id, content_format)
    return app.new_run(
        input=input,
        input_dir_path=input_dir_path,
        configuration=config,
        options=run_options or {},
        managed_input_id=managed_input_id,
    )
