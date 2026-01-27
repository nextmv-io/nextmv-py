"""
This module defines the cloud app push command for the Nextmv CLI.
"""

from datetime import datetime, timezone
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import error, in_progress, info, success
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.application import Application
from nextmv.cloud.instance import Instance
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
    # Options for unsupervised prompts.
    auto_create_yes: Annotated[
        bool,
        typer.Option(
            "--auto-create-yes",
            "-cy",
            help="Create a new version and instance after push. "
            "Skips confirmation prompt with [magenta]yes[/magenta]. Useful for non-interactive sessions.",
            rich_help_panel="Automatic creation and updating",
        ),
    ] = False,
    auto_create_no: Annotated[
        bool,
        typer.Option(
            "--auto-create-no",
            "-cn",
            help="Do not create a new version and instance after push. "
            "Skips confirmation prompt with [magenta]no[/magenta]. Useful for non-interactive sessions.",
            rich_help_panel="Automatic creation and updating",
        ),
    ] = False,
    update_default_instance_yes: Annotated[
        bool,
        typer.Option(
            "--update-default-instance-yes",
            "-uy",
            help="Update the default instance of the app after version/instance creation. "
            "Skips confirmation prompt with [magenta]yes[/magenta]. "
            "Useful for non-interactive sessions. Activates --auto-create-yes.",
            rich_help_panel="Automatic creation and updating",
        ),
    ] = False,
    update_default_instance_no: Annotated[
        bool,
        typer.Option(
            "--update-default-instance-no",
            "-un",
            help="Do not update the default instance of the app after version/instance creation. "
            "Skips confirmation prompt with [magenta]no[/magenta]. "
            "Useful for non-interactive sessions. Activates --auto-create-yes.",
            rich_help_panel="Automatic creation and updating",
        ),
    ] = False,
    # Options for version creation.
    version_id: Annotated[
        str | None,
        typer.Option(
            "--version-id",
            help="Custom version ID when pushing the application. Automatically generated if not provided. "
            "Activates --auto-create-yes.",
            rich_help_panel="Version control",
            metavar="VERSION_ID",
        ),
    ] = None,
    version_description: Annotated[
        str | None,
        typer.Option(
            "--version-description",
            help="Custom version description when pushing the application. Automatically generated if not provided. "
            "Activates --auto-create-yes.",
            rich_help_panel="Version control",
            metavar="VERSION_DESCRIPTION",
        ),
    ] = None,
    version_name: Annotated[
        str | None,
        typer.Option(
            "--version-name",
            help="Custom version name when pushing the application. Automatically generated if not provided. "
            "Activates --auto-create-yes.",
            rich_help_panel="Version control",
            metavar="VERSION_NAME",
        ),
    ] = None,
    # Options for instance creation.
    instance_id: Annotated[
        str | None,
        typer.Option(
            "--instance-id",
            help="Custom instance ID when pushing the application. Automatically generated if not provided. "
            "Activates --auto-create-yes.",
            rich_help_panel="Instance control",
            metavar="INSTANCE_ID",
        ),
    ] = None,
    instance_description: Annotated[
        str | None,
        typer.Option(
            "--instance-description",
            help="Custom instance description when pushing the application. Automatically generated if not provided. "
            "Activates --auto-create-yes.",
            rich_help_panel="Instance control",
            metavar="INSTANCE_DESCRIPTION",
        ),
    ] = None,
    instance_name: Annotated[
        str | None,
        typer.Option(
            "--instance-name",
            help="Custom instance name when pushing the application. Automatically generated if not provided. "
            "Activates --auto-create-yes.",
            rich_help_panel="Instance control",
            metavar="INSTANCE_NAME",
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


    By default, this command only pushes the app. After the push, you will be
    prompted to create a new version and instance. Use --auto-create-yes to
    automatically create a new version and instance (skipping the prompt), or
    --auto-create-no to skip creation.

    The --version-id, --version-name, and --version-description options allow
    you to customize the new version. The --instance-id, --instance-name, and
    --instance-description options allow you to customize the new instance. If
    any of these options are provided, --auto-create-yes is automatically
    activated.

    After version/instance creation, you will be prompted to set the new
    instance as the default. Use --update-default-instance-yes to automatically
    update the default instance (skipping the prompt), or
    --update-default-instance-no to skip updating. Providing either of these
    options automatically activates --auto-create-yes.

    [bold][underline]Examples[/underline][/bold]

    - Push an application, with ID [magenta]hare-app[/magenta], from the current directory.
        $ [dim]nextmv cloud app push --app-id hare-app[/dim]

    - Push an application, with ID [magenta]hare-app[/magenta], from the [magenta]./my-app[/magenta] directory.
        $ [dim]nextmv cloud app push --app-id hare-app --app-dir ./my-app[/dim]

    - Push an application, with ID [magenta]hare-app[/magenta], using a custom manifest file.
        $ [dim]nextmv cloud app push --app-id hare-app --manifest ./custom-manifest.yaml[/dim]

    - Push an application, with ID [magenta]hare-app[/magenta], from a specific [magenta]./my-app[/magenta] directory
      with a custom manifest.
        $ [dim]nextmv cloud app push --app-id hare-app --app-dir ./my-app --manifest ./custom-manifest.yaml[/dim]

    - Push and automatically create a new version and instance (no prompt).
        $ [dim]nextmv cloud app push --app-id hare-app --auto-create-yes[/dim]

    - Push and skip version/instance creation (no prompt).
        $ [dim]nextmv cloud app push --app-id hare-app --auto-create-no[/dim]

    - Push and automatically create a new version and instance, then set the new instance as default (no prompts).
        $ [dim]nextmv cloud app push --app-id hare-app --auto-create-yes --update-default-instance-yes[/dim]

    - Push and create a new version with a custom version ID (auto-create is activated).
        $ [dim]nextmv cloud app push --app-id hare-app --version-id v1.0.0[/dim]

    - Push with custom version and instance attributes, and set the new instance as default (all prompts skipped).
        $ [dim]nextmv cloud app push --app-id hare-app \\
            --version-id v1.0.0 \\
            --version-name "Release 1.0.0" \\
            --version-description "First stable release" \\
            --instance-id inst-1 \\
            --instance-name "Production Instance" \\
            --instance-description "Main deployment" \\
            --update-default-instance-yes[/dim]
    """

    if auto_create_yes and auto_create_no:
        error("Cannot specify both --auto-create-yes and --auto-create-no.")

    if update_default_instance_yes and update_default_instance_no:
        error("Cannot specify both --update-default-instance-yes and --update-default-instance-no.")

    cloud_app = build_app(app_id=app_id, profile=profile)
    loaded_manifest = Manifest.from_yaml(dirpath=manifest) if manifest is not None and manifest != "" else None
    cloud_app.push(
        manifest=loaded_manifest,
        app_dir=app_dir,
        verbose=True,
        rich_print=True,
    )

    instance, should_update = _handle_version_instance_creation(
        cloud_app=cloud_app,
        app_id=app_id,
        auto_create_yes=auto_create_yes,
        auto_create_no=auto_create_no,
        update_default_instance_yes=update_default_instance_yes,
        update_default_instance_no=update_default_instance_no,
        version_id=version_id,
        version_name=version_name,
        version_description=version_description,
        instance_id=instance_id,
        instance_name=instance_name,
        instance_description=instance_description,
    )
    _handle_instance_update(
        cloud_app=cloud_app,
        app_id=app_id,
        instance=instance,
        should_update=should_update,
        update_default_instance_yes=update_default_instance_yes,
        update_default_instance_no=update_default_instance_no,
    )


def _handle_version_instance_creation(
    cloud_app: Application,
    app_id: str,
    auto_create_yes: bool,
    auto_create_no: bool,
    update_default_instance_yes: bool,
    update_default_instance_no: bool,
    version_id: str | None,
    version_name: str | None,
    version_description: str | None,
    instance_id: str | None,
    instance_name: str | None,
    instance_description: str | None,
) -> tuple[Instance | None, bool]:
    if auto_create_no:
        info(
            msg="--auto-create-no activated, will not create a new version and instance.",
            emoji=":bulb:",
        )
        return None, False

    # Determine if we need to create a new version and instance based on the options provided.
    version_provided = version_id is not None or version_name is not None or version_description is not None
    instance_provided = instance_id is not None or instance_name is not None or instance_description is not None
    if version_provided or instance_provided or update_default_instance_yes or update_default_instance_no:
        auto_create_yes = True

    if not auto_create_yes:
        should_create = get_confirmation(
            f"Do you want to create a new version and instance for application [magenta]{app_id}[/magenta] now?"
        )

        if not should_create:
            info(
                msg="Will not create a new version and instance.",
                emoji=":bulb:",
            )
            return None, False

    in_progress("Creating a new version and instance...")
    now = datetime.now(timezone.utc)

    if version_description is None or version_description == "":
        version_description = f"Version created automatically from push at {now.strftime('%Y-%m-%dT%H:%M:%SZ')}"

    version = cloud_app.new_version(
        id=version_id,
        name=version_name,
        description=version_description,
    )
    success(f"New version [magenta]{version.id}[/magenta] created for application [magenta]{app_id}[/magenta].")

    if instance_description is None or instance_description == "":
        instance_description = f"Instance created automatically from push at {now.strftime('%Y-%m-%dT%H:%M:%SZ')}"

    instance = cloud_app.new_instance(
        version_id=version.id,
        id=instance_id,
        name=instance_name,
        description=instance_description,
    )
    success(
        f"New instance [magenta]{instance.id}[/magenta] created using version [magenta]{version.id}[/magenta] "
        f"for application [magenta]{app_id}[/magenta]."
    )

    return instance, True


def _handle_instance_update(
    cloud_app: Application,
    app_id: str,
    instance: Instance,
    should_update: bool,
    update_default_instance_yes: bool,
    update_default_instance_no: bool,
) -> None:
    if instance is None or not should_update:
        return

    if update_default_instance_no:
        info(
            msg="--update-default-instance-no activated, will not update the default instance.",
            emoji=":bulb:",
        )
        return

    if not update_default_instance_yes:
        should_update = get_confirmation(
            f"Do you want to set instance [magenta]{instance.id}[/magenta] as the default instance for "
            f"application [magenta]{app_id}[/magenta]?"
        )

        if not should_update:
            info(
                msg=f"Default instance for application [magenta]{app_id}[/magenta] not updated.",
                emoji=":bulb:",
            )
            return

    in_progress(
        f"Updating default instance for application [magenta]{app_id}[/magenta] to [magenta]{instance.id}[/magenta]..."
    )
    cloud_app.update(default_instance_id=instance.id)
    success(
        f"Default instance for application [magenta]{app_id}[/magenta] updated to [magenta]{instance.id}[/magenta].",
    )
