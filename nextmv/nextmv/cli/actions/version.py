"""Core version management actions."""

from typing import Any

from nextmv.cloud import Application, Client


def list_versions(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all versions for an application."""
    app = Application(client=client, id=app_id)
    return [v.to_dict() for v in app.list_versions()]


def get_version(client: Client, app_id: str, version_id: str) -> dict[str, Any]:
    """Get version details."""
    app = Application(client=client, id=app_id)
    return app.version(version_id=version_id).to_dict()


def create_version(
    client: Client,
    app_id: str,
    version_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    exist_ok: bool = False,
) -> dict[str, Any]:
    """Create a new version. Returns the version dict."""
    app = Application(client=client, id=app_id)
    return app.new_version(
        id=version_id,
        name=name,
        description=description,
        exist_ok=exist_ok,
    ).to_dict()


def update_version(
    client: Client,
    app_id: str,
    version_id: str,
    name: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Update a version. Returns the updated version dict."""
    app = Application(client=client, id=app_id)
    return app.update_version(
        version_id=version_id,
        name=name,
        description=description,
    ).to_dict()


def delete_version(client: Client, app_id: str, version_id: str) -> None:
    """Delete a version."""
    app = Application(client=client, id=app_id)
    app.delete_version(version_id=version_id)
