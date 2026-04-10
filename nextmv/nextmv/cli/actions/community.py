"""Core community app actions."""

from typing import Any

from nextmv.cloud import Client, clone_community_app, list_community_apps
from nextmv.cloud.community import CommunityApp


def get_community_apps(client: Client) -> list[CommunityApp]:
    """Return the list of available community app objects."""
    return list_community_apps(client)


def list_community_apps_dicts(client: Client) -> list[dict[str, Any]]:
    """List all available community apps as dicts."""
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
    """Clone a community app to a local directory."""
    clone_community_app(
        client=client,
        app=app,
        directory=directory,
        version=version,
        verbose=verbose,
        rich_print=rich_print,
        should_register=should_register,
    )
