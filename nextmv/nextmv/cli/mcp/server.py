"""Nextmv MCP server definition."""

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv import local
from nextmv.cloud import (
    Application,
    Client,
    clone_community_app,
    list_applications,
    list_community_apps,
)
from nextmv.polling import default_polling_options


def _get_client() -> Client:
    """Build a Cloud client from env var or CLI config."""

    api_key = os.getenv("NEXTMV_API_KEY")
    if api_key:
        endpoint = os.getenv("NEXTMV_ENDPOINT", "https://api.cloud.nextmv.io")
        if not endpoint.startswith("http"):
            endpoint = f"https://{endpoint}"
        return Client(api_key=api_key, url=endpoint)

    # Fall back to the CLI configuration file (~/.nextmv/config.yaml).
    try:
        from nextmv.cli.configuration.config import build_client

        return build_client()
    except Exception as e:
        raise ValueError(
            "No Nextmv API key found. Either set the NEXTMV_API_KEY "
            "environment variable or configure the CLI with: "
            "nextmv configuration create"
        ) from e


def _get_app(app_id: str) -> Application:
    """Build a cloud Application handle for the given ID."""

    client = _get_client()
    return Application(client=client, id=app_id)


def _get_local_app(app_dir: str, app_id: str | None = None) -> local.Application:
    """Build a local Application, registering it if needed."""

    app, _ = local.Application.get_or_register(app_src=app_dir, app_id=app_id)
    return app


# ════════════════════════════════════════════════════════════════
# Cloud: App management
# ════════════════════════════════════════════════════════════════


