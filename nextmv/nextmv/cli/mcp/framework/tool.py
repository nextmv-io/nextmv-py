"""``mcp_fw.tool()`` builder.

Given a pure action function under ``nextmv.cli.actions``, generates a
FastMCP tool wrapper whose signature mirrors the action's (minus the
``client`` parameter; MCP uses session-scoped client injection instead of a
per-call ``--profile`` flag). The wrapper reads metadata from the action's
``Annotated`` parameters so the same aliases drive both CLI and MCP tool
registration.

See ``docs/superpowers/specs/2026-04-10-mcp-cli-shared-connectors-design.md``
for the full design.
"""


def tool(*args, **kwargs):  # pragma: no cover - replaced in Task 8
    """Stub — real implementation in Task 8."""
    raise NotImplementedError("mcp_fw.tool() not yet implemented")
