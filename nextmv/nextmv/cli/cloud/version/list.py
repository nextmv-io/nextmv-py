"""
This module defines the cloud version list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def list(
    app_id: AppIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the version list information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    List all versions of a Nextmv Cloud application.

    [bold][underline]Examples[/underline][/bold]

    - List all versions of application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud version list --app-id hare-app[/dim]

    - List all versions using the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud version list --app-id hare-app --profile hare[/dim]

    - List all versions and save the information to a [magenta]versions.json[/magenta] file.
        $ [dim]nextmv cloud version list --app-id hare-app --output versions.json[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Listing versions...")
    versions = cloud_app.list_versions()
    versions_dicts = [version.to_dict() for version in versions]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(versions_dicts, f, indent=2)

        success(msg=f"Version list information saved to [magenta]{output}[/magenta].")

        return

    print_json(versions_dicts)
