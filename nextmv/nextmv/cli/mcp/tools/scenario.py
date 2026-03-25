"""MCP tools for cloud scenario tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.mcp.tools import _helpers

if TYPE_CHECKING:
    from nextmv.cloud.scenario import Scenario


def _build_scenario(s: dict[str, Any]) -> Scenario:
    """Convert a plain dict into a ``Scenario`` dataclass instance."""

    from nextmv.cloud.scenario import (
        Scenario,
        ScenarioConfiguration,
        ScenarioInput,
        ScenarioInputType,
    )

    # --- Build ScenarioInput ---
    raw_input = s["scenario_input"]
    if "scenario_input_type" in raw_input:
        si = ScenarioInput(
            scenario_input_type=ScenarioInputType(raw_input["scenario_input_type"]),
            scenario_input_data=raw_input["scenario_input_data"],
        )
    elif "input_set_id" in raw_input:
        si = ScenarioInput(
            scenario_input_type=ScenarioInputType.INPUT_SET,
            scenario_input_data=raw_input["input_set_id"],
        )
    elif "managed_input_ids" in raw_input:
        si = ScenarioInput(
            scenario_input_type=ScenarioInputType.INPUT,
            scenario_input_data=raw_input["managed_input_ids"],
        )
    else:
        raise ValueError(
            f"scenario_input must contain 'scenario_input_type' + "
            f"'scenario_input_data', or 'input_set_id', or "
            f"'managed_input_ids'. Got: {raw_input}"
        )

    # --- Build configuration ---
    config = None
    raw_config = s.get("configuration")
    if isinstance(raw_config, list):
        config = [
            ScenarioConfiguration(name=c["name"], values=c["values"])
            for c in raw_config
        ]
    elif isinstance(raw_config, dict):
        # Shorthand: {"options": {"key": "val"}} or {"key": "val"}
        opts = raw_config.get("options", raw_config)
        config = [
            ScenarioConfiguration(
                name=k,
                values=v if isinstance(v, list) else [v],
            )
            for k, v in opts.items()
        ]

    return Scenario(
        scenario_input=si,
        instance_id=s["instance_id"],
        scenario_id=s.get("scenario_id"),
        configuration=config,
    )


def _cloud_create_scenario_test_impl(
    app_id: str,
    scenarios: list[dict[str, Any]],
    scenario_test_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    repetitions: int = 0,
    content_type: str | None = None,
) -> str:
    """Implementation for creating a scenario test."""

    scenario_test_id = _helpers._none_if_empty(scenario_test_id)
    name = _helpers._none_if_empty(name)
    description = _helpers._none_if_empty(description)
    content_type = _helpers._none_if_empty(content_type)

    app = _helpers._get_app(app_id)
    try:
        scenario_objs = [_build_scenario(s) for s in scenarios]
    except (KeyError, ValueError) as exc:
        return f"Error: invalid scenario definition — {exc}"

    test_id = app.new_scenario_test(
        scenarios=scenario_objs,
        id=scenario_test_id,
        name=name,
        description=description,
        repetitions=repetitions,
        content_type=content_type,
    )
    return test_id


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

        app = _helpers._get_app(app_id)
        tests = app.list_scenario_tests()
        return [t.to_dict() for t in tests]

    @mcp.tool()
    def cloud_get_scenario_test(
        app_id: str,
        scenario_test_id: str,
    ) -> str:
        """Get details and results of a scenario test.

        Saves the full test data (including per-scenario run results)
        to a local temp file. Use file-reading tools to inspect the
        contents.

        Args:
            app_id: The application ID.
            scenario_test_id: The scenario test ID.
        """

        app = _helpers._get_app(app_id)
        test = app.scenario_test(scenario_test_id=scenario_test_id)
        return _helpers._save_to_json_file(test.to_dict(), prefix=f"scenario_test_{scenario_test_id}")

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

        return _cloud_create_scenario_test_impl(
            app_id=app_id,
            scenarios=scenarios,
            scenario_test_id=scenario_test_id,
            name=name,
            description=description,
            repetitions=repetitions,
            content_type=content_type,
        )

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

        app = _helpers._get_app(app_id)
        app.delete_scenario_test(scenario_test_id=scenario_test_id)
        return f"Deleted scenario test {scenario_test_id}"
