"""MCP tools for cloud batch experiments."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.batch import batch_metadata as _batch_metadata
from nextmv.cli.actions.batch import create_batch as _create_batch
from nextmv.cli.actions.batch import delete_batch as _delete_batch
from nextmv.cli.actions.batch import get_batch as _get_batch
from nextmv.cli.actions.batch import list_batches as _list_batches
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud batch experiment tools."""

    @mcp.tool()
    def cloud_create_batch(
        app_id: str,
        input_set_id: str,
        name: str | None = None,
        description: str | None = None,
        option_sets: dict[str, dict[str, str]] | None = None,
    ) -> str:
        """Create a batch experiment for a Nextmv Cloud application.

        A batch experiment runs the application against every input in
        an input set, optionally with multiple option sets to compare
        different solver configurations side by side. Returns the
        batch experiment ID.

        Args:
            app_id: The application ID.
            input_set_id: ID of the input set to run against.
            name: Optional human-readable name for the experiment.
            description: Optional description.
            option_sets: Optional option sets to compare. Keys are
                set names, values are dictionaries of solver options,
                e.g. ``{"fast": {"solve.duration": "5s"}}``.
        """

        name = _helpers._none_if_empty(name)
        description = _helpers._none_if_empty(description)

        client = _helpers._get_client()
        return _create_batch(
            client,
            app_id,
            input_set_id=input_set_id,
            name=name,
            description=description,
            option_sets=option_sets,
        )

    @mcp.tool()
    def cloud_get_batch(app_id: str, batch_id: str) -> str:
        """Get details and run results of a batch experiment.

        Saves the full experiment data (including individual run
        results) to a local temp file. Use file-reading tools to
        inspect the contents.

        Args:
            app_id: The application ID.
            batch_id: The batch experiment ID.
        """

        client = _helpers._get_client()
        data = _get_batch(client, app_id, batch_id)
        endpoint = _helpers._endpoint_from_client(client)
        return _helpers._save_experiment_file(data, endpoint, "batch", batch_id)

    @mcp.tool()
    def cloud_list_batches(app_id: str) -> list[dict[str, Any]]:
        """List all batch experiments for a Nextmv Cloud application.

        Returns a list of batch experiment summaries including ID,
        name, status, and creation timestamp.

        Args:
            app_id: The application ID.
        """

        client = _helpers._get_client()
        return _list_batches(client, app_id)

    @mcp.tool()
    def cloud_batch_metadata(app_id: str, batch_id: str) -> str:
        """Get metadata for a batch experiment.

        Returns experiment-level metadata including status, run
        counts, and timing information. Saves the result to a local
        temp file. Use file-reading tools to inspect the contents.

        Args:
            app_id: The application ID.
            batch_id: The batch experiment ID.
        """

        client = _helpers._get_client()
        data = _batch_metadata(client, app_id, batch_id)
        endpoint = _helpers._endpoint_from_client(client)
        return _helpers._save_experiment_file(data, endpoint, "batch", batch_id, filename="metadata.json")

    @mcp.tool()
    def cloud_delete_batch(app_id: str, batch_id: str) -> str:
        """Delete a batch experiment permanently.

        Args:
            app_id: The application ID.
            batch_id: The batch experiment ID to delete.
        """

        client = _helpers._get_client()
        _delete_batch(client, app_id, batch_id)
        return f"Deleted batch experiment {batch_id}"
