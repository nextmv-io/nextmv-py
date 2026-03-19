"""MCP tools for cloud run management."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.mcp.tools import _helpers
from nextmv.polling import default_polling_options


def _cloud_list_runs_impl(
    app_id: str,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """Implementation for listing cloud runs."""

    from nextmv.status import StatusV2

    app = _helpers._get_app(app_id)
    status_filter = StatusV2(status) if status else None
    runs = app.list_runs(status=status_filter)
    return [r.to_dict() for r in runs]


def _cloud_poll_run_logs_impl(app_id: str, run_id: str) -> str:
    """Implementation for polling cloud run logs."""

    collected: list[dict[str, Any]] = []

    def _collect(log_entry) -> None:
        collected.append({"timestamp": log_entry.timestamp, "log": log_entry.log})

    app = _helpers._get_app(app_id)
    app.poll_logs(
        run_id=run_id,
        polling_options=default_polling_options(),
        log_func=_collect,
    )
    return _helpers._save_to_file(collected, prefix=f"poll_logs_{run_id}")


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
        config = _helpers._build_run_configuration(content_format)
        result = app.new_run_with_result(
            input=input,
            input_dir_path=input_dir_path,
            configuration=config,
            instance_id=instance_id,
            run_options=run_options or {},
            polling_options=default_polling_options(),
            managed_input_id=managed_input_id,
        )
        return _helpers._save_to_file(result.to_dict(), prefix=f"cloud_run_{app_id}")

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
        return app.new_run(
            input=input,
            input_dir_path=input_dir_path,
            configuration=config,
            instance_id=instance_id,
            options=run_options or {},
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
        metadata = app.run_metadata(run_id=run_id)
        return metadata.to_dict()

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
        result = app.run_result(run_id=run_id)
        return _helpers._save_to_file(result.to_dict(), prefix=f"run_result_{run_id}")

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
        app.cancel_run(run_id=run_id)
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

        return _cloud_list_runs_impl(app_id=app_id, status=status)

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
        data = app.run_input(run_id=run_id)
        return _helpers._save_to_file(data, prefix=f"run_input_{run_id}")

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
        logs = app.run_logs(run_id=run_id)
        return _helpers._save_to_file(logs.to_dict(), prefix=f"run_logs_{run_id}")

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
