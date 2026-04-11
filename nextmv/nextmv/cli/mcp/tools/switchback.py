"""MCP tools for cloud switchback tests."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.switchback import (
    create_switchback_test,
    delete_switchback_test,
    get_switchback_test,
    list_switchback_tests,
    start_switchback_test,
    stop_switchback_test,
    switchback_test_metadata,
    update_switchback_test,
)
from nextmv.cli.mcp import framework as mcp_fw
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud switchback test tools."""

    mcp_fw.tool(mcp, list_switchback_tests, name="cloud_list_switchback_tests")

    @mcp.tool()
    def cloud_get_switchback_test(app_id: str, switchback_test_id: str) -> str:
        """Get details and results of a switchback test.

        Saves the full test data (including per-unit comparison
        results) to ~/.nextmv/experiments/. Use file-reading tools to
        inspect the contents.

        Args:
            app_id: The application ID.
            switchback_test_id: The switchback test ID.
        """

        client = mcp_fw.client()
        data = get_switchback_test(
            client, app_id=app_id, switchback_test_id=switchback_test_id
        )
        endpoint = _helpers._endpoint_from_client(client)
        return _helpers._save_experiment_file(
            data, endpoint, "switchback", switchback_test_id
        )

    @mcp.tool()
    def cloud_switchback_test_metadata(app_id: str, switchback_test_id: str) -> str:
        """Get metadata for a switchback test.

        Returns test-level metadata only — status, unit counts, and
        timing. Saves the result to ~/.nextmv/experiments/. Use
        file-reading tools to inspect the contents.

        Args:
            app_id: The application ID.
            switchback_test_id: The switchback test ID.
        """

        client = mcp_fw.client()
        data = switchback_test_metadata(
            client, app_id=app_id, switchback_test_id=switchback_test_id
        )
        endpoint = _helpers._endpoint_from_client(client)
        return _helpers._save_experiment_file(
            data,
            endpoint,
            "switchback",
            switchback_test_id,
            filename="metadata.json",
        )

    mcp_fw.tool(
        mcp,
        create_switchback_test,
        name="cloud_create_switchback_test",
        normalize_empty=["name", "description"],
    )

    mcp_fw.tool(
        mcp,
        update_switchback_test,
        name="cloud_update_switchback_test",
        normalize_empty=["name", "description"],
    )

    mcp_fw.tool(
        mcp,
        start_switchback_test,
        name="cloud_start_switchback_test",
        result_message="Started switchback test {switchback_test_id}",
    )

    mcp_fw.tool(
        mcp,
        stop_switchback_test,
        name="cloud_stop_switchback_test",
        result_message="Stopped switchback test {switchback_test_id} with intent {intent}",
    )

    mcp_fw.tool(
        mcp,
        delete_switchback_test,
        name="cloud_delete_switchback_test",
        result_message="Deleted switchback test {switchback_test_id}",
    )
