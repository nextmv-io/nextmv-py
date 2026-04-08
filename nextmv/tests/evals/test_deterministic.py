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


import os
from nextmv.evals.loader import load_eval_cases, EvalCase
from nextmv.evals.agent import ToolCall as TC


class TestLoader(unittest.TestCase):

    def _cases_dir(self):
        return os.path.join(
            os.path.dirname(__file__), "..", "..", "nextmv", "evals", "cases",
        )

    def test_loads_app_management_cases(self):
        cases = load_eval_cases(os.path.join(self._cases_dir(), "app_management.yaml"))
        self.assertGreater(len(cases), 0)

    def test_case_has_required_fields(self):
        cases = load_eval_cases(os.path.join(self._cases_dir(), "app_management.yaml"))
        case = cases[0]
        self.assertIsInstance(case, EvalCase)
        self.assertIsNotNone(case.id)
        self.assertIsNotNone(case.task)
        self.assertIsInstance(case.expected_tools, list)

    def test_deterministic_script_parsed_as_tool_calls(self):
        cases = load_eval_cases(os.path.join(self._cases_dir(), "app_management.yaml"))
        case = cases[0]
        self.assertEqual(len(case.deterministic), 1)
        self.assertIsInstance(case.deterministic[0], TC)
        self.assertEqual(case.deterministic[0].name, "cloud_list_apps")

    def test_case_with_no_deterministic_gets_empty_list(self):
        case = EvalCase(id="test", task="do something", expected_tools=[])
        self.assertEqual(case.deterministic, [])
