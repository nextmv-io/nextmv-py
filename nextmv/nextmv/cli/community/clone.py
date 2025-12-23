"""
This module defines the community clone command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.options import ProfileOption

# Set up subcommand application.
app = typer.Typer()


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
    ] = "latest",
    profile: ProfileOption = None,
) -> None:
    """
    Clone a community app locally.

    By default, the [magenta]latest[/magenta] version will be used. You can
    specify a version with the [code]--version[/code] flag, and customize the
    output directory with the [code]--directory[/code] flag. If you want to
    list the available apps, use the [code]nextmv community list[/code] command.

    [bold][underline]Examples[/underline][/bold]

    - Clone the [magenta]go-nextroute[/magenta] community app (under the
      [magenta]"go-nextroute"[/magenta] directory), using the [magenta]latest[/magenta] version.
        [green]nextmv community clone --app go-nextroute[/green]

    - Clone the [magenta]go-nextroute[/magenta] community app under the
      [magenta]"~/sample/my_app"[/magenta] directory, using the [magenta]latest[/magenta] version.
        [green]nextmv community clone --app go-nextroute --directory ~/sample/my_app[/green]

    - Clone the [magenta]go-nextroute[/magenta] community app (under the
      [magenta]"go-nextroute"[/magenta] directory), using version [magenta]v1.2.0[/magenta].
        [green]nextmv community clone --app go-nextroute --version v1.2.0[/green]
    """
