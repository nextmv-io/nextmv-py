"""Nextmv MCP server definition.

This module is the public entry point for the MCP server. It delegates
tool registration to domain-specific submodules under ``tools/`` and
re-exports shared helpers so that existing imports continue to work.
"""

from mcp.server.fastmcp import FastMCP

# Import tool registration submodules.
from nextmv.cli.mcp.tools import (
    acceptance,
    account,
    app,
    batch,
    community,
    ensemble,
    input_set,
    instance,
    local,
    managed_input,
    profile,
    run,
    scenario,
    secrets,
    shadow,
    sso,
    switchback,
    version,
)

# Re-export helpers for backward compatibility — tests and external code
# may import these directly from ``nextmv.cli.mcp.server``.
from nextmv.cli.mcp.tools._helpers import (  # noqa: F401
    _current_profile,
    _get_app,
    _get_client,
    _get_local_app,
    _mask_key,
    _save_to_file,
)

# Re-export SDK names that tests patch on this module.
from nextmv.cloud import list_applications  # noqa: F401


def create_server() -> FastMCP:
    """Create and return the Nextmv MCP server."""

    mcp = FastMCP(
        "nextmv",
        json_response=True,
        instructions=(
            "Nextmv is a platform for deploying and managing decision "
            "models (optimization, routing, scheduling, etc.). Use these "
            "tools to interact with Nextmv Cloud apps: list apps, submit "
            "runs, check results, manage versions/instances, run experiments, "
            "and work with local applications.\n\n"
            "IMPORTANT: Always use these MCP tools instead of shelling out "
            "to the `nextmv` CLI binary. Large responses (run results, "
            "inputs, logs) are automatically saved to local temp files to "
            "keep the context window small — the tool will return the file "
            "path so you can selectively read what you need. Large inputs "
            "can be passed directly as tool parameters without concern.\n\n"
            "PROFILES: The server supports multiple profiles from "
            "~/.nextmv/config.yaml. Use cloud_list_profiles to see "
            "available profiles and cloud_set_profile to switch. The "
            "default profile is used unless changed. When the user asks "
            "to use a specific profile (e.g. \"list apps in my dev "
            "profile\"), call cloud_set_profile first. Always state which "
            "profile you are using when calling cloud tools, e.g. "
            "(profile: \"default\").\n\n"
            "CLOUD RUN CACHE: Cloud run data (results, inputs, logs) is "
            "cached locally at ~/.nextmv/runs/{endpoint}/{run_id}/ using "
            "the same directory layout as local runs. The {endpoint} is the "
            "API endpoint (e.g. api.cloud.nextmv.io). If a file already "
            "exists there, it will not be re-downloaded. You can read "
            "cached cloud run data directly from these paths without "
            "calling the cloud tools again."
        ),
    )

    # Cloud tools
    profile.register(mcp)
    app.register(mcp)
    run.register(mcp)
    version.register(mcp)
    instance.register(mcp)
    batch.register(mcp)
    input_set.register(mcp)
    acceptance.register(mcp)
    scenario.register(mcp)
    ensemble.register(mcp)
    shadow.register(mcp)
    switchback.register(mcp)
    secrets.register(mcp)
    sso.register(mcp)
    account.register(mcp)
    managed_input.register(mcp)

    # Community tools
    community.register(mcp)

    # Local tools
    local.register(mcp)

    return mcp
