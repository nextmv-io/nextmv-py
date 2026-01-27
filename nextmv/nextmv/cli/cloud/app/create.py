"""
This module defines the cloud app create command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_client
from nextmv.cli.message import in_progress, print_json
from nextmv.cli.options import ProfileOption
from nextmv.cloud.application import Application

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    app_id: Annotated[
        str | None,
        typer.Option(
            "--app-id",
            "-a",
            help="An optional ID for the Nextmv Cloud application. If not provided, a random ID will be generated.",
            envvar="NEXTMV_APP_ID",
            metavar="APP_ID",
        ),
    ] = None,
    default_experiment_instance: Annotated[
        str | None,
        typer.Option(
            "--default-experiment-instance",
            "-x",
            help="An optional default experiment instance ID for the application.",
            metavar="DEFAULT_EXPERIMENT_INSTANCE",
        ),
    ] = None,
    default_instance_id: Annotated[
        str | None,
        typer.Option(
            "--default-instance-id",
            "-i",
            help="An optional default instance ID for the application.",
            metavar="DEFAULT_INSTANCE_ID",
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="An optional description for the application.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    exist_ok: Annotated[
        bool,
        typer.Option(
            "--exist-ok",
            "-e",
            help="If an application with the given ID already exists, do not raise an error, and simply return it.",
        ),
    ] = False,
    is_workflow: Annotated[
        bool,
        typer.Option(
            "--is-workflow",
            "-w",
            help="Whether the application is a workflow.",
        ),
    ] = False,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="An optional name for the application. If not provided, the application ID will be used as the name.",
            metavar="NAME",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Cloud application.

    Use the --exist-ok flag to avoid errors when creating an application with
    an ID that already exists. This is useful for scripts that need to ensure
    an application exists without worrying about whether it was created
    previously.

    An application can be marked as a workflow using the --is-workflow flag.
    Workflows allow for more complex decision-making processes by leveraging
    [link=https://github.com/nextmv-io/nextpipe][bold]Nextpipe[/bold][/link] to
    orchestrate multiple decision models.

    [bold][underline]Examples[/underline][/bold]

    - Create an application with the name [magenta]Hare App[/magenta]. A random ID will be generated.
        $ [dim]nextmv cloud app create --name "Hare App"[/dim]

    - Create an application with the specific ID [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud app create --name "Hare App" --app-id hare-app[/dim]

    - Create an application with an ID and description.
        $ [dim]nextmv cloud app create --name "Hare App" --app-id hare-app \\
            --description "An application for routing hares"[/dim]

    - Create an application, or get it if it already exists.
        $ [dim]nextmv cloud app create --name "Hare App" --app-id hare-app --exist-ok[/dim]

    - Create a workflow application.
        $ [dim]nextmv cloud app create --name "Hare Workflow" --app-id hare-workflow --is-workflow[/dim]

    - Create an application with a default instance ID.
        $ [dim]nextmv cloud app create --name "Hare App" --app-id hare-app \\
            --default-instance-id burrow[/dim]

    - Create an application with a default experiment instance.
        $ [dim]nextmv cloud app create --name "Hare App" --app-id hare-app \\
            --default-experiment-instance experiment-v1[/dim]
    """

    client = build_client(profile)
    if exist_ok:
        in_progress(msg="Creating or getting application...")
    else:
        in_progress(msg="Creating application...")

    cloud_app = Application.new(
        client=client,
        name=name,
        id=app_id,
        description=description,
        is_workflow=is_workflow,
        exist_ok=exist_ok,
        default_instance_id=default_instance_id,
        default_experiment_instance=default_experiment_instance,
    )
    print_json(cloud_app.to_dict())
