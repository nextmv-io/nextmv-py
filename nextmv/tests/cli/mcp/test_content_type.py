"""Tests for the content_type parameter added to SDK batch/scenario methods."""

import unittest
from unittest.mock import MagicMock, patch


class TestSDKContentType(unittest.TestCase):
    """Tests for the content_type parameter added to SDK batch/scenario methods."""

    def _make_app(self):
        """Create an Application with a mock client."""
        from nextmv.cloud import Application, Client

        client = Client(api_key="test-key", url="https://api.test.io")
        client.request = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "test-id"}
        client.request.return_value = mock_response
        return Application(client=client, id="test-app")

    def test_new_batch_experiment_passes_content_type(self):
        """new_batch_experiment includes content_type in the API payload."""
        app = self._make_app()
        app.new_batch_experiment(
            name="test",
            type="scenario",
            content_type="multi-file",
            runs=[],
        )

        payload = app.client.request.call_args[1]["payload"]
        self.assertEqual(payload["content_type"], "multi-file")

    def test_new_batch_experiment_omits_content_type_when_none(self):
        """new_batch_experiment does not include content_type when None."""
        app = self._make_app()
        app.new_batch_experiment(name="test")

        payload = app.client.request.call_args[1]["payload"]
        self.assertNotIn("content_type", payload)

    def test_new_scenario_test_passes_content_type(self):
        """new_scenario_test forwards content_type to new_batch_experiment.

        We verify this through the MCP tool layer, which calls the SDK's
        new_scenario_test. The tool-level tests in TestBugFixes already
        confirm content_type is passed. Here we test the SDK method
        directly by checking the API payload.
        """
        app = self._make_app()

        # Mock the instance and input_set lookups that new_scenario_test needs.
        mock_instance = MagicMock()
        mock_input_set = MagicMock()
        mock_input_set.id = "is-1"
        mock_input_set.input_ids = ["inp-1"]
        mock_input_set.inputs = []

        from nextmv.cloud.scenario import Scenario, ScenarioInput, ScenarioInputType

        scenario = Scenario(
            scenario_input=ScenarioInput(
                scenario_input_type=ScenarioInputType.INPUT_SET,
                scenario_input_data="is-1",
            ),
            instance_id="inst-1",
        )

        with (
            patch.object(type(app), "instance", return_value=mock_instance),
            patch.object(type(app), "input_set", return_value=mock_input_set),
        ):
            app.new_scenario_test(
                scenarios=[scenario],
                content_type="multi-file",
            )

        # The SDK should have made the API POST with content_type in the payload.
        payload = app.client.request.call_args[1]["payload"]
        self.assertEqual(payload.get("content_type"), "multi-file")