def _register_app_tools(mcp: FastMCP) -> None:
    """Register cloud application management tools."""

    @mcp.tool()
    def cloud_list_apps() -> list[dict[str, Any]]:
        """List all Nextmv Cloud applications in the account."""

        client = _get_client()
        apps = list_applications(client)
        return [a.to_dict() for a in apps]

    @mcp.tool()
    def cloud_get_app(app_id: str) -> dict[str, Any]:
        """Get details of a specific Nextmv Cloud application.

        Args:
            app_id: The application ID (e.g., 'my-routing-app').
        """

        client = _get_client()
        app = Application.get(client=client, id=app_id)
        return app.to_dict()

    @mcp.tool()
    def cloud_create_app(
        name: str,
        app_id: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a new Nextmv Cloud application.

        Args:
            name: A human-readable name for the application.
            app_id: Optional URL-friendly ID. Generated from name if omitted.
            description: Optional description of what the application does.
        """

        client = _get_client()
        app = Application.new(
            client=client,
            name=name,
            id=app_id,
            description=description,
        )
        return app.to_dict()

    @mcp.tool()
    def cloud_delete_app(app_id: str) -> str:
        """Delete a Nextmv Cloud application. This action is permanent.

        Args:
            app_id: The application ID to delete.
        """

        app = _get_app(app_id)
        app.delete()
        return f"Deleted application {app_id}"

    @mcp.tool()
    def cloud_app_exists(app_id: str) -> bool:
        """Check if a Nextmv Cloud application exists.

        Args:
            app_id: The application ID to check.
        """

        client = _get_client()
        return Application.exists(client=client, id=app_id)

    @mcp.tool()
    def cloud_update_app(
        app_id: str,
        name: str | None = None,
        description: str | None = None,
        default_instance_id: str | None = None,
    ) -> dict[str, Any]:
        """Update a Nextmv Cloud application.

        Args:
            app_id: The application ID to update.
            name: New name for the application.
            description: New description.
            default_instance_id: New default instance ID.
        """

        app = _get_app(app_id)
        updated = app.update(
            name=name,
            description=description,
            default_instance_id=default_instance_id,
        )
        return updated.to_dict()

    @mcp.tool()
    def cloud_push_app(app_id: str, app_dir: str) -> str:
        """Push local application code to a Nextmv Cloud application.

        Args:
            app_id: The application ID to push to.
            app_dir: Local directory path containing the application code.
        """

        app = _get_app(app_id)
        app.push(app_dir=app_dir)
        return f"Pushed {app_dir} to application {app_id}"


# ════════════════════════════════════════════════════════════════
# Cloud: Run management
# ════════════════════════════════════════════════════════════════


def _register_run_tools(mcp: FastMCP) -> None:
    """Register cloud run management tools."""

    @mcp.tool()
    def cloud_run(
        app_id: str,
        input: dict[str, Any],
        instance_id: str | None = None,
        run_options: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Run a Nextmv Cloud application and wait for the result.

        Submits the input to the app, polls until complete, and returns
        the full result including solution output and statistics.

        Args:
            app_id: The application ID.
            input: The input data (JSON object) for the optimization run.
            instance_id: Which instance to run against (default: app default).
            run_options: Solver options like {"solve.duration": "10s"}.
        """

        app = _get_app(app_id)
        result = app.new_run_with_result(
            input=input,
            instance_id=instance_id,
            run_options=run_options or {},
            polling_options=default_polling_options(),
        )
        return result.to_dict()

    @mcp.tool()
    def cloud_run_submit(
        app_id: str,
        input: dict[str, Any],
        instance_id: str | None = None,
        run_options: dict[str, str] | None = None,
    ) -> str:
        """Submit a run to a Nextmv Cloud application (non-blocking).

        Returns the run_id immediately. Use cloud_run_status or
        cloud_run_result to check on it later.

        Args:
            app_id: The application ID.
            input: The input data for the run.
            instance_id: Which instance to run against.
            run_options: Solver options.
        """

        app = _get_app(app_id)
        run_id = app.new_run(
            input=input,
            instance_id=instance_id,
            options=run_options or {},
        )
        return run_id

    @mcp.tool()
    def cloud_run_status(app_id: str, run_id: str) -> dict[str, Any]:
        """Check the status and metadata of a Nextmv Cloud run.

        Args:
            app_id: The application ID.
            run_id: The run ID returned from cloud_run_submit.
        """

        app = _get_app(app_id)
        metadata = app.run_metadata(run_id=run_id)
        return metadata.to_dict()

    @mcp.tool()
    def cloud_run_result(app_id: str, run_id: str) -> dict[str, Any]:
        """Get the full result of a completed Nextmv Cloud run.

        Args:
            app_id: The application ID.
            run_id: The run ID.
        """

        app = _get_app(app_id)
        result = app.run_result(run_id=run_id)
        return result.to_dict()

    @mcp.tool()
    def cloud_cancel_run(app_id: str, run_id: str) -> str:
        """Cancel a running or queued Nextmv Cloud run.

        Args:
            app_id: The application ID.
            run_id: The run ID to cancel.
        """

        app = _get_app(app_id)
        app.cancel_run(run_id=run_id)
        return f"Cancelled run {run_id}"

    @mcp.tool()
    def cloud_list_runs(
        app_id: str,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """List runs for a Nextmv Cloud application.

        Args:
            app_id: The application ID.
            status: Optional status filter (e.g., 'succeeded', 'failed',
                'running', 'queued', 'canceled').
        """

        from nextmv.run import StatusV2

        app = _get_app(app_id)
        status_filter = StatusV2(status) if status else None
        runs = app.list_runs(status=status_filter)
        return [r.to_dict() for r in runs]

    @mcp.tool()
    def cloud_run_input(app_id: str, run_id: str) -> dict[str, Any] | None:
        """Get the input data of a Nextmv Cloud run.

        Args:
            app_id: The application ID.
            run_id: The run ID.
        """

        app = _get_app(app_id)
        return app.run_input(run_id=run_id)

    @mcp.tool()
    def cloud_run_logs(app_id: str, run_id: str) -> dict[str, Any]:
        """Get the logs of a Nextmv Cloud run.

        Args:
            app_id: The application ID.
            run_id: The run ID.
        """

        app = _get_app(app_id)
        logs = app.run_logs(run_id=run_id)
        return logs.to_dict()


# ════════════════════════════════════════════════════════════════
# Cloud: Version management
# ════════════════════════════════════════════════════════════════


def _register_version_tools(mcp: FastMCP) -> None:
    """Register cloud version management tools."""

    @mcp.tool()
    def cloud_list_versions(app_id: str) -> list[dict[str, Any]]:
        """List all versions of a Nextmv Cloud application.

        Args:
            app_id: The application ID.
        """

        app = _get_app(app_id)
        versions = app.list_versions()
        return [v.to_dict() for v in versions]

    @mcp.tool()
    def cloud_get_version(app_id: str, version_id: str) -> dict[str, Any]:
        """Get details of a specific application version.

        Args:
            app_id: The application ID.
            version_id: The version ID.
        """

        app = _get_app(app_id)
        v = app.version(version_id=version_id)
        return v.to_dict()

    @mcp.tool()
    def cloud_create_version(
        app_id: str,
        version_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a new version for a Nextmv Cloud application.

        Args:
            app_id: The application ID.
            version_id: Optional version ID. Auto-generated if omitted.
            name: Optional human-readable name.
            description: Optional description.
        """

        app = _get_app(app_id)
        v = app.new_version(id=version_id, name=name, description=description)
        return v.to_dict()

    @mcp.tool()
    def cloud_update_version(
        app_id: str,
        version_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update a version of a Nextmv Cloud application.

        Args:
            app_id: The application ID.
            version_id: The version ID to update.
            name: New name.
            description: New description.
        """

        app = _get_app(app_id)
        v = app.update_version(version_id=version_id, name=name, description=description)
        return v.to_dict()

    @mcp.tool()
    def cloud_delete_version(app_id: str, version_id: str) -> str:
        """Delete a version of a Nextmv Cloud application.

        Args:
            app_id: The application ID.
            version_id: The version ID to delete.
        """

        app = _get_app(app_id)
        app.delete_version(version_id=version_id)
        return f"Deleted version {version_id}"


# ════════════════════════════════════════════════════════════════
# Cloud: Instance management
# ════════════════════════════════════════════════════════════════


def _register_instance_tools(mcp: FastMCP) -> None:
    """Register cloud instance management tools."""

    @mcp.tool()
    def cloud_list_instances(app_id: str) -> list[dict[str, Any]]:
        """List all instances of a Nextmv Cloud application.

        Instances represent deployed configurations (e.g., 'latest',
        'production', 'staging').

        Args:
            app_id: The application ID.
        """

        app = _get_app(app_id)
        instances = app.list_instances()
        return [i.to_dict() for i in instances]

    @mcp.tool()
    def cloud_get_instance(app_id: str, instance_id: str) -> dict[str, Any]:
        """Get details of a specific application instance.

        Args:
            app_id: The application ID.
            instance_id: The instance ID.
        """

        app = _get_app(app_id)
        inst = app.instance(instance_id=instance_id)
        return inst.to_dict()

    @mcp.tool()
    def cloud_create_instance(
        app_id: str,
        version_id: str,
        instance_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new instance for a Nextmv Cloud application.

        Args:
            app_id: The application ID.
            version_id: The version ID this instance points to.
            instance_id: Optional instance ID. Auto-generated if omitted.
            name: Optional human-readable name.
            description: Optional description.
            configuration: Optional instance configuration with keys like
                execution_class, options, secrets_collection_id,
                integration_id.
        """

        from nextmv.cloud import InstanceConfiguration

        app = _get_app(app_id)
        config = InstanceConfiguration(**configuration) if configuration else None
        inst = app.new_instance(
            version_id=version_id,
            id=instance_id,
            name=name,
            description=description,
            configuration=config,
        )
        return inst.to_dict()

    @mcp.tool()
    def cloud_update_instance(
        app_id: str,
        instance_id: str,
        name: str | None = None,
        version_id: str | None = None,
        description: str | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update an instance of a Nextmv Cloud application.

        Args:
            app_id: The application ID.
            instance_id: The instance ID to update.
            name: New name.
            version_id: New version ID to point to.
            description: New description.
            configuration: New instance configuration.
        """

        app = _get_app(app_id)
        inst = app.update_instance(
            id=instance_id,
            name=name,
            version_id=version_id,
            description=description,
            configuration=configuration,
        )
        return inst.to_dict()

    @mcp.tool()
    def cloud_delete_instance(app_id: str, instance_id: str) -> str:
        """Delete an instance of a Nextmv Cloud application.

        Args:
            app_id: The application ID.
            instance_id: The instance ID to delete.
        """

        app = _get_app(app_id)
        app.delete_instance(instance_id=instance_id)
        return f"Deleted instance {instance_id}"


# ════════════════════════════════════════════════════════════════
# Cloud: Batch experiments
# ════════════════════════════════════════════════════════════════


def _register_batch_tools(mcp: FastMCP) -> None:
    """Register cloud batch experiment tools."""

    @mcp.tool()
    def cloud_create_batch(
        app_id: str,
        input_set_id: str,
        name: str | None = None,
        description: str | None = None,
        option_sets: dict[str, dict[str, str]] | None = None,
    ) -> str:
        """Create a batch experiment for a Nextmv Cloud application.

        A batch experiment runs the app against an input set, optionally
        with multiple option sets to compare configurations.

        Args:
            app_id: The application ID.
            input_set_id: ID of the input set to use.
            name: Optional name for the experiment.
            description: Optional description.
            option_sets: Option sets to compare. Keys are set names, values
                are dicts of solver options.
        """

        app = _get_app(app_id)
        batch_id = app.new_batch_experiment(
            input_set_id=input_set_id,
            name=name,
            description=description,
            option_sets=option_sets,
        )
        return batch_id

    @mcp.tool()
    def cloud_get_batch(app_id: str, batch_id: str) -> dict[str, Any]:
        """Get batch experiment details and runs.

        Args:
            app_id: The application ID.
            batch_id: The batch experiment ID.
        """

        app = _get_app(app_id)
        batch = app.batch_experiment(batch_id=batch_id)
        return batch.to_dict()

    @mcp.tool()
    def cloud_list_batches(app_id: str) -> list[dict[str, Any]]:
        """List all batch experiments for a Nextmv Cloud application.

        Args:
            app_id: The application ID.
        """

        app = _get_app(app_id)
        batches = app.list_batch_experiments()
        return [b.to_dict() for b in batches]

    @mcp.tool()
    def cloud_batch_metadata(app_id: str, batch_id: str) -> dict[str, Any]:
        """Get metadata for a batch experiment.

        Args:
            app_id: The application ID.
            batch_id: The batch experiment ID.
        """

        app = _get_app(app_id)
        metadata = app.batch_experiment_metadata(batch_id=batch_id)
        return metadata.to_dict()

    @mcp.tool()
    def cloud_delete_batch(app_id: str, batch_id: str) -> str:
        """Delete a batch experiment.

        Args:
            app_id: The application ID.
            batch_id: The batch experiment ID to delete.
        """

        app = _get_app(app_id)
        app.delete_batch_experiment(batch_id=batch_id)
        return f"Deleted batch experiment {batch_id}"


# ════════════════════════════════════════════════════════════════
# Cloud: Input sets
# ════════════════════════════════════════════════════════════════


def _register_input_set_tools(mcp: FastMCP) -> None:
    """Register cloud input set tools."""

    @mcp.tool()
    def cloud_list_input_sets(app_id: str) -> list[dict[str, Any]]:
        """List input sets for a Nextmv Cloud application.

        Input sets are collections of inputs used for batch experiments
        and acceptance tests.

        Args:
            app_id: The application ID.
        """

        app = _get_app(app_id)
        input_sets = app.list_input_sets()
        return [s.to_dict() for s in input_sets]

    @mcp.tool()
    def cloud_get_input_set(app_id: str, input_set_id: str) -> dict[str, Any]:
        """Get details of a specific input set.

        Args:
            app_id: The application ID.
            input_set_id: The input set ID.
        """

        app = _get_app(app_id)
        input_set = app.input_set(input_set_id=input_set_id)
        return input_set.to_dict()

    @mcp.tool()
    def cloud_create_input_set(
        app_id: str,
        input_set_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        instance_id: str | None = None,
        maximum_runs: int | None = None,
    ) -> dict[str, Any]:
        """Create a new input set for a Nextmv Cloud application.

        An input set collects inputs (from historical runs or managed
        inputs) for use in batch experiments and acceptance tests.

        Args:
            app_id: The application ID.
            input_set_id: Optional ID for the input set.
            name: Optional human-readable name.
            description: Optional description.
            instance_id: Optional instance ID to collect runs from.
            maximum_runs: Maximum number of runs to include (default: 20).
        """

        app = _get_app(app_id)
        input_set = app.new_input_set(
            id=input_set_id,
            name=name,
            description=description,
            instance_id=instance_id,
            maximum_runs=maximum_runs,
        )
        return input_set.to_dict()

    @mcp.tool()
    def cloud_update_input_set(
        app_id: str,
        input_set_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update an input set.

        Args:
            app_id: The application ID.
            input_set_id: The input set ID to update.
            name: New name.
            description: New description.
        """

        app = _get_app(app_id)
        input_set = app.update_input_set(id=input_set_id, name=name, description=description)
        return input_set.to_dict()

    @mcp.tool()
    def cloud_delete_input_set(app_id: str, input_set_id: str) -> str:
        """Delete an input set.

        Args:
            app_id: The application ID.
            input_set_id: The input set ID to delete.
        """

        app = _get_app(app_id)
        app.delete_input_set(input_set_id=input_set_id)
        return f"Deleted input set {input_set_id}"


# ════════════════════════════════════════════════════════════════
# Cloud: Acceptance tests
# ════════════════════════════════════════════════════════════════


def _register_acceptance_tools(mcp: FastMCP) -> None:
    """Register cloud acceptance test tools."""

    @mcp.tool()
    def cloud_list_acceptance_tests(app_id: str) -> list[dict[str, Any]]:
        """List acceptance tests for a Nextmv Cloud application.

        Args:
            app_id: The application ID.
        """

        app = _get_app(app_id)
        tests = app.list_acceptance_tests()
        return [t.to_dict() for t in tests]

    @mcp.tool()
    def cloud_get_acceptance_test(
        app_id: str,
        acceptance_test_id: str,
    ) -> dict[str, Any]:
        """Get details of an acceptance test.

        Args:
            app_id: The application ID.
            acceptance_test_id: The acceptance test ID.
        """

        app = _get_app(app_id)
        test = app.acceptance_test(acceptance_test_id=acceptance_test_id)
        return test.to_dict()

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

        An acceptance test runs both instances against the same inputs
        and compares results using specified metrics.

        Args:
            app_id: The application ID.
            candidate_instance_id: The candidate instance to test.
            baseline_instance_id: The baseline instance to compare against.
            metrics: List of metric definitions. Each metric is a dict with
                keys: field, metric_type, params, statistic.
            acceptance_test_id: Optional test ID.
            name: Optional name.
            input_set_id: Optional input set to use.
            description: Optional description.
        """

        app = _get_app(app_id)
        test = app.new_acceptance_test(
            candidate_instance_id=candidate_instance_id,
            baseline_instance_id=baseline_instance_id,
            metrics=metrics,
            id=acceptance_test_id,
            name=name,
            input_set_id=input_set_id,
            description=description,
        )
        return test.to_dict()

    @mcp.tool()
    def cloud_delete_acceptance_test(
        app_id: str,
        acceptance_test_id: str,
    ) -> str:
        """Delete an acceptance test.

        Args:
            app_id: The application ID.
            acceptance_test_id: The acceptance test ID to delete.
        """

        app = _get_app(app_id)
        app.delete_acceptance_test(acceptance_test_id=acceptance_test_id)
        return f"Deleted acceptance test {acceptance_test_id}"


# ════════════════════════════════════════════════════════════════
# Cloud: Scenario tests
# ════════════════════════════════════════════════════════════════


def _register_scenario_tools(mcp: FastMCP) -> None:
    """Register cloud scenario test tools."""

    @mcp.tool()
    def cloud_list_scenario_tests(app_id: str) -> list[dict[str, Any]]:
        """List scenario tests for a Nextmv Cloud application.

        Args:
            app_id: The application ID.
        """

        app = _get_app(app_id)
        tests = app.list_scenario_tests()
        return [t.to_dict() for t in tests]

    @mcp.tool()
    def cloud_get_scenario_test(
        app_id: str,
        scenario_test_id: str,
    ) -> dict[str, Any]:
        """Get details of a scenario test.

        Args:
            app_id: The application ID.
            scenario_test_id: The scenario test ID.
        """

        app = _get_app(app_id)
        test = app.scenario_test(scenario_test_id=scenario_test_id)
        return test.to_dict()

    @mcp.tool()
    def cloud_create_scenario_test(
        app_id: str,
        scenarios: list[dict[str, Any]],
        scenario_test_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        repetitions: int = 0,
    ) -> str:
        """Create a scenario test for a Nextmv Cloud application.

        A scenario test runs the app with multiple scenario configurations
        to compare different setups.

        Args:
            app_id: The application ID.
            scenarios: List of scenario definitions. Each is a dict with
                keys: instance_id, scenario_input, scenario_id, configuration.
            scenario_test_id: Optional test ID.
            name: Optional name.
            description: Optional description.
            repetitions: Number of repetitions per scenario (default: 0).
        """

        app = _get_app(app_id)
        test_id = app.new_scenario_test(
            scenarios=scenarios,
            id=scenario_test_id,
            name=name,
            description=description,
            repetitions=repetitions,
        )
        return test_id

    @mcp.tool()
    def cloud_delete_scenario_test(
        app_id: str,
        scenario_test_id: str,
    ) -> str:
        """Delete a scenario test.

        Args:
            app_id: The application ID.
            scenario_test_id: The scenario test ID to delete.
        """

        app = _get_app(app_id)
        app.delete_scenario_test(scenario_test_id=scenario_test_id)
        return f"Deleted scenario test {scenario_test_id}"


# ════════════════════════════════════════════════════════════════
# Cloud: Ensemble definitions
# ════════════════════════════════════════════════════════════════


def _register_ensemble_tools(mcp: FastMCP) -> None:
    """Register cloud ensemble definition tools."""

    @mcp.tool()
    def cloud_list_ensembles(app_id: str) -> list[dict[str, Any]]:
        """List ensemble definitions for a Nextmv Cloud application.

        Args:
            app_id: The application ID.
        """

        app = _get_app(app_id)
        ensembles = app.list_ensemble_definitions()
        return [e.to_dict() for e in ensembles]

    @mcp.tool()
    def cloud_get_ensemble(
        app_id: str,
        ensemble_id: str,
    ) -> dict[str, Any]:
        """Get details of an ensemble definition.

        Args:
            app_id: The application ID.
            ensemble_id: The ensemble definition ID.
        """

        app = _get_app(app_id)
        ensemble = app.ensemble_definition(ensemble_definition_id=ensemble_id)
        return ensemble.to_dict()

    @mcp.tool()
    def cloud_create_ensemble(
        app_id: str,
        run_groups: list[dict[str, Any]],
        rules: list[dict[str, Any]],
        ensemble_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create an ensemble definition for a Nextmv Cloud application.

        An ensemble runs multiple instances/configurations and picks the
        best result based on evaluation rules.

        Args:
            app_id: The application ID.
            run_groups: List of run group definitions. Each is a dict with
                keys: id, instance_id, options, repetitions.
            rules: List of evaluation rules. Each is a dict with keys:
                id, statistics_path, objective, tolerance, index.
            ensemble_id: Optional ensemble definition ID.
            name: Optional name.
            description: Optional description.
        """

        app = _get_app(app_id)
        ensemble = app.new_ensemble_definition(
            run_groups=run_groups,
            rules=rules,
            id=ensemble_id,
            name=name,
            description=description,
        )
        return ensemble.to_dict()

    @mcp.tool()
    def cloud_delete_ensemble(app_id: str, ensemble_id: str) -> str:
        """Delete an ensemble definition.

        Args:
            app_id: The application ID.
            ensemble_id: The ensemble definition ID to delete.
        """

        app = _get_app(app_id)
        app.delete_ensemble_definition(ensemble_definition_id=ensemble_id)
        return f"Deleted ensemble definition {ensemble_id}"


# ════════════════════════════════════════════════════════════════
# Cloud: Shadow tests
# ════════════════════════════════════════════════════════════════


def _register_shadow_tools(mcp: FastMCP) -> None:
    """Register cloud shadow test tools."""

    @mcp.tool()
    def cloud_list_shadow_tests(app_id: str) -> list[dict[str, Any]]:
        """List shadow tests for a Nextmv Cloud application.

        A shadow test runs a candidate instance alongside a baseline
        to compare live traffic results.

        Args:
            app_id: The application ID.
        """

        app = _get_app(app_id)
        tests = app.list_shadow_tests()
        return [t.to_dict() for t in tests]

    @mcp.tool()
    def cloud_get_shadow_test(
        app_id: str,
        shadow_test_id: str,
    ) -> dict[str, Any]:
        """Get details of a shadow test.

        Args:
            app_id: The application ID.
            shadow_test_id: The shadow test ID.
        """

        app = _get_app(app_id)
        test = app.shadow_test(shadow_test_id=shadow_test_id)
        return test.to_dict()

    @mcp.tool()
    def cloud_create_shadow_test(
        app_id: str,
        comparisons: dict[str, list[str]],
        termination_events: dict[str, Any],
        shadow_test_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        start_events: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a shadow test for a Nextmv Cloud application.

        Args:
            app_id: The application ID.
            comparisons: Mapping of baseline instance IDs to lists of
                candidate instance IDs.
            termination_events: When to stop the test. Dict with keys
                like maximum_runs, time.
            shadow_test_id: Optional test ID.
            name: Optional name.
            description: Optional description.
            start_events: Optional start trigger. Dict with key: time.
        """

        app = _get_app(app_id)
        test = app.new_shadow_test(
            comparisons=comparisons,
            termination_events=termination_events,
            shadow_test_id=shadow_test_id,
            name=name,
            description=description,
            start_events=start_events,
        )
        return test.to_dict()

    @mcp.tool()
    def cloud_start_shadow_test(app_id: str, shadow_test_id: str) -> str:
        """Start a shadow test.

        Args:
            app_id: The application ID.
            shadow_test_id: The shadow test ID to start.
        """

        app = _get_app(app_id)
        app.start_shadow_test(shadow_test_id=shadow_test_id)
        return f"Started shadow test {shadow_test_id}"

    @mcp.tool()
    def cloud_stop_shadow_test(
        app_id: str,
        shadow_test_id: str,
        intent: str = "cancel",
    ) -> str:
        """Stop a running shadow test.

        Args:
            app_id: The application ID.
            shadow_test_id: The shadow test ID to stop.
            intent: Stop intent - 'cancel' or 'promote' (default: 'cancel').
        """

        from nextmv.cloud import StopIntent

        app = _get_app(app_id)
        app.stop_shadow_test(
            shadow_test_id=shadow_test_id,
            intent=StopIntent(intent),
        )
        return f"Stopped shadow test {shadow_test_id} with intent {intent}"

    @mcp.tool()
    def cloud_delete_shadow_test(app_id: str, shadow_test_id: str) -> str:
        """Delete a shadow test.

        Args:
            app_id: The application ID.
            shadow_test_id: The shadow test ID to delete.
        """

        app = _get_app(app_id)
        app.delete_shadow_test(shadow_test_id=shadow_test_id)
        return f"Deleted shadow test {shadow_test_id}"


# ════════════════════════════════════════════════════════════════
# Cloud: Switchback tests
# ════════════════════════════════════════════════════════════════


def _register_switchback_tools(mcp: FastMCP) -> None:
    """Register cloud switchback test tools."""

    @mcp.tool()
    def cloud_list_switchback_tests(app_id: str) -> list[dict[str, Any]]:
        """List switchback tests for a Nextmv Cloud application.

        A switchback test alternates between baseline and candidate
        instances over time periods to compare performance.

        Args:
            app_id: The application ID.
        """

        app = _get_app(app_id)
        tests = app.list_switchback_tests()
        return [t.to_dict() for t in tests]

    @mcp.tool()
    def cloud_get_switchback_test(
        app_id: str,
        switchback_test_id: str,
    ) -> dict[str, Any]:
        """Get details of a switchback test.

        Args:
            app_id: The application ID.
            switchback_test_id: The switchback test ID.
        """

        app = _get_app(app_id)
        test = app.switchback_test(switchback_test_id=switchback_test_id)
        return test.to_dict()

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

        Args:
            app_id: The application ID.
            baseline_instance_id: The baseline instance ID.
            candidate_instance_id: The candidate instance ID.
            unit_duration_minutes: Duration of each switchback unit in minutes.
            units: Total number of switchback units.
            switchback_test_id: Optional test ID.
            name: Optional name.
            description: Optional description.
        """

        from nextmv.cloud import TestComparisonSingle

        app = _get_app(app_id)
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
        )
        return test.to_dict()

    @mcp.tool()
    def cloud_start_switchback_test(
        app_id: str,
        switchback_test_id: str,
    ) -> str:
        """Start a switchback test.

        Args:
            app_id: The application ID.
            switchback_test_id: The switchback test ID to start.
        """

        app = _get_app(app_id)
        app.start_switchback_test(switchback_test_id=switchback_test_id)
        return f"Started switchback test {switchback_test_id}"

    @mcp.tool()
    def cloud_stop_switchback_test(
        app_id: str,
        switchback_test_id: str,
        intent: str = "cancel",
    ) -> str:
        """Stop a running switchback test.

        Args:
            app_id: The application ID.
            switchback_test_id: The switchback test ID to stop.
            intent: Stop intent - 'cancel' or 'promote' (default: 'cancel').
        """

        from nextmv.cloud import StopIntent

        app = _get_app(app_id)
        app.stop_switchback_test(
            switchback_test_id=switchback_test_id,
            intent=StopIntent(intent),
        )
        return f"Stopped switchback test {switchback_test_id} with intent {intent}"

    @mcp.tool()
    def cloud_delete_switchback_test(
        app_id: str,
        switchback_test_id: str,
    ) -> str:
        """Delete a switchback test.

        Args:
            app_id: The application ID.
            switchback_test_id: The switchback test ID to delete.
        """

        app = _get_app(app_id)
        app.delete_switchback_test(switchback_test_id=switchback_test_id)
        return f"Deleted switchback test {switchback_test_id}"


# ════════════════════════════════════════════════════════════════
# Cloud: Secrets
# ════════════════════════════════════════════════════════════════


def _register_secrets_tools(mcp: FastMCP) -> None:
    """Register cloud secrets management tools."""

    @mcp.tool()
    def cloud_list_secrets_collections(app_id: str) -> list[dict[str, Any]]:
        """List secrets collections for a Nextmv Cloud application.

        Args:
            app_id: The application ID.
        """

        app = _get_app(app_id)
        collections = app.list_secrets_collections()
        return [c.to_dict() for c in collections]

    @mcp.tool()
    def cloud_get_secrets_collection(
        app_id: str,
        secrets_collection_id: str,
    ) -> dict[str, Any]:
        """Get details of a secrets collection.

        Args:
            app_id: The application ID.
            secrets_collection_id: The secrets collection ID.
        """

        app = _get_app(app_id)
        collection = app.secrets_collection(secrets_collection_id=secrets_collection_id)
        return collection.to_dict()

    @mcp.tool()
    def cloud_create_secrets_collection(
        app_id: str,
        secrets: list[dict[str, str]],
        secrets_collection_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a secrets collection for a Nextmv Cloud application.

        Args:
            app_id: The application ID.
            secrets: List of secret definitions. Each is a dict with keys:
                type ('env' or 'file'), location (name/path), value.
            secrets_collection_id: Optional collection ID.
            name: Optional name.
            description: Optional description.
        """

        app = _get_app(app_id)
        collection = app.new_secrets_collection(
            secrets=secrets,
            id=secrets_collection_id,
            name=name,
            description=description,
        )
        return collection.to_dict()

    @mcp.tool()
    def cloud_delete_secrets_collection(
        app_id: str,
        secrets_collection_id: str,
    ) -> str:
        """Delete a secrets collection.

        Args:
            app_id: The application ID.
            secrets_collection_id: The secrets collection ID to delete.
        """

        app = _get_app(app_id)
        app.delete_secrets_collection(secrets_collection_id=secrets_collection_id)
        return f"Deleted secrets collection {secrets_collection_id}"


# ════════════════════════════════════════════════════════════════
# Cloud: Account & queue
# ════════════════════════════════════════════════════════════════


def _register_account_tools(mcp: FastMCP) -> None:
    """Register cloud account tools."""

    @mcp.tool()
    def cloud_get_account(account_id: str) -> dict[str, Any]:
        """Get details of a Nextmv Cloud account.

        Args:
            account_id: The account ID.
        """

        from nextmv.cloud.account import Account

        client = _get_client()
        account = Account.get(client=client, account_id=account_id)
        return account.to_dict()

    @mcp.tool()
    def cloud_get_queue(account_id: str) -> dict[str, Any]:
        """Get the run queue for a Nextmv Cloud account.

        Shows queued and running runs across all applications.

        Args:
            account_id: The account ID.
        """

        from nextmv.cloud.account import Account

        client = _get_client()
        account = Account.get(client=client, account_id=account_id)
        queue = account.queue()
        return queue.to_dict()


# ════════════════════════════════════════════════════════════════
# Cloud: Managed inputs
# ════════════════════════════════════════════════════════════════


def _register_managed_input_tools(mcp: FastMCP) -> None:
    """Register cloud managed input tools."""

    @mcp.tool()
    def cloud_list_managed_inputs(app_id: str) -> list[dict[str, Any]]:
        """List managed inputs for a Nextmv Cloud application.

        Managed inputs are reusable input data stored in the platform.

        Args:
            app_id: The application ID.
        """

        app = _get_app(app_id)
        inputs = app.list_managed_inputs()
        return [i.to_dict() for i in inputs]

    @mcp.tool()
    def cloud_get_managed_input(
        app_id: str,
        managed_input_id: str,
    ) -> dict[str, Any]:
        """Get details of a managed input.

        Args:
            app_id: The application ID.
            managed_input_id: The managed input ID.
        """

        app = _get_app(app_id)
        mi = app.managed_input(managed_input_id=managed_input_id)
        return mi.to_dict()

    @mcp.tool()
    def cloud_create_managed_input(
        app_id: str,
        managed_input_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        run_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a managed input for a Nextmv Cloud application.

        Args:
            app_id: The application ID.
            managed_input_id: Optional ID.
            name: Optional name.
            description: Optional description.
            run_id: Optional run ID to copy input from.
        """

        app = _get_app(app_id)
        mi = app.new_managed_input(
            id=managed_input_id,
            name=name,
            description=description,
            run_id=run_id,
        )
        return mi.to_dict()

    @mcp.tool()
    def cloud_delete_managed_input(
        app_id: str,
        managed_input_id: str,
    ) -> str:
        """Delete a managed input.

        Args:
            app_id: The application ID.
            managed_input_id: The managed input ID to delete.
        """

        app = _get_app(app_id)
        app.delete_managed_input(managed_input_id=managed_input_id)
        return f"Deleted managed input {managed_input_id}"


# ════════════════════════════════════════════════════════════════
# Community
# ════════════════════════════════════════════════════════════════


def _register_community_tools(mcp: FastMCP) -> None:
    """Register community app tools."""

    @mcp.tool()
    def community_list() -> list[dict[str, Any]]:
        """List available Nextmv community apps.

        Community apps are pre-built decision models for common
        problems like vehicle routing, knapsack, shift scheduling, etc.
        """

        client = _get_client()
        apps = list_community_apps(client)
        return [a.to_dict() for a in apps]

    @mcp.tool()
    def community_clone(app_name: str, target_dir: str = ".") -> str:
        """Clone a Nextmv community app to a local directory.

        Args:
            app_name: Name of the community app (e.g., 'python-ortools-routing').
            target_dir: Directory to clone into (default: current directory).
        """

        client = _get_client()
        clone_community_app(client=client, app=app_name, directory=target_dir)
        return f"Cloned {app_name} to {target_dir}"


# ════════════════════════════════════════════════════════════════
# Local
# ════════════════════════════════════════════════════════════════


def _register_local_tools(mcp: FastMCP) -> None:
    """Register local application tools."""

    @mcp.tool()
    def local_run(
        app_dir: str,
        input: dict[str, Any],
        app_id: str | None = None,
        run_options: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Run a local Nextmv application and wait for the result.

        Args:
            app_dir: Path to the local application directory.
            input: The input data (JSON object) for the run.
            app_id: Optional application ID for registry tracking.
            run_options: Solver options like {"solve.duration": "10s"}.
        """

        app = _get_local_app(app_dir=app_dir, app_id=app_id)
        result = app.new_run_with_result(
            input=input,
            run_options=run_options or {},
            polling_options=default_polling_options(),
        )
        return result.to_dict()

    @mcp.tool()
    def local_run_submit(
        app_dir: str,
        input: dict[str, Any],
        app_id: str | None = None,
        run_options: dict[str, str] | None = None,
    ) -> str:
        """Submit a local run (non-blocking). Returns the run ID.

        Args:
            app_dir: Path to the local application directory.
            input: The input data for the run.
            app_id: Optional application ID.
            run_options: Solver options.
        """

        app = _get_local_app(app_dir=app_dir, app_id=app_id)
        run_id = app.new_run(
            input=input,
            options=run_options or {},
        )
        return run_id

    @mcp.tool()
    def local_run_result(
        app_dir: str,
        run_id: str,
        app_id: str | None = None,
    ) -> dict[str, Any]:
        """Get the result of a local run.

        Args:
            app_dir: Path to the local application directory.
            run_id: The run ID.
            app_id: Optional application ID.
        """

        app = _get_local_app(app_dir=app_dir, app_id=app_id)
        result = app.run_result(run_id=run_id)
        return result.to_dict()

    @mcp.tool()
    def local_list_runs(
        app_dir: str,
        app_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """List runs for a local Nextmv application.

        Args:
            app_dir: Path to the local application directory.
            app_id: Optional application ID.
        """

        app = _get_local_app(app_dir=app_dir, app_id=app_id)
        runs = app.list_runs()
        return [r.to_dict() for r in runs]

    @mcp.tool()
    def local_run_logs(
        app_dir: str,
        run_id: str,
        app_id: str | None = None,
    ) -> str:
        """Get the logs of a local run.

        Args:
            app_dir: Path to the local application directory.
            run_id: The run ID.
            app_id: Optional application ID.
        """

        app = _get_local_app(app_dir=app_dir, app_id=app_id)
        return app.run_logs(run_id=run_id)

    @mcp.tool()
    def local_sync(
        app_dir: str,
        cloud_app_id: str,
        app_id: str | None = None,
        instance_id: str | None = None,
        run_ids: list[str] | None = None,
    ) -> str:
        """Sync local runs to a Nextmv Cloud application.

        Args:
            app_dir: Path to the local application directory.
            cloud_app_id: The cloud application ID to sync to.
            app_id: Optional local application ID.
            instance_id: Optional cloud instance ID for the synced runs.
            run_ids: Optional list of specific run IDs to sync.
                Syncs all runs if omitted.
        """

        local_app = _get_local_app(app_dir=app_dir, app_id=app_id)
        cloud_target = _get_app(cloud_app_id)
        local_app.sync(
            target=cloud_target,
            run_ids=run_ids,
            instance_id=instance_id,
        )
        return f"Synced local runs to cloud application {cloud_app_id}"


# ════════════════════════════════════════════════════════════════
# Server factory
# ════════════════════════════════════════════════════════════════


def create_server() -> FastMCP:
    """Create and return the Nextmv MCP server."""

    mcp = FastMCP(
        "nextmv",
        json_response=True,
        instructions=(
            "Nextmv is a platform for deploying and managing decision "
            "models (optimization, routing, scheduling, etc.). Use these "
            "tools to interact with Nextmv Cloud apps: list apps, submit "
            "runs, check results, manage versions/instances, run experiments, "
            "and work with local applications."
        ),
    )

    # Cloud tools
    _register_app_tools(mcp)
    _register_run_tools(mcp)
    _register_version_tools(mcp)
    _register_instance_tools(mcp)
    _register_batch_tools(mcp)
    _register_input_set_tools(mcp)
    _register_acceptance_tools(mcp)
    _register_scenario_tools(mcp)
    _register_ensemble_tools(mcp)
    _register_shadow_tools(mcp)
    _register_switchback_tools(mcp)
    _register_secrets_tools(mcp)
    _register_account_tools(mcp)
    _register_managed_input_tools(mcp)

    # Community tools
    _register_community_tools(mcp)

    # Local tools
    _register_local_tools(mcp)

    return mcp
