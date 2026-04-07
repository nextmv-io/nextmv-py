"""MCP tools for cloud application management."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.app import (
    app_exists,
    create_app,
    delete_app,
    get_app,
    list_apps,
    push_app,
    update_app,
)
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud application management tools."""

    @mcp.tool()
    def cloud_list_apps() -> list[dict[str, Any]]:
        """List all Nextmv Cloud applications in the current account.

        Returns a list of application dictionaries containing each
        application's ID, name, description, and default instance.
        """
        return list_apps(_helpers._get_client())

    @mcp.tool()
    def cloud_get_app(app_id: str) -> dict[str, Any]:
        """Get details of a specific Nextmv Cloud application.

        Returns the full application object including its name,
        description, default instance, and creation timestamp.

        Args:
            app_id: The application ID (e.g., ``"my-routing-app"``).
        """
        return get_app(_helpers._get_client(), app_id=app_id)

    @mcp.tool()
    def cloud_create_app(
        name: str,
        app_id: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a new Nextmv Cloud application.

        Returns the created application object. A version and default
        instance are automatically provisioned.

        Args:
            name: A human-readable name for the application.
            app_id: Optional URL-friendly ID. Auto-generated from
                the name if omitted.
            description: Optional description of what the application does.
        """
        return create_app(
            _helpers._get_client(),
            name=name,
            app_id=_helpers._none_if_empty(app_id),
            description=_helpers._none_if_empty(description),
        )

    @mcp.tool()
    def cloud_delete_app(app_id: str) -> str:
        """Delete a Nextmv Cloud application permanently.

        This action cannot be undone. All versions, instances, and
        run history associated with the application will be removed.

        Args:
            app_id: The application ID to delete.
        """
        delete_app(_helpers._get_client(), app_id=app_id)
        return f"Deleted application {app_id}"

    @mcp.tool()
    def cloud_app_exists(app_id: str) -> bool:
        """Check whether a Nextmv Cloud application exists.

        Returns True if an application with the given ID exists in
        the current account, False otherwise.

        Args:
            app_id: The application ID to check.
        """
        return app_exists(_helpers._get_client(), app_id=app_id)

    @mcp.tool()
    def cloud_update_app(
        app_id: str,
        name: str | None = None,
        description: str | None = None,
        default_instance_id: str | None = None,
    ) -> dict[str, Any]:
        """Update attributes of a Nextmv Cloud application.

        Only the provided fields are updated; omitted fields remain
        unchanged. Returns the updated application object.

        Args:
            app_id: The application ID to update.
            name: New human-readable name for the application.
            description: New description.
            default_instance_id: New default instance ID used when no
                instance is specified at run time.
        """
        return update_app(
            _helpers._get_client(),
            app_id=app_id,
            name=_helpers._none_if_empty(name),
            description=_helpers._none_if_empty(description),
            default_instance_id=_helpers._none_if_empty(default_instance_id),
        )

    @mcp.tool()
    def cloud_push_app(app_id: str, app_dir: str) -> str:
        """Push local application code to a Nextmv Cloud application.

        Uploads the contents of a local directory as a new version of
        the application. The directory must contain an ``app.yaml``
        manifest.

        Args:
            app_id: The application ID to push to.
            app_dir: Absolute path to the local directory containing the
                application code and ``app.yaml`` manifest.
        """
        push_app(_helpers._get_client(), app_id=app_id, app_dir=app_dir)
        return f"Pushed {app_dir} to application {app_id}"
