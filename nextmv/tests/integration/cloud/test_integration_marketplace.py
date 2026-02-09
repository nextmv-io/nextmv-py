import os

from nextpipe import FlowSpec, needs, step

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))


class MarketplaceIntegrationWorkflow(FlowSpec):
    @step
    def app(app_partner: tuple[str, str]) -> cloud.MarketplaceApplication:
        """
        Gets and lists a marketplace application.

        Parameters
        ----------
        app_partner : tuple[str, str]
            A tuple containing the application ID and partner ID.

        Returns
        -------
        cloud.MarketplaceApplication
            The marketplace application.
        """

        app_id, partner_id = app_partner

        # We can get the app.
        app = cloud.MarketplaceApplication.get(client=client, partner_id=partner_id, app_id=app_id)
        assert app is not None

        # We can list apps without the partner.
        apps = cloud.list_marketplace_applications(client)
        assert len(apps) > 0
        assert app.app_id in {a.app_id for a in apps}

        # We can list apps with the partner.
        apps = cloud.list_marketplace_applications(client, partner_id=partner_id)
        assert len(apps) > 0
        assert app.app_id in {a.app_id for a in apps}

        return app

    @needs(predecessors=[app])
    @step
    def versions(app: cloud.MarketplaceApplication) -> None:
        """
        Performs version operations on the app.

        Parameters
        ----------
        app : cloud.MarketplaceApplication
            The application to perform version operations on.
        """

        versions = app.list_versions()
        assert len(versions) > 0

        v1 = versions[0]
        version = app.version(version_id=v1.version_id)
        assert version is not None
        assert version.version_id == v1.version_id


def test_marketplace_integration():
    """Runs the workflow."""

    # Load input data
    app_id = "nextroute"
    partner_id = "nextmv"

    # Run workflow
    workflow = MarketplaceIntegrationWorkflow(name="DecisionWorkflow", input=(app_id, partner_id), client=client)
    workflow.run()
