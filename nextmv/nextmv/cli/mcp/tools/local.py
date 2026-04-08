"""MCP tools for local application management."""

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.local import (
    local_list_runs as _local_list_runs_action,
    local_run_metadata as _local_run_metadata_action,
    local_run_poll_result as _local_run_poll_result_action,
    local_sync as _local_sync_action,
    manifest_init as _manifest_init_action,
    new_local_run,
)
from nextmv.cli.mcp.tools import _helpers
from nextmv.input import INPUTS_KEY
from nextmv.local.local import DEFAULT_INPUT_JSON_FILE, LOGS_FILE, LOGS_KEY, NEXTMV_DIR, RUNS_KEY


def _local_run_dir(app_dir: str, run_id: str) -> str:
    """Return the path to a local run directory."""

    return os.path.join(app_dir, NEXTMV_DIR, RUNS_KEY, run_id)


def _local_run_input_impl(
    app_dir: str,
    run_id: str,
    app_id: str | None = None,
) -> str:
    """Implementation for getting the input data of a local run."""

    run_dir = _local_run_dir(app_dir, run_id)
    input_path = os.path.join(run_dir, INPUTS_KEY, DEFAULT_INPUT_JSON_FILE)
    if not os.path.exists(input_path):
        # Fall back to the SDK method for non-JSON inputs or
        # if the file doesn't exist at the expected path.
        app = _helpers._get_local_app(app_dir=app_dir, app_id=app_id)
        data = app.run_input(run_id=run_id)
        return _helpers._save_to_json_file(data, prefix=f"local_run_input_{run_id}")
    return f"Data saved to {input_path} — use file-reading tools to inspect the contents."


def _local_run_logs_impl(
    app_dir: str,
    run_id: str,
) -> str:
    """Implementation for getting the logs of a local run (path-based)."""

    run_dir = _local_run_dir(app_dir, run_id)
    logs_path = os.path.join(run_dir, LOGS_KEY, LOGS_FILE)
    if not os.path.exists(logs_path):
        return "No logs available for this run."
    return f"Data saved to {logs_path} — use file-reading tools to inspect the contents."


def _local_run_impl(
    app_dir: str,
    input: dict[str, Any] | None,
    input_dir_path: str | None,
    content_format: str | None,
    run_options: dict[str, str] | None,
) -> str:
    """Implementation for local_run."""

    content_format = _helpers._none_if_empty(content_format)
    input_dir_path = _helpers._none_if_empty(input_dir_path)

    app = _helpers._get_local_app(app_dir=app_dir)
    config = _helpers._build_run_configuration(content_format)
    run_id = new_local_run(
        app=app,
        input=input if input_dir_path is None else None,
        input_dir_path=input_dir_path,
        configuration=config,
        options=run_options,
    )
    _local_run_poll_result_action(app=app, run_id=run_id)
    run_dir = _local_run_dir(app_dir, run_id)
    result_path = os.path.join(run_dir, f"{run_id}.json")
    return (
        f"Run completed. Result saved to {result_path} "
        "— use file-reading tools to inspect the contents."
    )


def _local_run_submit_impl(
    app_dir: str,
    input: dict[str, Any] | None,
    input_dir_path: str | None,
    content_format: str | None,
    run_options: dict[str, str] | None,
) -> str:
    """Implementation for local_run_submit."""

    content_format = _helpers._none_if_empty(content_format)
    input_dir_path = _helpers._none_if_empty(input_dir_path)

    app = _helpers._get_local_app(app_dir=app_dir)
    config = _helpers._build_run_configuration(content_format)
    return new_local_run(
        app=app,
        input=input if input_dir_path is None else None,
        input_dir_path=input_dir_path,
        configuration=config,
        options=run_options,
    )


def _local_sync_impl(
    app_dir: str,
    cloud_app_id: str,
    app_id: str | None,
    instance_id: str | None,
    run_ids: list[str] | None,
) -> str:
    """Implementation for local_sync."""

    app_id = _helpers._none_if_empty(app_id)
    instance_id = _helpers._none_if_empty(instance_id)

    local_app = _helpers._get_local_app(app_dir=app_dir, app_id=app_id)
    cloud_target = _helpers._get_app(cloud_app_id)
    _local_sync_action(
        app=local_app,
        target=cloud_target,
        run_ids=run_ids,
        instance_id=instance_id,
    )
    return f"Synced local runs to cloud application {cloud_app_id}"


def _manifest_init_impl(
    manifest_type: str,
    content_format: str,
    dirpath: str,
) -> str:
    """Implementation for manifest_init."""

    dst = _manifest_init_action(
        manifest_type=manifest_type,
        content_format=content_format,
        dirpath=dirpath,
    )
    return f"Manifest initialized at {dst}"


