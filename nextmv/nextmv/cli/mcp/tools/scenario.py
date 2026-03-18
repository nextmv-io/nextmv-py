"""MCP tools for cloud scenario tests."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.mcp.tools import _helpers


def _build_scenario(s: dict[str, Any]) -> Any:
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


def _resolve_input_set_for_scenario(app: Any, sid: str, scenario: Any) -> Any:
    """Resolve the input set for a single scenario based on its input type.

    Returns the input set object for the given scenario.
    """

    from nextmv.cloud.input_set import ManagedInput
    from nextmv.cloud.scenario import ScenarioInputType
    from nextmv.safe import safe_name_and_id

    input_type = scenario.scenario_input.scenario_input_type
    input_data = scenario.scenario_input.scenario_input_data

    if input_type == ScenarioInputType.INPUT_SET:
        return app.input_set(input_set_id=input_data)

    if input_type == ScenarioInputType.INPUT:
        is_name, is_id = safe_name_and_id(prefix="inpset", entity_id=sid)
        return app.new_input_set(
            id=is_id,
            name=is_name,
            description=f"Automatically created from scenario test: {is_id}",
            maximum_runs=20,
            inputs=[
                ManagedInput.from_dict(data={"id": iid})
                for iid in input_data
            ],
        )

    if input_type == ScenarioInputType.NEW:
        managed_inputs = []
        for data in input_data:
            upload_url = app.upload_url()
            app.upload_data(data=data, upload_url=upload_url)
            mi_name, mi_id = safe_name_and_id(prefix="man-input", entity_id=sid)
            mi = app.new_managed_input(
                id=mi_id,
                name=mi_name,
                description=f"Automatically created from scenario test: {mi_id}",
                upload_id=upload_url.upload_id,
            )
            managed_inputs.append(mi)
        is_name, is_id = safe_name_and_id(prefix="inpset", entity_id=sid)
        return app.new_input_set(
            id=is_id,
            name=is_name,
            description=f"Automatically created from scenario test: {is_id}",
            maximum_runs=20,
            inputs=managed_inputs,
        )

    raise ValueError(
        f"Unknown scenario input type: {input_type}"
    )


def _build_multifile_batch_payload(
    app: Any,
    scenario_objs: list[Any],
    scenarios_by_id: dict[str, Any],
    scenario_test_id: str,
    name: str,
    description: str | None,
    repetitions: int,
    content_type: str,
) -> dict[str, Any]:
    """Build the batch experiment payload for multi-file content types.

    Returns the full payload dict ready to POST to the API.
    """

    from nextmv.cloud.batch_experiment import BatchExperimentRun
    from nextmv.cloud.input_set import ManagedInput
    from nextmv.cloud.scenario import _option_sets

    input_sets: dict[str, Any] = {}
    instances: dict[str, Any] = {}
    for sid, scenario in scenarios_by_id.items():
        instances[sid] = app.instance(instance_id=scenario.instance_id)
        input_sets[sid] = _resolve_input_set_for_scenario(app, sid, scenario)

    opt_sets_by_scenario = _option_sets(scenario_objs)

    runs: list[dict[str, Any]] = []
    opt_sets: dict[str, Any] = {}
    run_counter = 0
    for sid, scenario_opt_sets in opt_sets_by_scenario.items():
        opt_sets = {**opt_sets, **scenario_opt_sets}
        input_set = input_sets[sid]
        scenario = scenarios_by_id[sid]

        for set_key in scenario_opt_sets.keys():
            inp_ids = (
                input_set.input_ids
                if len(input_set.input_ids) > 0
                else input_set.inputs
            )
            for inp in inp_ids:
                input_id = inp.id if isinstance(inp, ManagedInput) else inp
                for rep in range(repetitions + 1):
                    run_counter += 1
                    run = BatchExperimentRun(
                        input_id=input_id,
                        input_set_id=input_set.id,
                        instance_id=scenario.instance_id,
                        option_set=set_key,
                        scenario_id=sid,
                        repetition=rep,
                        run_number=str(run_counter),
                    )
                    runs.append(run.to_dict())

    payload: dict[str, Any] = {
        "id": scenario_test_id,
        "name": name,
        "type": "scenario",
        "content_type": content_type,
        "option_sets": opt_sets,
        "runs": runs,
    }
    if description is not None:
        payload["description"] = description

    return payload


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

    from nextmv.cloud.scenario import _scenarios_by_id
    from nextmv.safe import safe_id

    app = _helpers._get_app(app_id)
    try:
        scenario_objs = [_build_scenario(s) for s in scenarios]
    except (KeyError, ValueError) as exc:
        return f"Error: invalid scenario definition — {exc}"

    if not content_type:
        # Standard flow — delegate entirely to the SDK.
        test_id = app.new_scenario_test(
            scenarios=scenario_objs,
            id=scenario_test_id,
            name=name,
            description=description,
            repetitions=repetitions,
        )
        return test_id

    # When content_type is specified (e.g. "multi-file"), we must
    # include it in the batch experiment creation payload.  The SDK's
    # new_scenario_test does not support this parameter, so we
    # replicate its core logic here and inject content_type into the
    # POST payload sent to the API.
    #
    # SYNC NOTE: This block mirrors Application.new_scenario_test in
    # cloud/application/_batch_scenario.py.  If that method changes,
    # this code must be updated to match.
    if not scenarios:
        return "Error: at least one scenario must be provided."

    if scenario_test_id is None or scenario_test_id == "":
        scenario_test_id = safe_id("scenario")
    if name is None or name == "":
        name = scenario_test_id

    scenarios_by_id = _scenarios_by_id(scenario_objs)

    payload = _build_multifile_batch_payload(
        app=app,
        scenario_objs=scenario_objs,
        scenarios_by_id=scenarios_by_id,
        scenario_test_id=scenario_test_id,
        name=name,
        description=description,
        repetitions=repetitions,
        content_type=content_type,
    )

    response = app.client.request(
        method="POST",
        endpoint=f"{app.experiments_endpoint}/batch",
        payload=payload,
    )
    return response.json()["id"]


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
        return _helpers._save_to_file(test.to_dict(), prefix=f"scenario_test_{scenario_test_id}")

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
