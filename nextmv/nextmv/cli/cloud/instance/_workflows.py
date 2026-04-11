"""CLI-only workflows for the cloud instance domain.

These functions wrap thin actions in ``nextmv.cli.actions.instance`` with
CLI-specific behavior that shouldn't bleed into the action layer:

* ``run_create_instance`` and ``run_update_instance`` build an
  ``InstanceConfiguration`` from many individual flags (a transformation
  the thin action layer doesn't do).
* ``run_update_instance`` enforces a precondition (at least one updatable
  field must be provided) and uses ``--output/-u`` instead of ``-o`` so the
  short flag does not collide with ``--options/-o``.
* ``run_instance_exists_check`` wraps ``instance_exists`` with a JSON print
  and ``exit 1`` on a missing instance for shell-script use.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.actions.instance import (
    create_instance,
    instance_exists,
    update_instance,
)
from nextmv.cli.framework.options import (
    AppIdRequiredOption,
    InstanceIdOption,
    OptionalInstanceIdOption,
    VersionIdOption,
)
from nextmv.cli.message import enum_values, error, in_progress, print_json, success
from nextmv.cloud.client import Client
from nextmv.cloud.instance import InstanceConfiguration
from nextmv.input import InputFormat
from nextmv.run import Format, FormatInput, RunQueuing


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


def run_create_instance(
    client: Client,
    app_id: AppIdRequiredOption,
    version_id: VersionIdOption,
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
    instance_id: OptionalInstanceIdOption = None,
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
) -> None:
    """Create a new Nextmv Cloud application instance.

    Use the ``--exist-ok`` flag to avoid errors when creating an instance
    with an ID that already exists. This is useful for scripts that need to
    ensure an instance exists without worrying about whether it was
    created previously.
    """

    in_progress(msg="Creating instance...")

    # Build the instance options from the CLI options.
    instance_options = build_options(options)

    # Build the instance configuration.
    instance_config = build_config(
        priority=priority,
        no_queuing=no_queuing,
        content_format=content_format,
        execution_class=execution_class,
        integration_id=integration_id,
        options=instance_options,
        secret_collection_id=secret_collection_id,
    )

    instance_dict = create_instance(
        client,
        app_id=app_id,
        version_id=version_id,
        instance_id=instance_id,
        name=name,
        description=description,
        configuration=instance_config.to_dict() if instance_config is not None else None,
        exist_ok=exist_ok,
    )
    print_json(instance_dict)


def run_update_instance(
    client: Client,
    app_id: AppIdRequiredOption,
    instance_id: InstanceIdOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="A new description for the instance.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    locked: Annotated[
        bool | None,
        typer.Option(
            "--locked/--unlocked",
            help="Whether to lock or unlock the instance. If not provided, the locked status will not be updated.",
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
) -> None:
    """Update a Nextmv Cloud application instance.

    Provide at least one of ``--description``, ``--locked``/``--unlocked``,
    ``--name``, ``--version-id``, or any ``Instance configuration`` option;
    omitted fields remain unchanged.
    """

    # Check if any configuration options are provided.
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

    if name is None and description is None and version_id is None and locked is None and not has_config_options:
        error(
            "Provide at least one option to update: --description, --locked/--unlocked, --name, "
            "--version-id, or any [magenta]Instance configuration[/magenta] option."
        )

    # Build configuration if any configuration options were provided.
    configuration: dict | None = None
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
        ).to_dict()

    in_progress(msg="Updating instance...")
    updated_instance_dict = update_instance(
        client,
        app_id=app_id,
        instance_id=instance_id,
        name=name,
        version_id=version_id,
        description=description,
        configuration=configuration,
        locked=locked,
    )
    success(
        f"Instance [magenta]{instance_id}[/magenta] updated successfully in application [magenta]{app_id}[/magenta]."
    )

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(updated_instance_dict, f, indent=2)

        success(msg=f"Updated instance information saved to [magenta]{output}[/magenta].")

        return

    print_json(updated_instance_dict)


def run_instance_exists_check(
    client: Client,
    app_id: AppIdRequiredOption,
    instance_id: InstanceIdOption,
) -> None:
    """Check whether a Nextmv Cloud application instance exists.

    Prints ``{"exists": true}`` or ``{"exists": false}`` as JSON. Exits
    with code 1 if the instance does not exist, so the command can be used
    in shell scripts:

    .. code-block:: bash

        if nextmv cloud instance exists --app-id hare-app --instance-id prod; then
            echo "instance exists"
        fi
    """
    ok = instance_exists(client, app_id=app_id, instance_id=instance_id)
    print_json({"exists": ok})
    if not ok:
        raise typer.Exit(code=1)
