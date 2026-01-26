"""
This module defines the cloud instance create command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import enum_values, error, in_progress, print_json
from nextmv.cli.options import AppIDOption, ProfileOption, VersionIDOption
from nextmv.cloud.instance import InstanceConfiguration
from nextmv.input import InputFormat
from nextmv.run import Format, FormatInput, RunQueuing

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    # Options for creating the instance.
    app_id: AppIDOption,
    version_id: VersionIDOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="An optional description for the instance.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    exist_ok: Annotated[
        bool,
        typer.Option(
            "--exist-ok",
            "-e",
            help="If an instance with the given ID already exists, do not raise an error, and simply return it.",
        ),
    ] = False,
    instance_id: Annotated[
        str | None,
        typer.Option(
            "--instance-id",
            "-i",
            help="The ID to assign to the new instance. If not provided, a random ID will be generated.",
            envvar="NEXTMV_INSTANCE_ID",
            metavar="INSTANCE_ID",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="A name for the instance. If a name is not provided, the instance ID will be used as the name.",
            metavar="NAME",
        ),
    ] = None,
    # Options for configuring the instance.
    content_format: Annotated[
        InputFormat | None,
        typer.Option(
            "--content-format",
            "-c",
            help=f"The content format of the instance to create. Allowed values are: {enum_values(InputFormat)}.",
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
        bool,
        typer.Option(
            "--no-queuing",
            help="Do not queue when running the instance. Default is [magenta]False[/magenta], "
            "meaning the instance's run [italic]will[/italic] be queued.",
            rich_help_panel="Instance configuration",
        ),
    ] = False,
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
        int,
        typer.Option(
            help="The priority of the runs in the instance. "
            "Priority is between 1 and 10, with 1 being the highest priority.",
            metavar="PRIORITY",
            rich_help_panel="Instance configuration",
        ),
    ] = 6,
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
    Create a new Nextmv Cloud application instance.

    Use the --exist-ok flag to avoid errors when creating an instance with an
    ID that already exists. This is useful for scripts that need to ensure an
    instance exists without worrying about whether it was created previously.

    [bold][underline]Examples[/underline][/bold]

    - Create an instance for application [magenta]hare-app[/magenta] version [magenta]v1[/magenta].
        $ [dim]nextmv cloud instance create --app-id hare-app --version-id v1 --instance-id prod[/dim]

    - Create an instance with a specific name.
        $ [dim]nextmv cloud instance create --app-id hare-app --version-id v1 \\
            --instance-id prod --name "Production Instance"[/dim]

    - Create an instance with a name and description.
        $ [dim]nextmv cloud instance create --app-id hare-app --version-id v1 \\
            --instance-id prod --name "Production Instance" \\
            --description "Instance for production routing jobs"[/dim]

    - Create an instance, or get it if it already exists.
        $ [dim]nextmv cloud instance create --app-id hare-app --version-id v1 \\
            --instance-id prod --exist-ok[/dim]

    - Create an instance with configuration options.
        $ [dim]nextmv cloud instance create --app-id hare-app --version-id v1 \\
            --instance-id prod --execution-class 6c9500mb870s --priority 1[/dim]

    - Create an instance with runtime options.
        $ [dim]nextmv cloud instance create --app-id hare-app --version-id v1 \\
            --instance-id prod --options max_duration=30 --options timeout=60[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    if exist_ok:
        in_progress(msg="Creating or getting instance...")
    else:
        in_progress(msg="Creating instance...")

    # Build the instance options from the CLI options
    instance_options = build_options(options)

    # Build the instance configuration
    instance_config = build_config(
        priority=priority,
        no_queuing=no_queuing,
        content_format=content_format,
        execution_class=execution_class,
        integration_id=integration_id,
        options=instance_options,
        secret_collection_id=secret_collection_id,
    )

    instance = cloud_app.new_instance(
        version_id=version_id,
        id=instance_id,
        name=name,
        description=description,
        configuration=instance_config,
        exist_ok=exist_ok,
    )
    print_json(instance.to_dict())


def build_options(options: list[str] | None) -> dict[str, str] | None:
    """
    Builds the instance options. One can pass options by either using the flag
    multiple times or by separating with commas in the same flag. A
    combination of both is also possible.

    Parameters
    ----------
    options : list[str] | None
        The list of instance options as strings.

    Returns
    -------
    dict[str, str]
        The built instance options.
    """

    if options is None:
        return None

    instance_options = {}
    for opt in options:
        # It is possible to pass multiple options separated by commas. The
        # default way though is to use the flag multiple times to specify
        # different options.
        sub_opts = opt.split(",")
        for sub_opt in sub_opts:
            key_value = sub_opt.split("=", 1)
            if len(key_value) != 2:
                error(f"Invalid option format: {sub_opt}. Expected format is [magenta]key=value[/magenta].")

            key, value = key_value
            instance_options[key] = value

    return instance_options


def build_config(
    priority: int,
    no_queuing: bool,
    content_format: InputFormat | None = None,
    execution_class: str | None = None,
    integration_id: str | None = None,
    options: dict | None = None,
    secret_collection_id: str | None = None,
) -> InstanceConfiguration:
    """
    Builds the instance configuration for the new instance.

    Parameters
    ----------
    priority : int
        The priority of the instance.
    no_queuing : bool
        Whether to disable queuing for the instance.
    content_format : InputFormat | None
        The content format for the instance, if applicable.
    execution_class : str | None
        The execution class to use for the instance, if applicable.
    integration_id : str | None
        The integration ID to use for the instance, if applicable.
    options : dict | None
        The runtime options for the instance, if applicable.
    secret_collection_id : str | None
        The secret collection ID to use for the instance, if applicable.

    Returns
    -------
    InstanceConfiguration
        The built instance configuration.
    """

    config = InstanceConfiguration(
        queuing=RunQueuing(
            priority=priority,
            disabled=no_queuing,
        ),
    )
    if execution_class is not None:
        config.execution_class = execution_class
    if options is not None:
        config.options = options
    if secret_collection_id is not None:
        config.secrets_collection_id = secret_collection_id
    if integration_id is not None:
        config.integration_id = integration_id
    if content_format is not None:
        config.format = Format(
            format_input=FormatInput(
                input_type=InputFormat(content_format),
            ),
        )

    return config
