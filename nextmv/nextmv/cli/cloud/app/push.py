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
    no_version: Annotated[
        bool,
        typer.Option(
            "--no-version",
            "-n",
            help="The application will be pushed without creating a new version. "
            "Default is to create a new version on each push.",
            rich_help_panel="Versioning control",
        ),
    ] = False,
    version_id: Annotated[
        str | None,
        typer.Option(
            "--version-id",
            "-v",
            help="Custom version ID when pushing the application. Automatically generated if not provided.",
            rich_help_panel="Versioning control",
            metavar="VERSION_ID",
        ),
    ] = None,
    version_name: Annotated[
        str | None,
        typer.Option(
            "--version-name",
            "-e",
            help="Custom version name when pushing the application. Automatically generated if not provided.",
            rich_help_panel="Versioning control",
            metavar="VERSION_NAME",
        ),
    ] = None,
    version_description: Annotated[
        str | None,
        typer.Option(
            "--version-description",
            "-r",
            help="Custom version description when pushing the application. Automatically generated if not provided.",
            rich_help_panel="Versioning control",
            metavar="VERSION_DESCRIPTION",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Push (deploy) a Nextmv application to Nextmv Cloud.

    Use the --app-dir option to specify the path to your application's root
    directory. By default, the current working directory is used.

    You can also provide a custom manifest file using the --manifest option. If
    not provided, the CLI will look for a file named
    [magenta]app.yaml[/magenta] in the application's root.

    The default behavior of this command is to create a new application version
    [italic]after[/italic] the app has been pushed. You can use the
    --no-version option to skip this step. The --version-id, --version-name,
    and --version-description options allow you to customize the attributes of
    the version that is created. If any of these options are not provided,
    automatically generated values will be used.

    [bold][underline]Examples[/underline][/bold]

    - Push an application, with ID [magenta]hare-app[/magenta], from the current directory.
        $ [dim]nextmv cloud app push --app-id hare-app[/dim]

    - Push an application, with ID [magenta]hare-app[/magenta], from the [magenta]./my-app[/magenta] directory.
        $ [dim]nextmv cloud app push --app-id hare-app --app-dir ./my-app[/dim]

    - Push an application, with ID [magenta]hare-app[/magenta], using a custom manifest file.
        $ [dim]nextmv cloud app push --app-id hare-app --manifest ./custom-manifest.yaml[/dim]

    - Push an application, with ID [magenta]hare-app[/magenta], from a specific
      [magenta]./my-app[/magenta] directory with a custom manifest under [magenta]./custom-manifest.yaml[/magenta].
        $ [dim]nextmv cloud app push --app-id hare-app --app-dir ./my-app \\
            --manifest ./custom-manifest.yaml[/dim]

    - Push an application without creating a new version.
        $ [dim]nextmv cloud app push --app-id hare-app --no-version[/dim]

    - Push an application with a custom version ID.
        $ [dim]nextmv cloud app push --app-id hare-app --version-id v1.0.0[/dim]

    - Push an application with custom version ID, name, and description.
        $ [dim]nextmv cloud app push --app-id hare-app --version-id v1.0.0 \\
            --version-name "Release 1.0.0" \\
            --version-description "First stable release"[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    loaded_manifest = Manifest.from_yaml(dirpath=manifest) if manifest is not None and manifest != "" else None
    cloud_app.push(
        manifest=loaded_manifest,
        app_dir=app_dir,
        verbose=True,
        rich_print=True,
        no_version=no_version,
        version_id=version_id,
        version_name=version_name,
        version_description=version_description,
    )
