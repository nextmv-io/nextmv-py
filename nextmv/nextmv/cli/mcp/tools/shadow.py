"""MCP tools for cloud shadow tests."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.shadow import (
    create_shadow_test,
    delete_shadow_test,
    get_shadow_test,
    list_shadow_tests,
    shadow_test_metadata,
    start_shadow_test,
    stop_shadow_test,
    update_shadow_test,
)
from nextmv.cli.mcp import framework as mcp_fw
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud shadow test tools."""

    mcp_fw.tool(mcp, list_shadow_tests, name="cloud_list_shadow_tests")

    @mcp.tool()
    def cloud_get_shadow_test(app_id: str, shadow_test_id: str) -> str:
        """Get details and results of a shadow test.

        Saves the full test data (including comparison results) to
        ~/.nextmv/experiments/. Use file-reading tools to inspect the
        contents.

        Args:
            app_id: The application ID.
            shadow_test_id: The shadow test ID.
        """

        client = mcp_fw.client()
        data = get_shadow_test(client, app_id=app_id, shadow_test_id=shadow_test_id)
        endpoint = _helpers._endpoint_from_client(client)
        return _helpers._save_experiment_file(data, endpoint, "shadow", shadow_test_id)

    @mcp.tool()
    def cloud_shadow_test_metadata(app_id: str, shadow_test_id: str) -> str:
        """Get metadata for a shadow test.

        Returns test-level metadata only — status, run counts, and
        timing. Saves the result to ~/.nextmv/experiments/. Use
        file-reading tools to inspect the contents.

        Args:
            app_id: The application ID.
            shadow_test_id: The shadow test ID.
        """

        client = mcp_fw.client()
        data = shadow_test_metadata(
            client, app_id=app_id, shadow_test_id=shadow_test_id
        )
        endpoint = _helpers._endpoint_from_client(client)
        return _helpers._save_experiment_file(
            data, endpoint, "shadow", shadow_test_id, filename="metadata.json"
        )

    # create stays inline: takes untyped dict parameters
    # (termination_events, start_events) that the mcp_fw introspection
    # layer can't describe usefully, and it benefits from catching bad
    # LLM payloads with a friendly error string.
    @mcp.tool()
    def cloud_create_shadow_test(
        app_id: str,
        comparisons: dict[str, list[str]],
        termination_events: dict,
        shadow_test_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        start_events: dict | None = None,
    ) -> dict | str:
        """Create a shadow test for a Nextmv Cloud application.

        A shadow test mirrors live traffic to candidate instances for
        comparison against the baseline without affecting production.

        Args:
            app_id: The application ID.
            comparisons: Mapping of baseline instance IDs to lists of
                candidate instance IDs, e.g.
                ``{"production": ["candidate-v2"]}``.
            termination_events: Conditions for stopping the test,
                e.g. ``{"maximum_runs": 1000}`` or
                ``{"time": "2024-12-31T00:00:00Z"}``.
            shadow_test_id: Optional test ID. Auto-generated if omitted.
            name: Optional human-readable name.
            description: Optional description.
            start_events: Optional start trigger, e.g.
                ``{"time": "2024-01-01T00:00:00Z"}``. Starts immediately
                if omitted.
        """

        shadow_test_id = _helpers._none_if_empty(shadow_test_id)
        name = _helpers._none_if_empty(name)
        description = _helpers._none_if_empty(description)

        client = mcp_fw.client()
        try:
            return create_shadow_test(
                client,
                app_id=app_id,
                comparisons=comparisons,
                termination_events=termination_events,
                shadow_test_id=shadow_test_id,
                name=name,
                description=description,
                start_events=start_events,
            )
        except (KeyError, ValueError) as exc:
            return f"Error: invalid shadow test definition — {exc}"

    mcp_fw.tool(
        mcp,
        update_shadow_test,
        name="cloud_update_shadow_test",
        normalize_empty=["name", "description"],
    )

    mcp_fw.tool(
        mcp,
        start_shadow_test,
        name="cloud_start_shadow_test",
        result_message="Started shadow test {shadow_test_id}",
    )

    mcp_fw.tool(
        mcp,
        stop_shadow_test,
        name="cloud_stop_shadow_test",
        result_message="Stopped shadow test {shadow_test_id} with intent {intent}",
    )

    mcp_fw.tool(
        mcp,
        delete_shadow_test,
        name="cloud_delete_shadow_test",
        result_message="Deleted shadow test {shadow_test_id}",
    )
