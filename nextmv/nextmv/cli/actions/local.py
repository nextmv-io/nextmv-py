"""Core local application actions."""

from typing import Any

from nextmv import local
from nextmv.cloud import Application
from nextmv.content_format import ContentFormat
from nextmv.manifest import ManifestType, initialize_manifest
from nextmv.polling import PollingOptions, default_polling_options
from nextmv.run import RunConfiguration
from nextmv.status import StatusV2


def new_local_run(
    app: local.Application,
    input: Any | None = None,
    input_dir_path: str | None = None,
    configuration: RunConfiguration | None = None,
    options: dict[str, str] | None = None,
    name: str | None = None,
    description: str | None = None,
) -> str:
    """Submit a local run. Returns the run ID."""
    return app.new_run(
        input=input,
        input_dir_path=input_dir_path,
        configuration=configuration,
        options=options,
        name=name,
        description=description,
    )


def new_local_run_with_result(
    app: local.Application,
    input: Any | None = None,
    input_dir_path: str | None = None,
    configuration: RunConfiguration | None = None,
    run_options: dict[str, str] | None = None,
    polling_options: PollingOptions | None = None,
    output_dir_path: str | None = None,
    name: str | None = None,
    description: str | None = None,
):
    """Submit a local run and poll until complete. Returns the RunResult."""
    return app.new_run_with_result(
        input=input,
        input_dir_path=input_dir_path,
        configuration=configuration,
        run_options=run_options,
        polling_options=polling_options or default_polling_options(),
        output_dir_path=output_dir_path,
        name=name,
        description=description,
    )


def local_run_poll_result(
    app: local.Application,
    run_id: str,
    polling_options: PollingOptions | None = None,
    output_dir_path: str | None = None,
):
    """Poll a local run until complete. Returns the RunResult."""
    return app.run_result_with_polling(
        run_id=run_id,
        polling_options=polling_options or default_polling_options(),
        output_dir_path=output_dir_path,
    )


def local_run_metadata(app: local.Application, run_id: str) -> dict[str, Any]:
    """Get metadata for a local run as a dict."""
    return app.run_metadata(run_id=run_id).to_dict()


def local_list_runs(
    app: local.Application,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """List runs for a local application, optionally filtered by status."""
    status_filter = StatusV2(status) if status else None
    return [r.to_dict() for r in app.list_runs(status=status_filter)]


def local_run_result(
    app: local.Application,
    run_id: str,
    output_dir_path: str | None = None,
):
    """Fetch the result of a completed local run. Returns the RunResult."""
    return app.run_result(run_id=run_id, output_dir_path=output_dir_path)


def local_run_input(
    app: local.Application,
    run_id: str,
    output_dir_path: str | None = None,
):
    """Fetch the input for a local run."""
    return app.run_input(run_id=run_id, output_dir_path=output_dir_path)


def local_run_logs(app: local.Application, run_id: str) -> str:
    """Fetch the logs for a local run."""
    return app.run_logs(run_id=run_id)


def local_sync(
    app: local.Application,
    target: Application,
    run_ids: list[str] | None = None,
    instance_id: str | None = None,
    verbose: bool = False,
    rich_print: bool = False,
) -> None:
    """Sync local runs to a cloud application."""
    app.sync(
        target=target,
        run_ids=run_ids,
        instance_id=instance_id,
        verbose=verbose,
        rich_print=rich_print,
    )


def manifest_init(
    manifest_type: str,
    content_format: str,
    dirpath: str = ".",
) -> str:
    """Initialize an app.yaml manifest. Returns the path to the created file."""
    return initialize_manifest(
        manifest_type=ManifestType(manifest_type),
        content_format=ContentFormat(content_format),
        dirpath=dirpath,
    )
