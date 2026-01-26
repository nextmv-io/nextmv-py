"""
This module defines the cloud app update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import error, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def update(
    app_id: AppIDOption,
    default_experiment_instance: Annotated[
        str | None,
        typer.Option(
            "--default-experiment-instance",
            "-x",
            help="A new default experiment instance ID for the application.",
            metavar="DEFAULT_EXPERIMENT_INSTANCE",
        ),
    ] = None,
    default_instance_id: Annotated[
        str | None,
        typer.Option(
            "--default-instance-id",
            "-i",
            help="A new default instance ID for the application.",
            metavar="DEFAULT_INSTANCE_ID",
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="A new description for the application.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="A new name for the application.",
            metavar="NAME",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated app information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Updates a Nextmv Cloud application.

    Please note that you cannot change the type of an application, you must
    create a new one.

    [bold][underline]Examples[/underline][/bold]

    - Update an application's name.
        $ [dim]nextmv cloud app update --app-id hare-app --name "New Hare App"[/dim]

    - Update an application's description.
        $ [dim]nextmv cloud app update --app-id hare-app --name "Hare App" \\
            --description "An updated description for routing hares"[/dim]

    - Update an application's default instance ID.
        $ [dim]nextmv cloud app update --app-id hare-app --name "Hare App" \\
            --default-instance-id burrow[/dim]

    - Update an application's default experiment instance.
        $ [dim]nextmv cloud app update --app-id hare-app --name "Hare App" \\
            --default-experiment-instance experiment-v1[/dim]

    - Update multiple application properties at once.
        $ [dim]nextmv cloud app update --app-id hare-app --name "Hare App" \\
            --description "Updated description" --default-instance-id burrow \\
            --default-experiment-instance experiment-v1[/dim]

    - Update an application and save the updated information to an [magenta]updated_app.json[/magenta] file.
        $ [dim]nextmv cloud app update --app-id hare-app --name "New Hare App" --output updated_app.json[/dim]
    """

    if name is None and description is None and default_instance_id is None and default_experiment_instance is None:
        error(
            "Provide at least one option to update: --name, --description, "
            "--default-instance-id, or --default-experiment-instance."
        )

    cloud_app = build_app(app_id=app_id, profile=profile)
    updated_app = cloud_app.update(
        name=name,
        description=description,
        default_instance_id=default_instance_id,
        default_experiment_instance=default_experiment_instance,
    )
    success(f"Application [magenta]{app_id}[/magenta] updated successfully.")
    updated_app_dict = updated_app.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(updated_app_dict, f, indent=2)

        success(msg=f"Updated application information saved to [magenta]{output}[/magenta].")

        return

    print_json(updated_app_dict)
