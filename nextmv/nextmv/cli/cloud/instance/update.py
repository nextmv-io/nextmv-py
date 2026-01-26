"""
This module defines the cloud instance update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.cloud.instance.create import build_config, build_options
from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import enum_values, error, print_json, success
from nextmv.cli.options import AppIDOption, InstanceIDOption, ProfileOption
from nextmv.input import InputFormat

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
            "-u",
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
    # Options for updating the instance configuration.
    content_format: Annotated[
        InputFormat | None,
        typer.Option(
            "--content-format",
            "-c",
            help=f"The content format for the instance. Allowed values are: {enum_values(InputFormat)}.",
            metavar="CONTENT_FORMAT",
            rich_help_panel="Instance configuration",
        ),
    ] = None,
    execution_class: Annotated[
        str | None,
        typer.Option(
            "--execution-class",
            "-x",
            help="The execution class to use for the instance.",
            metavar="EXECUTION_CLASS",
            rich_help_panel="Instance configuration",
        ),
    ] = None,
    integration_id: Annotated[
        str | None,
        typer.Option(
            help="The integration ID to use for the runs of the instance, if applicable.",
            metavar="INTEGRATION_ID",
            rich_help_panel="Instance configuration",
        ),
    ] = None,
    no_queuing: Annotated[
        bool | None,
        typer.Option(
            "--no-queuing",
            help="Do not queue when running the instance.",
            rich_help_panel="Instance configuration",
        ),
    ] = None,
    options: Annotated[
        list[str] | None,
        typer.Option(
            "--options",
            "-o",
            help="Options to always use when running the instance. Format: [magenta]key=value[/magenta]. "
            "Pass multiple options by repeating the flag, or separating with commas.",
            metavar="KEY=VALUE",
            rich_help_panel="Instance configuration",
        ),
    ] = None,
    priority: Annotated[
        int | None,
        typer.Option(
            help="The priority of the runs in the instance. "
            "Priority is between 1 and 10, with 1 being the highest priority.",
            metavar="PRIORITY",
            rich_help_panel="Instance configuration",
        ),
    ] = None,
    secret_collection_id: Annotated[
        str | None,
        typer.Option(
            "--secret-collection-id",
            "-s",
            help="The secret collection ID to use for the instance, if applicable.",
            metavar="SECRET_COLLECTION_ID",
            rich_help_panel="Instance configuration",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Updates a Nextmv Cloud application instance.

    [bold][underline]Examples[/underline][/bold]

    - Update an instance's name.
        $ [dim]nextmv cloud instance update --app-id hare-app --instance-id prod --name "Production Instance"[/dim]

    - Update an instance's description.
        $ [dim]nextmv cloud instance update --app-id hare-app --instance-id prod \\
            --description "Instance for production routing jobs"[/dim]

    - Update an instance to use a different version.
        $ [dim]nextmv cloud instance update --app-id hare-app --instance-id prod --version-id v2[/dim]

    - Update an instance's name and description at once.
        $ [dim]nextmv cloud instance update --app-id hare-app --instance-id prod \\
            --name "Production Instance" --description "Instance for production routing jobs"[/dim]

    - Update an instance and save the updated information to a [magenta]updated_instance.json[/magenta] file.
        $ [dim]nextmv cloud instance update --app-id hare-app --instance-id prod \\
            --name "Production Instance" --output updated_instance.json[/dim]

    - Update an instance's execution class and priority.
        $ [dim]nextmv cloud instance update --app-id hare-app --instance-id prod \\
            --execution-class 6c9500mb870s --priority 1[/dim]

    - Update an instance's runtime options.
        $ [dim]nextmv cloud instance update --app-id hare-app --instance-id prod \\
            --options max_duration=30 --options timeout=60[/dim]
    """

    # Check if any configuration options are provided
    has_config_options = any(
        [
            content_format is not None,
            execution_class is not None,
            integration_id is not None,
            no_queuing is not None,
            options is not None,
            priority is not None,
            secret_collection_id is not None,
        ]
    )

    if name is None and description is None and version_id is None and not has_config_options:
        error(
            "Provide at least one option to update: --name, --description, "
            "--version-id, or any [magenta]Instance configuration[/magenta] option."
        )

    cloud_app = build_app(app_id=app_id, profile=profile)

    # Build configuration if any configuration options were provided.
    configuration = None
    if has_config_options:
        instance_options = build_options(options)
        configuration = build_config(
            priority=priority,
            no_queuing=no_queuing,
            content_format=content_format,
            execution_class=execution_class,
            integration_id=integration_id,
            options=instance_options,
            secret_collection_id=secret_collection_id,
        )

    updated_instance = cloud_app.update_instance(
        id=instance_id,
        name=name,
        description=description,
        version_id=version_id,
        configuration=configuration,
    )
    success(
        f"Instance [magenta]{instance_id}[/magenta] updated successfully in application [magenta]{app_id}[/magenta]."
    )
    updated_instance_dict = updated_instance.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(updated_instance_dict, f, indent=2)

        success(msg=f"Updated instance information saved to [magenta]{output}[/magenta].")

        return

    print_json(updated_instance_dict)
