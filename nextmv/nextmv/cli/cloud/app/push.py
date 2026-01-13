"""
This module defines the cloud app push command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.manifest import Manifest

# Set up subcommand application.
app = typer.Typer()


@app.command()
def push(
    app_id: AppIDOption,
    app_dir: Annotated[
        str | None,
        typer.Option(
            "--app-dir",
            "-d",
            help="The path to the application's root directory.",
            metavar="APP_DIR",
        ),
    ] = ".",
    manifest: Annotated[
        str | None,
        typer.Option(
            "--manifest",
            "-m",
            help="Path to the application manifest file ([magenta]app.yaml[/magenta]).",
            metavar="MANIFEST_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Push (deploy) a Nextmv application to Nextmv Cloud.

    Use the [code]--app-dir[/code] option to specify the path to your
    application's root directory. By default, the current working directory is
    used.

    You can also provide a custom manifest file using the [code]--manifest[/code]
    option. If not provided, the CLI will look for a file named [magenta]app.yaml[/magenta]
    in the application's root.

    [bold][underline]Examples[/underline][/bold]

    - Push an application, with ID [magenta]hare-app[/magenta], from the current directory.
        $ [green]nextmv cloud app push --app-id hare-app[/green]

    - Push an application, with ID [magenta]hare-app[/magenta], from the [magenta]./my-app[/magenta] directory.
        $ [green]nextmv cloud app push --app-id hare-app --app-dir ./my-app[/green]

    - Push an application, with ID [magenta]hare-app[/magenta], using a custom manifest file.
        $ [green]nextmv cloud app push --app-id hare-app --manifest ./custom-manifest.yaml[/green]

    - Push an application, with ID [magenta]hare-app[/magenta], from a specific
      [magenta]./my-app[/magenta] directory with a custom manifest under [magenta]./custom-manifest.yaml[/magenta].
        $ [green]nextmv cloud app push --app-id hare-app --app-dir ./my-app \\
            --manifest ./custom-manifest.yaml[/green]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    loaded_manifest = Manifest.from_yaml(dirpath=manifest) if manifest is not None and manifest != "" else None
    cloud_app.push(
        manifest=loaded_manifest,
        app_dir=app_dir,
        verbose=True,
        rich_print=True,
    )
