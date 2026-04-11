"""Core community app actions.

Pure functions that wrap SDK calls. No CLI or MCP presentation concerns.

Community apps are pre-built decision models maintained in the
nextmv-io/community-apps GitHub repository.
"""

from typing import Any

from nextmv.cloud import Client, clone_community_app, list_community_apps
from nextmv.cloud.community import CommunityApp


def get_community_apps(client: Client) -> list[CommunityApp]:
    """Return the list of available community app objects.

    Returns a list of ``CommunityApp`` instances with rich metadata
    (name, app type, latest version, description, all versions).
    This action is intended for CLI use where the objects are rendered
    directly into Rich tables. MCP callers should use
    ``list_community_apps_dicts`` instead.
    """
    return list_community_apps(client)


def list_community_apps_dicts(client: Client) -> list[dict[str, Any]]:
    """List all available Nextmv community apps as dicts.

    Each dict includes the app name, description, and supported
    language/app type.
    """
    return [a.to_dict() for a in list_community_apps(client)]


def clone_app(
    client: Client,
    app: str,
    directory: str | None = None,
    version: str | None = "latest",
    verbose: bool = False,
    rich_print: bool = False,
    should_register: bool = False,
) -> None:
    """Clone a Nextmv community app to a local directory.

    Downloads the community app source code to the target directory and
    optionally registers it locally so it can be run via
    ``nextmv local run``. By default the ``latest`` version is used.
    """
    clone_community_app(
        client=client,
        app=app,
        directory=directory,
        version=version,
        verbose=verbose,
        rich_print=rich_print,
        should_register=should_register,
    )
