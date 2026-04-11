"""MCP tools for cloud scenario tests."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.scenario import (
    create_scenario_test,
    delete_scenario_test,
    get_scenario_test,
    list_scenario_tests,
    update_scenario_test,
)
from nextmv.cli.mcp import framework as mcp_fw
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud scenario test tools."""

    mcp_fw.tool(mcp, list_scenario_tests, name="cloud_list_scenario_tests")

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

        client = mcp_fw.client()
        data = get_scenario_test(
            client, app_id=app_id, scenario_test_id=scenario_test_id
        )
        endpoint = _helpers._endpoint_from_client(client)
        return _helpers._save_experiment_file(data, endpoint, "scenario", scenario_test_id)

    @mcp.tool()
    def cloud_create_scenario_test(
        app_id: str,
        scenarios: list[dict],
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

        client = mcp_fw.client()
        try:
            return create_scenario_test(
                client,
                app_id=app_id,
                scenarios=scenarios,
                scenario_test_id=scenario_test_id,
                name=name,
                description=description,
                repetitions=repetitions,
                content_type=content_type,
            )
        except (KeyError, ValueError) as exc:
            return f"Error: invalid scenario definition — {exc}"

    mcp_fw.tool(
        mcp,
        update_scenario_test,
        name="cloud_update_scenario_test",
        normalize_empty=["name", "description"],
    )

    mcp_fw.tool(
        mcp,
        delete_scenario_test,
        name="cloud_delete_scenario_test",
        result_message="Deleted scenario test {scenario_test_id}",
    )
