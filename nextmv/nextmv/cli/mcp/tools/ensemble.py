"""MCP tools for cloud ensemble definitions and runs."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.mcp.tools import _helpers
from nextmv.cloud import Application
from nextmv.cloud.ensemble import (
    EvaluationRule,
    RuleObjective,
    RuleTolerance,
    RuleToleranceType,
    RunGroup,
)
from nextmv.polling import default_polling_options
from nextmv.run import RunConfiguration, RunType, RunTypeConfiguration


def _cloud_create_ensemble_impl(
    app_id: str,
    run_groups: list[dict[str, Any]],
    rules: list[dict[str, Any]],
    ensemble_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
) -> dict[str, Any] | str:
    """Implementation for creating an ensemble definition."""

    app = _helpers._get_app(app_id)

    if not run_groups:
        return "Error: run_groups must contain at least one run group."
    if not rules:
        return "Error: rules must contain at least one evaluation rule."

    # Convert plain dicts to RunGroup/EvaluationRule objects so the
    # SDK can call .to_dict() on them internally.
    run_group_objs = []
    for i, rg in enumerate(run_groups):
        try:
            run_group_objs.append(RunGroup.from_dict(rg))
        except Exception as exc:
            return (
                f"Error: run_groups[{i}] is invalid (requires at least "
                f"'id' and 'instance_id'): {exc}"
            )

    rule_objs = []
    for i, r in enumerate(rules):
        try:
            rule_obj = _parse_evaluation_rule(r, i)
            if isinstance(rule_obj, str):
                return rule_obj  # Error message
            rule_objs.append(rule_obj)
        except KeyError as exc:
            return (
                f"Error: rules[{i}] is missing required field {exc}. "
                f"Required: id, statistics_path, objective."
            )
        except Exception as exc:
            return f"Error: rules[{i}] is invalid: {exc}"

    ensemble = app.new_ensemble_definition(
        run_groups=run_group_objs,
        rules=rule_objs,
        id=ensemble_id,
        name=name,
        description=description,
    )
    return ensemble.to_dict()


def _parse_evaluation_rule(r: dict[str, Any], index: int) -> Any:
    """Parse a single evaluation rule dict into an EvaluationRule.

    Returns an ``EvaluationRule`` on success, or an error string on failure.
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
        return (
            f"Error: rules[{index}] has unknown objective '{raw_obj}'; "
            f"use one of: {sorted(valid_objectives)} "
            f"(or shorthand 'min'/'max')."
        )
    objective = RuleObjective(mapped)

    return EvaluationRule(
        id=r["id"],
        statistics_path=r["statistics_path"],
        objective=objective,
        tolerance=tol,
        index=r.get("index", 0),
    )


def _build_ensemble_run_config(
    app_id: str,
    ensemble_id: str,
    content_format: str | None,
) -> tuple[Application, RunConfiguration]:
    """Build the Application and RunConfiguration for an ensemble run.

    Raises ``ValueError`` if required parameters are empty.
    """

    app_id = _helpers._require_non_empty(app_id, "app_id")
    ensemble_id = _helpers._require_non_empty(ensemble_id, "ensemble_id")

    content_format = _helpers._none_if_empty(content_format)

    app = _helpers._get_app(app_id)
    config = _helpers._build_run_configuration(content_format) or RunConfiguration()
    config.run_type = RunTypeConfiguration(
        run_type=RunType.ENSEMBLE,
        definition_id=ensemble_id,
    )
    return app, config


