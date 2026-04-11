"""Core version management actions.

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
    NameOption,
    OptionalVersionIdOption,
    VersionIdOption,
)
from nextmv.cloud import Application, Client


def list_versions(client: Client, app_id: AppIdRequiredOption) -> list[dict[str, Any]]:
    """List all versions of a Nextmv Cloud application.

    Each version represents a snapshot of the application code that was
    pushed. Returns a list of version dicts including ID, name, description,
    and creation timestamp.
    """
    app = Application(client=client, id=app_id)
    return [v.to_dict() for v in app.list_versions()]


def get_version(
    client: Client,
    app_id: AppIdRequiredOption,
    version_id: VersionIdOption,
) -> dict[str, Any]:
    """Get details of a specific version of a Nextmv Cloud application.

    Returns the full version object including name, description, and
    creation timestamp.
    """
    app = Application(client=client, id=app_id)
    return app.version(version_id=version_id).to_dict()


def create_version(
    client: Client,
    app_id: AppIdRequiredOption,
    version_id: OptionalVersionIdOption = None,
    name: NameOption = None,
    description: DescriptionOption = None,
    exist_ok: ExistOkOption = False,
) -> dict[str, Any]:
    """Create a new version for a Nextmv Cloud application.

    Set ``exist_ok`` to avoid errors when a version with the given ID
    already exists; the existing version is returned instead.

    Returns the created (or existing) version object.
    """
    app = Application(client=client, id=app_id)
    return app.new_version(
        id=version_id,
        name=name,
        description=description,
        exist_ok=exist_ok,
    ).to_dict()


def update_version(
    client: Client,
    app_id: AppIdRequiredOption,
    version_id: VersionIdOption,
    name: NameOption = None,
    description: DescriptionOption = None,
) -> dict[str, Any]:
    """Update a Nextmv Cloud application version.

    Only the provided fields are updated; omitted fields remain unchanged.
    Returns the updated version object.
    """
    app = Application(client=client, id=app_id)
    return app.update_version(
        version_id=version_id,
        name=name,
        description=description,
    ).to_dict()


def delete_version(
    client: Client,
    app_id: AppIdRequiredOption,
    version_id: VersionIdOption,
) -> None:
    """Delete a Nextmv Cloud application version permanently.

    This action cannot be undone.
    """
    app = Application(client=client, id=app_id)
    app.delete_version(version_id=version_id)


def version_exists(
    client: Client,
    app_id: AppIdRequiredOption,
    version_id: VersionIdOption,
) -> bool:
    """Check whether a Nextmv Cloud application version exists.

    Returns ``True`` if a version with the given ID exists for the given
    application, ``False`` otherwise.
    """
    app = Application(client=client, id=app_id)
    return app.version_exists(version_id=version_id)
