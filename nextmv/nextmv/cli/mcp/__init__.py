"""MCP (Model Context Protocol) server for the Nextmv CLI."""

import typer

from nextmv.cli.mcp.serve import app as serve_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(serve_app)


@app.callback()
def callback() -> None:
    """
    Model Context Protocol (MCP) server for LLM integrations.

    Start an MCP server so that any MCP-compatible client (Claude Code,
    Cursor, VS Code, etc.) can interact with Nextmv Cloud through natural
    language.

    [bold][underline]Quick start[/underline][/bold]

    - Register with Claude Code.
        $ [dim]claude mcp add nextmv -- nextmv mcp serve[/dim]
    """
    pass
