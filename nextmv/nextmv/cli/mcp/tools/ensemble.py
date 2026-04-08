"""MCP tools for cloud ensemble definitions and runs."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.ensemble import create_ensemble as _create_ensemble
from nextmv.cli.actions.ensemble import delete_ensemble as _delete_ensemble
from nextmv.cli.actions.ensemble import ensemble_run_submit as _ensemble_run_submit
from nextmv.cli.actions.ensemble import ensemble_run_with_result as _ensemble_run_with_result
from nextmv.cli.actions.ensemble import get_ensemble as _get_ensemble
from nextmv.cli.actions.ensemble import list_ensembles as _list_ensembles
from nextmv.cli.mcp.tools import _helpers
from nextmv.polling import default_polling_options


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

        client = _helpers._get_client()
        return _list_ensembles(client, app_id)

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

        client = _helpers._get_client()
        data = _get_ensemble(client, app_id, ensemble_id)
        return _helpers._save_to_json_file(data, prefix=f"ensemble_{ensemble_id}")

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

        if not run_groups:
            return "Error: run_groups must contain at least one run group."
        if not rules:
            return "Error: rules must contain at least one evaluation rule."

        client = _helpers._get_client()
        try:
            return _create_ensemble(
                client,
                app_id,
                run_groups=run_groups,
                rules=rules,
                ensemble_id=ensemble_id,
                name=name,
                description=description,
            )
        except Exception as exc:
            return f"Error: {exc}"

    @mcp.tool()
    def cloud_delete_ensemble(app_id: str, ensemble_id: str) -> str:
        """Delete an ensemble definition permanently.

        Args:
            app_id: The application ID.
            ensemble_id: The ensemble definition ID to delete.
        """

        client = _helpers._get_client()
        _delete_ensemble(client, app_id, ensemble_id)
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
            _helpers._require_non_empty(app_id, "app_id")
            _helpers._require_non_empty(ensemble_id, "ensemble_id")
        except ValueError as e:
            return f"Error building ensemble run configuration: {e}"

        client = _helpers._get_client()
        try:
            result = _ensemble_run_with_result(
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

        return _helpers._save_to_json_file(result, prefix=f"ensemble_run_{app_id}_{ensemble_id}")

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

        client = _helpers._get_client()
        try:
            return _ensemble_run_submit(
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
