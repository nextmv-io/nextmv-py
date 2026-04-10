"""Core switchback test actions.

Pure functions that wrap SDK calls. No CLI or MCP concerns.
"""

from typing import Any

from nextmv.cloud import Application, Client, StopIntent, TestComparisonSingle


def list_switchback_tests(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all switchback tests for an application."""
    app = Application(client=client, id=app_id)
    tests = app.list_switchback_tests()
    return [t.to_dict() for t in tests]


def get_switchback_test(client: Client, app_id: str, switchback_test_id: str) -> dict[str, Any]:
    """Get details and results of a switchback test."""
    app = Application(client=client, id=app_id)
    test = app.switchback_test(switchback_test_id=switchback_test_id)
    return test.to_dict()


def create_switchback_test(
    client: Client,
    app_id: str,
    baseline_instance_id: str,
    candidate_instance_id: str,
    unit_duration_minutes: float,
    units: int,
    switchback_test_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Create a switchback test. Returns the test dict."""
    app = Application(client=client, id=app_id)
    comparison = TestComparisonSingle(
        baseline_instance_id=baseline_instance_id,
        candidate_instance_id=candidate_instance_id,
    )
    test = app.new_switchback_test(
        comparison=comparison,
        unit_duration_minutes=unit_duration_minutes,
        units=units,
        switchback_test_id=switchback_test_id,
        name=name,
        description=description,
    )
    return test.to_dict()


def start_switchback_test(client: Client, app_id: str, switchback_test_id: str) -> None:
    """Start a switchback test."""
    app = Application(client=client, id=app_id)
    app.start_switchback_test(switchback_test_id=switchback_test_id)


def stop_switchback_test(client: Client, app_id: str, switchback_test_id: str, intent: str = "cancel") -> None:
    """Stop a switchback test."""
    app = Application(client=client, id=app_id)
    app.stop_switchback_test(
        switchback_test_id=switchback_test_id,
        intent=StopIntent(intent),
    )


def delete_switchback_test(client: Client, app_id: str, switchback_test_id: str) -> None:
    """Delete a switchback test."""
    app = Application(client=client, id=app_id)
    app.delete_switchback_test(switchback_test_id=switchback_test_id)
