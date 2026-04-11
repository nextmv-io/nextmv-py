"""Tests for nextmv.cli.mcp.framework.tool."""

import unittest
from typing import Annotated
from unittest.mock import MagicMock, patch

import typer
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from nextmv.cloud.client import Client

_NAME_HELP = "A name."
_NameOpt = Annotated[
    str | None,
    typer.Option("--name", "-n", help=_NAME_HELP),
    Field(description=_NAME_HELP),
]


class TestMcpToolBuilder(unittest.TestCase):
    def test_rejects_action_without_client_first_param(self) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        def bad_action(name: str) -> dict:
            return {"name": name}

        server = FastMCP("test")
        with self.assertRaises(TypeError) as ctx:
            tool(server, bad_action, name="bad")
        self.assertIn("client", str(ctx.exception))

    def test_registers_tool_with_given_name(self) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        def list_things(client: Client) -> list[dict]:
            """List all things."""
            return []

        server = FastMCP("test")
        tool(server, list_things, name="test_list_things")
        self.assertIn("test_list_things", server._tool_manager._tools)

    def test_tool_description_from_action_docstring(self) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        def list_things(client: Client) -> list[dict]:
            """List all things in the system."""
            return []

        server = FastMCP("test")
        tool(server, list_things, name="t_list")
        t = server._tool_manager._tools["t_list"]
        self.assertIn("List all things in the system.", t.description)

    def test_description_override(self) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        def list_things(client: Client) -> list[dict]:
            """Original docstring."""
            return []

        server = FastMCP("test")
        tool(
            server,
            list_things,
            name="t_list2",
            description="Overridden.",
        )
        t = server._tool_manager._tools["t_list2"]
        self.assertIn("Overridden.", t.description)

    @patch("nextmv.cli.mcp.framework.tool._get_client")
    def test_tool_invocation_forwards_args_and_returns_result(
        self, mock_get_client
    ) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        mock_client = MagicMock(spec=Client)
        mock_get_client.return_value = mock_client
        captured: dict = {}

        def create_thing(client: Client, name: _NameOpt = None) -> dict:
            """Create a thing."""
            captured["client"] = client
            captured["name"] = name
            return {"name": name}

        server = FastMCP("test")
        tool(server, create_thing, name="t_create")

        t = server._tool_manager._tools["t_create"]
        result = t.fn(name="hello")
        self.assertEqual(result, {"name": "hello"})
        self.assertIs(captured["client"], mock_client)
        self.assertEqual(captured["name"], "hello")

    @patch("nextmv.cli.mcp.framework.tool._get_client")
    def test_normalize_empty_converts_empty_strings_to_none(
        self, mock_get_client
    ) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        mock_get_client.return_value = MagicMock(spec=Client)
        captured: dict = {}

        def create_thing(
            client: Client,
            name: _NameOpt = None,
            description: _NameOpt = None,
        ) -> dict:
            """Create."""
            captured["name"] = name
            captured["description"] = description
            return {}

        server = FastMCP("test")
        tool(
            server,
            create_thing,
            name="t_create2",
            normalize_empty=["name", "description"],
        )
        t = server._tool_manager._tools["t_create2"]
        t.fn(name="", description="  ")
        self.assertIsNone(captured["name"])
        self.assertIsNone(captured["description"])

    @patch("nextmv.cli.mcp.framework.tool._get_client")
    def test_result_message_string_template(self, mock_get_client) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        mock_get_client.return_value = MagicMock(spec=Client)

        def delete_thing(client: Client, app_id: str) -> None:
            """Delete."""

        server = FastMCP("test")
        tool(
            server,
            delete_thing,
            name="t_delete",
            result_message="Deleted {app_id}",
        )
        t = server._tool_manager._tools["t_delete"]
        result = t.fn(app_id="foo")
        self.assertEqual(result, "Deleted foo")

    @patch("nextmv.cli.mcp.framework.tool._get_client")
    def test_result_message_callable(self, mock_get_client) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        mock_get_client.return_value = MagicMock(spec=Client)

        def push_thing(client: Client, app_id: str, app_dir: str) -> None:
            """Push."""

        server = FastMCP("test")
        tool(
            server,
            push_thing,
            name="t_push",
            result_message=lambda result, kwargs: (
                f"Pushed {kwargs['app_dir']} to {kwargs['app_id']}"
            ),
        )
        t = server._tool_manager._tools["t_push"]
        result = t.fn(app_id="foo", app_dir="/p")
        self.assertEqual(result, "Pushed /p to foo")


if __name__ == "__main__":
    unittest.main()
