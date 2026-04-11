"""MCP tools for cloud managed inputs."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.managed_input import (
    create_managed_input,
    delete_managed_input,
    get_managed_input,
    list_managed_inputs,
    update_managed_input,
)
from nextmv.cli.mcp import framework as mcp_fw


def register(mcp: FastMCP) -> None:
    """Register cloud managed input tools."""

    mcp_fw.tool(mcp, list_managed_inputs, name="cloud_list_managed_inputs")

    mcp_fw.tool(mcp, get_managed_input, name="cloud_get_managed_input")

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
        """

        return create_managed_input(
            mcp_fw.client(),
            app_id=app_id,
            data=input,
            managed_input_id=mcp_fw.clean(managed_input_id),
            name=mcp_fw.clean(name),
            description=mcp_fw.clean(description),
            run_id=mcp_fw.clean(run_id),
        )

    mcp_fw.tool(
        mcp,
        update_managed_input,
        name="cloud_update_managed_input",
        normalize_empty=["name", "description"],
    )

    mcp_fw.tool(
        mcp,
        delete_managed_input,
        name="cloud_delete_managed_input",
        result_message="Deleted managed input {managed_input_id}",
    )
