"""MCP tools for cloud acceptance tests."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.acceptance import create_acceptance_test as _create_acceptance_test
from nextmv.cli.actions.acceptance import delete_acceptance_test as _delete_acceptance_test
from nextmv.cli.actions.acceptance import get_acceptance_test as _get_acceptance_test
from nextmv.cli.actions.acceptance import list_acceptance_tests as _list_acceptance_tests
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud acceptance test tools."""

    @mcp.tool()
    def cloud_list_acceptance_tests(app_id: str) -> list[dict[str, Any]]:
        """List acceptance tests for a Nextmv Cloud application.

        Acceptance tests compare a candidate instance against a
        baseline using defined metrics. Returns a list of test
        summaries.

        Args:
            app_id: The application ID.
        """

        client = _helpers._get_client()
        return _list_acceptance_tests(client, app_id)

    @mcp.tool()
    def cloud_get_acceptance_test(
        app_id: str,
        acceptance_test_id: str,
    ) -> str:
        """Get details and results of an acceptance test.

        Saves the full test data (including metric comparisons and
        pass/fail results) to a local temp file. Use file-reading
        tools to inspect the contents.

        Args:
            app_id: The application ID.
            acceptance_test_id: The acceptance test ID.
        """

        client = _helpers._get_client()
        data = _get_acceptance_test(client, app_id, acceptance_test_id)
        return _helpers._save_to_json_file(data, prefix=f"acceptance_test_{acceptance_test_id}")

    @mcp.tool()
    def cloud_create_acceptance_test(
        app_id: str,
        candidate_instance_id: str,
        baseline_instance_id: str,
        metrics: list[dict[str, Any]],
        acceptance_test_id: str | None = None,
        name: str | None = None,
        input_set_id: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create an acceptance test comparing two instances.

        An acceptance test runs both instances against the same input
        set and compares results using the specified metrics to
        determine whether the candidate meets acceptance criteria.

        Args:
            app_id: The application ID.
            candidate_instance_id: The candidate instance to evaluate.
            baseline_instance_id: The baseline instance to compare
                the candidate against.
            metrics: List of metric definitions. Each metric is a dict
                with keys: ``field``, ``metric_type``, ``params``,
                ``statistic``.
            acceptance_test_id: Optional test ID. Auto-generated if
                omitted.
            name: Optional human-readable name.
            input_set_id: Optional input set ID to run the test against.
            description: Optional description.
        """

        acceptance_test_id = _helpers._none_if_empty(acceptance_test_id)
        name = _helpers._none_if_empty(name)
        input_set_id = _helpers._none_if_empty(input_set_id)
        description = _helpers._none_if_empty(description)

        client = _helpers._get_client()
        return _create_acceptance_test(
            client,
            app_id,
            candidate_instance_id=candidate_instance_id,
            baseline_instance_id=baseline_instance_id,
            metrics=metrics,
            acceptance_test_id=acceptance_test_id,
            name=name,
            input_set_id=input_set_id,
            description=description,
        )

    @mcp.tool()
    def cloud_delete_acceptance_test(
        app_id: str,
        acceptance_test_id: str,
    ) -> str:
        """Delete an acceptance test permanently.

        Args:
            app_id: The application ID.
            acceptance_test_id: The acceptance test ID to delete.
        """

        client = _helpers._get_client()
        _delete_acceptance_test(client, app_id, acceptance_test_id)
        return f"Deleted acceptance test {acceptance_test_id}"
