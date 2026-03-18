"""MCP tools for cloud shadow tests."""

from typing import Any

from mcp.server.fastmcp import FastMCP

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

        app = _helpers._get_app(app_id)
        tests = app.list_shadow_tests()
        return [t.to_dict() for t in tests]

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

        app = _helpers._get_app(app_id)
        test = app.shadow_test(shadow_test_id=shadow_test_id)
        return _helpers._save_to_file(test.to_dict(), prefix=f"shadow_test_{shadow_test_id}")

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

        app = _helpers._get_app(app_id)
        test = app.new_shadow_test(
            comparisons=comparisons,
            termination_events=termination_events,
            shadow_test_id=shadow_test_id,
            name=name,
            description=description,
            start_events=start_events,
        )
        return test.to_dict()

    @mcp.tool()
    def cloud_start_shadow_test(app_id: str, shadow_test_id: str) -> str:
        """Start a shadow test that is in draft state.

        The test must have been created but not yet started. Once
        started, live traffic will be mirrored to candidate instances.

        Args:
            app_id: The application ID.
            shadow_test_id: The shadow test ID to start.
        """

        app = _helpers._get_app(app_id)
        app.start_shadow_test(shadow_test_id=shadow_test_id)
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

        from nextmv.cloud import StopIntent

        app = _helpers._get_app(app_id)
        app.stop_shadow_test(
            shadow_test_id=shadow_test_id,
            intent=StopIntent(intent),
        )
        return f"Stopped shadow test {shadow_test_id} with intent {intent}"

    @mcp.tool()
    def cloud_delete_shadow_test(app_id: str, shadow_test_id: str) -> str:
        """Delete a shadow test permanently.

        Args:
            app_id: The application ID.
            shadow_test_id: The shadow test ID to delete.
        """

        app = _helpers._get_app(app_id)
        app.delete_shadow_test(shadow_test_id=shadow_test_id)
        return f"Deleted shadow test {shadow_test_id}"
