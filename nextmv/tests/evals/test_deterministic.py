import unittest
from nextmv.evals.agent import DeterministicAgent, ToolCall


class TestDeterministicAgent(unittest.TestCase):

    def test_returns_scripted_tool_calls(self):
        script = [ToolCall(name="cloud_list_apps", arguments={})]
        agent = DeterministicAgent(script=script)
        result = agent.next_action(messages=[], tool_results=[])
        self.assertEqual(result.name, "cloud_list_apps")
        self.assertEqual(result.arguments, {})

    def test_returns_none_when_script_exhausted(self):
        script = [ToolCall(name="cloud_list_apps", arguments={})]
        agent = DeterministicAgent(script=script)
        agent.next_action(messages=[], tool_results=[])
        result = agent.next_action(messages=[], tool_results=[])
        self.assertIsNone(result)

    def test_replays_multiple_calls_in_order(self):
        script = [
            ToolCall(name="cloud_list_apps", arguments={}),
            ToolCall(name="cloud_get_app", arguments={"app_id": "my-app"}),
        ]
        agent = DeterministicAgent(script=script)
        first = agent.next_action(messages=[], tool_results=[])
        self.assertEqual(first.name, "cloud_list_apps")
        second = agent.next_action(messages=[], tool_results=[])
        self.assertEqual(second.name, "cloud_get_app")
        self.assertEqual(second.arguments, {"app_id": "my-app"})

    def test_empty_script_returns_none_immediately(self):
        agent = DeterministicAgent(script=[])
        result = agent.next_action(messages=[], tool_results=[])
        self.assertIsNone(result)
