"""MCP tools for cloud run management."""

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.run import (
    cancel_run,
    list_runs,
    run_input,
    run_logs,
    run_metadata,
    run_result,
    submit_run,
    submit_run_with_result,
)
from nextmv.cli.mcp.tools import _helpers
from nextmv.input import INPUTS_KEY
from nextmv.local.local import LOGS_FILE, LOGS_KEY
from nextmv.output import OUTPUTS_KEY
from nextmv.polling import default_polling_options
from nextmv.safe import safe_id


def _cloud_poll_run_logs_impl(app_id: str, run_id: str) -> str:
    """Implementation for polling cloud run logs."""

    app = _helpers._get_app(app_id)
    endpoint = _helpers._endpoint_from_app(app)

    path = os.path.join(_helpers._cloud_run_dir(endpoint, run_id), LOGS_KEY, LOGS_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Stream log entries directly to the file to avoid unbounded
    # memory growth for long-running jobs.
    with open(path, "w") as fh:

        def _write(log_entry) -> None:
            ts = log_entry.timestamp or ""
            log = log_entry.log or ""
            fh.write(f"{ts} {log}\n")

        app.poll_logs(
            run_id=run_id,
            polling_options=default_polling_options(),
            log_func=_write,
        )

    return f"Downloaded: {path}"


def register(mcp: FastMCP) -> None:
    """Register cloud run management tools."""

    @mcp.tool()
    def cloud_run(
        app_id: str,
        input: dict[str, Any] | None = None,
        input_dir_path: str | None = None,
        content_format: str | None = None,
        instance_id: str | None = None,
        run_options: dict[str, str] | None = None,
        managed_input_id: str | None = None,
    ) -> str:
        """Run a Nextmv Cloud application and wait for the result.

        Submits the input to the application, polls until the run
        completes, and saves the full result (solution output and
        statistics) to a local temp file. Use file-reading tools to
        inspect the contents.

        For JSON apps, provide ``input`` as a JSON object. For
        multi-file or CSV archive apps, provide ``input_dir_path``
        pointing to a local directory of input files and set
        ``content_format`` accordingly (e.g. ``"multi-file"``).

        Args:
            app_id: The application ID.
            input: The input data (JSON object) for the run. Used for
                JSON apps. Ignored when ``input_dir_path`` or
                ``managed_input_id`` is provided.
            input_dir_path: Path to a local directory containing input
                files. Use for multi-file or CSV archive apps. When
                provided, ``content_format`` must also be set.
            content_format: Content format of the input. Required when
                ``input_dir_path`` is set. Allowed values:
                ``"multi-file"``, ``"csv-archive"``, ``"json"``.
            instance_id: Instance to run against. Uses the application's
                default instance if omitted.
            run_options: Solver options passed to the application, e.g.
                ``{"solve.duration": "10s"}``.
            managed_input_id: ID of an existing managed input to use
                instead of the inline ``input`` data.
        """

        content_format = _helpers._none_if_empty(content_format)
        instance_id = _helpers._none_if_empty(instance_id)
        managed_input_id = _helpers._none_if_empty(managed_input_id)
        input_dir_path = _helpers._none_if_empty(input_dir_path)

        app = _helpers._get_app(app_id)
        endpoint = _helpers._endpoint_from_app(app)
        config = _helpers._build_run_configuration(content_format)

        # For non-JSON formats, prepare an output directory in the cache.
        # safe_id generates a unique random suffix, so concurrent runs
        # each get their own directory.
        output_dir_path = None
        if content_format and content_format != "json":
            output_dir_path = os.path.join(
                _helpers._cloud_run_dir(endpoint, safe_id("pending")),
                OUTPUTS_KEY,
            )

        result = submit_run_with_result(
            app,
            input=input,
            input_dir_path=input_dir_path,
            configuration=config,
            instance_id=instance_id,
            options=run_options,
            managed_input_id=managed_input_id,
            output_dir_path=output_dir_path,
        )

        run_id = result.id
        run_dir = _helpers._cloud_run_dir(endpoint, run_id)

        # If we used a temporary __pending__ output dir, move it.
        if output_dir_path and os.path.isdir(output_dir_path):
            final_output = os.path.join(run_dir, OUTPUTS_KEY)
            os.makedirs(os.path.dirname(final_output), exist_ok=True)
            os.rename(output_dir_path, final_output)

        result_dict = result.to_dict()
        path = _helpers._save_cloud_run_file(
            result_dict, endpoint, run_id, f"{run_id}.json"
        )
        _helpers._extract_cloud_run_outputs(result_dict, endpoint, run_id)
        return f"Downloaded: {path}"

    @mcp.tool()
    def cloud_run_submit(
        app_id: str,
        input: dict[str, Any] | None = None,
        input_dir_path: str | None = None,
        content_format: str | None = None,
        instance_id: str | None = None,
        run_options: dict[str, str] | None = None,
        managed_input_id: str | None = None,
    ) -> str:
        """Submit a run to a Nextmv Cloud application without waiting.

        Returns the run ID immediately. Use ``cloud_run_status`` or
        ``cloud_run_result`` to check on the run later.

        For JSON apps, provide ``input`` as a JSON object. For
        multi-file or CSV archive apps, provide ``input_dir_path``
        pointing to a local directory of input files and set
        ``content_format`` accordingly (e.g. ``"multi-file"``).

        Args:
            app_id: The application ID.
            input: The input data (JSON object) for the run. Used for
                JSON apps. Ignored when ``input_dir_path`` or
                ``managed_input_id`` is provided.
            input_dir_path: Path to a local directory containing input
                files. Use for multi-file or CSV archive apps. When
                provided, ``content_format`` must also be set.
            content_format: Content format of the input. Required when
                ``input_dir_path`` is set. Allowed values:
                ``"multi-file"``, ``"csv-archive"``, ``"json"``.
            instance_id: Instance to run against. Uses the application's
                default instance if omitted.
            run_options: Solver options passed to the application, e.g.
                ``{"solve.duration": "10s"}``.
            managed_input_id: ID of an existing managed input to use
                instead of the inline ``input`` data.
        """

        content_format = _helpers._none_if_empty(content_format)
        instance_id = _helpers._none_if_empty(instance_id)
        managed_input_id = _helpers._none_if_empty(managed_input_id)
        input_dir_path = _helpers._none_if_empty(input_dir_path)

        app = _helpers._get_app(app_id)
        config = _helpers._build_run_configuration(content_format)
        return submit_run(
            app,
            input=input,
            input_dir_path=input_dir_path,
            configuration=config,
            instance_id=instance_id,
            options=run_options,
            managed_input_id=managed_input_id,
        )

    @mcp.tool()
    def cloud_run_status(app_id: str, run_id: str) -> dict[str, Any]:
        """Get the status and metadata of a Nextmv Cloud run.

        Returns a dictionary with run metadata including status
        (``"queued"``, ``"running"``, ``"succeeded"``, ``"failed"``,
        ``"canceled"``), duration, timestamps, and error information.

        Args:
            app_id: The application ID.
            run_id: The run ID returned from ``cloud_run_submit``.
        """

        app = _helpers._get_app(app_id)
        return run_metadata(app, run_id=run_id)

    @mcp.tool()
    def cloud_run_result(app_id: str, run_id: str) -> str:
        """Get the full result of a completed Nextmv Cloud run.

        Saves the result (solution output, statistics, and metadata)
        to a local temp file. Use file-reading tools to inspect the
        contents.

        Args:
            app_id: The application ID.
            run_id: The run ID.
        """

        app = _helpers._get_app(app_id)
        endpoint = _helpers._endpoint_from_app(app)

        # Check cache.
        cached = _helpers._cloud_run_file_exists(endpoint, run_id, f"{run_id}.json")
        if cached:
            return f"Cached: {cached}"

        # Download. For non-JSON, extract output archive into cache.
        run_dir = _helpers._cloud_run_dir(endpoint, run_id)
        output_subdir = os.path.join(run_dir, OUTPUTS_KEY)
        result = run_result(app, run_id=run_id, output_dir_path=output_subdir)

        result_dict = result.to_dict()
        path = _helpers._save_cloud_run_file(
            result_dict, endpoint, run_id, f"{run_id}.json"
        )
        _helpers._extract_cloud_run_outputs(result_dict, endpoint, run_id)
        return f"Downloaded: {path}"

    @mcp.tool()
    def cloud_cancel_run(app_id: str, run_id: str) -> str:
        """Cancel a queued or running Nextmv Cloud run.

        The run must be in ``"queued"`` or ``"running"`` status.
        Already completed or canceled runs cannot be canceled.

        Args:
            app_id: The application ID.
            run_id: The run ID to cancel.
        """

        app = _helpers._get_app(app_id)
        cancel_run(app, run_id=run_id)
        return f"Cancelled run {run_id}"

    @mcp.tool()
    def cloud_list_runs(
        app_id: str,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """List runs for a Nextmv Cloud application.

        Returns a list of run metadata dictionaries. Optionally filter
        by status to retrieve only runs in a specific state.

        Args:
            app_id: The application ID.
            status: Optional status filter. Allowed values:
                ``"succeeded"``, ``"failed"``, ``"running"``,
                ``"queued"``, ``"canceled"``.
        """

        status = _helpers._none_if_empty(status)
        app = _helpers._get_app(app_id)
        return list_runs(app, status=status)

    @mcp.tool()
    def cloud_run_input(app_id: str, run_id: str) -> str:
        """Get the input data that was submitted to a Nextmv Cloud run.

        Saves the input to a local temp file. Use file-reading tools
        to inspect the contents.

        Args:
            app_id: The application ID.
            run_id: The run ID.
        """

        app = _helpers._get_app(app_id)
        endpoint = _helpers._endpoint_from_app(app)
        run_dir = _helpers._cloud_run_dir(endpoint, run_id)
        inputs_dir = os.path.join(run_dir, INPUTS_KEY)

        # Check cache: JSON input or multi-file inputs directory.
        cached_json = _helpers._cloud_run_file_exists(endpoint, run_id, INPUTS_KEY, "input.json")
        if cached_json:
            return f"Cached: {cached_json}"
        if os.path.isdir(inputs_dir) and os.listdir(inputs_dir):
            return f"Cached: {inputs_dir}"

        # Download. For non-JSON, the SDK extracts files into inputs_dir.
        data = run_input(app, run_id=run_id, output_dir_path=inputs_dir)
        if data is not None:
            # JSON input — save it.
            path = _helpers._save_cloud_run_file(data, endpoint, run_id, INPUTS_KEY, "input.json")
            return f"Downloaded: {path}"
        # Non-JSON: files were extracted into inputs_dir by the SDK.
        return f"Downloaded: {inputs_dir}"

    @mcp.tool()
    def cloud_run_logs(app_id: str, run_id: str) -> str:
        """Get a snapshot of the logs from a Nextmv Cloud run.

        Fetches the current log entries and saves them to a local temp
        file. For runs still in progress, use ``cloud_poll_run_logs``
        to stream logs continuously. Use file-reading tools to inspect
        the contents.

        Args:
            app_id: The application ID.
            run_id: The run ID.
        """

        app = _helpers._get_app(app_id)
        endpoint = _helpers._endpoint_from_app(app)

        # Check cache.
        cached = _helpers._cloud_run_file_exists(endpoint, run_id, LOGS_KEY, LOGS_FILE)
        if cached:
            return f"Cached: {cached}"

        logs = run_logs(app, run_id=run_id)
        path = _helpers._save_cloud_run_logs(
            logs.to_dict(), endpoint, run_id,
        )
        return f"Downloaded: {path}"

    @mcp.tool()
    def cloud_poll_run_logs(app_id: str, run_id: str) -> str:
        """Poll logs from an active Nextmv Cloud run until it completes.

        Unlike ``cloud_run_logs`` (which fetches a single snapshot),
        this tool polls the run continuously until it finishes and
        collects all log entries in chronological order. Useful for
        monitoring a run that is still in progress. Saves all collected
        logs to a local temp file. Use file-reading tools to inspect
        the contents.

        Args:
            app_id: The application ID.
            run_id: The run ID.
        """

        return _cloud_poll_run_logs_impl(app_id=app_id, run_id=run_id)
