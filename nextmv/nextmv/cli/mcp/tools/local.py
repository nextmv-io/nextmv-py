"""MCP tools for local application management."""

import json
import os
import subprocess
import tempfile
from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.mcp.tools import _helpers
from nextmv.polling import default_polling_options


def _local_run_dir(app_dir: str, run_id: str) -> str:
    """Return the path to a local run directory."""

    from nextmv.local.local import NEXTMV_DIR, RUNS_KEY

    return os.path.join(app_dir, NEXTMV_DIR, RUNS_KEY, run_id)


def _run_via_cli(
    app_dir: str,
    input_data: dict[str, Any],
    run_options: dict[str, str] | None = None,
    wait: bool = False,
) -> str:
    """Execute a local run via ``uv run nextmv local run create``.

    This invokes the Nextmv CLI through ``uv``, which ensures that
    the application's ``requirements.txt`` dependencies are installed
    and available at runtime (unlike calling the SDK directly with
    ``sys.executable``).

    Args:
        app_dir: Absolute path to the local application directory.
        input_data: The input data (JSON object) for the run.
        run_options: Optional solver options passed as ``--options key=value``.
        wait: If True, blocks until the run completes (``--wait``).

    Returns:
        The run ID (parsed from the CLI's JSON stdout output).

    Raises:
        RuntimeError: If the CLI process exits with a non-zero return code.
    """

    # Write input to a temp file so the CLI can read it via --input.
    fd, input_path = tempfile.mkstemp(suffix=".json", prefix="mcp_local_input_")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(input_data, fh)

        cmd: list[str] = [
            "uv", "run", "nextmv",
            "local", "run", "create",
            "--app-src", os.path.abspath(app_dir),
            "--input", input_path,
        ]

        if run_options:
            for key, value in run_options.items():
                cmd.extend(["--options", f"{key}={value}"])

        if wait:
            cmd.append("--wait")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            env=os.environ,
        )

        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise RuntimeError(
                f"nextmv local run create failed (exit {result.returncode}): {stderr}"
            )

        # The CLI prints JSON with a "run_id" key to stdout when not
        # waiting, or the full result when waiting.
        stdout = result.stdout.strip()
        try:
            parsed = json.loads(stdout)
            if isinstance(parsed, dict) and "run_id" in parsed:
                return parsed["run_id"]
        except json.JSONDecodeError:
            pass

        # When --wait is used the CLI may print the run_id via a
        # success message to stderr. Fall back to extracting the
        # run_id from the run directory listing.
        from nextmv.local.local import NEXTMV_DIR, RUNS_KEY

        runs_dir = os.path.join(
            os.path.abspath(app_dir), NEXTMV_DIR, RUNS_KEY,
        )
        if os.path.isdir(runs_dir):
            entries = sorted(
                os.listdir(runs_dir),
                key=lambda d: os.path.getmtime(
                    os.path.join(runs_dir, d)
                ),
            )
            if entries:
                return entries[-1]

        raise RuntimeError(
            f"Could not determine run_id from CLI output: {stdout}"
        )
    finally:
        # Clean up the temp input file.
        if os.path.exists(input_path):
            os.unlink(input_path)


def _local_run_input_impl(
    app_dir: str,
    run_id: str,
    app_id: str | None = None,
) -> str:
    """Implementation for getting the input data of a local run."""

    from nextmv.input import INPUTS_KEY
    from nextmv.local.local import DEFAULT_INPUT_JSON_FILE

    run_dir = _local_run_dir(app_dir, run_id)
    input_path = os.path.join(run_dir, INPUTS_KEY, DEFAULT_INPUT_JSON_FILE)
    if not os.path.exists(input_path):
        # Fall back to the SDK method for non-JSON inputs or
        # if the file doesn't exist at the expected path.
        app = _helpers._get_local_app(app_dir=app_dir, app_id=app_id)
        data = app.run_input(run_id=run_id)
        return _helpers._save_to_file(data, prefix=f"local_run_input_{run_id}")
    return f"Data saved to {input_path} — use file-reading tools to inspect the contents."


