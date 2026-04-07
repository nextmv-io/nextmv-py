"""MCP tools for cloud shadow tests."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.shadow import create_shadow_test as _create_shadow_test
from nextmv.cli.actions.shadow import delete_shadow_test as _delete_shadow_test
from nextmv.cli.actions.shadow import get_shadow_test as _get_shadow_test
from nextmv.cli.actions.shadow import list_shadow_tests as _list_shadow_tests
from nextmv.cli.actions.shadow import start_shadow_test as _start_shadow_test
from nextmv.cli.actions.shadow import stop_shadow_test as _stop_shadow_test
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud shadow test tools."""

    @mcp.tool()
    def cloud_list_shadow_tests(app_id: str) -> list[dict[str, Any]]:
        """List shadow tests for a Nextmv Cloud application.

        A shadow test mirrors live production traffic to a candidate
        instance running alongside the baseline, allowing side-by-side
        comparison of results without affecting production.

        Args:
            app_id: The application ID.
        """

        client = _helpers._get_client()
        return _list_shadow_tests(client, app_id)

    @mcp.tool()
    def cloud_get_shadow_test(
        app_id: str,
        shadow_test_id: str,
    ) -> str:
        """Get details and results of a shadow test.

        Saves the full test data (including comparison results) to a
        local temp file. Use file-reading tools to inspect the
        contents.

        Args:
            app_id: The application ID.
            shadow_test_id: The shadow test ID.
        """

        client = _helpers._get_client()
        data = _get_shadow_test(client, app_id, shadow_test_id)
        return _helpers._save_to_json_file(data, prefix=f"shadow_test_{shadow_test_id}")

    @mcp.tool()
    def cloud_create_shadow_test(
        app_id: str,
        comparisons: dict[str, list[str]],
        termination_events: dict[str, Any],
        shadow_test_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        start_events: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
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

        client = _helpers._get_client()
        return _create_shadow_test(
            client,
            app_id,
            comparisons=comparisons,
            termination_events=termination_events,
            shadow_test_id=shadow_test_id,
            name=name,
            description=description,
            start_events=start_events,
        )

    @mcp.tool()
    def cloud_start_shadow_test(app_id: str, shadow_test_id: str) -> str:
        """Start a shadow test that is in draft state.

        The test must have been created but not yet started. Once
        started, live traffic will be mirrored to candidate instances.

        Args:
            app_id: The application ID.
            shadow_test_id: The shadow test ID to start.
        """

        client = _helpers._get_client()
        _start_shadow_test(client, app_id, shadow_test_id)
        return f"Started shadow test {shadow_test_id}"

    @mcp.tool()
    def cloud_stop_shadow_test(
        app_id: str,
        shadow_test_id: str,
        intent: str = "cancel",
    ) -> str:
        """Stop a running shadow test.

        Use ``"cancel"`` to discard the test or ``"promote"`` to
        promote the candidate instance to production.

        Args:
            app_id: The application ID.
            shadow_test_id: The shadow test ID to stop.
            intent: Stop intent. Allowed values: ``"cancel"``
                (default) or ``"promote"``.
        """

        client = _helpers._get_client()
        _stop_shadow_test(client, app_id, shadow_test_id, intent=intent)
        return f"Stopped shadow test {shadow_test_id} with intent {intent}"

    @mcp.tool()
    def cloud_delete_shadow_test(app_id: str, shadow_test_id: str) -> str:
        """Delete a shadow test permanently.

        Args:
            app_id: The application ID.
            shadow_test_id: The shadow test ID to delete.
        """

        client = _helpers._get_client()
        _delete_shadow_test(client, app_id, shadow_test_id)
        return f"Deleted shadow test {shadow_test_id}"