def register(mcp: FastMCP) -> None:
    """Register local application tools."""

    # Split into two functions to stay under the C901 complexity limit
    # (10 @mcp.tool closures in a single function body exceeds it).
    _register_run_tools(mcp)
    _register_management_tools(mcp)


def _register_run_tools(mcp: FastMCP) -> None:
    """Register local run tools."""

    @mcp.tool()
    def local_run(
        app_dir: str,
        input: dict[str, Any] | None = None,
        input_dir_path: str | None = None,
        content_format: str | None = None,
        run_options: dict[str, str] | None = None,
    ) -> str:
        """Run a local Nextmv application and wait for the result.

        Executes the application using the Nextmv SDK and polls until the
        run completes. The result is stored in the local run directory at
        ``{app_dir}/.nextmv/runs/{run_id}/``. Use file-reading tools to
        inspect the result file.

        For JSON apps, provide ``input`` as a JSON object. For multi-file
        or CSV archive apps, provide ``input_dir_path`` pointing to a
        directory of input files and set ``content_format`` accordingly
        (e.g. ``"multi-file"`` or ``"csv-archive"``).

        Args:
            app_dir: Absolute path to the local application directory
                containing an app.yaml manifest.
            input: The input data (JSON object) for the run. Used for
                JSON apps. Ignored when ``input_dir_path`` is provided.
            input_dir_path: Path to a directory containing input files.
                Use for multi-file or CSV archive apps. When provided,
                ``content_format`` must also be set.
            content_format: Content format of the input. Required when
                ``input_dir_path`` is set. Allowed values:
                ``"multi-file"``, ``"csv-archive"``, ``"json"``.
            run_options: Optional solver options passed to the application,
                e.g. ``{"solve.duration": "10s"}``.
        """

        return _local_run_impl(
            app_dir=app_dir,
            input=input,
            input_dir_path=input_dir_path,
            content_format=content_format,
            run_options=run_options,
        )

    @mcp.tool()
    def local_run_submit(
        app_dir: str,
        input: dict[str, Any] | None = None,
        input_dir_path: str | None = None,
        content_format: str | None = None,
        run_options: dict[str, str] | None = None,
    ) -> str:
        """Submit a local run without waiting for completion.

        Executes the application using the Nextmv SDK and returns the run
        ID immediately. Use ``local_run_poll_result`` or
        ``local_run_status`` to check on the run later.

        For JSON apps, provide ``input`` as a JSON object. For multi-file
        or CSV archive apps, provide ``input_dir_path`` pointing to a
        directory of input files and set ``content_format`` accordingly
        (e.g. ``"multi-file"`` or ``"csv-archive"``).

        Args:
            app_dir: Absolute path to the local application directory
                containing an app.yaml manifest.
            input: The input data (JSON object) for the run. Used for
                JSON apps. Ignored when ``input_dir_path`` is provided.
            input_dir_path: Path to a directory containing input files.
                Use for multi-file or CSV archive apps. When provided,
                ``content_format`` must also be set.
            content_format: Content format of the input. Required when
                ``input_dir_path`` is set. Allowed values:
                ``"multi-file"``, ``"csv-archive"``, ``"json"``.
            run_options: Optional solver options passed to the application,
                e.g. ``{"solve.duration": "10s"}``.
        """

        return _local_run_submit_impl(
            app_dir=app_dir,
            input=input,
            input_dir_path=input_dir_path,
            content_format=content_format,
            run_options=run_options,
        )

    @mcp.tool()
    def local_run_status(
        app_dir: str,
        run_id: str,
        app_id: str | None = None,
    ) -> dict[str, Any]:
        """Get the status and metadata of a local run.

        Returns a dictionary with run metadata including status, duration,
        timestamps, and error information (if any).

        Args:
            app_dir: Absolute path to the local application directory.
            run_id: The run ID to look up.
            app_id: Optional application ID for registry lookup.
        """

        app = _helpers._get_local_app(app_dir=app_dir, app_id=app_id)
        return _local_run_metadata_action(app=app, run_id=run_id)

    @mcp.tool()
    def local_run_result(
        app_dir: str,
        run_id: str,
        app_id: str | None = None,
    ) -> str:
        """Get the file path to the result of a completed local run.

        Validates that the run exists, then returns the path to the
        run result JSON file. Use file-reading tools to inspect the
        contents.

        Args:
            app_dir: Absolute path to the local application directory.
            run_id: The run ID.
            app_id: Optional application ID for registry lookup.
        """

        # Validate the run exists by calling run_metadata.
        app = _helpers._get_local_app(app_dir=app_dir, app_id=app_id)
        _local_run_metadata_action(app=app, run_id=run_id)
        result_path = os.path.join(_local_run_dir(app_dir, run_id), f"{run_id}.json")
        return f"Data saved to {result_path} — use file-reading tools to inspect the contents."

    @mcp.tool()
    def local_run_poll_result(
        app_dir: str,
        run_id: str,
        app_id: str | None = None,
    ) -> str:
        """Poll a local run until it completes and return the result path.

        Use this after ``local_run_submit`` to wait for a previously
        submitted run to finish. Returns the path to the run result
        JSON file. Use file-reading tools to inspect the contents.

        Args:
            app_dir: Absolute path to the local application directory.
            run_id: The run ID returned from ``local_run_submit``.
            app_id: Optional application ID for registry lookup.
        """

        app = _helpers._get_local_app(app_dir=app_dir, app_id=app_id)
        _local_run_poll_result_action(app=app, run_id=run_id)
        result_path = os.path.join(_local_run_dir(app_dir, run_id), f"{run_id}.json")
        return f"Data saved to {result_path} — use file-reading tools to inspect the contents."


