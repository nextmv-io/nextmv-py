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


import asyncio
from unittest.mock import AsyncMock
from types import SimpleNamespace
from nextmv.evals.runner import EvalRunner, EvalResult
from nextmv.evals.loader import EvalCase as EC


class TestEvalRunner(unittest.TestCase):

    def _make_mock_server(self):
        server = AsyncMock()
        server.list_tools.return_value = []

        async def mock_call_tool(name, args):
            responses = {
                "cloud_list_apps": ([SimpleNamespace(text='[{"id": "routing-demo", "name": "Routing Demo"}]')], None),
                "cloud_get_app": ([SimpleNamespace(text='{"id": "routing-demo", "name": "Routing Demo"}')], None),
            }
            return responses.get(name, ([SimpleNamespace(text="{}")], None))

        server.call_tool = AsyncMock(side_effect=mock_call_tool)
        return server

    def test_runs_deterministic_case(self):
        case = EC(
            id="list_apps",
            task="List apps",
            expected_tools=["cloud_list_apps"],
            success={"tool_called": "cloud_list_apps"},
            deterministic=[ToolCall(name="cloud_list_apps", arguments={})],
        )
        server = self._make_mock_server()
        runner = EvalRunner(server=server)
        result = asyncio.run(runner.run_case(case, mode="deterministic"))

        self.assertIsInstance(result, EvalResult)
        self.assertEqual(result.case_id, "list_apps")
        self.assertEqual(result.tools_called, ["cloud_list_apps"])
        self.assertEqual(result.tool_score, 1.0)
        self.assertTrue(result.outcome_passed)

    def test_multi_step_deterministic(self):
        case = EC(
            id="create_and_get",
            task="Create and get app",
            expected_tools=["cloud_list_apps", "cloud_get_app"],
            success={"tool_called": "cloud_get_app"},
            deterministic=[
                ToolCall(name="cloud_list_apps", arguments={}),
                ToolCall(name="cloud_get_app", arguments={"app_id": "routing-demo"}),
            ],
        )
        server = self._make_mock_server()
        runner = EvalRunner(server=server)
        result = asyncio.run(runner.run_case(case, mode="deterministic"))

        self.assertEqual(result.tools_called, ["cloud_list_apps", "cloud_get_app"])
        self.assertEqual(result.tool_score, 1.0)
        self.assertTrue(result.outcome_passed)

    def test_max_steps_prevents_infinite_loop(self):
        long_script = [ToolCall(name="cloud_list_apps", arguments={})] * 100
        case = EC(
            id="long",
            task="Long task",
            expected_tools=["cloud_list_apps"],
            deterministic=long_script,
        )
        server = self._make_mock_server()
        runner = EvalRunner(server=server, max_steps=5)
        result = asyncio.run(runner.run_case(case, mode="deterministic"))
        self.assertEqual(len(result.tools_called), 5)
