"""MCP tool that returns the Nextmv app development workflow guide."""

import os

from mcp.server.fastmcp import FastMCP

_WORKFLOW_FILE = os.path.join(os.path.dirname(__file__), "WORKFLOW.md")


def register(mcp: FastMCP) -> None:
    """Register the workflow guide tool."""

    @mcp.tool()
    def nextmv_workflow_guide() -> str:
        """Get the step-by-step workflow for creating and deploying Nextmv apps.

        Returns the full development guide covering app structure,
        manifest configuration, main.py patterns, visualizations,
        local testing, Cloud deployment, and experiment workflows.

        Call this tool before starting any new app or deployment.
        """

        with open(_WORKFLOW_FILE) as f:
            return f.read()
