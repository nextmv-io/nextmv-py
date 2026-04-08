"""Agent protocol and deterministic agent for eval replay."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class ToolCall:
    """A single tool invocation."""

    name: str
    arguments: dict[str, Any]


class Agent(Protocol):
    """Interface that all eval agents implement.

    next_action() is called in a loop by the eval runner.
    It receives the conversation history and the results of
    any previous tool calls. It returns the next ToolCall
    to execute, or None if the agent is done.
    """

    def next_action(
        self,
        messages: list[dict[str, Any]],
        tool_results: list[dict[str, Any]],
    ) -> ToolCall | None: ...


class DeterministicAgent:
    """Replays a scripted sequence of tool calls.

    Ignores messages and tool_results — just steps through
    the script in order. Returns None when exhausted.
    """

    def __init__(self, script: list[ToolCall]) -> None:
        self._script = list(script)
        self._index = 0

    def next_action(
        self,
        messages: list[dict[str, Any]],
        tool_results: list[dict[str, Any]],
    ) -> ToolCall | None:
        if self._index >= len(self._script):
            return None
        call = self._script[self._index]
        self._index += 1
        return call
