"""
This module defines the community clone command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_client
from nextmv.cli.message import error
from nextmv.cli.options import ProfileOption
from nextmv.cloud.community import clone_community_app

# Set up subcommand application.
app = typer.Typer()

# Helpful constants.
LATEST_VERSION = "latest"


@app.command()
def clone(
    app: Annotated[
        str,
        typer.Option("--app", "-a", help="The name of the community app to clone.", metavar="COMMUNITY_APP"),
    ],
    directory: Annotated[
        str | None,
        typer.Option(
            "--directory",
            "-d",
            help="The directory in which to clone the app. Default is the name of the app at current directory.",
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
    profile: ProfileOption = None,
) -> None:
    """
    Clone a community app locally.

    By default, the [magenta]latest[/magenta] version will be used. You can
    specify a version with the --version flag, and customize the output
    directory with the --directory flag. If you want to list the available
    apps, use the [code]nextmv community list[/code] command.

    [bold][underline]Examples[/underline][/bold]

    - Clone the [magenta]go-nextroute[/magenta] community app (under the
      [magenta]"go-nextroute"[/magenta] directory), using the [magenta]latest[/magenta] version.
        $ [dim]nextmv community clone --app go-nextroute[/dim]

    - Clone the [magenta]go-nextroute[/magenta] community app under the
      [magenta]"~/sample/my_app"[/magenta] directory, using the [magenta]latest[/magenta] version.
        $ [dim]nextmv community clone --app go-nextroute --directory ~/sample/my_app[/dim]

    - Clone the [magenta]go-nextroute[/magenta] community app (under the
      [magenta]"go-nextroute"[/magenta] directory), using version [magenta]v1.2.0[/magenta].
        $ [dim]nextmv community clone --app go-nextroute --version v1.2.0[/dim]

    - Clone the [magenta]go-nextroute[/magenta] community app (under the
      [magenta]"go-nextroute"[/magenta] directory), using the [magenta]latest[/magenta] version
      and a profile named [magenta]hare[/magenta].
        $ [dim]nextmv community clone --app go-nextroute --profile hare[/dim]
    """

    if version is not None and version == "":
        error("The --version flag cannot be an empty string.")

    client = build_client(profile)
    clone_community_app(
        client=client,
        app=app,
        directory=directory,
        version=version,
        verbose=True,
        rich_print=True,
    )
