"""Convert MCP tool schemas to LLM provider tool formats."""

from typing import Any


def mcp_tool_to_anthropic(tool: Any) -> dict:
    """Convert an MCP Tool object to Anthropic API tool format.

    Anthropic expects:
    {
        "name": "tool_name",
        "description": "what it does",
        "input_schema": { JSON Schema without title }
    }
    """
    schema = dict(tool.inputSchema)
    schema.pop("title", None)

    return {
        "name": tool.name,
        "description": tool.description or "",
        "input_schema": schema,
    }


def mcp_tool_to_openai(tool: Any) -> dict:
    """Convert an MCP Tool object to OpenAI API tool format.

    OpenAI expects:
    {
        "type": "function",
        "function": {
            "name": "tool_name",
            "description": "what it does",
            "parameters": { JSON Schema without title }
        }
    }
    """
    schema = dict(tool.inputSchema)
    schema.pop("title", None)

    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": schema,
        },
    }
