"""LLM-powered eval tests.

These tests call real LLM APIs. They are skipped by default in CI.
Run with: pytest -m llm

For Ollama (local): just have Ollama running on localhost:11434
For Claude: set ANTHROPIC_API_KEY
"""

import asyncio
import glob
import json
import os
import unittest

import pytest

from nextmv.evals.loader import load_eval_cases
from nextmv.evals.prompts import EVAL_SYSTEM_PROMPT
from nextmv.evals.runner import EvalRunner


def _ollama_base_url():
    """Return the Ollama base URL from OLLAMA_HOST or default."""
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    if not host.startswith("http"):
        host = f"http://{host}"
    return host


def _is_ollama_available():
    """Check if Ollama is running."""
    try:
        import urllib.request

        urllib.request.urlopen(f"{_ollama_base_url()}/api/tags", timeout=2)
        return True
    except Exception:
        return False


def _cases_dir():
    return os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "nextmv",
        "evals",
        "cases",
    )


def _load_all_cases():
    cases = []
    for yaml_file in sorted(glob.glob(os.path.join(_cases_dir(), "*.yaml"))):
        if "tool_groups" in os.path.basename(yaml_file):
            continue
        cases.extend(load_eval_cases(yaml_file))
    return cases


def _make_mock_server():
    """Mock MCP server with canned responses and real tool schemas."""
    from types import SimpleNamespace
    from unittest.mock import AsyncMock

    server = AsyncMock()

    # We need real tool schemas for scoping. Load them from the actual server.
    from nextmv.cli.mcp.server import create_server

    real_tools = asyncio.run(create_server().list_tools())
    server.list_tools.return_value = real_tools

    async def mock_call_tool(name, args):
        responses = {
            "cloud_list_apps": json.dumps(
                [
                    {
                        "id": "routing-demo",
                        "name": "Routing Demo",
                        "description": "VRP solver",
                    },
                    {
                        "id": "scheduling-app",
                        "name": "Shift Scheduling",
                        "description": "Schedule optimizer",
                    },
                    {
                        "id": "knapsack-solver",
                        "name": "Knapsack Solver",
                        "description": "Bin packing",
                    },
                ]
            ),
            "cloud_get_app": json.dumps(
                {
                    "id": "routing-demo",
                    "name": "Routing Demo",
                    "description": "VRP solver",
                }
            ),
            "cloud_create_app": json.dumps({"id": "eval-test", "name": "eval-test"}),
            "cloud_delete_app": "Deleted application does-not-exist-xyz",
            "cloud_app_exists": json.dumps({"exists": False}),
            "cloud_run_submit": json.dumps({"run_id": "latest-abc123"}),
            "cloud_run": json.dumps(
                {"id": "latest-abc123", "status": "succeeded"}
            ),
            "cloud_run_result": json.dumps(
                {"id": "latest-abc123", "output": {"routes": []}}
            ),
            "cloud_run_status": json.dumps(
                {"id": "latest-abc123", "status": "succeeded"}
            ),
            "cloud_run_input": json.dumps({"stops": 5}),
            "cloud_run_logs": "Run completed successfully",
            "cloud_list_runs": json.dumps(
                [{"id": "latest-abc123", "status": "succeeded"}]
            ),
            "cloud_cancel_run": "Run cancelled",
        }
        text = responses.get(name, json.dumps({"status": "ok"}))
        return ([SimpleNamespace(text=text)], None)

    server.call_tool = AsyncMock(side_effect=mock_call_tool)
    return server


@pytest.mark.llm
class TestOllamaEvals(unittest.TestCase):
    """Run eval cases against a local Ollama instance."""

    @classmethod
    def setUpClass(cls):
        if not _is_ollama_available():
            raise unittest.SkipTest(
                f"Ollama not available at {_ollama_base_url()}"
            )
        cls.model = os.environ.get("EVAL_MODEL", "gemma4:26b")
        cls.base_url = f"{_ollama_base_url()}/v1"
        cls.server = _make_mock_server()
        cls.runner = EvalRunner(server=cls.server, max_steps=5)
        cls.cases = _load_all_cases()

    def test_all_cases(self):
        from nextmv.evals.providers.openai import OpenAIAgent

        results = []
        for case in self.cases:
            with self.subTest(case_id=case.id):
                scoped_tools = asyncio.run(self.runner.get_tools(case))
                agent = OpenAIAgent(
                    tools=scoped_tools,
                    model=self.model,
                    system=EVAL_SYSTEM_PROMPT,
                    base_url=self.base_url,
                )
                result = asyncio.run(
                    self.runner.run_case(case, mode="llm", agent=agent)
                )
                results.append(result)
                self.assertGreater(
                    result.tool_score,
                    0.5,
                    f"Case {case.id}: tool_score={result.tool_score}, "
                    f"called={result.tools_called}, "
                    f"expected={case.expected_tools}",
                )

        # Print summary
        passed = sum(1 for r in results if r.outcome_passed)
        print(f"\n{'='*50}")
        print(f"LLM Eval Results ({self.model}): {passed}/{len(results)} passed")
        for r in results:
            status = "PASS" if r.outcome_passed else "FAIL"
            print(f"  {r.case_id}: {status} tools={r.tools_called}")
        print(f"{'='*50}")


@pytest.mark.llm
class TestAnthropicEvals(unittest.TestCase):
    """Run eval cases with Claude (requires ANTHROPIC_API_KEY)."""

    @classmethod
    def setUpClass(cls):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise unittest.SkipTest("ANTHROPIC_API_KEY not set")
        cls.model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        cls.server = _make_mock_server()
        cls.runner = EvalRunner(server=cls.server, max_steps=5)
        cls.cases = _load_all_cases()

    def test_all_cases(self):
        from nextmv.evals.providers.anthropic import AnthropicAgent

        results = []
        for case in self.cases:
            with self.subTest(case_id=case.id):
                scoped_tools = asyncio.run(self.runner.get_tools(case))
                agent = AnthropicAgent(
                    tools=scoped_tools,
                    model=self.model,
                    system=EVAL_SYSTEM_PROMPT,
                )
                result = asyncio.run(
                    self.runner.run_case(case, mode="llm", agent=agent)
                )
                results.append(result)
                self.assertGreater(
                    result.tool_score,
                    0.5,
                    f"Case {case.id}: tool_score={result.tool_score}, "
                    f"called={result.tools_called}, "
                    f"expected={case.expected_tools}",
                )


