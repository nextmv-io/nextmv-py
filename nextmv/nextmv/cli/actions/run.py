"""Core run management actions."""

from typing import Any

from nextmv.cloud import Application
from nextmv.polling import PollingOptions, default_polling_options
from nextmv.run import RunConfiguration, RunResult
from nextmv.status import StatusV2


def submit_run(
    app: Application,
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
    """Submit a run. Returns the run ID."""
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
    app: Application,
    input: Any | None = None,
    input_dir_path: str | None = None,
    configuration: RunConfiguration | None = None,
    instance_id: str | None = None,
    options: dict[str, str] | None = None,
    managed_input_id: str | None = None,
    polling_options: PollingOptions | None = None,
    output_dir_path: str | None = None,
) -> RunResult:
    """Submit a run and poll until complete. Returns the RunResult."""
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


def run_metadata(app: Application, run_id: str) -> dict[str, Any]:
    """Get run status and metadata."""
    return app.run_metadata(run_id=run_id).to_dict()


def run_result(app: Application, run_id: str, output_dir_path: str | None = None) -> RunResult:
    """Fetch the result of a completed run. Returns the RunResult."""
    return app.run_result(run_id=run_id, output_dir_path=output_dir_path)


def run_input(app: Application, run_id: str, output_dir_path: str | None = None) -> Any:
    """Fetch the input data for a run."""
    return app.run_input(run_id=run_id, output_dir_path=output_dir_path)


def run_logs(app: Application, run_id: str) -> Any:
    """Fetch log snapshot for a run."""
    return app.run_logs(run_id=run_id)


def cancel_run(app: Application, run_id: str) -> None:
    """Cancel a queued or running run."""
    app.cancel_run(run_id=run_id)


def list_runs(app: Application, status: str | None = None) -> list[dict[str, Any]]:
    """List runs, optionally filtered by status."""
    status_filter = StatusV2(status) if status else None
    return [r.to_dict() for r in app.list_runs(status=status_filter)]


def delete_run(app: Application, run_id: str) -> None:
    """Delete a run."""
    app.delete_run(run_id=run_id)
