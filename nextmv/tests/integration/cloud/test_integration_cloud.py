import os
import tempfile
from datetime import datetime, timedelta, timezone

from nextmv.safe import safe_id
from nextpipe import FlowSpec, needs, step

import nextmv
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))


class CloudIntegrationWorkflow(FlowSpec):
    @step
    def init_app(app_id: str) -> cloud.Application:
        """
        Initializes the app and performs app operations.

        We are making sure that app-level operations work as expected, like
        updating, pushing, listing, etc.

        Parameters
        ----------
        app_id : str
            The app ID to use for creating the app.

        Returns
        -------
        cloud.Application
            The created application.
        """

        # We can create the app.
        app = cloud.Application.new(client=client, id=app_id)

        # We can get the app, and it exists.
        app = cloud.Application.get(client=client, id=app.id)
        assert app is not None
        exists = cloud.Application.exists(client=client, id=app.id)
        assert exists

        # We can update the app.
        name = "Fluffy cotton tail"
        description = "A burrow of bunnies"
        app = app.update(name=name, description=description)
        assert app.name == name
        assert app.description == description

        # We can list apps.
        apps = cloud.list_applications(client)
        assert len(apps) > 0
        assert app.id in {a.id for a in apps}

        return app

    @needs(predecessors=[init_app])
    @step
    def community_push(app: cloud.Application) -> None:
        """
        Performs community app operations and pushes the app to Cloud.

        Parameters
        ----------
        app : cloud.Application
            The application to perform operations on.
        """

        # We can list community apps.
        comm_apps = cloud.list_community_apps(client=client)
        assert len(comm_apps) > 0

        # Use a temp dir to clone and push a community app.
        with tempfile.TemporaryDirectory() as temp_dir:
            # We can clone a community app.
            name = "python-hello-world"
            clone_dir = os.path.join(temp_dir, name)
            cloud.clone_community_app(
                client=client,
                app=name,
                directory=clone_dir,
                verbose=True,
            )
            assert os.path.exists(clone_dir)
            assert os.path.exists(os.path.join(clone_dir, "README.md"))

            # We can push the app.
            app.push(app_dir=clone_dir, verbose=True)

    @needs(predecessors=[init_app, community_push])
    @step
    def versions(app: cloud.Application, __unused) -> cloud.Version:
        """
        Performs version operations on the app, like creating and updating
        versions.

        Parameters
        ----------
        app : cloud.Application
            The application to perform version operations on.

        __unused : Any
            Placeholder for the unused predecessor.

        Returns
        -------
        cloud.Version
            The version after performing version operations.
        """

        # We can create a couple of new versions.
        v1 = app.new_version()
        v2 = app.new_version()

        # We can list versions.
        versions = app.list_versions()
        assert len(versions) >= 2
        version_ids = {v.id for v in versions}
        assert v1.id in version_ids
        assert v2.id in version_ids

        # We can get a version and it exists.
        v1 = app.version(version_id=v1.id)
        assert v1 is not None
        exists = app.version_exists(version_id=v1.id)
        assert exists

        # We can update a version.
        name = "Carrots Galore"
        description = "A never ending supply of carrots"
        v1 = app.update_version(version_id=v1.id, name=name, description=description)
        assert v1.name == name
        assert v1.description == description

        # We can delete a version.
        app.delete_version(version_id=v2.id)
        exists = app.version_exists(version_id=v2.id)
        assert not exists

        return v1

    @needs(predecessors=[init_app, versions])
    @step
    def instances(app: cloud.Application, version: cloud.Version) -> tuple[cloud.Instance, cloud.Instance]:
        """
        Performs instance operations on the app version.

        Parameters
        ----------
        app : cloud.Application
            The application to perform instance operations on.

        version : cloud.Version
            The version of the application to perform instance operations on.
        """

        # We can create some instances
        inst1 = app.new_instance(version_id=version.id)
        inst2 = app.new_instance(version_id=version.id)
        inst3 = app.new_instance(version_id=version.id)

        # We can list instances.
        instances = app.list_instances()
        assert len(instances) >= 3
        instance_ids = {i.id for i in instances}
        assert inst1.id in instance_ids
        assert inst2.id in instance_ids
        assert inst3.id in instance_ids

        # We can get the instance and it exists.
        inst1 = app.instance(instance_id=inst1.id)
        assert inst1 is not None
        exists = app.instance_exists(instance_id=inst1.id)
        assert exists

        # We can update the instance.
        name = "Jumping McJumpface"
        description = "Loves to hop around"
        inst1 = app.update_instance(id=inst1.id, name=name, description=description)
        assert inst1.name == name
        assert inst1.description == description

        # We can delete an instance.
        app.delete_instance(instance_id=inst3.id)
        exists = app.instance_exists(instance_id=inst3.id)
        assert not exists

        # We can set the default instance of an app.
        app.update(default_instance_id=inst1.id)

        return inst1, inst2

    @needs(predecessors=[init_app, instances])
    @step
    def runs(app: cloud.Application, instances: tuple[cloud.Instance, cloud.Instance]) -> list[nextmv.RunResult]:
        """
        Performs different variations of runs.

        Parameters
        ----------
        app : cloud.Application
            The application to perform run operations on.

        instances : tuple[cloud.Instance, cloud.Instance]
            The instances of the application to perform run operations on.

        Returns
        -------
        list[nextmv.RunResult]
            The list of runs performed.
        """

        inst1, inst2 = instances
        input_data = {"name": "world", "radius": 6378, "distance": 147.6}

        # Start runs in different ways.
        run1 = app.new_run_with_result(input=input_data)
        run2 = app.new_run_with_result(input=input_data, instance_id=inst1.id)
        run3 = app.new_run_with_result(input=input_data, instance_id=inst2.id)
        run4 = app.new_run_with_result(input=input_data, instance_id="latest")
        run5 = app.new_run_with_result(input=input_data, run_options={"details": "false"})
        runs: list[nextmv.RunResult] = [run1, run2, run3, run4, run5]

        # Perform different checks on the runs.
        for run in runs:
            assert run.metadata.status_v2 == nextmv.StatusV2.succeeded

            run_input = app.run_input(run_id=run.id)
            assert run_input == input_data

            logs = app.run_logs(run_id=run.id)
            assert logs.log is not None and logs.log != ""

            info = app.run_metadata(run_id=run.id)
            assert info.metadata.status_v2 == nextmv.StatusV2.succeeded

            result = app.run_result(run_id=run.id)
            assert result is not None
            assert result.output is not None and result.output != {}

        # We can list runs.
        run_list = app.list_runs()
        assert len(run_list) >= 5
        run_ids = {r.id for r in run_list}
        for run in runs:
            assert run.id in run_ids

        # Start and cancel a run.
        run_id = app.new_run(input=input_data)
        app.cancel_run(run_id=run_id)

        return runs

    @needs(predecessors=[init_app, instances, runs])
    @step
    def input_sets(
        app: cloud.Application,
        instances: tuple[cloud.Instance, cloud.Instance],
        runs: list[nextmv.RunResult],
    ) -> cloud.InputSet:
        """
        Performs input set operations.

        Parameters
        ----------
        app : cloud.Application
            The application to perform input set operations on.
        instances : tuple[cloud.Instance, cloud.Instance]
            The instances to use for creating the input set.
        runs : list[nextmv.RunResult]
            The runs to use for creating the input set.

        Returns
        -------
        cloud.InputSet
            The created input set.
        """

        inst1, _ = instances
        now = datetime.now(timezone.utc)

        # We can create an input set from different methodologies.
        set1 = app.new_input_set(run_ids=[run.id for run in runs])
        set2 = app.new_input_set(
            instance_id=inst1.id,
            maximum_runs=20,
            end_time=now,
            start_time=now - timedelta(days=1),
        )

        # We can get an input set.
        set1 = app.input_set(input_set_id=set1.id)
        set2 = app.input_set(input_set_id=set2.id)
        assert set1 is not None
        assert set2 is not None

        # We can list input sets.
        input_sets = app.list_input_sets()
        assert len(input_sets) >= 2
        input_set_ids = {s.id for s in input_sets}
        assert set1.id in input_set_ids
        assert set2.id in input_set_ids

        # We can update an input set.
        name = "Bunny Input Set"
        description = "Input set for all bunny runs"
        set1 = app.update_input_set(id=set1.id, name=name, description=description)
        assert set1.name == name
        assert set1.description == description

        # We can delete an input set.
        app.delete_input_set(input_set_id=set2.id)

        return set1

    @needs(predecessors=[init_app, instances, input_sets])
    @step
    def scenario_tests(
        app: cloud.Application,
        instances: tuple[cloud.Instance, cloud.Instance],
        input_set: cloud.InputSet,
    ) -> None:
        """
        Performs scenario test operations.

        Parameters
        ----------
        app : cloud.Application
            The application to perform scenario test operations on.
        input_set : cloud.InputSet
            The input set to use for the scenario test.
        """

        inst1, _ = instances

        # We can create a batch experiment from the input set.
        test1_id = app.new_scenario_test(
            scenarios=[
                cloud.Scenario(
                    scenario_input=cloud.ScenarioInput(
                        scenario_input_type=cloud.ScenarioInputType.INPUT_SET,
                        scenario_input_data=input_set.id,
                    ),
                    instance_id=inst1.id,
                )
            ],
            repetitions=0,
        )

        # We can get a scenario test.
        scenario_list = app.list_scenario_tests()
        assert len(scenario_list) >= 1
        scenario_ids = {s.id for s in scenario_list}
        assert test1_id in scenario_ids

        # We can get a scenario test.
        test1 = app.scenario_test(scenario_test_id=test1_id)
        assert test1 is not None

        # We can get the metadata of a scenario test.
        test1_metadata = app.scenario_test_metadata(scenario_test_id=test1.id)
        assert test1_metadata is not None
        assert test1_metadata.number_of_runs > 0

        # We can update a scenario test.
        name = "Cotton-tailed Jumper"
        description = "A bunny that loves to jump"
        test1 = app.update_scenario_test(scenario_test_id=test1.id, name=name, description=description)
        assert test1.name == name
        assert test1.description == description

        # We can delete a scenario test.
        app.delete_scenario_test(scenario_test_id=test1.id)

    @needs(predecessors=[init_app, instances])
    @step
    def shadow_tests(app: cloud.Application, instances: tuple[cloud.Instance, cloud.Instance]) -> None:
        """
        Performs shadow test operations.

        Parameters
        ----------
        app : cloud.Application
            The application to perform shadow test operations on.
        instances : tuple[cloud.Instance, cloud.Instance]
            The instances to use for the shadow test.
        """

        inst1, inst2 = instances

        # We can start a shadow test in draft mode.
        shadow_test = app.new_shadow_test(
            comparisons={
                inst1.id: [inst2.id],
            },
            termination_events=cloud.TerminationEvents(
                maximum_runs=4,
            ),
        )
        metadata = app.shadow_test_metadata(shadow_test_id=shadow_test.shadow_test_id)
        assert metadata.status == cloud.ExperimentStatus.DRAFT

        # We can get a shadow test.
        shadow_test = app.shadow_test(shadow_test_id=shadow_test.shadow_test_id)
        assert shadow_test is not None

        # We can list shadow tests.
        shadow_tests = app.list_shadow_tests()
        assert len(shadow_tests) >= 1
        shadow_test_ids = {s.shadow_test_id for s in shadow_tests}
        assert shadow_test.shadow_test_id in shadow_test_ids

        # We can update a shadow test.
        name = "Hoppy Shadow & Light"
        description = "A shadow test for hoppy bunnies"
        shadow_test = app.update_shadow_test(
            shadow_test_id=shadow_test.shadow_test_id,
            name=name,
            description=description,
        )
        assert shadow_test.name == name
        assert shadow_test.description == description

        # We can start a shadow test.
        app.start_shadow_test(shadow_test_id=shadow_test.shadow_test_id)
        metadata = app.shadow_test_metadata(shadow_test_id=shadow_test.shadow_test_id)
        assert metadata.status == cloud.ExperimentStatus.STARTED

        # Do some runs to let the shadow test collect data.
        input_data = {"name": "world", "radius": 6378, "distance": 147.6}
        for _ in range(2):
            _ = app.new_run_with_result(input=input_data, instance_id=inst1.id)

        # Stop the shadow test.
        app.stop_shadow_test(shadow_test_id=shadow_test.shadow_test_id, intent=cloud.StopIntent.complete)
        metadata = app.shadow_test_metadata(shadow_test_id=shadow_test.shadow_test_id)
        assert metadata.status == cloud.ExperimentStatus.COMPLETED or metadata.status == cloud.ExperimentStatus.STOPPING

        # Get the results of the shadow test and assert that it registered the
        # runs.
        shadow_test = app.shadow_test(shadow_test_id=shadow_test.shadow_test_id)
        assert len(shadow_test.runs) > 0

        # We can delete a shadow test.
        app.delete_shadow_test(shadow_test_id=shadow_test.shadow_test_id)

    # We make switchback a successor of shadow tests to reuse the instances.
    @needs(predecessors=[init_app, instances, shadow_tests])
    @step
    def switchback_tests(app: cloud.Application, instances: tuple[cloud.Instance, cloud.Instance], __unused) -> None:
        """
        Performs switchback test operations.

        Parameters
        ----------
        app : cloud.Application
            The application to perform switchback test operations on.
        instances : tuple[cloud.Instance, cloud.Instance]
            The instances to use for the switchback test.
        """

        inst1, inst2 = instances

        # We can start a switchback test in draft mode.
        switchback_test = app.new_switchback_test(
            comparison=cloud.TestComparisonSingle(
                baseline_instance_id=inst1.id,
                candidate_instance_id=inst2.id,
            ),
            unit_duration_minutes=1,
            units=1,
        )
        metadata = app.switchback_test_metadata(switchback_test_id=switchback_test.switchback_test_id)
        assert metadata.status == cloud.ExperimentStatus.DRAFT

        # We can get a switchback test.
        switchback_test = app.switchback_test(switchback_test_id=switchback_test.switchback_test_id)
        assert switchback_test is not None

        # We can list switchback tests.
        switchback_tests = app.list_switchback_tests()
        assert len(switchback_tests) >= 1
        switchback_test_ids = {s.switchback_test_id for s in switchback_tests}
        assert switchback_test.switchback_test_id in switchback_test_ids

        # We can update a switchback test.
        name = "Hoppy switchback & Light"
        description = "A switchback test for hoppy bunnies"
        switchback_test = app.update_switchback_test(
            switchback_test_id=switchback_test.switchback_test_id,
            name=name,
            description=description,
        )
        assert switchback_test.name == name
        assert switchback_test.description == description

        # We can start a switchback test.
        app.start_switchback_test(switchback_test_id=switchback_test.switchback_test_id)
        metadata = app.switchback_test_metadata(switchback_test_id=switchback_test.switchback_test_id)
        assert metadata.status == cloud.ExperimentStatus.STARTED

        # Do some runs to let the switchback test collect data.
        input_data = {"name": "world", "radius": 6378, "distance": 147.6}
        for _ in range(2):
            _ = app.new_run_with_result(input=input_data, instance_id=inst1.id)

        # Stop the switchback test.
        app.stop_switchback_test(
            switchback_test_id=switchback_test.switchback_test_id,
            intent=cloud.StopIntent.complete,
        )
        metadata = app.switchback_test_metadata(switchback_test_id=switchback_test.switchback_test_id)
        assert metadata.status == cloud.ExperimentStatus.COMPLETED or metadata.status == cloud.ExperimentStatus.STOPPING

        # Get the results of the switchback test and assert that it registered the
        # runs.
        switchback_test = app.switchback_test(switchback_test_id=switchback_test.switchback_test_id)
        assert len(switchback_test.runs) > 0

        # We can delete a switchback test.
        app.delete_switchback_test(switchback_test_id=switchback_test.switchback_test_id)

    @needs(predecessors=[init_app, instances, input_sets])
    @step
    def acceptance_tests(
        app: cloud.Application,
        instances: tuple[cloud.Instance, cloud.Instance],
        input_set: cloud.InputSet,
    ) -> None:
        """
        Performs acceptance test operations.

        Parameters
        ----------
        app : cloud.Application
            The application to perform acceptance test operations on.
        instances : tuple[cloud.Instance, cloud.Instance]
            The instances to use for the acceptance test.
        input_set : cloud.InputSet
            The input set to use for the acceptance test.
        """

        inst1, inst2 = instances

        # We can create an acceptance test.
        acceptance = app.new_acceptance_test_with_result(
            baseline_instance_id=inst1.id,
            candidate_instance_id=inst2.id,
            metrics=[
                cloud.Metric(
                    field="result.value",
                    metric_type=cloud.MetricType.direct_comparison,
                    params=cloud.MetricParams(
                        operator=cloud.Comparison.equal_to,
                        tolerance=cloud.MetricTolerance(
                            type=cloud.MetricToleranceType.absolute,
                            value=0.01,
                        ),
                    ),
                    statistic=cloud.StatisticType.mean,
                ),
            ],
            input_set_id=input_set.id,
        )
        assert acceptance is not None

        # We can list acceptance tests.
        acceptance_tests = app.list_acceptance_tests()
        assert len(acceptance_tests) >= 1
        acceptance_test_ids = {a.id for a in acceptance_tests}
        assert acceptance.id in acceptance_test_ids

        # We can get an acceptance test.
        acceptance = app.acceptance_test(acceptance_test_id=acceptance.id)
        assert acceptance is not None

        # We can update an acceptance test.
        name = "Hoppy Acceptance & Light"
        description = "An acceptance test for hoppy bunnies"
        acceptance = app.update_acceptance_test(
            acceptance_test_id=acceptance.id,
            name=name,
            description=description,
        )
        assert acceptance.name == name
        assert acceptance.description == description

        # We can delete an acceptance test.
        app.delete_acceptance_test(acceptance_test_id=acceptance.id)

    @needs(predecessors=[init_app, community_push])
    @step
    def secrets(app: cloud.Application, __unused) -> None:
        """
        Performs secret operations.

        Parameters
        ----------
        app : cloud.Application
            The application to perform secret operations on.
        """

        # We can create a secrets collection.
        secrets = [
            cloud.Secret(
                secret_type=cloud.SecretType.ENV,
                location="BURROW_ENTRANCE",
                value="Make 2 lefts and a hop forward",
            )
        ]
        summary = app.new_secrets_collection(
            secrets=secrets,
        )

        # We can get a secrets collection.
        collection = app.secrets_collection(secrets_collection_id=summary.collection_id)
        assert collection is not None
        assert len(collection.secrets) == 1
        assert collection.secrets[0].location == secrets[0].location
        assert collection.secrets[0].value == secrets[0].value

        # We can list secret collections.
        collections = app.list_secrets_collections()
        assert len(collections) >= 1
        collection_ids = {c.collection_id for c in collections}
        assert summary.collection_id in collection_ids

        # We can update a secrets collection.
        name = "Bunny Secrets"
        description = "Secrets for bunny application"
        summary = app.update_secrets_collection(
            secrets_collection_id=summary.collection_id,
            name=name,
            description=description,
        )
        assert summary.name == name
        assert summary.description == description

        # We can start a run using the secrets collection.
        input_data = {"name": "world", "radius": 6378, "distance": 147.6}
        app.new_run(
            input=input_data,
            configuration=nextmv.RunConfiguration(
                secrets_collection_id=summary.collection_id,
            ),
        )

        # We can delete a secrets collection.
        app.delete_secrets_collection(secrets_collection_id=summary.collection_id)

    @needs(predecessors=[init_app, instances])
    @step
    def ensembles(app: cloud.Application, instances: tuple[cloud.Instance, cloud.Instance]) -> None:
        """
        Performs ensemble operations.

        Parameters
        ----------
        app : cloud.Application
            The application to perform ensemble operations on.
        instances : tuple[cloud.Instance, cloud.Instance]
            The instances to use for the ensemble definition.
        """

        inst1, _ = instances

        # We can create an ensemble definition.
        definition = app.new_ensemble_definition(
            run_groups=[
                cloud.RunGroup(
                    id="run-group-1",
                    instance_id=inst1.id,
                ),
            ],
            rules=[
                cloud.EvaluationRule(
                    id="eval-rule-1",
                    statistics_path="result.value",
                    objective=cloud.RuleObjective.MAXIMIZE,
                    tolerance=cloud.RuleTolerance(
                        value=0.01,
                        type=cloud.RuleToleranceType.ABSOLUTE,
                    ),
                    index=0,
                ),
            ],
        )

        # We can get an ensemble definition.
        definition = app.ensemble_definition(ensemble_definition_id=definition.id)
        assert definition is not None

        # We can list ensemble definitions.
        definitions = app.list_ensemble_definitions()
        assert len(definitions) >= 1
        definition_ids = {d.id for d in definitions}
        assert definition.id in definition_ids

        # We can update an ensemble definition.
        name = "Bunny Ensemble"
        description = "Ensemble for bunny runs"
        definition = app.update_ensemble_definition(
            id=definition.id,
            name=name,
            description=description,
        )
        assert definition.name == name
        assert definition.description == description

        # We can start an ensemble run.
        input_data = {"name": "world", "radius": 6378, "distance": 147.6}
        app.new_run(
            input=input_data,
            configuration=nextmv.RunConfiguration(
                run_type=nextmv.RunTypeConfiguration(
                    run_type=nextmv.RunType.ENSEMBLE,
                    definition_id=definition.id,
                ),
            ),
        )

        # We can delete an ensemble definition.
        app.delete_ensemble_definition(ensemble_definition_id=definition.id)

    # For this step, all other steps are predecessors to make sure there are no
    # on-going processes before cleanup.
    @needs(
        predecessors=[
            init_app,
            versions,
            instances,
            runs,
            input_sets,
            scenario_tests,
            shadow_tests,
            switchback_tests,
            acceptance_tests,
            secrets,
            ensembles,
        ]
    )
    @step
    def cleanup(
        app: cloud.Application,
        version: cloud.Version,
        instances: tuple[cloud.Instance, cloud.Instance],
        __unused,  # Unused placeholders for predecessors whose return values we don't need.
        input_set: cloud.InputSet,
        __unused2,
        __unused3,
        __unused4,
        __unused5,
        __unused6,
        __unused7,
    ) -> None:
        """Performs cleanup operations."""

        # We clean up the version.
        app.delete_version(version_id=version.id)

        # Reset the default instance so that we can clean up the instances.
        app.update(default_instance_id="latest")
        for inst in instances:
            app.delete_instance(instance_id=inst.id)

        # Clean up the input set.
        app.delete_input_set(input_set_id=input_set.id)

        # We can delete the app after cleanup.
        app.delete()


def test_cloud_integration():
    """Runs the workflow."""

    # Load input data
    app_id = safe_id("cloud-integration-app")

    # Run workflow
    workflow = CloudIntegrationWorkflow(name="DecisionWorkflow", input=app_id, client=client)
    workflow.run()
