"""Core run management actions.

Pure functions that wrap SDK calls. No CLI or MCP presentation concerns.

Each action takes ``client: Client`` as its first parameter so the CLI and
MCP frameworks can inject a client at call time. Actions that operate on a
specific application also accept an ``app_id`` and construct the
``Application`` internally — callers never need to build cloud handles.
"""

from typing import Any

from nextmv.cli.framework.options import (
    AppIdRequiredOption,
    RunIdOption,
)
from nextmv.cloud import Application, Client
from nextmv.polling import PollingOptions, default_polling_options
from nextmv.run import RunConfiguration, RunResult
from nextmv.status import StatusV2


def submit_run(
    client: Client,
    app_id: AppIdRequiredOption,
    input: Any | None = None,
    input_dir_path: str | None = None,
    configuration: RunConfiguration | None = None,
    instance_id: str | None = None,
    options: dict[str, str] | None = None,
    managed_input_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    upload_id: str | None = None,
) -> str:
    """Submit a run to a Nextmv Cloud application.

    Returns the run ID immediately without waiting for completion. Use
    ``run_metadata`` to poll for status or ``run_result`` to fetch the
    final output once the run has finished.
    """
    app = Application(client=client, id=app_id)
    return app.new_run(
        input=input,
        input_dir_path=input_dir_path,
        configuration=configuration,
        instance_id=instance_id,
        options=options or {},
        managed_input_id=managed_input_id,
        name=name,
        description=description,
        upload_id=upload_id,
    )


def submit_run_with_result(
    client: Client,
    app_id: AppIdRequiredOption,
    input: Any | None = None,
    input_dir_path: str | None = None,
    configuration: RunConfiguration | None = None,
    instance_id: str | None = None,
    options: dict[str, str] | None = None,
    managed_input_id: str | None = None,
    polling_options: PollingOptions | None = None,
    output_dir_path: str | None = None,
) -> RunResult:
    """Submit a run to a Nextmv Cloud application and wait for the result.

    Polls the run until it finishes (or the poll timeout expires) and
    returns the ``RunResult`` object.
    """
    app = Application(client=client, id=app_id)
    return app.new_run_with_result(
        input=input,
        input_dir_path=input_dir_path,
        configuration=configuration,
        instance_id=instance_id,
        run_options=options or {},
        polling_options=polling_options or default_polling_options(),
        managed_input_id=managed_input_id,
        output_dir_path=output_dir_path,
    )


def run_metadata(
    client: Client,
    app_id: AppIdRequiredOption,
    run_id: RunIdOption,
) -> dict[str, Any]:
    """Get the metadata of a Nextmv Cloud application run.

    Returns a dictionary with run metadata including status, duration,
    timestamps, and error information.
    """
    app = Application(client=client, id=app_id)
    return app.run_metadata(run_id=run_id).to_dict()


def run_result(
    client: Client,
    app_id: AppIdRequiredOption,
    run_id: RunIdOption,
    output_dir_path: str | None = None,
) -> RunResult:
    """Fetch the result of a completed Nextmv Cloud run.

    Returns the ``RunResult`` containing the solution output, statistics,
    and run metadata. For multi-file or CSV archive apps, pass
    ``output_dir_path`` so the SDK extracts the downloaded files into a
    directory on disk.
    """
    app = Application(client=client, id=app_id)
    return app.run_result(run_id=run_id, output_dir_path=output_dir_path)


def run_input(
    client: Client,
    app_id: AppIdRequiredOption,
    run_id: RunIdOption,
    output_dir_path: str | None = None,
) -> Any:
    """Fetch the input data that was submitted to a Nextmv Cloud run.

    For JSON apps the input is returned inline. For multi-file or CSV
    archive apps, pass ``output_dir_path`` so the SDK extracts the
    downloaded files into a directory on disk (``None`` is returned in
    that case).
    """
    app = Application(client=client, id=app_id)
    return app.run_input(run_id=run_id, output_dir_path=output_dir_path)


def run_logs(
    client: Client,
    app_id: AppIdRequiredOption,
    run_id: RunIdOption,
) -> Any:
    """Fetch a snapshot of the logs from a Nextmv Cloud run.

    Returns the ``RunLog`` object exposing the collected log text. For
    runs still in progress this returns whatever has been captured so
    far.
    """
    app = Application(client=client, id=app_id)
    return app.run_logs(run_id=run_id)


def cancel_run(
    client: Client,
    app_id: AppIdRequiredOption,
    run_id: RunIdOption,
) -> None:
    """Cancel a queued or running Nextmv Cloud run.

    The run must be in ``queued`` or ``running`` status. Already
    completed or canceled runs cannot be canceled.
    """
    app = Application(client=client, id=app_id)
    app.cancel_run(run_id=run_id)


def list_runs(
    client: Client,
    app_id: AppIdRequiredOption,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """List runs for a Nextmv Cloud application.

    Returns a list of run metadata dicts. Optionally filter by status
    to retrieve only runs in a specific state (e.g. ``"succeeded"``,
    ``"failed"``, ``"running"``, ``"queued"``, ``"canceled"``).
    """
    app = Application(client=client, id=app_id)
    status_filter = StatusV2(status) if status else None
    return [r.to_dict() for r in app.list_runs(status=status_filter)]


def delete_run(
    client: Client,
    app_id: AppIdRequiredOption,
    run_id: RunIdOption,
) -> None:
    """Delete a Nextmv Cloud application run permanently.

    This action cannot be undone.
    """
    app = Application(client=client, id=app_id)
    app.delete_run(run_id=run_id)