def _register_management_tools(mcp: FastMCP) -> None:
    """Register local management tools."""

    @mcp.tool()
    def local_list_runs(
        app_dir: str,
        app_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """List all runs for a local Nextmv application.

        Returns a list of run metadata dictionaries, each containing
        the run ID, status, timestamps, and other metadata.

        Args:
            app_dir: Absolute path to the local application directory.
            app_id: Optional application ID for registry lookup.
        """

        app = _helpers._get_local_app(app_dir=app_dir, app_id=app_id)
        return _local_list_runs_action(app=app)

    @mcp.tool()
    def local_run_input(
        app_dir: str,
        run_id: str,
        app_id: str | None = None,
    ) -> str:
        """Get the file path to the input data of a local run.

        Returns the path to the input JSON file stored in the local
        run directory. Falls back to saving a temp file for non-JSON
        inputs. Use file-reading tools to inspect the contents.

        Args:
            app_dir: Absolute path to the local application directory.
            run_id: The run ID.
            app_id: Optional application ID for registry lookup.
        """

        return _local_run_input_impl(app_dir=app_dir, run_id=run_id, app_id=app_id)

    @mcp.tool()
    def local_run_logs(
        app_dir: str,
        run_id: str,
        app_id: str | None = None,
    ) -> str:
        """Get the file path to the logs of a local run.

        Returns the path to the logs file stored in the local run
        directory. Use file-reading tools to inspect the contents.
        Returns a message if no logs are available.

        Args:
            app_dir: Absolute path to the local application directory.
            run_id: The run ID.
            app_id: Optional application ID for registry lookup.
        """

        return _local_run_logs_impl(app_dir=app_dir, run_id=run_id)

    @mcp.tool()
    def local_sync(
        app_dir: str,
        cloud_app_id: str,
        app_id: str | None = None,
        instance_id: str | None = None,
        run_ids: list[str] | None = None,
    ) -> str:
        """Sync local runs to a Nextmv Cloud application.

        Uploads local run data (inputs, outputs, metadata) to a cloud
        application for tracking, comparison, and experiment purposes.

        Args:
            app_dir: Absolute path to the local application directory.
            cloud_app_id: The cloud application ID to sync to.
            app_id: Optional local application ID for registry lookup.
            instance_id: Optional cloud instance ID to tag the synced runs.
            run_ids: Optional list of specific run IDs to sync. If omitted,
                all local runs are synced.
        """

        return _local_sync_impl(
            app_dir=app_dir,
            cloud_app_id=cloud_app_id,
            app_id=app_id,
            instance_id=instance_id,
            run_ids=run_ids,
        )

    @mcp.tool()
    def manifest_init(
        manifest_type: str,
        content_format: str,
        dirpath: str = ".",
    ) -> str:
        """Initialize an app.yaml manifest file in a local directory.

        Creates a sample app.yaml manifest file for a Nextmv application.
        If the directory does not exist it will be created. An existing
        manifest file in the directory will be overwritten.

        Args:
            manifest_type: The application type. Allowed values:
                ``"python"``, ``"go"``, ``"java"``, ``"binary"``.
            content_format: The content format for app input/output.
                Allowed values: ``"json"``, ``"multi-file"``.
            dirpath: Directory where the manifest will be written.
                Defaults to the current directory.
        """

        return _manifest_init_impl(
            manifest_type=manifest_type,
            content_format=content_format,
            dirpath=dirpath,
        )
