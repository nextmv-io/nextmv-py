"""MCP tools for community apps."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.mcp.tools import _helpers
from nextmv.cloud import clone_community_app, list_community_apps


def register(mcp: FastMCP) -> None:
    """Register community app tools."""

    @mcp.tool()
    def community_list() -> list[dict[str, Any]]:
        """List all available Nextmv community apps.

        Community apps are pre-built decision models for common
        optimization problems like vehicle routing, knapsack, shift
        scheduling, and more. Each entry includes the app name,
        description, and supported languages.
        """

        client = _helpers._get_client()
        apps = list_community_apps(client)
        return [a.to_dict() for a in apps]

    @mcp.tool()
    def community_clone(app_name: str, target_dir: str = ".") -> str:
        """Clone a Nextmv community app to a local directory.

        Downloads the community app source code into the target
        directory. The app is ready to run locally after cloning.

        Args:
            app_name: Name of the community app, e.g.
                ``"python-ortools-routing"``. Use ``community_list``
                to see available apps.
            target_dir: Directory to clone into. Defaults to the
                current working directory.
        """

        client = _helpers._get_client()
        clone_community_app(client=client, app=app_name, directory=target_dir)
        return f"Cloned {app_name} to {target_dir}"
