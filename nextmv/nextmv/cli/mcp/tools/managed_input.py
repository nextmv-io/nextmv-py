"""MCP tools for cloud managed inputs."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.managed_input import create_managed_input as _create_managed_input
from nextmv.cli.actions.managed_input import delete_managed_input as _delete_managed_input
from nextmv.cli.actions.managed_input import get_managed_input as _get_managed_input
from nextmv.cli.actions.managed_input import list_managed_inputs as _list_managed_inputs
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud managed input tools."""

    @mcp.tool()
    def cloud_list_managed_inputs(app_id: str) -> list[dict[str, Any]]:
        """List managed inputs for a Nextmv Cloud application.

        Managed inputs are reusable input data objects stored on the
        platform. They can be referenced by ID when creating runs or
        building input sets.

        Args:
            app_id: The application ID.
        """

        client = _helpers._get_client()
        return _list_managed_inputs(client, app_id=app_id)

    @mcp.tool()
    def cloud_get_managed_input(
        app_id: str,
        managed_input_id: str,
    ) -> dict[str, Any]:
        """Get details of a managed input.

        Returns the managed input metadata (ID, name, description).
        Does not return the input data itself.

        Args:
            app_id: The application ID.
            managed_input_id: The managed input ID to retrieve.
        """

        client = _helpers._get_client()
        return _get_managed_input(client, app_id=app_id, managed_input_id=managed_input_id)

    @mcp.tool()
    def cloud_create_managed_input(
        app_id: str,
        managed_input_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        run_id: str | None = None,
        input: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a managed input for a Nextmv Cloud application.

        Provide exactly one of ``run_id`` (to copy the input from an
        existing run) or ``input`` (to upload raw JSON data directly).

        Args:
            app_id: The application ID.
            managed_input_id: Optional ID for the managed input.
                Auto-generated if omitted.
            name: Optional human-readable name.
            description: Optional description.
            run_id: Copy the input data from this existing run ID.
            input: Raw input data (JSON object) to upload directly.
        """

        managed_input_id = _helpers._none_if_empty(managed_input_id)
        name = _helpers._none_if_empty(name)
        description = _helpers._none_if_empty(description)
        run_id = _helpers._none_if_empty(run_id)

        client = _helpers._get_client()
        return _create_managed_input(
            client,
            app_id=app_id,
            data=input,
            managed_input_id=managed_input_id,
            name=name,
            description=description,
            run_id=run_id,
        )

    @mcp.tool()
    def cloud_delete_managed_input(
        app_id: str,
        managed_input_id: str,
    ) -> str:
        """Delete a managed input permanently.

        Args:
            app_id: The application ID.
            managed_input_id: The managed input ID to delete.
        """

        client = _helpers._get_client()
        _delete_managed_input(client, app_id=app_id, managed_input_id=managed_input_id)
        return f"Deleted managed input {managed_input_id}"
