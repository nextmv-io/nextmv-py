"""Core scenario test actions.

Pure functions that wrap SDK calls. No CLI or MCP concerns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from nextmv.cloud import Application, Client

if TYPE_CHECKING:
    from nextmv.cloud.scenario import Scenario


def build_scenario(s: dict[str, Any]) -> Scenario:
    """Convert a plain dict into a ``Scenario`` dataclass instance."""

    from nextmv.cloud.scenario import (
        Scenario,
        ScenarioConfiguration,
        ScenarioInput,
        ScenarioInputType,
    )

    # --- Validate required keys ---
    missing = [k for k in ("scenario_input", "instance_id") if k not in s]
    if missing:
        raise ValueError(f"scenario is missing required keys: {missing}")

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
        for i, c in enumerate(raw_config):
            cfg_missing = [k for k in ("name", "values") if k not in c]
            if cfg_missing:
                raise ValueError(
                    f"configuration[{i}] is missing required keys: {cfg_missing}"
                )
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


def list_scenario_tests(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all scenario tests for an application."""
    app = Application(client=client, id=app_id)
    tests = app.list_scenario_tests()
    return [t.to_dict() for t in tests]


def get_scenario_test(client: Client, app_id: str, scenario_test_id: str) -> dict[str, Any]:
    """Get details and results of a scenario test."""
    app = Application(client=client, id=app_id)
    test = app.scenario_test(scenario_test_id=scenario_test_id)
    return test.to_dict()


def create_scenario_test(
    client: Client,
    app_id: str,
    scenarios: list[dict[str, Any]],
    scenario_test_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    repetitions: int = 0,
    content_type: str | None = None,
) -> str:
    """Create a scenario test. Returns the scenario test ID."""
    app = Application(client=client, id=app_id)
    scenario_objs = [build_scenario(s) for s in scenarios]
    return app.new_scenario_test(
        scenarios=scenario_objs,
        id=scenario_test_id,
        name=name,
        description=description,
        repetitions=repetitions,
        content_type=content_type,
    )


def delete_scenario_test(client: Client, app_id: str, scenario_test_id: str) -> None:
    """Delete a scenario test."""
    app = Application(client=client, id=app_id)
    app.delete_scenario_test(scenario_test_id=scenario_test_id)
