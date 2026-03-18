"""MCP tools for cloud application management."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.mcp.tools import _helpers
from nextmv.cloud import Application, list_applications


def register(mcp: FastMCP) -> None:
    """Register cloud application management tools."""

    @mcp.tool()
    def cloud_list_apps() -> list[dict[str, Any]]:
        """List all Nextmv Cloud applications in the current account.

        Returns a list of application dictionaries containing each
        application's ID, name, description, and default instance.
        """

        client = _helpers._get_client()
        apps = list_applications(client)
        return [a.to_dict() for a in apps]

    @mcp.tool()
    def cloud_get_app(app_id: str) -> dict[str, Any]:
        """Get details of a specific Nextmv Cloud application.

        Returns the full application object including its name,
        description, default instance, and creation timestamp.

        Args:
            app_id: The application ID (e.g., ``"my-routing-app"``).
        """

        client = _helpers._get_client()
        app = Application.get(client=client, id=app_id)
        return app.to_dict()

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

        client = _helpers._get_client()
        app = Application.new(
            client=client,
            name=name,
            id=app_id,
            description=description,
        )
        return app.to_dict()

    @mcp.tool()
    def cloud_delete_app(app_id: str) -> str:
        """Delete a Nextmv Cloud application permanently.

        This action cannot be undone. All versions, instances, and
        run history associated with the application will be removed.

        Args:
            app_id: The application ID to delete.
        """

        app = _helpers._get_app(app_id)
        app.delete()
        return f"Deleted application {app_id}"

    @mcp.tool()
    def cloud_app_exists(app_id: str) -> bool:
        """Check whether a Nextmv Cloud application exists.

        Returns True if an application with the given ID exists in
        the current account, False otherwise.

        Args:
            app_id: The application ID to check.
        """

        client = _helpers._get_client()
        return Application.exists(client=client, id=app_id)

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

        app = _helpers._get_app(app_id)
        updated = app.update(
            name=name,
            description=description,
            default_instance_id=default_instance_id,
        )
        return updated.to_dict()

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

        app = _helpers._get_app(app_id)
        app.push(app_dir=app_dir)
        return f"Pushed {app_dir} to application {app_id}"
