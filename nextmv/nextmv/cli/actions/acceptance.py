"""Core acceptance test actions.

Pure functions that wrap SDK calls. No CLI or MCP concerns.
"""

from typing import Any

from nextmv.cloud import Application, Client


def list_acceptance_tests(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all acceptance tests for an application."""
    app = Application(client=client, id=app_id)
    tests = app.list_acceptance_tests()
    return [t.to_dict() for t in tests]


def get_acceptance_test(client: Client, app_id: str, acceptance_test_id: str) -> dict[str, Any]:
    """Get details and results of an acceptance test."""
    app = Application(client=client, id=app_id)
    test = app.acceptance_test(acceptance_test_id=acceptance_test_id)
    return test.to_dict()


def create_acceptance_test(
    client: Client,
    app_id: str,
    candidate_instance_id: str,
    baseline_instance_id: str,
    metrics: list[Any],
    acceptance_test_id: str | None = None,
    name: str | None = None,
    input_set_id: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Create an acceptance test. Returns the test dict."""
    app = Application(client=client, id=app_id)
    test = app.new_acceptance_test(
        candidate_instance_id=candidate_instance_id,
        baseline_instance_id=baseline_instance_id,
        metrics=metrics,
        id=acceptance_test_id,
        name=name,
        input_set_id=input_set_id,
        description=description,
    )
    return test.to_dict()


def delete_acceptance_test(client: Client, app_id: str, acceptance_test_id: str) -> None:
    """Delete an acceptance test."""
    app = Application(client=client, id=app_id)
    app.delete_acceptance_test(acceptance_test_id=acceptance_test_id)
