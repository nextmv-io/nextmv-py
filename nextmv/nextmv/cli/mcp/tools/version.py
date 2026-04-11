"""MCP tools for cloud version management."""

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.version import (
    create_version,
    delete_version,
    get_version,
    list_versions,
    update_version,
    version_exists,
)
from nextmv.cli.mcp import framework as mcp_fw


def register(mcp: FastMCP) -> None:
    """Register cloud version management tools."""

    mcp_fw.tool(mcp, list_versions, name="cloud_list_versions")

    mcp_fw.tool(mcp, get_version, name="cloud_get_version")

    mcp_fw.tool(
        mcp,
        create_version,
        name="cloud_create_version",
        normalize_empty=["version_id", "name", "description"],
    )

    mcp_fw.tool(
        mcp,
        update_version,
        name="cloud_update_version",
        normalize_empty=["name", "description"],
    )

    mcp_fw.tool(
        mcp,
        delete_version,
        name="cloud_delete_version",
        result_message="Deleted version {version_id}",
    )

    mcp_fw.tool(mcp, version_exists, name="cloud_version_exists")
