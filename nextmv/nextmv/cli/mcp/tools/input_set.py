"""MCP tools for cloud input sets."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.input_set import (
    create_input_set,
    delete_input_set,
    get_input_set,
    list_input_sets,
    update_input_set,
)
from nextmv.cli.mcp import framework as mcp_fw


def register(mcp: FastMCP) -> None:
    """Register cloud input set tools."""

    mcp_fw.tool(mcp, list_input_sets, name="cloud_list_input_sets")

    mcp_fw.tool(mcp, get_input_set, name="cloud_get_input_set")

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
    ) -> dict[str, Any] | str:
        """Create a new input set for a Nextmv Cloud application.

        An input set collects inputs (from historical runs or managed
        inputs) for use in batch experiments and acceptance tests.

        Three creation methods (use exactly one):
        1. ``instance_id`` -- collect recent runs from that instance.
        2. ``run_ids`` -- use specific run IDs.
        3. ``managed_input_ids`` -- use existing managed inputs.
        """

        input_set_id = mcp_fw.clean(input_set_id)
        name = mcp_fw.clean(name)
        description = mcp_fw.clean(description)
        instance_id = mcp_fw.clean(instance_id)

        # Validate that exactly one creation method is provided.
        methods = sum([bool(instance_id), bool(run_ids), bool(managed_input_ids)])
        if methods == 0:
            return "Error: provide exactly one of instance_id, run_ids, or managed_input_ids."
        if methods > 1:
            return "Error: provide only one of instance_id, run_ids, or managed_input_ids (got multiple)."

        return create_input_set(
            mcp_fw.client(),
            app_id=app_id,
            input_set_id=input_set_id,
            name=name,
            description=description,
            instance_id=instance_id,
            maximum_runs=maximum_runs,
            run_ids=run_ids,
            managed_input_ids=managed_input_ids,
        )

    mcp_fw.tool(
        mcp,
        update_input_set,
        name="cloud_update_input_set",
        normalize_empty=["name", "description"],
    )

    mcp_fw.tool(
        mcp,
        delete_input_set,
        name="cloud_delete_input_set",
        result_message="Deleted input set {input_set_id}",
    )
