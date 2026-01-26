"""
This module defines the community list command for the Nextmv CLI.
"""

from typing import Annotated, Any

import requests
import rich
import typer
import yaml
from rich.console import Console
from rich.table import Table

from nextmv.cli.configuration.config import build_client
from nextmv.cli.message import error
from nextmv.cli.options import ProfileOption

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

    manifest = download_manifest(profile=profile)
    if flat and app is None:
        apps_list(manifest)
        raise typer.Exit()
    elif not flat and app is None:
        apps_table(manifest)
        raise typer.Exit()
    elif flat and app is not None and app != "":
        versions_list(manifest, app)
        raise typer.Exit()
    elif not flat and app is not None and app != "":
        versions_table(manifest, app)
        raise typer.Exit()


def download_manifest(profile: str | None = None) -> dict:
    """
    Downloads and returns the community apps manifest.

    Parameters
    ----------
    profile : str | None
        The profile name to use. If None, the default profile is used.

    Returns
    -------
    dict
        The community apps manifest as a dictionary.

    Raises
    requests.HTTPError
        If the response status code is not 2xx.
    """

    response = download_file(directory="community-apps", file="manifest.yml", profile=profile)
    manifest = yaml.safe_load(response.text)

    return manifest


def apps_table(manifest: dict[str, Any]) -> None:
    """
    This function prints a table of community apps from the manifest.

    Parameters
    ----------
    manifest : dict[str, Any]
        The community apps manifest.
    """

    table = Table("Name", "Type", "Latest", "Description", border_style="cyan", header_style="cyan")
    for app in manifest.get("apps", []):
        table.add_row(
            app.get("name", ""),
            app.get("type", ""),
            app.get("latest_app_version", ""),
            app.get("description", ""),
        )

    console.print(table)


def apps_list(manifest: dict[str, Any]) -> None:
    """
    This function prints a flat list of community app names from the manifest.

    Parameters
    ----------
    manifest : dict[str, Any]
        The community apps manifest.
    """

    names = [app.get("name", "") for app in manifest.get("apps", [])]
    print("\n".join(names))


def versions_table(manifest: dict[str, Any], app: str) -> None:
    """
    This function prints a table of versions for a specific community app.

    Parameters
    ----------
    manifest : dict[str, Any]
        The community apps manifest.
    app : str
        The name of the community app.
    """

    app_obj = find_app(manifest, app)
    latest_version = app_obj.get("latest_app_version", "")

    # Add the latest version with indicator
    table = Table("Version", "Latest?", border_style="cyan", header_style="cyan")
    table.add_row(f"[cyan underline]{latest_version}[/cyan underline]", "[cyan]<--[/cyan]")
    table.add_row("", "")  # Empty row to separate latest from others.

    # Add all other versions (excluding the latest)
    versions = app_obj.get("app_versions", [])
    for version in versions:
        if version != latest_version:
            table.add_row(version, "")

    console.print(table)


def versions_list(manifest: dict[str, Any], app: str) -> None:
    """
    This function prints a flat list of versions for a specific community app.

    Parameters
    ----------
    manifest : dict[str, Any]
        The community apps manifest.
    app : str
        The name of the community app.
    """

    app_obj = find_app(manifest, app)
    versions = app_obj.get("app_versions", [])

    versions_output = ""
    for version in versions:
        versions_output += f"{version}\n"

    print("\n".join(app_obj.get("app_versions", [])))


def download_file(
    directory: str,
    file: str,
    profile: str | None = None,
) -> requests.Response:
    """
    Gets a file from an internal bucket and return it.

    Parameters
    ----------
    directory : str
        The directory in the bucket where the file is located.
    file : str
        The name of the file to download.
    profile : str | None
        The profile name to use. If None, the default profile is used.

    Returns
    -------
    requests.Response
        The response object containing the file data.

    Raises
    requests.HTTPError
        If the response status code is not 2xx.
    """

    client = build_client(profile)

    # Request the download URL for the file.
    response = client.request(
        method="GET",
        endpoint="v0/internal/tools",
        headers=client.headers | {"request-source": "cli"},  # Pass `client.headers` to preserve auth.
        query_params={"file": f"{directory}/{file}"},
    )

    # Use the URL obtained to download the file.
    body = response.json()
    download_response = client.request(
        method="GET",
        endpoint=body.get("url"),
        headers={"Content-Type": "application/json"},
    )

    return download_response


def find_app(manifest: dict[str, Any], app: str) -> dict[str, Any] | None:
    """
    Finds and returns a community app from the manifest by its name.

    Parameters
    ----------
    manifest : dict[str, Any]
        The community apps manifest.
    app : str
        The name of the community app to find.

    Returns
    -------
    dict[str, Any] | None
        The community app dictionary if found, otherwise None.
    """

    for manifest_app in manifest.get("apps", []):
        if manifest_app.get("name", "") == app:
            return manifest_app

    # We don't use error() here to allow printing something before exiting.
    rich.print(f"[red]Error:[/red] Community app [magenta]{app}[/magenta] was not found. Here are the available apps:")
    apps_table(manifest)

    raise typer.Exit(code=1)
