"""MCP tools for cloud application management.

Each tool wraps a pure action function from ``nextmv.cli.actions.app``. The
parameter signatures, types, and descriptions are derived from the action;
per-tool wiring (tool name, empty-string normalization, result-message
formatting) lives here.
"""

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
from nextmv.cli.mcp import framework as mcp_fw


def register(mcp: FastMCP) -> None:
    """Register cloud application management tools."""

    mcp_fw.tool(mcp, list_apps, name="cloud_list_apps")

    mcp_fw.tool(
        mcp,
        get_app,
        name="cloud_get_app",
    )

    mcp_fw.tool(
        mcp,
        create_app,
        name="cloud_create_app",
        normalize_empty=["app_id", "description", "name"],
    )

    mcp_fw.tool(
        mcp,
        delete_app,
        name="cloud_delete_app",
        result_message="Deleted application {app_id}",
    )

    mcp_fw.tool(
        mcp,
        app_exists,
        name="cloud_app_exists",
    )

    mcp_fw.tool(
        mcp,
        update_app,
        name="cloud_update_app",
        normalize_empty=[
            "name",
            "description",
            "default_instance_id",
            "default_experiment_instance",
        ],
    )

    mcp_fw.tool(
        mcp,
        push_app,
        name="cloud_push_app",
        result_message="Pushed {app_dir} to application {app_id}",
    )
