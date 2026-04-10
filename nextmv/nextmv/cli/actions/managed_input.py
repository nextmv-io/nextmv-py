"""Core managed input management actions.

Pure functions that wrap SDK calls. No CLI or MCP concerns.
"""

from typing import Any

from nextmv.cloud import Application, Client


def list_managed_inputs(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all managed inputs for an application."""
    app = Application(client=client, id=app_id)
    return [i.to_dict() for i in app.list_managed_inputs()]


def get_managed_input(client: Client, app_id: str, managed_input_id: str) -> dict[str, Any]:
    """Get a managed input by ID."""
    app = Application(client=client, id=app_id)
    return app.managed_input(managed_input_id=managed_input_id).to_dict()


def create_managed_input(
    client: Client,
    app_id: str,
    data: dict[str, Any] | None = None,
    managed_input_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    upload_id: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Create a new managed input.

    Provide one of: ``data`` (raw JSON to upload), ``upload_id``, or ``run_id``.
    If ``data`` is provided, it is uploaded via a pre-signed URL first.
    """
    app = Application(client=client, id=app_id)

    if data is not None:
        upload_url = app.upload_url()
        app.upload_data(upload_url=upload_url, data=data)
        upload_id = upload_url.upload_id

    return app.new_managed_input(
        id=managed_input_id,
        name=name,
        description=description,
        upload_id=upload_id,
        run_id=run_id,
    ).to_dict()


def delete_managed_input(client: Client, app_id: str, managed_input_id: str) -> None:
    """Delete a managed input."""
    app = Application(client=client, id=app_id)
    app.delete_managed_input(managed_input_id=managed_input_id)
