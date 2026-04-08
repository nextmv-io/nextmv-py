"""MCP tools for cloud switchback tests."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.switchback import create_switchback_test as _create_switchback_test
from nextmv.cli.actions.switchback import delete_switchback_test as _delete_switchback_test
from nextmv.cli.actions.switchback import get_switchback_test as _get_switchback_test
from nextmv.cli.actions.switchback import list_switchback_tests as _list_switchback_tests
from nextmv.cli.actions.switchback import start_switchback_test as _start_switchback_test
from nextmv.cli.actions.switchback import stop_switchback_test as _stop_switchback_test
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud switchback test tools."""

    @mcp.tool()
    def cloud_list_switchback_tests(app_id: str) -> list[dict[str, Any]]:
        """List switchback tests for a Nextmv Cloud application.

        A switchback test alternates live traffic between baseline and
        candidate instances over fixed time periods, providing a
        statistically robust comparison of performance.

        Args:
            app_id: The application ID.
        """

        client = _helpers._get_client()
        return _list_switchback_tests(client, app_id)

    @mcp.tool()
    def cloud_get_switchback_test(
        app_id: str,
        switchback_test_id: str,
    ) -> str:
        """Get details and results of a switchback test.

        Saves the full test data (including per-unit comparison
        results) to a local temp file. Use file-reading tools to
        inspect the contents.

        Args:
            app_id: The application ID.
            switchback_test_id: The switchback test ID.
        """

        client = _helpers._get_client()
        data = _get_switchback_test(client, app_id, switchback_test_id)
        return _helpers._save_to_json_file(data, prefix=f"switchback_test_{switchback_test_id}")

    @mcp.tool()
    def cloud_create_switchback_test(
        app_id: str,
        baseline_instance_id: str,
        candidate_instance_id: str,
        unit_duration_minutes: float,
        units: int,
        switchback_test_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a switchback test for a Nextmv Cloud application.

        A switchback test alternates live traffic between baseline and
        candidate instances over fixed time periods (units). The total
        test duration is ``unit_duration_minutes * units``.

        Args:
            app_id: The application ID.
            baseline_instance_id: The baseline instance ID.
            candidate_instance_id: The candidate instance ID to
                compare against the baseline.
            unit_duration_minutes: Duration of each switchback unit
                in minutes (e.g., ``60.0`` for one-hour units).
            units: Total number of switchback units (alternating
                periods between baseline and candidate).
            switchback_test_id: Optional test ID. Auto-generated if
                omitted.
            name: Optional human-readable name.
            description: Optional description.
        """

        switchback_test_id = _helpers._none_if_empty(switchback_test_id)
        name = _helpers._none_if_empty(name)
        description = _helpers._none_if_empty(description)

        client = _helpers._get_client()
        return _create_switchback_test(
            client,
            app_id,
            baseline_instance_id=baseline_instance_id,
            candidate_instance_id=candidate_instance_id,
            unit_duration_minutes=unit_duration_minutes,
            units=units,
            switchback_test_id=switchback_test_id,
            name=name,
            description=description,
        )

    @mcp.tool()
    def cloud_start_switchback_test(
        app_id: str,
        switchback_test_id: str,
    ) -> str:
        """Start a switchback test that is in draft state.

        Once started, live traffic will begin alternating between
        the baseline and candidate instances.

        Args:
            app_id: The application ID.
            switchback_test_id: The switchback test ID to start.
        """

        client = _helpers._get_client()
        _start_switchback_test(client, app_id, switchback_test_id)
        return f"Started switchback test {switchback_test_id}"

    @mcp.tool()
    def cloud_stop_switchback_test(
        app_id: str,
        switchback_test_id: str,
        intent: str = "cancel",
    ) -> str:
        """Stop a running switchback test.

        Use ``"cancel"`` to discard the test or ``"promote"`` to
        promote the candidate instance to production.

        Args:
            app_id: The application ID.
            switchback_test_id: The switchback test ID to stop.
            intent: Stop intent. Allowed values: ``"cancel"``
                (default) or ``"promote"``.
        """

        client = _helpers._get_client()
        _stop_switchback_test(client, app_id, switchback_test_id, intent=intent)
        return f"Stopped switchback test {switchback_test_id} with intent {intent}"

    @mcp.tool()
    def cloud_delete_switchback_test(
        app_id: str,
        switchback_test_id: str,
    ) -> str:
        """Delete a switchback test permanently.

        Args:
            app_id: The application ID.
            switchback_test_id: The switchback test ID to delete.
        """

        client = _helpers._get_client()
        _delete_switchback_test(client, app_id, switchback_test_id)
        return f"Deleted switchback test {switchback_test_id}"
