"""Core secrets management actions.

Pure functions that wrap SDK calls. No CLI or MCP concerns.
"""

from typing import Any

from nextmv.cloud import Application, Client


def list_secrets_collections(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all secrets collections for an application."""
    app = Application(client=client, id=app_id)
    return [c.to_dict() for c in app.list_secrets_collections()]


def get_secrets_collection(client: Client, app_id: str, secrets_collection_id: str) -> dict[str, Any]:
    """Get a secrets collection by ID."""
    app = Application(client=client, id=app_id)
    return app.secrets_collection(secrets_collection_id=secrets_collection_id).to_dict()


def create_secrets_collection(
    client: Client,
    app_id: str,
    secrets: Any,
    secrets_collection_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Create a new secrets collection. Returns the collection dict."""
    app = Application(client=client, id=app_id)
    return app.new_secrets_collection(
        secrets=secrets,
        id=secrets_collection_id,
        name=name,
        description=description,
    ).to_dict()


def delete_secrets_collection(client: Client, app_id: str, secrets_collection_id: str) -> None:
    """Delete a secrets collection."""
    app = Application(client=client, id=app_id)
    app.delete_secrets_collection(secrets_collection_id=secrets_collection_id)
