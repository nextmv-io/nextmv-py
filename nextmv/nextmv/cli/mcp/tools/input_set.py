"""MCP tools for cloud input sets."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.input_set import create_input_set as _create_input_set
from nextmv.cli.actions.input_set import delete_input_set as _delete_input_set
from nextmv.cli.actions.input_set import get_input_set as _get_input_set
from nextmv.cli.actions.input_set import list_input_sets as _list_input_sets
from nextmv.cli.actions.input_set import update_input_set as _update_input_set
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud input set tools."""

    @mcp.tool()
    def cloud_list_input_sets(app_id: str) -> list[dict[str, Any]]:
        """List input sets for a Nextmv Cloud application.

        Input sets are reusable collections of inputs used in batch
        experiments, scenario tests, and acceptance tests. Each entry
        includes the input set ID, name, and number of inputs.

        Args:
            app_id: The application ID.
        """

        client = _helpers._get_client()
        return _list_input_sets(client, app_id=app_id)

    @mcp.tool()
    def cloud_get_input_set(app_id: str, input_set_id: str) -> dict[str, Any]:
        """Get details of a specific input set.

        Returns the input set metadata and the list of input IDs it
        contains.

        Args:
            app_id: The application ID.
            input_set_id: The input set ID to retrieve.
        """

        client = _helpers._get_client()
        return _get_input_set(client, app_id=app_id, input_set_id=input_set_id)

    @mcp.tool()
    def cloud_create_input_set(
        app_id: str,
        input_set_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        instance_id: str | None = None,
        maximum_runs: int | None = None,
        run_ids: list[str] | None = None,
        managed_input_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new input set for a Nextmv Cloud application.

        An input set collects inputs (from historical runs or managed
        inputs) for use in batch experiments and acceptance tests.

        Three creation methods (use exactly one):
        1. ``instance_id`` -- collect recent runs from that instance.
        2. ``run_ids`` -- use specific run IDs.
        3. ``managed_input_ids`` -- use existing managed inputs.

        Args:
            app_id: The application ID.
            input_set_id: Optional ID for the input set.
            name: Optional human-readable name.
            description: Optional description.
            instance_id: Optional instance ID to collect runs from.
            maximum_runs: Maximum number of runs to include (default: 20).
            run_ids: Optional list of specific run IDs.
            managed_input_ids: Optional list of managed input IDs.
        """

        input_set_id = _helpers._none_if_empty(input_set_id)
        name = _helpers._none_if_empty(name)
        description = _helpers._none_if_empty(description)
        instance_id = _helpers._none_if_empty(instance_id)

        # Validate that exactly one creation method is provided.
        methods = sum([bool(instance_id), bool(run_ids), bool(managed_input_ids)])
        if methods == 0:
            return "Error: provide exactly one of instance_id, run_ids, or managed_input_ids."
        if methods > 1:
            return "Error: provide only one of instance_id, run_ids, or managed_input_ids (got multiple)."

        client = _helpers._get_client()
        return _create_input_set(
            client,
            app_id=app_id,
            input_set_id=input_set_id,
            name=name,
            description=description,
            instance_id=instance_id,
            maximum_runs=maximum_runs,
            run_ids=run_ids,
            managed_input_ids=managed_input_ids,
        )

    @mcp.tool()
    def cloud_update_input_set(
        app_id: str,
        input_set_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update an input set's name or description.

        Only the provided fields are updated; omitted fields remain
        unchanged. Returns the updated input set object.

        Args:
            app_id: The application ID.
            input_set_id: The input set ID to update.
            name: New human-readable name.
            description: New description.
        """

        name = _helpers._none_if_empty(name)
        description = _helpers._none_if_empty(description)

        client = _helpers._get_client()
        return _update_input_set(client, app_id=app_id, input_set_id=input_set_id, name=name, description=description)

    @mcp.tool()
    def cloud_delete_input_set(app_id: str, input_set_id: str) -> str:
        """Delete an input set permanently.

        Args:
            app_id: The application ID.
            input_set_id: The input set ID to delete.
        """

        client = _helpers._get_client()
        _delete_input_set(client, app_id=app_id, input_set_id=input_set_id)
        return f"Deleted input set {input_set_id}"
