"""
This module defines the cloud version update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import error, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption, VersionIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def update(
    app_id: AppIDOption,
    version_id: VersionIDOption,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="A new name for the version.",
            metavar="NAME",
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="A new description for the version.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated version information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Updates a Nextmv Cloud application version.

    [bold][underline]Examples[/underline][/bold]

    - Update a version's name.
        $ [green]nextmv cloud version update --app-id hare-app --version-id v1 --name "Version 1.0"[/green]

    - Update a version's description.
        $ [green]nextmv cloud version update --app-id hare-app --version-id v1 \\
            --description "Initial stable release"[/green]

    - Update a version's name and description at once.
        $ [green]nextmv cloud version update --app-id hare-app --version-id v1 \\
            --name "Version 1.0" --description "Initial stable release"[/green]

    - Update a version and save the updated information to a [magenta]updated_version.json[/magenta] file.
        $ [green]nextmv cloud version update --app-id hare-app --version-id v1 \\
            --name "Version 1.0" --output updated_version.json[/green]
    """

    if name is None and description is None:
        error("Provide at least one option to update: [code]--name[/code] or [code]--description[/code].")

    cloud_app = build_app(app_id=app_id, profile=profile)
    updated_version = cloud_app.update_version(
        version_id=version_id,
        name=name,
        description=description,
    )
    success(f"Version [magenta]{version_id}[/magenta] updated successfully in application [magenta]{app_id}[/magenta].")
    updated_version_dict = updated_version.to_dict()

    if output is not None:
        with open(output, "w") as f:
            json.dump(updated_version_dict, f, indent=2)

        success(msg=f"Updated version information saved to [magenta]{output}[/magenta].")

        return

    print_json(updated_version_dict)
