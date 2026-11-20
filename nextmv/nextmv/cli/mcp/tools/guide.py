"""MCP tool that returns the DecisionOps workflow guide."""

import os

from mcp.server.mcpserver import MCPServer

_WORKFLOW_FILE = os.path.join(os.path.dirname(__file__), "WORKFLOW.md")


def register(mcp: MCPServer) -> None:
    """Register the DecisionOps workflow guide tool."""

    @mcp.tool()
    def decisionops_workflow_guide() -> str:
        """Get the DecisionOps workflow for creating and deploying apps.

        Returns the full DecisionOps workflow guide covering app structure,
        manifest configuration, connecting existing models, entry point
        patterns, visualizations, local testing, deployment to FICO Platform
        DecisionOps, and experiment workflows.

        Call this tool before starting any new app or deployment.
        """

        with open(_WORKFLOW_FILE) as f:
            return f.read()
