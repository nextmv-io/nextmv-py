"""OpenAI-compatible agent for MCP evals.

Works with OpenAI API, Azure OpenAI, GitHub Copilot,
and Ollama (any endpoint that speaks the OpenAI chat completions format).
"""

from __future__ import annotations

import json
import os
from typing import Any

import openai

from nextmv.evals.agent import ToolCall
from nextmv.evals.bridge import mcp_tool_to_openai


class OpenAIAgent:
    """Agent that uses an OpenAI-compatible model to decide which MCP tools to call.

    Maintains a conversation, translating tool_calls responses
    into ToolCall objects and feeding tool results back as
    tool-role messages.
    """

    def __init__(
        self,
        tools: list[Any],
        model: str = "gpt-4o",
        system: str = "",
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self._client = openai.OpenAI(
            api_key=api_key or os.environ.get("OPENAI_API_KEY", "ollama"),
            base_url=base_url,
        )
        self._model = model
        self._system = system
        self._tools = [mcp_tool_to_openai(t) for t in tools]
        self._messages: list[dict[str, Any]] = []
        self._pending_tool_call_id: str | None = None

    def next_action(
        self,
        messages: list[dict[str, Any]],
        tool_results: list[dict[str, Any]],
    ) -> ToolCall | None:
        # Build the messages list for the API call
        if not self._messages:
            if self._system:
                self._messages.append({"role": "system", "content": self._system})
            self._messages.append({"role": "user", "content": messages[0]["content"]})
        elif self._pending_tool_call_id and tool_results:
            last_result = tool_results[-1]
            self._messages.append({
                "role": "tool",
                "tool_call_id": self._pending_tool_call_id,
                "content": last_result["content"],
            })

        response = self._client.chat.completions.create(
            model=self._model,
            messages=self._messages,
            tools=self._tools if self._tools else openai.NOT_GIVEN,
        )

        choice = response.choices[0]

        # Add assistant message to history
        self._messages.append(choice.message.model_dump())

        # Check for tool calls
        if choice.message.tool_calls:
            tool_call = choice.message.tool_calls[0]
            self._pending_tool_call_id = tool_call.id
            arguments = json.loads(tool_call.function.arguments)
            return ToolCall(name=tool_call.function.name, arguments=arguments)

        # No tool call — model is done
        return None
