import unittest
from types import SimpleNamespace

from nextmv.evals.bridge import mcp_tool_to_anthropic, mcp_tool_to_openai


class TestMCPToolToAnthropic(unittest.TestCase):

    def _make_mcp_tool(self):
        return SimpleNamespace(
            name="cloud_list_apps",
            description="List all applications.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
                "title": "cloud_list_appsArguments",
            },
        )

    def _make_mcp_tool_with_params(self):
        return SimpleNamespace(
            name="cloud_get_app",
            description="Get an application by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_id": {"type": "string", "title": "App Id"},
                },
                "required": ["app_id"],
                "title": "cloud_get_appArguments",
            },
        )

    def test_converts_name_and_description(self):
        tool = self._make_mcp_tool()
        result = mcp_tool_to_anthropic(tool)
        self.assertEqual(result["name"], "cloud_list_apps")
        self.assertEqual(result["description"], "List all applications.")

    def test_converts_input_schema(self):
        tool = self._make_mcp_tool_with_params()
        result = mcp_tool_to_anthropic(tool)
        self.assertEqual(result["input_schema"]["type"], "object")
        self.assertIn("app_id", result["input_schema"]["properties"])

    def test_strips_title_from_schema(self):
        tool = self._make_mcp_tool()
        result = mcp_tool_to_anthropic(tool)
        self.assertNotIn("title", result["input_schema"])


class TestMCPToolToOpenAI(unittest.TestCase):

    def _make_mcp_tool(self):
        return SimpleNamespace(
            name="cloud_list_apps",
            description="List all applications.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
                "title": "cloud_list_appsArguments",
            },
        )

    def test_wraps_in_function_type(self):
        tool = self._make_mcp_tool()
        result = mcp_tool_to_openai(tool)
        self.assertEqual(result["type"], "function")
        self.assertIn("function", result)

    def test_converts_name_and_description(self):
        tool = self._make_mcp_tool()
        result = mcp_tool_to_openai(tool)
        self.assertEqual(result["function"]["name"], "cloud_list_apps")
        self.assertEqual(result["function"]["description"], "List all applications.")

    def test_converts_parameters(self):
        tool = self._make_mcp_tool()
        result = mcp_tool_to_openai(tool)
        self.assertEqual(result["function"]["parameters"]["type"], "object")
