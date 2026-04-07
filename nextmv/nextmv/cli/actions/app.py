"""Core application management actions.

Pure functions that wrap SDK calls. No CLI or MCP concerns.
"""

from typing import Any

from nextmv.cloud import Application, Client, list_applications


def list_apps(client: Client) -> list[dict[str, Any]]:
    """List all applications in the account."""
    apps = list_applications(client)
    return [a.to_dict() for a in apps]


def create_app(
    client: Client,
    name: str,
    app_id: str | None = None,
    description: str | None = None,
    is_workflow: bool = False,
    exist_ok: bool = False,
    default_instance_id: str | None = None,
    default_experiment_instance: str | None = None,
) -> dict[str, Any]:
    """Create a new application. Returns the app dict."""
    return Application.new(
        client=client,
        name=name,
        id=app_id,
        description=description,
        is_workflow=is_workflow,
        exist_ok=exist_ok,
        default_instance_id=default_instance_id,
        default_experiment_instance=default_experiment_instance,
    ).to_dict()


def get_app(client: Client, app_id: str) -> dict[str, Any]:
    """Get application details."""
    return Application.get(client=client, id=app_id).to_dict()


def delete_app(client: Client, app_id: str) -> None:
    """Delete an application."""
    Application(client=client, id=app_id).delete()


def app_exists(client: Client, app_id: str) -> bool:
    """Check whether an application exists."""
    return Application.exists(client=client, id=app_id)


def update_app(
    client: Client,
    app_id: str,
    name: str | None = None,
    description: str | None = None,
    default_instance_id: str | None = None,
    default_experiment_instance: str | None = None,
) -> dict[str, Any]:
    """Update application attributes. Returns the updated app dict."""
    app = Application(client=client, id=app_id)
    return app.update(
        name=name,
        description=description,
        default_instance_id=default_instance_id,
        default_experiment_instance=default_experiment_instance,
    ).to_dict()


def push_app(client: Client, app_id: str, app_dir: str) -> None:
    """Push local code to a cloud application."""
    app = Application(client=client, id=app_id)
    app.push(app_dir=app_dir)
