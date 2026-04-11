"""Core scenario test actions.

Pure functions that wrap SDK calls. No CLI or MCP presentation concerns.

Scenario tests run an application with multiple scenario definitions —
each combining an instance, an input source, and optional configuration
variations — to compare different solver setups side by side. The
underlying storage is batch experiments.

The ``build_scenario`` helper converts a plain dict (from CLI JSON
parsing or an LLM payload) into a typed SDK ``Scenario`` object, so the
action layer can accept loose dicts while the SDK keeps its typed
interface.
"""

from typing import TYPE_CHECKING, Any

from nextmv.cli.framework.options import (
    AppIdRequiredOption,
    DescriptionOption,
    NameOption,
    OptionalScenarioTestIdOption,
    ScenarioTestIdOption,
)
from nextmv.cloud import Application, Client

if TYPE_CHECKING:
    from nextmv.cloud.scenario import Scenario


def build_scenario(s: dict[str, Any]) -> "Scenario":
    """Convert a plain dict into a ``Scenario`` dataclass instance.

    Accepts the three ``scenario_input`` shapes: explicit
    ``scenario_input_type`` / ``scenario_input_data``, ``input_set_id``
    shorthand, or ``managed_input_ids`` shorthand. Also accepts either a
    list of ``configuration`` entries or a dict shorthand.
    """

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


def list_scenario_tests(
    client: Client,
    app_id: AppIdRequiredOption,
) -> list[dict[str, Any]]:
    """List all Nextmv Cloud scenario tests for an application.

    Returns a list of scenario test dicts.
    """
    app = Application(client=client, id=app_id)
    tests = app.list_scenario_tests()
    return [t.to_dict() for t in tests]


def get_scenario_test(
    client: Client,
    app_id: AppIdRequiredOption,
    scenario_test_id: ScenarioTestIdOption,
) -> dict[str, Any]:
    """Get details and results of a Nextmv Cloud scenario test.

    Returns the scenario test status and per-scenario run results (if
    the test has completed).
    """
    app = Application(client=client, id=app_id)
    test = app.scenario_test(scenario_test_id=scenario_test_id)
    return test.to_dict()


def create_scenario_test(
    client: Client,
    app_id: AppIdRequiredOption,
    scenarios: list[dict[str, Any]],
    scenario_test_id: OptionalScenarioTestIdOption = None,
    name: NameOption = None,
    description: DescriptionOption = None,
    repetitions: int = 0,
    content_type: str | None = None,
) -> str:
    """Create a new Nextmv Cloud scenario test.

    Each scenario definition dict is first converted to a typed
    ``Scenario`` object via :func:`build_scenario`. The SDK then creates
    the underlying batch experiment and returns the scenario test ID.

    Returns the new scenario test ID.
    """
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


def update_scenario_test(
    client: Client,
    app_id: AppIdRequiredOption,
    scenario_test_id: ScenarioTestIdOption,
    name: NameOption = None,
    description: DescriptionOption = None,
) -> dict[str, Any]:
    """Update a Nextmv Cloud scenario test.

    Only the provided fields are updated; omitted fields remain
    unchanged. Returns the updated scenario test dict.
    """
    app = Application(client=client, id=app_id)
    return app.update_scenario_test(
        scenario_test_id=scenario_test_id,
        name=name,
        description=description,
    ).to_dict()


def delete_scenario_test(
    client: Client,
    app_id: AppIdRequiredOption,
    scenario_test_id: ScenarioTestIdOption,
) -> None:
    """Delete a Nextmv Cloud scenario test permanently.

    This action cannot be undone.
    """
    app = Application(client=client, id=app_id)
    app.delete_scenario_test(scenario_test_id=scenario_test_id)
