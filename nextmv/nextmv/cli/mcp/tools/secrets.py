"""MCP tools for cloud secrets management."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud secrets management tools."""

    @mcp.tool()
    def cloud_list_secrets_collections(app_id: str) -> list[dict[str, Any]]:
        """List secrets collections for a Nextmv Cloud application.

        Secrets collections provide environment variables and files
        to application instances at runtime (e.g., solver licenses,
        API keys). Returns collection summaries without secret values.

        Args:
            app_id: The application ID.
        """

        app = _helpers._get_app(app_id)
        collections = app.list_secrets_collections()
        return [c.to_dict() for c in collections]

    @mcp.tool()
    def cloud_get_secrets_collection(
        app_id: str,
        secrets_collection_id: str,
    ) -> dict[str, Any]:
        """Get details of a secrets collection.

        Returns the collection metadata and the list of secret
        definitions (types and locations, but not the secret values).

        Args:
            app_id: The application ID.
            secrets_collection_id: The secrets collection ID to
                retrieve.
        """

        app = _helpers._get_app(app_id)
        collection = app.secrets_collection(secrets_collection_id=secrets_collection_id)
        return collection.to_dict()

    @mcp.tool()
    def cloud_create_secrets_collection(
        app_id: str,
        secrets: list[dict[str, str]],
        secrets_collection_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a secrets collection for a Nextmv Cloud application.

        Secrets are injected into the application instance at runtime
        as environment variables or files.

        Args:
            app_id: The application ID.
            secrets: List of secret definitions. Each is a dict with
                keys: ``type`` (``"env"`` or ``"file"``), ``location``
                (env var name or file path), ``value`` (the secret).
            secrets_collection_id: Optional collection ID.
                Auto-generated if omitted.
            name: Optional human-readable name.
            description: Optional description.
        """

        secrets_collection_id = _helpers._none_if_empty(secrets_collection_id)
        name = _helpers._none_if_empty(name)
        description = _helpers._none_if_empty(description)

        app = _helpers._get_app(app_id)
        collection = app.new_secrets_collection(
            secrets=secrets,
            id=secrets_collection_id,
            name=name,
            description=description,
        )
        return collection.to_dict()

    @mcp.tool()
    def cloud_delete_secrets_collection(
        app_id: str,
        secrets_collection_id: str,
    ) -> str:
        """Delete a secrets collection permanently.

        Args:
            app_id: The application ID.
            secrets_collection_id: The secrets collection ID to delete.
        """

        app = _helpers._get_app(app_id)
        app.delete_secrets_collection(secrets_collection_id=secrets_collection_id)
        return f"Deleted secrets collection {secrets_collection_id}"
