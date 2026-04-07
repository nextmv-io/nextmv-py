"""Core instance management actions."""

from typing import Any

from nextmv.cloud import Application, Client, InstanceConfiguration


def list_instances(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all instances for an application."""
    app = Application(client=client, id=app_id)
    return [i.to_dict() for i in app.list_instances()]


def get_instance(client: Client, app_id: str, instance_id: str) -> dict[str, Any]:
    """Get instance details."""
    app = Application(client=client, id=app_id)
    return app.instance(instance_id=instance_id).to_dict()


def create_instance(
    client: Client,
    app_id: str,
    version_id: str,
    instance_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    configuration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a new instance. Returns the instance dict."""
    app = Application(client=client, id=app_id)
    config = InstanceConfiguration(**configuration) if configuration else None
    return app.new_instance(
        version_id=version_id,
        id=instance_id,
        name=name,
        description=description,
        configuration=config,
    ).to_dict()


def update_instance(
    client: Client,
    app_id: str,
    instance_id: str,
    name: str | None = None,
    version_id: str | None = None,
    description: str | None = None,
    configuration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Update an instance. Returns the updated instance dict."""
    app = Application(client=client, id=app_id)
    return app.update_instance(
        id=instance_id,
        name=name,
        version_id=version_id,
        description=description,
        configuration=configuration,
    ).to_dict()


def delete_instance(client: Client, app_id: str, instance_id: str) -> None:
    """Delete an instance."""
    app = Application(client=client, id=app_id)
    app.delete_instance(instance_id=instance_id)
