"""MCP server command for the Nextmv CLI."""

from typing import Annotated

import typer

from nextmv.cli.mcp.server import create_server
from nextmv.cli.message import error

# Set up subcommand application.
app = typer.Typer()


@app.command()
def serve(
    port: Annotated[
        int,
        typer.Option(
            "--port",
            help="Port for the HTTP transport.",
            metavar="PORT",
        ),
    ] = 8080,
    transport: Annotated[
        str,
        typer.Option(
            "--transport",
            "-t",
            help="Transport protocol. "
            "Allowed values: [magenta]stdio[/magenta], [magenta]streamable-http[/magenta].",
            metavar="TRANSPORT",
        ),
    ] = "stdio",
) -> None:
    """
    Start the Nextmv MCP server.

    The MCP server exposes Nextmv Cloud functionality as tools that any
    MCP-compatible client can use. The default transport is
    [magenta]stdio[/magenta], which is what Claude Code, Cursor, and most
    local clients expect.

    [bold][underline]Examples[/underline][/bold]

    - Start the MCP server with stdio transport (default).
        $ [dim]nextmv mcp serve[/dim]

    - Start the MCP server with HTTP transport on port 9090.
        $ [dim]nextmv mcp serve --transport streamable-http --port 9090[/dim]

    - Register with Claude Code.
        $ [dim]claude mcp add nextmv -- nextmv mcp serve[/dim]
    """

    server = create_server()

    if transport == "stdio":
        server.run(transport="stdio")
    elif transport in ("http", "streamable-http"):
        server.run(transport="streamable-http", port=port)
    else:
        error(
            f"Unknown transport [magenta]{transport}[/magenta]. "
            "Allowed values are: [magenta]stdio[/magenta], [magenta]streamable-http[/magenta]."
        )
