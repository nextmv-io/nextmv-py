"""Core switchback test actions.

Pure functions that wrap SDK calls. No CLI or MCP presentation concerns.

A switchback test alternates live traffic between a baseline and a
candidate instance over fixed time intervals (units), providing a
statistically robust side-by-side comparison. Tests are created in a
draft state, started explicitly or on a schedule, and eventually
stopped with a ``StopIntent`` value.
"""

from datetime import datetime
from typing import Any

from nextmv.cli.framework.options import (
    AppIdRequiredOption,
    DescriptionOption,
    NameOption,
    SwitchbackTestIdOption,
)
from nextmv.cloud import Application, Client, StopIntent, TestComparisonSingle


def list_switchback_tests(
    client: Client,
    app_id: AppIdRequiredOption,
) -> list[dict[str, Any]]:
    """List all Nextmv Cloud switchback tests for an application.

    Returns a list of switchback test summary dicts including ID,
    name, status, and creation timestamp.
    """
    app = Application(client=client, id=app_id)
    tests = app.list_switchback_tests()
    return [t.to_dict() for t in tests]


def get_switchback_test(
    client: Client,
    app_id: AppIdRequiredOption,
    switchback_test_id: SwitchbackTestIdOption,
) -> dict[str, Any]:
    """Get details and results of a Nextmv Cloud switchback test.

    Returns the full test dict including configuration, status, and
    per-unit comparison results.
    """
    app = Application(client=client, id=app_id)
    test = app.switchback_test(switchback_test_id=switchback_test_id)
    return test.to_dict()


def switchback_test_metadata(
    client: Client,
    app_id: AppIdRequiredOption,
    switchback_test_id: SwitchbackTestIdOption,
) -> dict[str, Any]:
    """Get metadata for a Nextmv Cloud switchback test.

    Returns test-level metadata only — status, unit counts, and
    timing — without the full per-unit details. Faster than
    :func:`get_switchback_test` when per-unit results are not needed.
    """
    app = Application(client=client, id=app_id)
    metadata = app.switchback_test_metadata(switchback_test_id=switchback_test_id)
    return metadata.to_dict()


def create_switchback_test(
    client: Client,
    app_id: AppIdRequiredOption,
    baseline_instance_id: str,
    candidate_instance_id: str,
    unit_duration_minutes: float,
    units: int,
    switchback_test_id: str | None = None,
    name: NameOption = None,
    description: DescriptionOption = None,
    start: datetime | None = None,
) -> dict[str, Any]:
    """Create a new Nextmv Cloud switchback test in draft mode.

    The test alternates between the baseline and candidate instances
    for ``units`` intervals of ``unit_duration_minutes`` minutes each.
    Total test duration is ``unit_duration_minutes * units``.

    Returns the created test dict.
    """
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
        start=start,
    )
    return test.to_dict()


def update_switchback_test(
    client: Client,
    app_id: AppIdRequiredOption,
    switchback_test_id: SwitchbackTestIdOption,
    name: NameOption = None,
    description: DescriptionOption = None,
) -> dict[str, Any]:
    """Update a Nextmv Cloud switchback test.

    Only the provided fields are updated; omitted fields remain
    unchanged. Returns the updated test dict.
    """
    app = Application(client=client, id=app_id)
    return app.update_switchback_test(
        switchback_test_id=switchback_test_id,
        name=name,
        description=description,
    ).to_dict()


def start_switchback_test(
    client: Client,
    app_id: AppIdRequiredOption,
    switchback_test_id: SwitchbackTestIdOption,
) -> None:
    """Start a Nextmv Cloud switchback test that is in draft state.

    Once started, live traffic will begin alternating between the
    baseline and candidate instances.
    """
    app = Application(client=client, id=app_id)
    app.start_switchback_test(switchback_test_id=switchback_test_id)


def stop_switchback_test(
    client: Client,
    app_id: AppIdRequiredOption,
    switchback_test_id: SwitchbackTestIdOption,
    intent: str = "cancel",
) -> None:
    """Stop a running Nextmv Cloud switchback test.

    ``intent`` is the string value of a ``StopIntent`` enum entry —
    typically ``"cancel"`` (discard the test) or ``"complete"``
    (mark the test as successfully complete).
    """
    app = Application(client=client, id=app_id)
    app.stop_switchback_test(
        switchback_test_id=switchback_test_id,
        intent=StopIntent(intent),
    )


def delete_switchback_test(
    client: Client,
    app_id: AppIdRequiredOption,
    switchback_test_id: SwitchbackTestIdOption,
) -> None:
    """Delete a Nextmv Cloud switchback test permanently.

    This action cannot be undone. All associated data, including run
    results, will be deleted.
    """
    app = Application(client=client, id=app_id)
    app.delete_switchback_test(switchback_test_id=switchback_test_id)
