"""Core batch experiment actions.

Pure functions that wrap SDK calls. No CLI or MCP concerns.
"""

from typing import Any

from nextmv.cloud import Application, Client


def list_batches(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all batch experiments for an application."""
    app = Application(client=client, id=app_id)
    batches = app.list_batch_experiments()
    return [b.to_dict() for b in batches]


def get_batch(client: Client, app_id: str, batch_id: str) -> dict[str, Any]:
    """Get a batch experiment including its runs."""
    app = Application(client=client, id=app_id)
    batch = app.batch_experiment(batch_id=batch_id)
    return batch.to_dict()


def batch_metadata(client: Client, app_id: str, batch_id: str) -> dict[str, Any]:
    """Get metadata for a batch experiment."""
    app = Application(client=client, id=app_id)
    metadata = app.batch_experiment_metadata(batch_id=batch_id)
    return metadata.to_dict()


def create_batch(
    client: Client,
    app_id: str,
    input_set_id: str,
    name: str | None = None,
    description: str | None = None,
    option_sets: dict[str, dict[str, str]] | None = None,
) -> str:
    """Create a batch experiment. Returns the batch experiment ID."""
    app = Application(client=client, id=app_id)
    return app.new_batch_experiment(
        input_set_id=input_set_id,
        name=name,
        description=description,
        option_sets=option_sets,
    )


def delete_batch(client: Client, app_id: str, batch_id: str) -> None:
    """Delete a batch experiment."""
    app = Application(client=client, id=app_id)
    app.delete_batch_experiment(batch_id=batch_id)
