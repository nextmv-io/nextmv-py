"""
This module defines the cloud instance update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import error, print_json, success
from nextmv.cli.options import AppIDOption, InstanceIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def update(
    app_id: AppIDOption,
    instance_id: InstanceIDOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="A new description for the instance.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="A new name for the instance.",
            metavar="NAME",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated instance information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    version_id: Annotated[
        str | None,
        typer.Option(
            "--version-id",
            "-v",
            help="Update the instance to use a different version.",
            metavar="VERSION_ID",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Updates a Nextmv Cloud application instance.

    [bold][underline]Examples[/underline][/bold]

    - Update an instance's name.
        $ [green]nextmv cloud instance update --app-id hare-app --instance-id prod --name "Production Instance"[/green]

    - Update an instance's description.
        $ [green]nextmv cloud instance update --app-id hare-app --instance-id prod \\
            --description "Instance for production routing jobs"[/green]

    - Update an instance to use a different version.
        $ [green]nextmv cloud instance update --app-id hare-app --instance-id prod --version-id v2[/green]

    - Update an instance's name and description at once.
        $ [green]nextmv cloud instance update --app-id hare-app --instance-id prod \\
            --name "Production Instance" --description "Instance for production routing jobs"[/green]

    - Update an instance and save the updated information to a [magenta]updated_instance.json[/magenta] file.
        $ [green]nextmv cloud instance update --app-id hare-app --instance-id prod \\
            --name "Production Instance" --output updated_instance.json[/green]
    """

    if name is None and description is None and version_id is None:
        error(
            "Provide at least one option to update: [code]--name[/code], [code]--description[/code], "
            "or [code]--version-id[/code]."
        )

    cloud_app = build_app(app_id=app_id, profile=profile)
    updated_instance = cloud_app.update_instance(
        id=instance_id,
        name=name,
        description=description,
        version_id=version_id,
    )
    success(
        f"Instance [magenta]{instance_id}[/magenta] updated successfully in application [magenta]{app_id}[/magenta]."
    )
    updated_instance_dict = updated_instance.to_dict()

    if output is not None:
        with open(output, "w") as f:
            json.dump(updated_instance_dict, f, indent=2)

        success(msg=f"Updated instance information saved to [magenta]{output}[/magenta].")

        return

    print_json(updated_instance_dict)
