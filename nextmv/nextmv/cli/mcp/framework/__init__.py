"""Helpers for registering MCP tools from pure action functions.

This package is the MCP-side half of the shared-connectors framework. It
pairs with ``nextmv.cli.framework`` which provides the CLI-side helpers.

Import at call sites as::

    from nextmv.cli.mcp import framework as mcp_fw

``mcp_fw.tool()`` registers a FastMCP tool wrapping a pure action function.
``mcp_fw.client()`` returns the current session client (re-export of
``nextmv.cli.mcp.tools._helpers._get_client``).
``mcp_fw.clean()`` normalizes a possibly-empty string to ``None`` (re-export
of ``nextmv.cli.mcp.tools._helpers._none_if_empty``).

The alias ``mcp_fw`` avoids shadowing the top-level ``mcp`` package from the
MCP Python SDK.

See ``docs/superpowers/specs/2026-04-10-mcp-cli-shared-connectors-design.md``
for the full design.
"""

from nextmv.cli.mcp.framework.tool import tool
from nextmv.cli.mcp.tools._helpers import _get_client as client
from nextmv.cli.mcp.tools._helpers import _none_if_empty as clean

__all__ = ["tool", "client", "clean"]
