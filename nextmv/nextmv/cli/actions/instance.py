"""Core instance management actions.

Pure functions that wrap SDK calls. No CLI or MCP presentation concerns.

Each action takes ``client: Client`` as its first parameter so the CLI and
MCP frameworks can inject a client at call time. Remaining parameters use
dual-purpose ``Annotated`` aliases from ``nextmv.cli.framework.options`` so
the same metadata drives both Typer's ``--help`` output and FastMCP's tool
input schema.
"""

from typing import Any

from nextmv.cli.framework.options import (
    AppIdRequiredOption,
    DescriptionOption,
    ExistOkOption,
    InstanceIdOption,
    NameOption,
    OptionalInstanceIdOption,
    VersionIdOption,
)
from nextmv.cloud import Application, Client, InstanceConfiguration


def list_instances(client: Client, app_id: AppIdRequiredOption) -> list[dict[str, Any]]:
    """List all instances of a Nextmv Cloud application.

    An instance represents a deployed configuration of a specific version
    (for example ``"latest"``, ``"production"``, or ``"staging"``). Each
    instance points to a version and may carry its own execution class,
    runtime options, and secrets collection.

    Returns a list of instance dictionaries.
    """
    app = Application(client=client, id=app_id)
    return [i.to_dict() for i in app.list_instances()]


def get_instance(
    client: Client,
    app_id: AppIdRequiredOption,
    instance_id: InstanceIdOption,
) -> dict[str, Any]:
    """Get details of a specific instance of a Nextmv Cloud application.

    Returns the instance configuration including the version it points to,
    execution class, runtime options, and secrets collection.
    """
    app = Application(client=client, id=app_id)
    return app.instance(instance_id=instance_id).to_dict()


def create_instance(
    client: Client,
    app_id: AppIdRequiredOption,
    version_id: VersionIdOption,
    instance_id: OptionalInstanceIdOption = None,
    name: NameOption = None,
    description: DescriptionOption = None,
    configuration: dict[str, Any] | None = None,
    exist_ok: ExistOkOption = False,
) -> dict[str, Any]:
    """Create a new instance for a Nextmv Cloud application.

    An instance points to a specific version and can be configured with its
    own execution class, runtime options, secrets collection, and queuing
    behavior. The ``configuration`` argument is a dict that will be passed
    to ``InstanceConfiguration`` (keys such as ``execution_class``,
    ``options``, ``secrets_collection_id``, ``integration_id``, ``queuing``,
    and ``format``).

    Set ``exist_ok`` to avoid errors when an instance with the given ID
    already exists; the existing instance is returned instead.

    Returns the created (or existing) instance object.
    """
    app = Application(client=client, id=app_id)
    config = InstanceConfiguration(**configuration) if configuration else None
    return app.new_instance(
        version_id=version_id,
        id=instance_id,
        name=name,
        description=description,
        configuration=config,
        exist_ok=exist_ok,
    ).to_dict()


def update_instance(
    client: Client,
    app_id: AppIdRequiredOption,
    instance_id: InstanceIdOption,
    name: NameOption = None,
    version_id: str | None = None,
    description: DescriptionOption = None,
    configuration: dict[str, Any] | None = None,
    locked: bool | None = None,
) -> dict[str, Any]:
    """Update a Nextmv Cloud application instance.

    Only the provided fields are updated; omitted fields remain unchanged.
    The ``configuration`` argument, if provided, replaces the instance's
    configuration. The ``locked`` flag, when not ``None``, also locks or
    unlocks the instance.

    Returns the updated instance object.
    """
    app = Application(client=client, id=app_id)
    return app.update_instance(
        id=instance_id,
        name=name,
        version_id=version_id,
        description=description,
        configuration=configuration,
        locked=locked,
    ).to_dict()


def delete_instance(
    client: Client,
    app_id: AppIdRequiredOption,
    instance_id: InstanceIdOption,
) -> None:
    """Delete a Nextmv Cloud application instance permanently.

    This action cannot be undone.
    """
    app = Application(client=client, id=app_id)
    app.delete_instance(instance_id=instance_id)


def instance_exists(
    client: Client,
    app_id: AppIdRequiredOption,
    instance_id: InstanceIdOption,
) -> bool:
    """Check whether a Nextmv Cloud application instance exists.

    Returns ``True`` if an instance with the given ID exists for the given
    application, ``False`` otherwise.
    """
    app = Application(client=client, id=app_id)
    return app.instance_exists(instance_id=instance_id)
