"""Core input set management actions.

Pure functions that wrap SDK calls. No CLI or MCP concerns.
"""

from typing import Any

from nextmv.cloud import Application, Client


def list_input_sets(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all input sets for an application."""
    app = Application(client=client, id=app_id)
    return [s.to_dict() for s in app.list_input_sets()]


def get_input_set(client: Client, app_id: str, input_set_id: str) -> dict[str, Any]:
    """Get input set details."""
    app = Application(client=client, id=app_id)
    return app.input_set(input_set_id=input_set_id).to_dict()


def create_input_set(
    client: Client,
    app_id: str,
    input_set_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    instance_id: str | None = None,
    maximum_runs: int | None = None,
    run_ids: list[str] | None = None,
    managed_input_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Create a new input set. Returns the input set dict."""
    from nextmv.cloud.input_set import ManagedInput

    app = Application(client=client, id=app_id)

    inputs = None
    if managed_input_ids is not None:
        inputs = [ManagedInput(id=mid) for mid in managed_input_ids]

    return app.new_input_set(
        id=input_set_id,
        name=name,
        description=description,
        instance_id=instance_id,
        maximum_runs=maximum_runs,
        run_ids=run_ids,
        inputs=inputs,
    ).to_dict()


def update_input_set(
    client: Client,
    app_id: str,
    input_set_id: str,
    name: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Update an input set's name or description. Returns the updated input set dict."""
    app = Application(client=client, id=app_id)
    return app.update_input_set(id=input_set_id, name=name, description=description).to_dict()


def delete_input_set(client: Client, app_id: str, input_set_id: str) -> None:
    """Delete an input set."""
    app = Application(client=client, id=app_id)
    app.delete_input_set(input_set_id=input_set_id)
