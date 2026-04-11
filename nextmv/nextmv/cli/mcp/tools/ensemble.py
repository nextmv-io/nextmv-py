"""MCP tools for cloud ensemble definitions and runs."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.ensemble import (
    create_ensemble,
    delete_ensemble,
    ensemble_run_submit,
    ensemble_run_with_result,
    get_ensemble,
    list_ensembles,
    update_ensemble,
)
from nextmv.cli.mcp import framework as mcp_fw
from nextmv.cli.mcp.tools import _helpers
from nextmv.polling import default_polling_options


def register(mcp: FastMCP) -> None:
    """Register cloud ensemble definition and run tools."""

    # Split into two helper functions to stay under the C901 complexity
    # limit (multiple @mcp.tool closures in a single body exceeds it).
    _register_definition_tools(mcp)
    _register_run_tools(mcp)


def _register_definition_tools(mcp: FastMCP) -> None:
    """Register ensemble definition CRUD tools."""

    mcp_fw.tool(mcp, list_ensembles, name="cloud_list_ensembles")
    mcp_fw.tool(mcp, get_ensemble, name="cloud_get_ensemble")

    @mcp.tool()
    def cloud_create_ensemble(
        app_id: str,
        run_groups: list[dict[str, Any]],
        rules: list[dict[str, Any]],
        ensemble_definition_id: str | None = None,
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
            ensemble_definition_id: Optional ensemble definition ID.
            name: Optional name.
            description: Optional description.
        """

        ensemble_definition_id = _helpers._none_if_empty(ensemble_definition_id)
        name = _helpers._none_if_empty(name)
        description = _helpers._none_if_empty(description)

        if not run_groups:
            return "Error: run_groups must contain at least one run group."
        if not rules:
            return "Error: rules must contain at least one evaluation rule."

        client = mcp_fw.client()
        try:
            return create_ensemble(
                client,
                app_id=app_id,
                run_groups=run_groups,
                rules=rules,
                ensemble_definition_id=ensemble_definition_id,
                name=name,
                description=description,
            )
        except Exception as exc:
            return f"Error: {exc}"

    mcp_fw.tool(
        mcp,
        update_ensemble,
        name="cloud_update_ensemble",
        normalize_empty=["name", "description"],
    )

    mcp_fw.tool(
        mcp,
        delete_ensemble,
        name="cloud_delete_ensemble",
        result_message="Deleted ensemble definition {ensemble_definition_id}",
    )


def _register_run_tools(mcp: FastMCP) -> None:
    """Register ensemble run tools (inline — bespoke input handling)."""

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
            _helpers._require_non_empty(app_id, "app_id")
            _helpers._require_non_empty(ensemble_id, "ensemble_id")
        except ValueError as e:
            return f"Error building ensemble run configuration: {e}"

        client = mcp_fw.client()
        try:
            result = ensemble_run_with_result(
                client,
                app_id,
                ensemble_id,
                input=input,
                input_dir_path=input_dir_path,
                content_format=content_format,
                run_options=run_options,
                managed_input_id=managed_input_id,
                polling_options=default_polling_options(),
            )
        except ValueError as e:
            return f"Error building ensemble run configuration: {e}"

        endpoint = _helpers._endpoint_from_client(client)
        return _helpers._save_experiment_file(result, endpoint, "ensemble", ensemble_id, filename="run_result.json")

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
            _helpers._require_non_empty(app_id, "app_id")
            _helpers._require_non_empty(ensemble_id, "ensemble_id")
        except ValueError as e:
            return f"Error building ensemble run configuration: {e}"

        client = mcp_fw.client()
        try:
            return ensemble_run_submit(
                client,
                app_id,
                ensemble_id,
                input=input,
                input_dir_path=input_dir_path,
                content_format=content_format,
                run_options=run_options,
                managed_input_id=managed_input_id,
            )
        except ValueError as e:
            return f"Error building ensemble run configuration: {e}"
