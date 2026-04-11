"""Core shadow test actions.

Pure functions that wrap SDK calls. No CLI or MCP presentation concerns.

A shadow test mirrors live production traffic to one or more candidate
instances running alongside a baseline, allowing side-by-side comparison
of results without affecting production. Tests are created in a draft
state, started explicitly or on a schedule, and eventually stopped with
a ``StopIntent`` value.
"""

from typing import Any

from nextmv.cli.framework.options import (
    AppIdRequiredOption,
    DescriptionOption,
    NameOption,
    ShadowTestIdOption,
)
from nextmv.cloud import Application, Client, StopIntent


def list_shadow_tests(
    client: Client,
    app_id: AppIdRequiredOption,
) -> list[dict[str, Any]]:
    """List all Nextmv Cloud shadow tests for an application.

    Returns a list of shadow test summary dicts including ID, name,
    status, and creation timestamp.
    """
    app = Application(client=client, id=app_id)
    tests = app.list_shadow_tests()
    return [t.to_dict() for t in tests]


def get_shadow_test(
    client: Client,
    app_id: AppIdRequiredOption,
    shadow_test_id: ShadowTestIdOption,
) -> dict[str, Any]:
    """Get details and results of a Nextmv Cloud shadow test.

    Returns the full test dict including configuration, status, and
    comparison run results (if the test has runs).
    """
    app = Application(client=client, id=app_id)
    test = app.shadow_test(shadow_test_id=shadow_test_id)
    return test.to_dict()


def shadow_test_metadata(
    client: Client,
    app_id: AppIdRequiredOption,
    shadow_test_id: ShadowTestIdOption,
) -> dict[str, Any]:
    """Get metadata for a Nextmv Cloud shadow test.

    Returns test-level metadata only — status, run counts, and timing
    — without the full per-run details. Faster than :func:`get_shadow_test`
    when per-run results are not needed.
    """
    app = Application(client=client, id=app_id)
    metadata = app.shadow_test_metadata(shadow_test_id=shadow_test_id)
    return metadata.to_dict()


def create_shadow_test(
    client: Client,
    app_id: AppIdRequiredOption,
    comparisons: dict[str, list[str]],
    termination_events: Any,
    shadow_test_id: str | None = None,
    name: NameOption = None,
    description: DescriptionOption = None,
    start_events: Any | None = None,
) -> dict[str, Any]:
    """Create a new Nextmv Cloud shadow test in draft mode.

    ``comparisons`` maps baseline instance IDs to lists of candidate
    instance IDs. ``termination_events`` and ``start_events`` are SDK
    dataclasses or plain dicts carrying the stop/start conditions.

    Returns the created test dict.
    """
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


def update_shadow_test(
    client: Client,
    app_id: AppIdRequiredOption,
    shadow_test_id: ShadowTestIdOption,
    name: NameOption = None,
    description: DescriptionOption = None,
) -> dict[str, Any]:
    """Update a Nextmv Cloud shadow test.

    Only the provided fields are updated; omitted fields remain
    unchanged. Returns the updated test dict.
    """
    app = Application(client=client, id=app_id)
    return app.update_shadow_test(
        shadow_test_id=shadow_test_id,
        name=name,
        description=description,
    ).to_dict()


def start_shadow_test(
    client: Client,
    app_id: AppIdRequiredOption,
    shadow_test_id: ShadowTestIdOption,
) -> None:
    """Start a Nextmv Cloud shadow test that is in draft state.

    Once started, live traffic will be mirrored to candidate instances
    as configured by the test's comparisons.
    """
    app = Application(client=client, id=app_id)
    app.start_shadow_test(shadow_test_id=shadow_test_id)


def stop_shadow_test(
    client: Client,
    app_id: AppIdRequiredOption,
    shadow_test_id: ShadowTestIdOption,
    intent: str = "cancel",
) -> None:
    """Stop a running Nextmv Cloud shadow test.

    ``intent`` is the string value of a ``StopIntent`` enum entry —
    typically ``"cancel"`` (discard the test) or ``"complete"``
    (mark the test as successfully complete).
    """
    app = Application(client=client, id=app_id)
    app.stop_shadow_test(
        shadow_test_id=shadow_test_id,
        intent=StopIntent(intent),
    )


def delete_shadow_test(
    client: Client,
    app_id: AppIdRequiredOption,
    shadow_test_id: ShadowTestIdOption,
) -> None:
    """Delete a Nextmv Cloud shadow test permanently.

    This action cannot be undone. All associated data, including run
    results, will be deleted.
    """
    app = Application(client=client, id=app_id)
    app.delete_shadow_test(shadow_test_id=shadow_test_id)
