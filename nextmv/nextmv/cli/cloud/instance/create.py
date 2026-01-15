"""
This module defines the cloud instance create command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json
from nextmv.cli.options import AppIDOption, ProfileOption, VersionIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
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
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Cloud application instance.

    Use the [code]--exist-ok[/code] flag to avoid errors when creating an
    instance with an ID that already exists. This is useful for scripts that
    need to ensure an instance exists without worrying about whether it was
    created previously.

    [bold][underline]Examples[/underline][/bold]

    - Create an instance for application [magenta]hare-app[/magenta] version [magenta]v1[/magenta].
        $ [green]nextmv cloud instance create --app-id hare-app --version-id v1 --instance-id prod[/green]

    - Create an instance with a specific name.
        $ [green]nextmv cloud instance create --app-id hare-app --version-id v1 \\
            --instance-id prod --name "Production Instance"[/green]

    - Create an instance with a name and description.
        $ [green]nextmv cloud instance create --app-id hare-app --version-id v1 \\
            --instance-id prod --name "Production Instance" \\
            --description "Instance for production routing jobs"[/green]

    - Create an instance, or get it if it already exists.
        $ [green]nextmv cloud instance create --app-id hare-app --version-id v1 \\
            --instance-id prod --exist-ok[/green]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    if exist_ok:
        in_progress(msg="Creating or getting instance...")
    else:
        in_progress(msg="Creating instance...")

    instance = cloud_app.new_instance(
        version_id=version_id,
        id=instance_id,
        name=name,
        description=description,
        exist_ok=exist_ok,
    )
    print_json(instance.to_dict())
