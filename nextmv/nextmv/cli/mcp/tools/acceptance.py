"""MCP tools for cloud acceptance tests."""

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.acceptance import (
    create_acceptance_test,
    delete_acceptance_test,
    get_acceptance_test,
    list_acceptance_tests,
    update_acceptance_test,
)
from nextmv.cli.mcp import framework as mcp_fw
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud acceptance test tools."""

    mcp_fw.tool(mcp, list_acceptance_tests, name="cloud_list_acceptance_tests")

    @mcp.tool()
    def cloud_get_acceptance_test(
        app_id: str,
        acceptance_test_id: str,
    ) -> str:
        """Get details and results of an acceptance test.

        Saves the full test data (including metric comparisons and
        pass/fail results) to a local experiment cache file. Use file-
        reading tools to inspect the contents.
        """

        client = mcp_fw.client()
        data = get_acceptance_test(
            client, app_id=app_id, acceptance_test_id=acceptance_test_id
        )
        endpoint = _helpers._endpoint_from_client(client)
        return _helpers._save_experiment_file(
            data, endpoint, "acceptance", acceptance_test_id
        )

    mcp_fw.tool(
        mcp,
        create_acceptance_test,
        name="cloud_create_acceptance_test",
        normalize_empty=[
            "acceptance_test_id",
            "name",
            "input_set_id",
            "description",
        ],
    )

    mcp_fw.tool(
        mcp,
        update_acceptance_test,
        name="cloud_update_acceptance_test",
        normalize_empty=["name", "description"],
    )

    mcp_fw.tool(
        mcp,
        delete_acceptance_test,
        name="cloud_delete_acceptance_test",
        result_message="Deleted acceptance test {acceptance_test_id}",
    )