def _local_run_logs_impl(
    app_dir: str,
    run_id: str,
) -> str:
    """Implementation for getting the logs of a local run."""

    from nextmv.local.local import LOGS_FILE, LOGS_KEY

    run_dir = _local_run_dir(app_dir, run_id)
    logs_path = os.path.join(run_dir, LOGS_KEY, LOGS_FILE)
    if not os.path.exists(logs_path):
        return "No logs available for this run."
    return f"Data saved to {logs_path} — use file-reading tools to inspect the contents."


def local_run(
    app_dir: str,
    input: dict[str, Any],
    run_options: dict[str, str] | None = None,
) -> str:
    """Run a local Nextmv application and wait for the result.

    Executes the application via ``uv run nextmv local run create
    --wait``, which handles dependency installation (e.g.
    requirements.txt) automatically. The result is stored in the
    local run directory at ``{app_dir}/.nextmv/runs/{run_id}/``.
    Use file-reading tools to inspect the result file.

    Args:
        app_dir: Absolute path to the local application directory
            containing an app.yaml manifest.
        input: The input data (JSON object) for the optimization run.
        run_options: Optional solver options passed to the application,
            e.g. ``{"solve.duration": "10s"}``.
    """

    run_id = _run_via_cli(
        app_dir=app_dir,
        input_data=input,
        run_options=run_options,
        wait=True,
    )
    run_dir = _local_run_dir(app_dir, run_id)
    result_path = os.path.join(run_dir, f"{run_id}.json")
    return (
        f"Run completed. Result saved to {result_path} "
        "— use file-reading tools to inspect the contents."
    )


def local_run_submit(
    app_dir: str,
    input: dict[str, Any],
    run_options: dict[str, str] | None = None,
) -> str:
    """Submit a local run without waiting for completion.

    Executes the application via ``uv run nextmv local run create``
    (non-blocking). Returns the run ID immediately. Use
    ``local_run_poll_result`` or ``local_run_status`` to check on
    the run later.

    Args:
        app_dir: Absolute path to the local application directory
            containing an app.yaml manifest.
        input: The input data (JSON object) for the run.
        run_options: Optional solver options passed to the application,
            e.g. ``{"solve.duration": "10s"}``.
    """

    return _run_via_cli(
        app_dir=app_dir,
        input_data=input,
        run_options=run_options,
        wait=False,
    )


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
    metadata = app.run_metadata(run_id=run_id)
    return metadata.to_dict()


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
    app.run_metadata(run_id=run_id)
    result_path = os.path.join(_local_run_dir(app_dir, run_id), f"{run_id}.json")
    return f"Data saved to {result_path} — use file-reading tools to inspect the contents."


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
    app.run_result_with_polling(
        run_id=run_id,
        polling_options=default_polling_options(),
    )
    result_path = os.path.join(_local_run_dir(app_dir, run_id), f"{run_id}.json")
    return f"Data saved to {result_path} — use file-reading tools to inspect the contents."


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
    runs = app.list_runs()
    return [r.to_dict() for r in runs]


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

    local_app = _helpers._get_local_app(app_dir=app_dir, app_id=app_id)
    cloud_target = _helpers._get_app(cloud_app_id)
    local_app.sync(
        target=cloud_target,
        run_ids=run_ids,
        instance_id=instance_id,
    )
    return f"Synced local runs to cloud application {cloud_app_id}"


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

    from nextmv.content_format import ContentFormat
    from nextmv.manifest import ManifestType, initialize_manifest

    dst = initialize_manifest(
        manifest_type=ManifestType(manifest_type),
        content_format=ContentFormat(content_format),
        dirpath=dirpath,
    )
    return f"Manifest initialized at {dst}"


def register(mcp: FastMCP) -> None:
    """Register local application tools."""

    mcp.tool()(local_run)
    mcp.tool()(local_run_submit)
    mcp.tool()(local_run_status)
    mcp.tool()(local_run_result)
    mcp.tool()(local_run_poll_result)
    mcp.tool()(local_list_runs)
    mcp.tool()(local_run_input)
    mcp.tool()(local_run_logs)
    mcp.tool()(local_sync)
    mcp.tool()(manifest_init)
