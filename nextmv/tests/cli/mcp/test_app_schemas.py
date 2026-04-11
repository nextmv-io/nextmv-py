"""Schema-shape assertions for the cloud app MCP tools.

These tests are the MCP-side equivalent of the CLI help-output tests: they
assert that the tool descriptions and input schemas match what the
mcp_fw.tool() builder produces from the action signatures, so that any
LLM or MCP client consuming these tools sees the expected interface.

If a test fails, either:
  (a) the action signature in cli/actions/app.py changed, and the change
      is intentional - update the test, or
  (b) the framework's schema generation regressed, and the framework
      must be fixed.
"""

import unittest

from nextmv.cli.mcp.server import create_server


class TestAppToolSchemas(unittest.TestCase):
    """Assert the tool name, description, and input schema for each app tool."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = create_server()
        cls.tools = cls.server._tool_manager._tools

    def test_cloud_list_apps_has_no_parameters(self) -> None:
        tool = self.tools["cloud_list_apps"]
        self.assertIn("List all Nextmv Cloud applications", tool.description)
        schema = tool.parameters
        properties = schema.get("properties", {})
        self.assertEqual(properties, {})

    def test_cloud_get_app_requires_app_id(self) -> None:
        tool = self.tools["cloud_get_app"]
        self.assertIn("Get details", tool.description)
        schema = tool.parameters
        self.assertIn("app_id", schema.get("properties", {}))
        self.assertIn("app_id", schema.get("required", []))

    def test_cloud_create_app_has_all_optional_params(self) -> None:
        """cloud_create_app schema covers all seven action params, all optional.

        Note: `name` was previously required in the hand-written MCP wrapper
        (the action always accepted None, but the wrapper declared ``name: str``).
        After the refactor, the action's signature drives the schema, so `name`
        is now optional. See the commit message for Task 13 for context.
        """
        tool = self.tools["cloud_create_app"]
        self.assertIn("Create a new Nextmv Cloud application", tool.description)
        props = tool.parameters.get("properties", {})
        for name in [
            "name",
            "app_id",
            "description",
            "is_workflow",
            "exist_ok",
            "default_instance_id",
            "default_experiment_instance",
        ]:
            self.assertIn(
                name,
                props,
                msg=f"cloud_create_app schema missing parameter: {name}",
            )
        # None of these are required (all have defaults on the action).
        self.assertEqual(tool.parameters.get("required", []), [])

    def test_cloud_create_app_param_descriptions_come_from_field(self) -> None:
        """The dual-purpose Annotated aliases must surface Field(description=)
        into the MCP schema."""
        tool = self.tools["cloud_create_app"]
        props = tool.parameters["properties"]
        # app_id help comes from _APP_ID_HELP
        self.assertIn("description", props["app_id"])
        self.assertIn("optional ID", props["app_id"]["description"])
        # is_workflow help comes from _IS_WORKFLOW_HELP
        self.assertIn("description", props["is_workflow"])
        self.assertIn("workflow", props["is_workflow"]["description"])

    def test_cloud_delete_app_requires_app_id(self) -> None:
        tool = self.tools["cloud_delete_app"]
        self.assertIn("Delete a Nextmv Cloud application", tool.description)
        schema = tool.parameters
        self.assertIn("app_id", schema.get("required", []))

    def test_cloud_app_exists_requires_app_id(self) -> None:
        tool = self.tools["cloud_app_exists"]
        self.assertIn("Check whether", tool.description)
        schema = tool.parameters
        self.assertIn("app_id", schema.get("required", []))

    def test_cloud_update_app_requires_app_id_only(self) -> None:
        tool = self.tools["cloud_update_app"]
        self.assertIn("Update attributes", tool.description)
        schema = tool.parameters
        self.assertIn("app_id", schema.get("required", []))
        # All other params are optional.
        for name in [
            "name",
            "description",
            "default_instance_id",
            "default_experiment_instance",
        ]:
            self.assertIn(name, schema.get("properties", {}))
            self.assertNotIn(name, schema.get("required", []))

    def test_cloud_push_app_requires_app_id_and_app_dir(self) -> None:
        tool = self.tools["cloud_push_app"]
        self.assertIn("Push local application code", tool.description)
        schema = tool.parameters
        required = set(schema.get("required", []))
        self.assertEqual(required, {"app_id", "app_dir"})


if __name__ == "__main__":
    unittest.main()
