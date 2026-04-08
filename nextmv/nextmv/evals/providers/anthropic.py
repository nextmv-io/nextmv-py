"""Anthropic Claude agent for MCP evals."""

from __future__ import annotations

import os
from typing import Any

import anthropic

from nextmv.evals.agent import ToolCall
from nextmv.evals.bridge import mcp_tool_to_anthropic


class AnthropicAgent:
    """Agent that uses Claude to decide which MCP tools to call.

    Single-use: create a new instance for each eval case.
    The agent accumulates conversation state across calls to
    next_action() and cannot be reused for a different task.
    """

    def __init__(
        self,
        tools: list[Any],
        model: str = "claude-sonnet-4-20250514",
        system: str = "",
        api_key: str | None = None,
    ) -> None:
        self._client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"),
        )
        self._model = model
        self._system = system
        self._tools = [mcp_tool_to_anthropic(t) for t in tools]
        self._messages: list[dict[str, Any]] = []
        self._pending_tool_use_id: str | None = None

    def next_action(
        self,
        messages: list[dict[str, Any]],
        tool_results: list[dict[str, Any]],
    ) -> ToolCall | None:
        if not messages:
            return None

        # Build the messages list for the API call
        if not self._messages:
            self._messages.append({"role": "user", "content": messages[0]["content"]})
        elif self._pending_tool_use_id and tool_results:
            last_result = tool_results[-1]
            self._messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": self._pending_tool_use_id,
                    "content": str(last_result["content"]),
                }],
            })

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=1024,
                system=self._system,
                tools=self._tools,
                messages=self._messages,
            )
        except anthropic.APIError as exc:
            raise RuntimeError(f"Anthropic API error: {exc}") from exc

        # Add assistant response to history
        self._messages.append({"role": "assistant", "content": response.content})

        # Look for a tool_use block in the response
        for block in response.content:
            if block.type == "tool_use":
                self._pending_tool_use_id = block.id
                return ToolCall(name=block.name, arguments=block.input)

        # No tool call — model is done (gave a text response)
        return None
