"""
This module defines the cloud version get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption, VersionIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    app_id: AppIDOption,
    version_id: VersionIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the version information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get a Nextmv Cloud application version.

    This command is useful to get the attributes of an existing Nextmv Cloud
    application version by its ID.

    [bold][underline]Examples[/underline][/bold]

    - Get the version with the ID [magenta]v1[/magenta] from application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud version get --app-id hare-app --version-id v1[/dim]

    - Get the version with the ID [magenta]v1[/magenta] and save the information to a
      [magenta]version.json[/magenta] file.
        $ [dim]nextmv cloud version get --app-id hare-app --version-id v1 --output version.json[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Getting version...")
    version = cloud_app.version(version_id=version_id)
    version_dict = version.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(version_dict, f, indent=2)

        success(msg=f"Version information saved to [magenta]{output}[/magenta].")

        return

    print_json(version_dict)
