"""MCP tools for cloud batch experiments."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.batch import (
    batch_metadata,
    create_batch,
    delete_batch,
    get_batch,
    list_batches,
    update_batch,
)
from nextmv.cli.mcp import framework as mcp_fw
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud batch experiment tools."""

    mcp_fw.tool(mcp, list_batches, name="cloud_list_batches")

    @mcp.tool()
    def cloud_get_batch(app_id: str, batch_experiment_id: str) -> str:
        """Get details and run results of a batch experiment.

        Saves the full experiment data (including individual run
        results) to ~/.nextmv/experiments/. Use file-reading tools to
        inspect the contents.

        Args:
            app_id: The application ID.
            batch_experiment_id: The batch experiment ID.
        """

        client = mcp_fw.client()
        data = get_batch(client, app_id=app_id, batch_experiment_id=batch_experiment_id)
        endpoint = _helpers._endpoint_from_client(client)
        return _helpers._save_experiment_file(data, endpoint, "batch", batch_experiment_id)

    @mcp.tool()
    def cloud_batch_metadata(app_id: str, batch_experiment_id: str) -> str:
        """Get metadata for a batch experiment.

        Returns experiment-level metadata including status, run
        counts, and timing information. Saves the result to
        ~/.nextmv/experiments/. Use file-reading tools to inspect
        the contents.

        Args:
            app_id: The application ID.
            batch_experiment_id: The batch experiment ID.
        """

        client = mcp_fw.client()
        data = batch_metadata(
            client, app_id=app_id, batch_experiment_id=batch_experiment_id
        )
        endpoint = _helpers._endpoint_from_client(client)
        return _helpers._save_experiment_file(
            data, endpoint, "batch", batch_experiment_id, filename="metadata.json"
        )

    mcp_fw.tool(
        mcp,
        create_batch,
        name="cloud_create_batch",
        normalize_empty=["name", "description"],
    )

    mcp_fw.tool(
        mcp,
        update_batch,
        name="cloud_update_batch",
        normalize_empty=["name", "description"],
    )

    mcp_fw.tool(
        mcp,
        delete_batch,
        name="cloud_delete_batch",
        result_message="Deleted batch experiment {batch_experiment_id}",
    )
