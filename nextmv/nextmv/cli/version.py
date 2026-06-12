"""
This module defines the version command for the Nextmv CLI.
"""

import requests
import typer

from nextmv.__about__ import __version__
from nextmv.cli.message import success, warning
from nextmv.cli.options import DebugOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def version(_: DebugOption = False) -> None:
    """
    Show the current version of the Nextmv CLI.

    [bold][underline]Examples[/underline][/bold]

    - Show the version.
        $ [dim]nextmv version[/dim]
    """

    version_callback(True)


def version_callback(value: bool):
    """
    Callback function to display the version.

    Parameters
    ----------
    value : bool
        If True, print the version and exit.
    """

    if value:
        latest, pypi_ver = latest_version()
        if latest:
            success("You are on the [magenta]latest[/magenta] version of the Nextmv CLI!")
        else:
            warning(
                f"Your Nextmv CLI is outdated, the latest version is [magenta]{pypi_ver}[/magenta]. Consider updating!"
            )

        print(__version__)
        raise typer.Exit()


def latest_version() -> tuple[bool | None, str | None]:
    """
    This function checks if the current version of the Nextmv CLI is the latest
    version available on PyPI.

    Returns
    -------
    tuple[bool | None, str | None]
        A tuple containing a boolean indicating if the current version is the
        latest and a string with the latest version number. If there was an
        error during the check, both values will be None.
    """

    try:
        response = requests.get("https://pypi.org/pypi/nextmv/json")
    except requests.RequestException:
        return None, None

    try:
        response.raise_for_status()
    except requests.HTTPError:
        return None, None

    if response.status_code != 200:
        return None, None

    pypi_ver = response.json().get("info", {}).get("version")
    if pypi_ver is None:
        return None, None

    pypi_ver = f"v{pypi_ver}" if not pypi_ver.startswith("v") else pypi_ver

    latest = __version__ == pypi_ver
    return latest, pypi_ver
