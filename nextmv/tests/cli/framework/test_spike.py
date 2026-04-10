"""Feasibility spike: does Annotated carry both typer.Option and pydantic.Field?

This file is deleted once ``test_options.py`` supersedes it as the permanent
regression guard. Its only purpose is to confirm that a single Annotated alias
can drive both Typer and FastMCP without either library choking on the other's
metadata marker.
"""

import unittest
from typing import Annotated, TypeAlias

import typer
from mcp.server.fastmcp import FastMCP
from pydantic import Field, TypeAdapter
from typer.testing import CliRunner

_HELP = "An optional test value."

TestOption: TypeAlias = Annotated[
    str | None,
    typer.Option("--value", "-v", help=_HELP, metavar="VALUE"),
    Field(description=_HELP),
]


class TestDualPurposeAnnotated(unittest.TestCase):
    def test_typer_consumes_option_metadata(self) -> None:
        app = typer.Typer()

        @app.command()
        def echo(value: TestOption = None) -> None:
            typer.echo(f"value={value}")

        runner = CliRunner()
        result = runner.invoke(app, ["--value", "hello"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("value=hello", result.stdout)

        # Short flag still works
        result = runner.invoke(app, ["-v", "short"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("value=short", result.stdout)

    def test_pydantic_type_adapter_accepts_alias(self) -> None:
        # Pydantic must ignore the typer.OptionInfo and still build a schema
        # that picks up the Field(description=...).
        adapter = TypeAdapter(TestOption)
        schema = adapter.json_schema()
        # The description should come from the Field(...) metadata.
        # The alias is `str | None`, so Pydantic renders it as anyOf.
        self.assertIn("description", schema)
        self.assertEqual(schema["description"], _HELP)

    def test_fastmcp_registers_tool_with_alias(self) -> None:
        server = FastMCP("spike-test")

        @server.tool(name="spike_echo")
        def spike_echo(value: TestOption = None) -> str:
            """Echo the value back."""
            return f"value={value}"

        # Tool is registered and its input schema carries the description.
        tool = server._tool_manager._tools["spike_echo"]
        self.assertIsNotNone(tool)
        schema = tool.parameters
        # FastMCP builds a JSON schema with a `properties` dict keyed by
        # parameter name.
        self.assertIn("value", schema["properties"])
        self.assertEqual(schema["properties"]["value"].get("description"), _HELP)


if __name__ == "__main__":
    unittest.main()