def register(mcp: FastMCP) -> None:
    """Register cloud ensemble definition and run tools."""

    @mcp.tool()
    def cloud_list_ensembles(app_id: str) -> list[dict[str, Any]]:
        """List ensemble definitions for a Nextmv Cloud application.

        An ensemble runs multiple instances or configurations in
        parallel and selects the best result based on evaluation
        rules.

        Args:
            app_id: The application ID.
        """

        app = _helpers._get_app(app_id)
        ensembles = app.list_ensemble_definitions()
        return [e.to_dict() for e in ensembles]

    @mcp.tool()
    def cloud_get_ensemble(
        app_id: str,
        ensemble_id: str,
    ) -> str:
        """Get details of an ensemble definition.

        Returns run groups, evaluation rules, and configuration.
        Saves the result to a local temp file. Use file-reading
        tools to inspect the contents.

        Args:
            app_id: The application ID.
            ensemble_id: The ensemble definition ID.
        """

        app = _helpers._get_app(app_id)
        ensemble = app.ensemble_definition(ensemble_definition_id=ensemble_id)
        return _helpers._save_to_json_file(ensemble.to_dict(), prefix=f"ensemble_{ensemble_id}")

    @mcp.tool()
    def cloud_create_ensemble(
        app_id: str,
        run_groups: list[dict[str, Any]],
        rules: list[dict[str, Any]],
        ensemble_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any] | str:
        """Create an ensemble definition for a Nextmv Cloud application.

        An ensemble runs multiple instances/configurations and picks the
        best result based on evaluation rules.

        Args:
            app_id: The application ID.
            run_groups: List of run group definitions. Each is a dict with
                keys: id, instance_id, options, repetitions.
            rules: List of evaluation rules. Each is a dict with keys:
                id (str, required), statistics_path (str, required),
                objective (str, required -- "minimize"/"min" or
                "maximize"/"max"), tolerance (float for relative, or
                dict with "value" and "type"), index (int, optional --
                defaults to 0; lower indices are evaluated first).
            ensemble_id: Optional ensemble definition ID.
            name: Optional name.
            description: Optional description.
        """

        ensemble_id = _helpers._none_if_empty(ensemble_id)
        name = _helpers._none_if_empty(name)
        description = _helpers._none_if_empty(description)

        return _cloud_create_ensemble_impl(
            app_id=app_id,
            run_groups=run_groups,
            rules=rules,
            ensemble_id=ensemble_id,
            name=name,
            description=description,
        )

    @mcp.tool()
    def cloud_delete_ensemble(app_id: str, ensemble_id: str) -> str:
        """Delete an ensemble definition permanently.

        Args:
            app_id: The application ID.
            ensemble_id: The ensemble definition ID to delete.
        """

        app = _helpers._get_app(app_id)
        app.delete_ensemble_definition(ensemble_definition_id=ensemble_id)
        return f"Deleted ensemble definition {ensemble_id}"

    @mcp.tool()
    def cloud_ensemble_run(
        app_id: str,
        ensemble_id: str,
        input: dict[str, Any] | None = None,
        input_dir_path: str | None = None,
        content_format: str | None = None,
        run_options: dict[str, str] | None = None,
        managed_input_id: str | None = None,
    ) -> str:
        """Run a Nextmv Cloud ensemble and wait for the result.

        Submits input to an ensemble definition, which runs multiple
        instances/configurations in parallel and selects the best
        result based on evaluation rules. Polls until the ensemble
        run completes and saves the full result to a local temp file.

        Args:
            app_id: The application ID.
            ensemble_id: The ensemble definition ID to run against.
            input: The input data (JSON object) for the run. Used for
                JSON apps. Ignored when ``input_dir_path`` or
                ``managed_input_id`` is provided.
            input_dir_path: Path to a local directory containing input
                files. Use for multi-file or CSV archive apps. When
                provided, ``content_format`` must also be set.
            content_format: Content format of the input. Required when
                ``input_dir_path`` is set. Allowed values:
                ``"multi-file"``, ``"csv-archive"``, ``"json"``.
            run_options: Solver options passed to the application, e.g.
                ``{"solve.duration": "10s"}``.
            managed_input_id: ID of an existing managed input to use
                instead of the inline ``input`` data.
        """

        input_dir_path = _helpers._none_if_empty(input_dir_path)
        managed_input_id = _helpers._none_if_empty(managed_input_id)
        content_format = _helpers._none_if_empty(content_format)

        try:
            app, config = _build_ensemble_run_config(app_id, ensemble_id, content_format)
        except ValueError as e:
            return f"Error building ensemble run configuration: {e}"

        run_result = app.new_run_with_result(
            input=input,
            input_dir_path=input_dir_path,
            configuration=config,
            run_options=run_options or {},
            polling_options=default_polling_options(),
            managed_input_id=managed_input_id,
        )
        return _helpers._save_to_json_file(run_result.to_dict(), prefix=f"ensemble_run_{app_id}_{ensemble_id}")

    @mcp.tool()
    def cloud_ensemble_run_submit(
        app_id: str,
        ensemble_id: str,
        input: dict[str, Any] | None = None,
        input_dir_path: str | None = None,
        content_format: str | None = None,
        run_options: dict[str, str] | None = None,
        managed_input_id: str | None = None,
    ) -> str:
        """Submit an ensemble run without waiting for the result.

        Returns the run ID immediately. Use ``cloud_run_status`` or
        ``cloud_run_result`` to check on the run later.

        Args:
            app_id: The application ID.
            ensemble_id: The ensemble definition ID to run against.
            input: The input data (JSON object) for the run. Used for
                JSON apps. Ignored when ``input_dir_path`` or
                ``managed_input_id`` is provided.
            input_dir_path: Path to a local directory containing input
                files. Use for multi-file or CSV archive apps. When
                provided, ``content_format`` must also be set.
            content_format: Content format of the input. Required when
                ``input_dir_path`` is set. Allowed values:
                ``"multi-file"``, ``"csv-archive"``, ``"json"``.
            run_options: Solver options passed to the application, e.g.
                ``{"solve.duration": "10s"}``.
            managed_input_id: ID of an existing managed input to use
                instead of the inline ``input`` data.
        """

        input_dir_path = _helpers._none_if_empty(input_dir_path)
        managed_input_id = _helpers._none_if_empty(managed_input_id)
        content_format = _helpers._none_if_empty(content_format)

        try:
            app, config = _build_ensemble_run_config(app_id, ensemble_id, content_format)
        except ValueError as e:
            return f"Error building ensemble run configuration: {e}"

        return app.new_run(
            input=input,
            input_dir_path=input_dir_path,
            configuration=config,
            options=run_options or {},
            managed_input_id=managed_input_id,
        )
