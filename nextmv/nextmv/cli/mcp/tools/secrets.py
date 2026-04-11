"""MCP tools for cloud secrets management."""

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.secrets import (
    create_secrets_collection,
    delete_secrets_collection,
    get_secrets_collection,
    list_secrets_collections,
    update_secrets_collection,
)
from nextmv.cli.mcp import framework as mcp_fw


def register(mcp: FastMCP) -> None:
    """Register cloud secrets management tools."""

    mcp_fw.tool(mcp, list_secrets_collections, name="cloud_list_secrets_collections")

    mcp_fw.tool(mcp, get_secrets_collection, name="cloud_get_secrets_collection")

    mcp_fw.tool(
        mcp,
        create_secrets_collection,
        name="cloud_create_secrets_collection",
        normalize_empty=["secrets_collection_id", "name", "description"],
    )

    mcp_fw.tool(
        mcp,
        update_secrets_collection,
        name="cloud_update_secrets_collection",
        normalize_empty=["name", "description"],
    )

    mcp_fw.tool(
        mcp,
        delete_secrets_collection,
        name="cloud_delete_secrets_collection",
        result_message="Deleted secrets collection {secrets_collection_id}",
    )
