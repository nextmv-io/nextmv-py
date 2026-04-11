"""MCP tools for community apps."""

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.community import clone_app, list_community_apps_dicts
from nextmv.cli.mcp import framework as mcp_fw


def register(mcp: FastMCP) -> None:
    """Register community app tools."""

    mcp_fw.tool(mcp, list_community_apps_dicts, name="community_list")

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

        clone_app(client=mcp_fw.client(), app=app_name, directory=target_dir)
        return f"Cloned {app_name} to {target_dir}"
