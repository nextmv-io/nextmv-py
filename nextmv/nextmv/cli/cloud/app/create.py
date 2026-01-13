"""
This module defines the cloud app create command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_client
from nextmv.cli.message import info, print_json
from nextmv.cli.options import ProfileOption
from nextmv.cloud.application import Application

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="A name for the application.",
            metavar="NAME",
        ),
    ],
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
    default_instance_id: Annotated[
        str | None,
        typer.Option(
            "--default-instance-id",
            "-i",
            help="An optional default instance ID for the application.",
            metavar="DEFAULT_INSTANCE_ID",
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
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Cloud application.

    A Nextmv application is an entity that contains a decision model as
    executable code. An application can make a run by taking an input,
    executing the decision model, and producing an output.

    Use the [code]--exist-ok[/code] flag to avoid errors when creating an
    application with an ID that already exists. This is useful for scripts that
    need to ensure an application exists without worrying about whether it was
    created previously.

    An application can be marked as a workflow using the
    [code]--is-workflow[/code] flag. Workflows allow for more complex
    decision-making processes by leveraging
    [link=https://github.com/nextmv-io/nextpipe][bold]Nextpipe[/bold][/link] to
    orchestrate multiple decision models.

    [bold][underline]Examples[/underline][/bold]

    - Create an application with the name [magenta]Hare App[/magenta]. A random ID will be generated.
        $ [green]nextmv cloud app create --name "Hare App"[/green]

    - Create an application with the specific ID [magenta]hare-app[/magenta].
        $ [green]nextmv cloud app create --name "Hare App" --app-id hare-app[/green]

    - Create an application with an ID and description.
        $ [green]nextmv cloud app create --name "Hare App" --app-id hare-app \\
            --description "An application for routing hares"[/green]

    - Create an application, or get it if it already exists.
        $ [green]nextmv cloud app create --name "Hare App" --app-id hare-app --exist-ok[/green]

    - Create a workflow application.
        $ [green]nextmv cloud app create --name "Hare Workflow" --app-id hare-workflow --is-workflow[/green]

    - Create an application with a default instance ID.
        $ [green]nextmv cloud app create --name "Hare App" --app-id hare-app \\
            --default-instance-id burrow[/green]

    - Create an application with a default experiment instance.
        $ [green]nextmv cloud app create --name "Hare App" --app-id hare-app \\
            --default-experiment-instance experiment-v1[/green]
    """

    client = build_client(profile)
    if exist_ok:
        info(msg="Creating or getting application...", emoji=":hourglass_flowing_sand:")
    else:
        info(msg="Creating application...", emoji=":hourglass_flowing_sand:")

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
