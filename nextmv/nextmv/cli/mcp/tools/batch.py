"""MCP tools for cloud batch experiments."""

from typing import Any

from mcp.server.fastmcp import FastMCP

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

        app = _helpers._get_app(app_id)
        batch_id = app.new_batch_experiment(
            input_set_id=input_set_id,
            name=name,
            description=description,
            option_sets=option_sets,
        )
        return batch_id

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

        app = _helpers._get_app(app_id)
        batch = app.batch_experiment(batch_id=batch_id)
        return _helpers._save_to_file(batch.to_dict(), prefix=f"batch_{batch_id}")

    @mcp.tool()
    def cloud_list_batches(app_id: str) -> list[dict[str, Any]]:
        """List all batch experiments for a Nextmv Cloud application.

        Returns a list of batch experiment summaries including ID,
        name, status, and creation timestamp.

        Args:
            app_id: The application ID.
        """

        app = _helpers._get_app(app_id)
        batches = app.list_batch_experiments()
        return [b.to_dict() for b in batches]

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

        app = _helpers._get_app(app_id)
        metadata = app.batch_experiment_metadata(batch_id=batch_id)
        return _helpers._save_to_file(metadata.to_dict(), prefix=f"batch_metadata_{batch_id}")

    @mcp.tool()
    def cloud_delete_batch(app_id: str, batch_id: str) -> str:
        """Delete a batch experiment permanently.

        Args:
            app_id: The application ID.
            batch_id: The batch experiment ID to delete.
        """

        app = _helpers._get_app(app_id)
        app.delete_batch_experiment(batch_id=batch_id)
        return f"Deleted batch experiment {batch_id}"
