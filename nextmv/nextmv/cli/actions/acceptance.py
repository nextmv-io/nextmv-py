"""Core acceptance test actions.

Pure functions that wrap SDK calls. No CLI or MCP presentation concerns.

Acceptance tests compare a candidate instance against a baseline using a
set of metrics. The ``get_acceptance_test_with_polling`` action blocks
until the test completes (or the poll timeout expires).
"""

from typing import Any

from nextmv.cli.framework.options import (
    AcceptanceTestIdOption,
    AppIdRequiredOption,
    DescriptionOption,
    NameOption,
    OptionalAcceptanceTestIdOption,
)
from nextmv.cloud import Application, Client


def list_acceptance_tests(
    client: Client,
    app_id: AppIdRequiredOption,
) -> list[dict[str, Any]]:
    """List all Nextmv Cloud acceptance tests for an application.

    Returns a list of acceptance test dicts.
    """
    app = Application(client=client, id=app_id)
    return [t.to_dict() for t in app.list_acceptance_tests()]


def get_acceptance_test(
    client: Client,
    app_id: AppIdRequiredOption,
    acceptance_test_id: AcceptanceTestIdOption,
) -> dict[str, Any]:
    """Get details and results of a Nextmv Cloud acceptance test.

    Returns the test status, metric comparisons, and pass/fail outcome
    (if the test has completed).
    """
    app = Application(client=client, id=app_id)
    return app.acceptance_test(acceptance_test_id=acceptance_test_id).to_dict()


def create_acceptance_test(
    client: Client,
    app_id: AppIdRequiredOption,
    candidate_instance_id: str,
    baseline_instance_id: str,
    metrics: list[Any],
    acceptance_test_id: OptionalAcceptanceTestIdOption = None,
    name: NameOption = None,
    input_set_id: str | None = None,
    description: DescriptionOption = None,
) -> dict[str, Any]:
    """Create a new Nextmv Cloud acceptance test.

    An acceptance test runs both the candidate and baseline instances
    against the same input set and compares results using the specified
    metrics to determine whether the candidate meets acceptance criteria.

    Returns the created test dict.
    """
    app = Application(client=client, id=app_id)
    return app.new_acceptance_test(
        candidate_instance_id=candidate_instance_id,
        baseline_instance_id=baseline_instance_id,
        metrics=metrics,
        id=acceptance_test_id,
        name=name,
        input_set_id=input_set_id,
        description=description,
    ).to_dict()


def update_acceptance_test(
    client: Client,
    app_id: AppIdRequiredOption,
    acceptance_test_id: AcceptanceTestIdOption,
    name: NameOption = None,
    description: DescriptionOption = None,
) -> dict[str, Any]:
    """Update a Nextmv Cloud acceptance test.

    Only the provided fields are updated; omitted fields remain unchanged.
    Returns the updated test dict.
    """
    app = Application(client=client, id=app_id)
    return app.update_acceptance_test(
        acceptance_test_id=acceptance_test_id,
        name=name,
        description=description,
    ).to_dict()


def delete_acceptance_test(
    client: Client,
    app_id: AppIdRequiredOption,
    acceptance_test_id: AcceptanceTestIdOption,
) -> None:
    """Delete a Nextmv Cloud acceptance test permanently.

    This action cannot be undone.
    """
    app = Application(client=client, id=app_id)
    app.delete_acceptance_test(acceptance_test_id=acceptance_test_id)
