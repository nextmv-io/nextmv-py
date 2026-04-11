"""CLI-only workflows for the community domain.

The ``list`` command renders Rich tables (not JSON) and supports a
``--flat`` mode for scripting use. The ``clone`` command passes several
CLI-specific flags through to the SDK (verbose, rich_print, and an
implicit ``should_register=True``).
"""

from typing import Annotated

import rich
import typer
from rich.console import Console
from rich.table import Table

from nextmv.cli.actions.community import clone_app, get_community_apps
from nextmv.cli.message import error
from nextmv.cloud.client import Client
from nextmv.cloud.community import CommunityApp

LATEST_VERSION = "latest"
_console = Console()


def run_list_community_apps(
    client: Client,
    app: Annotated[
        str | None,
        typer.Option(
            "--app",
            "-a",
            help="The community app to list versions for.",
            metavar="COMMUNITY_APP",
        ),
    ] = None,
    flat: Annotated[
        bool,
        typer.Option("--flat", "-f", help="Flatten the list output."),
    ] = False,
) -> None:
    """List the available community apps.

    Use the ``--app`` flag to list a specific app's versions. Use the
    ``--flat`` flag to flatten the list of names/versions into a plain
    newline-delimited stream suitable for scripting.

    To clone a community app locally, use ``nextmv community clone``.
    """

    if app is not None and app == "":
        error("The --app flag cannot be an empty string.")

    if flat and app is None:
        _apps_list(client)
        raise typer.Exit()
    if not flat and app is None:
        _apps_table(client)
        raise typer.Exit()
    if flat and app is not None:
        _versions_list(client, app)
        raise typer.Exit()
    _versions_table(client, app)
    raise typer.Exit()


def run_clone_community_app(
    client: Client,
    app: Annotated[
        str,
        typer.Option(
            "--app",
            "-a",
            help="The name of the community app to clone.",
            metavar="COMMUNITY_APP",
        ),
    ],
    directory: Annotated[
        str | None,
        typer.Option(
            "--directory",
            "-d",
            help=(
                "The directory in which to clone the app. Default is the "
                "name of the app at current directory."
            ),
            metavar="DIRECTORY",
        ),
    ] = None,
    version: Annotated[
        str | None,
        typer.Option(
            "--version",
            "-v",
            help="The version of the community app to clone.",
            metavar="VERSION",
        ),
    ] = LATEST_VERSION,
) -> None:
    """Clone a community app locally.

    By default the ``latest`` version is cloned. You can specify a
    version with ``--version`` and customize the output directory with
    ``--directory``. Use ``nextmv community list`` to discover available
    apps.

    When an app is cloned, it is automatically registered locally so you
    can run it with ``nextmv local run`` using the generated app ID.
    """

    if version is not None and version == "":
        error("The --version flag cannot be an empty string.")

    clone_app(
        client=client,
        app=app,
        directory=directory,
        version=version,
        verbose=True,
        rich_print=True,
        should_register=True,
    )


def _apps_table(client: Client) -> None:
    """Print a table of community apps."""
    apps = get_community_apps(client)
    table = Table(
        "Name",
        "Type",
        "Latest",
        "Description",
        border_style="cyan",
        header_style="cyan",
    )
    for a in apps:
        table.add_row(
            a.name,
            a.app_type,
            a.latest_app_version if a.latest_app_version is not None else "",
            a.description,
        )
    _console.print(table)


def _apps_list(client: Client) -> None:
    """Print a flat list of community app names."""
    apps = get_community_apps(client)
    print("\n".join(a.name for a in apps))


def _versions_table(client: Client, app: str) -> None:
    """Print a table of versions for a specific community app."""
    comm_app = _find_app(client, app)
    latest_version = comm_app.latest_app_version if comm_app.latest_app_version is not None else ""

    table = Table("Version", "Latest?", border_style="cyan", header_style="cyan")
    table.add_row(f"[cyan underline]{latest_version}[/cyan underline]", "[cyan]<--[/cyan]")
    table.add_row("", "")

    versions = comm_app.app_versions if comm_app.app_versions is not None else []
    for version in versions:
        if version != latest_version:
            table.add_row(version, "")
    _console.print(table)


def _versions_list(client: Client, app: str) -> None:
    """Print a flat list of versions for a specific community app."""
    comm_app = _find_app(client, app)
    versions = comm_app.app_versions if comm_app.app_versions is not None else []
    print("\n".join(versions))


def _find_app(client: Client, app: str) -> CommunityApp:
    """Find a community app by name, or exit 1 after printing available apps."""
    comm_apps = get_community_apps(client)
    for comm_app in comm_apps:
        if comm_app.name == app:
            return comm_app

    rich.print(
        f"[red]Error:[/red] Community app [magenta]{app}[/magenta] was not found. "
        "Here are the available apps:"
    )
    _apps_table(client)
    raise typer.Exit(code=1)
