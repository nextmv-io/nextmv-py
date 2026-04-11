"""Core secrets management actions.

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
    NameOption,
    OptionalSecretsCollectionIdOption,
    SecretsCollectionIdOption,
)
from nextmv.cloud import Application, Client


def list_secrets_collections(
    client: Client,
    app_id: AppIdRequiredOption,
) -> list[dict[str, Any]]:
    """List all secrets collections for a Nextmv Cloud application.

    Secrets collections provide environment variables and files to
    application instances at runtime (e.g., solver licenses, API keys).
    Returns a list of collection dicts.
    """
    app = Application(client=client, id=app_id)
    return [c.to_dict() for c in app.list_secrets_collections()]


def get_secrets_collection(
    client: Client,
    app_id: AppIdRequiredOption,
    secrets_collection_id: SecretsCollectionIdOption,
) -> dict[str, Any]:
    """Get details of a Nextmv Cloud secrets collection.

    Returns the collection metadata and the list of secret definitions,
    including secret values. Handle the result with care.
    """
    app = Application(client=client, id=app_id)
    return app.secrets_collection(secrets_collection_id=secrets_collection_id).to_dict()


def create_secrets_collection(
    client: Client,
    app_id: AppIdRequiredOption,
    secrets: Any,
    secrets_collection_id: OptionalSecretsCollectionIdOption = None,
    name: NameOption = None,
    description: DescriptionOption = None,
) -> dict[str, Any]:
    """Create a new Nextmv Cloud secrets collection.

    Secrets are injected into the application instance at runtime as
    environment variables or files. Each secret is a dict with keys
    ``type`` (``"env"`` or ``"file"``), ``location`` (env var name or
    file path), and ``value`` (the secret value).

    Returns the created collection dict.
    """
    app = Application(client=client, id=app_id)
    return app.new_secrets_collection(
        secrets=secrets,
        id=secrets_collection_id,
        name=name,
        description=description,
    ).to_dict()


def update_secrets_collection(
    client: Client,
    app_id: AppIdRequiredOption,
    secrets_collection_id: SecretsCollectionIdOption,
    name: NameOption = None,
    description: DescriptionOption = None,
    secrets: Any | None = None,
) -> dict[str, Any]:
    """Update a Nextmv Cloud secrets collection.

    Only the provided fields are updated; omitted fields remain unchanged.
    When ``secrets`` is provided, the entire list replaces the existing
    secrets in the collection. Returns the updated collection dict.
    """
    app = Application(client=client, id=app_id)
    return app.update_secrets_collection(
        secrets_collection_id=secrets_collection_id,
        name=name,
        description=description,
        secrets=secrets,
    ).to_dict()


def delete_secrets_collection(
    client: Client,
    app_id: AppIdRequiredOption,
    secrets_collection_id: SecretsCollectionIdOption,
) -> None:
    """Delete a Nextmv Cloud secrets collection permanently.

    This action cannot be undone.
    """
    app = Application(client=client, id=app_id)
    app.delete_secrets_collection(secrets_collection_id=secrets_collection_id)
