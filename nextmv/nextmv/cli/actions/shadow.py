"""Core shadow test actions.

Pure functions that wrap SDK calls. No CLI or MCP concerns.
"""

from typing import Any

from nextmv.cloud import Application, Client, StopIntent


def list_shadow_tests(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all shadow tests for an application."""
    app = Application(client=client, id=app_id)
    tests = app.list_shadow_tests()
    return [t.to_dict() for t in tests]


def get_shadow_test(client: Client, app_id: str, shadow_test_id: str) -> dict[str, Any]:
    """Get details and results of a shadow test."""
    app = Application(client=client, id=app_id)
    test = app.shadow_test(shadow_test_id=shadow_test_id)
    return test.to_dict()


def create_shadow_test(
    client: Client,
    app_id: str,
    comparisons: dict[str, list[str]],
    termination_events: dict[str, Any],
    shadow_test_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    start_events: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a shadow test. Returns the test dict."""
    app = Application(client=client, id=app_id)
    test = app.new_shadow_test(
        comparisons=comparisons,
        termination_events=termination_events,
        shadow_test_id=shadow_test_id,
        name=name,
        description=description,
        start_events=start_events,
    )
    return test.to_dict()


def start_shadow_test(client: Client, app_id: str, shadow_test_id: str) -> None:
    """Start a shadow test."""
    app = Application(client=client, id=app_id)
    app.start_shadow_test(shadow_test_id=shadow_test_id)


def stop_shadow_test(client: Client, app_id: str, shadow_test_id: str, intent: str = "cancel") -> None:
    """Stop a shadow test."""
    app = Application(client=client, id=app_id)
    app.stop_shadow_test(
        shadow_test_id=shadow_test_id,
        intent=StopIntent(intent),
    )


def delete_shadow_test(client: Client, app_id: str, shadow_test_id: str) -> None:
    """Delete a shadow test."""
    app = Application(client=client, id=app_id)
    app.delete_shadow_test(shadow_test_id=shadow_test_id)
