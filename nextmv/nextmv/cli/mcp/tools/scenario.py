"""MCP tools for cloud scenario tests."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.scenario import create_scenario_test as _create_scenario_test
from nextmv.cli.actions.scenario import delete_scenario_test as _delete_scenario_test
from nextmv.cli.actions.scenario import get_scenario_test as _get_scenario_test
from nextmv.cli.actions.scenario import list_scenario_tests as _list_scenario_tests
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud scenario test tools."""

    @mcp.tool()
    def cloud_list_scenario_tests(app_id: str) -> list[dict[str, Any]]:
        """List scenario tests for a Nextmv Cloud application.

        Scenario tests run the application with multiple
        configurations (scenarios) to compare different solver
        setups side by side.

        Args:
            app_id: The application ID.
        """

        client = _helpers._get_client()
        return _list_scenario_tests(client, app_id)

    @mcp.tool()
    def cloud_get_scenario_test(
        app_id: str,
        scenario_test_id: str,
    ) -> str:
        """Get details and results of a scenario test.

        Saves the full test data (including per-scenario run results)
        to ~/.nextmv/experiments/. Use file-reading tools to inspect
        the contents.

        Args:
            app_id: The application ID.
            scenario_test_id: The scenario test ID.
        """

        client = _helpers._get_client()
        data = _get_scenario_test(client, app_id, scenario_test_id)
        endpoint = _helpers._endpoint_from_client(client)
        return _helpers._save_experiment_file(data, endpoint, "scenario", scenario_test_id)

    @mcp.tool()
    def cloud_create_scenario_test(
        app_id: str,
        scenarios: list[dict[str, Any]],
        scenario_test_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        repetitions: int = 0,
        content_type: str | None = None,
    ) -> str:
        """Create a scenario test for a Nextmv Cloud application.

        A scenario test runs the app with multiple scenario configurations
        to compare different setups.

        Args:
            app_id: The application ID.
            scenarios: List of scenario definitions. Each dict has keys:

                - instance_id (str, required): Instance to run against.
                - scenario_id (str, optional): ID for this scenario.
                - scenario_input (dict, required): Must contain
                  ``scenario_input_type`` ("input_set", "input", or "new")
                  and ``scenario_input_data`` (a string input-set ID, a list
                  of input IDs, or a list of raw dicts).
                - configuration (list[dict], optional): Each entry has
                  ``name`` (str) and ``values`` (list[str]).  A shorthand
                  ``options`` dict (``{"key": "value", ...}``) is also
                  accepted and is expanded to single-value configurations.
            scenario_test_id: Optional test ID.
            name: Optional name.
            description: Optional description.
            repetitions: Number of extra repetitions per scenario (default: 0).
                0 means each scenario executes once. 1 means each scenario
                executes twice (the original run plus one repetition), etc.
            content_type: Content type for the app's input/output format.
                Set to "multi-file" for multi-file apps, or "json" for
                standard JSON apps. If not provided, defaults to the app's
                configured content type. Required for multi-file apps.
        """

        scenario_test_id = _helpers._none_if_empty(scenario_test_id)
        name = _helpers._none_if_empty(name)
        description = _helpers._none_if_empty(description)
        content_type = _helpers._none_if_empty(content_type)

        if not scenarios:
            return "Error: at least one scenario is required."

        client = _helpers._get_client()
        try:
            return _create_scenario_test(
                client,
                app_id,
                scenarios=scenarios,
                scenario_test_id=scenario_test_id,
                name=name,
                description=description,
                repetitions=repetitions,
                content_type=content_type,
            )
        except (KeyError, ValueError) as exc:
            return f"Error: invalid scenario definition — {exc}"

    @mcp.tool()
    def cloud_delete_scenario_test(
        app_id: str,
        scenario_test_id: str,
    ) -> str:
        """Delete a scenario test permanently.

        Args:
            app_id: The application ID.
            scenario_test_id: The scenario test ID to delete.
        """

        client = _helpers._get_client()
        _delete_scenario_test(client, app_id, scenario_test_id)
        return f"Deleted scenario test {scenario_test_id}"
