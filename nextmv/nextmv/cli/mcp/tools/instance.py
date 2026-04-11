"""MCP tools for cloud instance management."""

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.instance import (
    create_instance,
    delete_instance,
    get_instance,
    instance_exists,
    list_instances,
    update_instance,
)
from nextmv.cli.mcp import framework as mcp_fw


def register(mcp: FastMCP) -> None:
    """Register cloud instance management tools."""

    mcp_fw.tool(mcp, list_instances, name="cloud_list_instances")

    mcp_fw.tool(mcp, get_instance, name="cloud_get_instance")

    mcp_fw.tool(
        mcp,
        create_instance,
        name="cloud_create_instance",
        normalize_empty=["instance_id", "name", "description"],
    )

    mcp_fw.tool(
        mcp,
        update_instance,
        name="cloud_update_instance",
        normalize_empty=["name", "version_id", "description"],
    )

    mcp_fw.tool(
        mcp,
        delete_instance,
        name="cloud_delete_instance",
        result_message="Deleted instance {instance_id}",
    )

    mcp_fw.tool(mcp, instance_exists, name="cloud_instance_exists")
