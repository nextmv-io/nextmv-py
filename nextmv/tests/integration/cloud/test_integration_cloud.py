import os
import tempfile

from nextmv.safe import safe_id
from nextpipe import FlowSpec, needs, step

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
    def version(app: cloud.Application, __unused) -> cloud.Version:
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

    @needs(predecessors=[init_app, version])
    @step
    def instance(app: cloud.Application, version: cloud.Version) -> tuple[cloud.Instance, cloud.Instance]:
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

    @needs(predecessors=[init_app, version, instance])
    @step
    def cleanup(
        app: cloud.Application,
        version: cloud.Version,
        instances: tuple[cloud.Instance, cloud.Instance],
    ) -> None:
        """Performs cleanup operations."""

        # We can delete the version.
        app.delete_version(version_id=version.id)

        # We can delete the instances.
        for inst in instances:
            app.delete_instance(instance_id=inst.id)

        # We can delete the app and it should not exist.
        app.delete()
        exists = cloud.Application.exists(client=client, id=app.id)
        assert not exists


def test_cloud_integration():
    """Runs the workflow."""

    # Load input data
    app_id = safe_id("cloud-integration-app")

    # Run workflow
    workflow = CloudIntegrationWorkflow(name="DecisionWorkflow", input=app_id, client=client)
    workflow.run()
