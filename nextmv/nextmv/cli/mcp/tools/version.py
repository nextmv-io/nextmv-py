"""MCP tools for cloud version management."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud version management tools."""

    @mcp.tool()
    def cloud_list_versions(app_id: str) -> list[dict[str, Any]]:
        """List all versions of a Nextmv Cloud application.

        Each version represents a snapshot of the application code
        that was pushed. Returns version ID, name, description, and
        creation timestamp.

        Args:
            app_id: The application ID.
        """

        app = _helpers._get_app(app_id)
        versions = app.list_versions()
        return [v.to_dict() for v in versions]

    @mcp.tool()
    def cloud_get_version(app_id: str, version_id: str) -> dict[str, Any]:
        """Get details of a specific version of a Nextmv Cloud application.

        Args:
            app_id: The application ID.
            version_id: The version ID to retrieve.
        """

        app = _helpers._get_app(app_id)
        v = app.version(version_id=version_id)
        return v.to_dict()

    @mcp.tool()
    def cloud_create_version(
        app_id: str,
        version_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a new version for a Nextmv Cloud application.

        If ``version_id`` is provided and a version with that ID
        already exists, the existing version is returned (idempotent).
        If ``version_id`` is omitted, a unique ID is auto-generated.

        Args:
            app_id: The application ID.
            version_id: Optional version ID. Auto-generated if omitted.
            name: Optional human-readable name for the version.
            description: Optional description of what changed in this
                version.
        """

        version_id = _helpers._none_if_empty(version_id)
        name = _helpers._none_if_empty(name)
        description = _helpers._none_if_empty(description)

        app = _helpers._get_app(app_id)
        v = app.new_version(
            id=version_id,
            name=name,
            description=description,
            exist_ok=version_id is not None,
        )
        return v.to_dict()

    @mcp.tool()
    def cloud_update_version(
        app_id: str,
        version_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update a version of a Nextmv Cloud application.

        Only the provided fields are updated; omitted fields remain
        unchanged. Returns the updated version object.

        Args:
            app_id: The application ID.
            version_id: The version ID to update.
            name: New human-readable name.
            description: New description.
        """

        name = _helpers._none_if_empty(name)
        description = _helpers._none_if_empty(description)

        app = _helpers._get_app(app_id)
        v = app.update_version(version_id=version_id, name=name, description=description)
        return v.to_dict()

    @mcp.tool()
    def cloud_delete_version(app_id: str, version_id: str) -> str:
        """Delete a version of a Nextmv Cloud application permanently.

        Args:
            app_id: The application ID.
            version_id: The version ID to delete.
        """

        app = _helpers._get_app(app_id)
        app.delete_version(version_id=version_id)
        return f"Deleted version {version_id}"
