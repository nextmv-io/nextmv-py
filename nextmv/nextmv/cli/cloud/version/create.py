"""
This module defines the cloud version create command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json
from nextmv.cli.options import AppIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    app_id: AppIDOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="An optional description for the version.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    exist_ok: Annotated[
        bool,
        typer.Option(
            "--exist-ok",
            "-e",
            help="If a version with the given ID already exists, do not raise an error, and simply return it.",
        ),
    ] = False,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="A name for the version. If a name is not provided, the version ID will be used as the name.",
            metavar="NAME",
        ),
    ] = None,
    version_id: Annotated[
        str | None,
        typer.Option(
            "--version-id",
            "-v",
            help="The ID to assign to the new version. If not provided, a random ID will be generated.",
            envvar="NEXTMV_VERSION_ID",
            metavar="VERSION_ID",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Cloud application version.

    Use the --exist-ok flag to avoid errors when creating a version with an ID
    that already exists. This is useful for scripts that need to ensure a
    version exists without worrying about whether it was created previously.

    [bold][underline]Examples[/underline][/bold]

    - Create a version for application [magenta]hare-app[/magenta]. A random ID will be generated.
        $ [dim]nextmv cloud version create --app-id hare-app[/dim]

    - Create a version with a specific name.
        $ [dim]nextmv cloud version create --app-id hare-app --name "v1.0.0"[/dim]

    - Create a version with a specific ID.
        $ [dim]nextmv cloud version create --app-id hare-app --version-id v1[/dim]

    - Create a version with a name and description.
        $ [dim]nextmv cloud version create --app-id hare-app --name "v1.0.0" \\
            --description "Initial release with routing optimization"[/dim]

    - Create a version, or get it if it already exists.
        $ [dim]nextmv cloud version create --app-id hare-app --version-id v1 --exist-ok[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    if exist_ok:
        in_progress(msg="Creating or getting version...")
    else:
        in_progress(msg="Creating version...")

    version = cloud_app.new_version(
        id=version_id,
        name=name,
        description=description,
        exist_ok=exist_ok,
    )
    print_json(version.to_dict())
