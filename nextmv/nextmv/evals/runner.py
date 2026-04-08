"""Eval runner: orchestrates agent <-> MCP tool execution loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nextmv.evals.agent import Agent, DeterministicAgent, ToolCall
from nextmv.evals.loader import EvalCase
from nextmv.evals.scorer import score_outcome, score_tool_sequence


@dataclass
class EvalResult:
    """Result of running a single eval case."""

    case_id: str
    tools_called: list[str]
    tool_results: list[dict[str, Any]]
    tool_score: float
    outcome_passed: bool


class EvalRunner:
    """Runs eval cases by driving an agent through MCP tool calls."""

    def __init__(self, server: Any, max_steps: int = 20) -> None:
        self._server = server
        self._max_steps = max_steps
        self._all_tools: list[Any] | None = None

    async def get_tools(self, case: EvalCase | None = None) -> list[Any]:
        """Get tool schemas, scoped to the case's tool list if specified."""
        if self._all_tools is None:
            self._all_tools = await self._server.list_tools()
        if case and case.tools:
            allowed = set(case.tools)
            return [t for t in self._all_tools if t.name in allowed]
        return list(self._all_tools)

    async def run_case(
        self,
        case: EvalCase,
        mode: str = "deterministic",
        agent: Agent | None = None,
    ) -> EvalResult:
        if mode == "deterministic":
            agent = DeterministicAgent(script=case.deterministic)
        elif agent is None:
            raise ValueError("agent is required when mode is 'llm'")

        tools_called: list[str] = []
        tool_results: list[dict[str, Any]] = []
        messages: list[dict[str, Any]] = [{"role": "user", "content": case.task}]

        for _ in range(self._max_steps):
            action = agent.next_action(messages=messages, tool_results=tool_results)
            if action is None:
                break

            content_list, _ = await self._server.call_tool(action.name, action.arguments)
            result_text = content_list[0].text if content_list else ""

            tools_called.append(action.name)
            tool_results.append({
                "role": "tool",
                "tool": action.name,
                "content": result_text,
            })

        return EvalResult(
            case_id=case.id,
            tools_called=tools_called,
            tool_results=tool_results,
            tool_score=score_tool_sequence(case.expected_tools, tools_called),
            outcome_passed=score_outcome(tool_results, case.success),
        )
