"""MCP tools for cloud instance management."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud instance management tools."""

    @mcp.tool()
    def cloud_list_instances(app_id: str) -> list[dict[str, Any]]:
        """List all instances of a Nextmv Cloud application.

        Instances represent deployed configurations of a specific
        version (e.g., ``"latest"``, ``"production"``, ``"staging"``).
        Each instance points to a version and can have its own
        execution class, options, and secrets.

        Args:
            app_id: The application ID.
        """

        app = _helpers._get_app(app_id)
        instances = app.list_instances()
        return [i.to_dict() for i in instances]

    @mcp.tool()
    def cloud_get_instance(app_id: str, instance_id: str) -> dict[str, Any]:
        """Get details of a specific instance of a Nextmv Cloud application.

        Returns the instance configuration including the version it
        points to, execution class, options, and secrets collection.

        Args:
            app_id: The application ID.
            instance_id: The instance ID to retrieve.
        """

        app = _helpers._get_app(app_id)
        inst = app.instance(instance_id=instance_id)
        return inst.to_dict()

    @mcp.tool()
    def cloud_create_instance(
        app_id: str,
        version_id: str,
        instance_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> dict[str, Any] | str:
        """Create a new instance for a Nextmv Cloud application.

        An instance points to a specific version and can be configured
        with its own execution class, solver options, and secrets.

        Args:
            app_id: The application ID.
            version_id: The version ID this instance should point to.
            instance_id: Optional instance ID. Auto-generated if omitted.
            name: Optional human-readable name for the instance.
            description: Optional description.
            configuration: Optional instance configuration dictionary
                with keys: ``execution_class``, ``options``,
                ``secrets_collection_id``, ``integration_id``.
        """

        from nextmv.cloud import InstanceConfiguration

        try:
            version_id = _helpers._require_non_empty(version_id, "version_id")
        except ValueError as e:
            return str(e)
        instance_id = _helpers._none_if_empty(instance_id)
        name = _helpers._none_if_empty(name)
        description = _helpers._none_if_empty(description)

        app = _helpers._get_app(app_id)
        config = InstanceConfiguration(**configuration) if configuration else None
        inst = app.new_instance(
            version_id=version_id,
            id=instance_id,
            name=name,
            description=description,
            configuration=config,
        )
        return inst.to_dict()

    @mcp.tool()
    def cloud_update_instance(
        app_id: str,
        instance_id: str,
        name: str | None = None,
        version_id: str | None = None,
        description: str | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update an instance of a Nextmv Cloud application.

        Only the provided fields are updated; omitted fields remain
        unchanged. Returns the updated instance object.

        Args:
            app_id: The application ID.
            instance_id: The instance ID to update.
            name: New human-readable name.
            version_id: New version ID to point the instance to.
            description: New description.
            configuration: New instance configuration dictionary.
        """

        name = _helpers._none_if_empty(name)
        version_id = _helpers._none_if_empty(version_id)
        description = _helpers._none_if_empty(description)

        app = _helpers._get_app(app_id)
        inst = app.update_instance(
            id=instance_id,
            name=name,
            version_id=version_id,
            description=description,
            configuration=configuration,
        )
        return inst.to_dict()

    @mcp.tool()
    def cloud_delete_instance(app_id: str, instance_id: str) -> str:
        """Delete an instance of a Nextmv Cloud application permanently.

        Args:
            app_id: The application ID.
            instance_id: The instance ID to delete.
        """

        app = _helpers._get_app(app_id)
        app.delete_instance(instance_id=instance_id)
        return f"Deleted instance {instance_id}"
