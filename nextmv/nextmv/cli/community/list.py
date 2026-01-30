"""
This module defines the community list command for the Nextmv CLI.
"""

from typing import Annotated

import rich
import typer
from rich.console import Console
from rich.table import Table

from nextmv.cli.configuration.config import build_client
from nextmv.cli.message import error
from nextmv.cli.options import ProfileOption
from nextmv.cloud.client import Client
from nextmv.cloud.community import CommunityApp, list_community_apps

# Set up subcommand application.
app = typer.Typer()
console = Console()


@app.command()
def list(
    app: Annotated[
        str | None,
        typer.Option(
            "--app",
            "-a",
            help="The community app to list versions for.",
            metavar="COMMUNITY_APP",
        ),
    ] = None,
    flat: Annotated[bool, typer.Option("--flat", "-f", help="Flatten the list output.")] = False,
    profile: ProfileOption = None,
) -> None:
    """
    List the available community apps

    Use the --app flag to list that app's versions. Use the --flat flag to
    flatten the list of names/versions. If you want to clone a community app
    locally, use the [code]nextmv community clone[/code] command.

    [bold][underline]Examples[/underline][/bold]

    - List the available community apps.
        $ [dim]nextmv community list[/dim]

    - List the available versions of the [magenta]go-nextroute[/magenta] community app.
        $ [dim]nextmv community list --app go-nextroute[/dim]

    - List the names of the available community apps as a flat list.
        $ [dim]nextmv community list --flat[/dim]

    - List the available versions of the [magenta]go-nextroute[/magenta] community app as a flat list.
        $ [dim]nextmv community list --app go-nextroute --flat[/dim]

    - List the available community apps using a profile named [magenta]hare[/magenta].
        $ [dim]nextmv community list --profile hare[/dim]
    """

    if app is not None and app == "":
        error("The --app flag cannot be an empty string.")

    client = build_client(profile)
    if flat and app is None:
        _apps_list(client)
        raise typer.Exit()
    elif not flat and app is None:
        _apps_table(client)
        raise typer.Exit()
    elif flat and app is not None and app != "":
        _versions_list(client, app)
        raise typer.Exit()
    elif not flat and app is not None and app != "":
        _versions_table(client, app)
        raise typer.Exit()


def _apps_table(client: Client) -> None:
    """
    This function prints a table of community apps.

    Parameters
    ----------
    client : Client
        The Nextmv Cloud client to use for the request.
    """

    apps = list_community_apps(client)
    table = Table("Name", "Type", "Latest", "Description", border_style="cyan", header_style="cyan")
    for app in apps:
        table.add_row(
            app.name,
            app.app_type,
            app.latest_app_version if app.latest_app_version is not None else "",
            app.description,
        )

    console.print(table)


def _apps_list(client: Client) -> None:
    """
    This function prints a flat list of community app names.

    Parameters
    ----------
    client : Client
        The Nextmv Cloud client to use for the request.
    """

    apps = list_community_apps(client)
    names = [app.name for app in apps]
    print("\n".join(names))


def _versions_table(client: Client, app: str) -> None:
    """
    This function prints a table of versions for a specific community app.

    Parameters
    ----------
    client : Client
        The Nextmv Cloud client to use for the request.
    app : str
        The name of the community app.
    """

    comm_app = _find_app(client, app)
    latest_version = comm_app.latest_app_version if comm_app.latest_app_version is not None else ""

    # Add the latest version with indicator
    table = Table("Version", "Latest?", border_style="cyan", header_style="cyan")
    table.add_row(f"[cyan underline]{latest_version}[/cyan underline]", "[cyan]<--[/cyan]")
    table.add_row("", "")  # Empty row to separate latest from others.

    # Add all other versions (excluding the latest)
    versions = comm_app.app_versions if comm_app.app_versions is not None else []
    for version in versions:
        if version != latest_version:
            table.add_row(version, "")

    console.print(table)


def _versions_list(client: Client, app: str) -> None:
    """
    This function prints a flat list of versions for a specific community app.

    Parameters
    ----------
    client : Client
        The Nextmv Cloud client to use for the request.
    app : str
        The name of the community app.
    """

    comm_app = _find_app(client, app)
    versions = comm_app.app_versions if comm_app.app_versions is not None else []

    versions_output = ""
    for version in versions:
        versions_output += f"{version}\n"

    print(versions_output.rstrip("\n"))


def _find_app(client: Client, app: str) -> CommunityApp:
    """
    Finds and returns a community app from the manifest by its name.

    Parameters
    ----------
    client : Client
        The Nextmv Cloud client to use for the request.
    app : str
        The name of the community app to find.

    Returns
    -------
    CommunityApp
        The community app if found.

    Raises
    ------
    ValueError
        If the community app is not found.
    """

    comm_apps = list_community_apps(client)
    for comm_app in comm_apps:
        if comm_app.name == app:
            return comm_app

    # We don't use error() here to allow printing something before exiting.
    rich.print(f"[red]Error:[/red] Community app [magenta]{app}[/magenta] was not found. Here are the available apps:")
    _apps_table(client)

    raise typer.Exit(code=1)
