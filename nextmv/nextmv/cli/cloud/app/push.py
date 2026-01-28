"""
This module defines the cloud app push command for the Nextmv CLI.
"""

import sys
from datetime import datetime, timezone
from typing import Annotated

import typer
from rich.prompt import Prompt

from nextmv.cli.configuration.config import build_app
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import error, in_progress, info, success
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.application import Application
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
    # Options for version control.
    version_id: Annotated[
        str | None,
        typer.Option(
            "--version-id",
            "-v",
            help="Custom ID for version creation after app push. Automatically generated if not provided. "
            "Activates --version-yes.",
            metavar="VERSION_ID",
            rich_help_panel="Version control",
        ),
    ] = None,
    version_yes: Annotated[
        bool,
        typer.Option(
            "--version-yes",
            "-y",
            help="Create a new version after push. Skips confirmation prompt. Useful for non-interactive sessions.",
            rich_help_panel="Version control",
        ),
    ] = False,
    # Options for instance control.
    create_instance_id: Annotated[
        str | None,
        typer.Option(
            "--create-instance-id",
            "-c",
            help="Link the newly created version to a [yellow]new[/yellow] instance with this ID. "
            "Skips prompt to provide an instance ID. Useful for non-interactive sessions.",
            metavar="CREATE_INSTANCE_ID",
            rich_help_panel="Instance control",
        ),
    ] = None,
    update_instance_id: Annotated[
        str | None,
        typer.Option(
            "--update-instance-id",
            "-u",
            help="Link the newly created version to an [yellow]existing[/yellow] instance with this ID. "
            "Skips prompt to provide an instance ID. Useful for non-interactive sessions.",
            metavar="UPDATE_INSTANCE_ID",
            rich_help_panel="Instance control",
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
    prompted to create a new version. If a new version is created, you will be
    prompted to link it to an instance. If the instance exists, you will be
    asked if you want to update it. If it doesn't, you will be asked to create
    it. You can use the following flags to skip the prompts, useful in
    non-interactive sessions like in a CI/CD pipeline: --version-yes,
    --version-id, --create-instance-id, and --update-instance-id.

    [bold][underline]Examples[/underline][/bold]

    - Push an application, with ID [magenta]hare-app[/magenta], from the current directory.
        $ [dim]nextmv cloud app push --app-id hare-app[/dim]

    - Push an application, with ID [magenta]hare-app[/magenta], from the [magenta]./my-app[/magenta] directory.
        $ [dim]nextmv cloud app push --app-id hare-app --app-dir ./my-app[/dim]

    - Push an application, with ID [magenta]hare-app[/magenta], using a custom manifest file.
        $ [dim]nextmv cloud app push --app-id hare-app --manifest ./custom-manifest.yaml[/dim]

    - Push and automatically create a new version (no prompt).
        $ [dim]nextmv cloud app push --app-id hare-app --version-yes[/dim]

    - Push and create a new version with a custom version ID (no prompt).
        $ [dim]nextmv cloud app push --app-id hare-app --version-id v1.0.0[/dim]

    - Push and create a new version, then link it to a new instance with a specific ID (no prompt).
        $ [dim]nextmv cloud app push --app-id hare-app --version-yes --create-instance-id inst-1[/dim]

    - Push and create a new version, then link it to an existing instance (no prompt).
        $ [dim]nextmv cloud app push --app-id hare-app --version-yes --update-instance-id inst-1[/dim]
    """

    # We cannot create and update an instance at the same time.
    update_defined = update_instance_id is not None and update_instance_id != ""
    create_defined = create_instance_id is not None and create_instance_id != ""
    if update_defined and create_defined:
        error("Cannot use --update-instance-id and --create-instance-id at the same time.")

    cloud_app = build_app(app_id=app_id, profile=profile)

    # We cannot update an instance that does not exist.
    if update_defined and not cloud_app.instance_exists(instance_id=update_instance_id):
        error(
            f"Used option --update-instance-id but the instance {update_instance_id} does not exist. "
            "Use --create-instance-id instead."
        )

    # We cannot create an instance that already exists.
    if create_defined and cloud_app.instance_exists(instance_id=create_instance_id):
        error(
            f"Used option --create-instance-id but the instance {create_instance_id} already exists. "
            "Use --update-instance-id instead."
        )

    # Do the normal push first.
    loaded_manifest = Manifest.from_yaml(dirpath=manifest) if manifest is not None and manifest != "" else None
    cloud_app.push(
        manifest=loaded_manifest,
        app_dir=app_dir,
        verbose=True,
        rich_print=True,
    )

    now = datetime.now(timezone.utc)
    version_id, should_continue = _handle_version_creation(
        cloud_app=cloud_app,
        app_id=app_id,
        version_id=version_id,
        version_yes=version_yes,
        now=now,
    )
    if not should_continue:
        return

    # If the override for updating an instance was used, we update the instance
    # and we are done.
    if update_defined:
        info("Used option --update-instance-id to link version to existing instance.", emoji=":bulb:")
        _update_instance(
            cloud_app=cloud_app,
            app_id=app_id,
            version_id=version_id,
            instance_id=update_instance_id,
        )

        return

    # If the override for creating a new instance was used, we create the
    # instance and we are done.
    if create_defined:
        info("Used option --create-instance-id to link version to new instance.", emoji=":bulb:")
        _create_instance(
            cloud_app=cloud_app,
            app_id=app_id,
            version_id=version_id,
            instance_id=create_instance_id,
            now=now,
        )

        return

    # If no overrides are used, we handle instance prompting.
    _handle_instance_prompting(
        cloud_app=cloud_app,
        app_id=app_id,
        version_id=version_id,
        now=now,
    )


def _handle_version_creation(
    cloud_app: Application,
    app_id: str,
    version_id: str | None,
    version_yes: bool,
    now: datetime,
) -> tuple[str, bool]:
    """
    Handle the logic for version creation after pushing an application.

    If a version ID is provided and exists, it is used directly. If not, the user is prompted (unless auto-confirmed)
    to create a new version. If confirmed, a new version is created with an automatic description.

    Parameters
    ----------
    cloud_app : Application
        The cloud application object to interact with Nextmv Cloud.
    app_id : str
        The application ID.
    version_id : str or None
        The version ID to use or check for existence. If None or empty, a new version may be created.
    version_yes : bool
        Whether to skip the prompt and auto-create a new version.
    now : datetime
        The current datetime, used for version description.

    Returns
    -------
    tuple[str, bool]
        A tuple containing the version ID (empty string if not created) and a boolean indicating
        whether to continue with subsequent steps (True if a version is selected or created, False otherwise).
    """

    # If the user provides a version, and it exists, we use it directly and we
    # are done.
    if version_id is not None and version_id != "":
        exists = cloud_app.version_exists(version_id=version_id)
        if exists:
            error(
                f"Version [magenta]{version_id}[/magenta] already exists for application [magenta]{app_id}[/magenta]."
            )

            return "", False

        info(
            msg=f"Version [magenta]{version_id}[/magenta] does not exist. A new version will be created.",
            emoji=":bulb:",
        )

        version_yes = True  # Activate auto-confirm since user provided a version ID.

    # If we are not auto-confirming version creation, ask the user.
    if not version_yes:
        should_create = get_confirmation(
            msg=f"Do you want to create a new version [magenta]{app_id}[/magenta] now?",
            default=True,
        )

        # If the user does not want to create a new version, we are done.
        if not should_create:
            info(
                msg="Will not create a new version.",
                emoji=":bulb:",
            )
            return "", False

    # Create a new version if either the user confirms by prompt or by using
    # the flag.
    in_progress("Creating a new version...")
    version_description = f"Version created automatically from push at {now.strftime('%Y-%m-%dT%H:%M:%SZ')}"
    version = cloud_app.new_version(
        id=version_id,
        description=version_description,
    )
    version_id = version.id
    success(f"New version [magenta]{version_id}[/magenta] created for application [magenta]{app_id}[/magenta].")

    return version_id, True


def _handle_instance_prompting(
    cloud_app: Application,
    app_id: str,
    version_id: str,
    now: datetime,
) -> None:
    """
    Handle interactive prompting for linking a version to an instance after a push.

    In interactive terminals, prompts the user to link the new version to an existing or new instance.
    If the terminal is non-interactive, skips prompting. Handles both updating existing instances and creating new ones.

    Parameters
    ----------
    cloud_app : Application
        The cloud application object to interact with Nextmv Cloud.
    app_id : str
        The application ID.
    version_id : str
        The version ID to link to an instance.
    now : datetime
        The current datetime, used for instance description if a new instance is created.
    """

    # If this is not an interactive terminal, do not ask for instance linking,
    # to avoid hanging indefinitely waiting for a user response.
    if not sys.stdin.isatty():
        info(
            msg="Non-interactive terminal detected. Skipping instance linking.",
            emoji=":bulb:",
        )

        return

    # Prompt the user for an instance ID to link the new version to.
    instance_id = Prompt.ask(
        f"Do you want to link version [magenta]{version_id}[/magenta] to an instance? If so, enter the instance ID. "
        "Leave blank to abort",
        case_sensitive=False,
    )
    if instance_id == "":
        info(
            msg="No instance ID provided. Skipping instance linking.",
            emoji=":bulb:",
        )
        return

    # Based on whether the instance exists or not, ask the user if they want to
    # update or create it.
    exists = cloud_app.instance_exists(instance_id=instance_id)

    # If the instance exists, ask if we want to update it.
    if exists:
        should_update = get_confirmation(
            msg=f"Instance [magenta]{instance_id}[/magenta] exists. "
            f"Do you want to link it to version [magenta]{version_id}[/magenta]?",
            default=True,
        )

        if not should_update:
            info(
                msg=f"Will not update instance [magenta]{instance_id}[/magenta].",
                emoji=":bulb:",
            )
            return

        _update_instance(
            cloud_app=cloud_app,
            app_id=app_id,
            version_id=version_id,
            instance_id=instance_id,
        )

        return

    # If the instance does not exist, ask if we want to create it.
    should_create = get_confirmation(
        msg=f"Instance [magenta]{instance_id}[/magenta] does not exist. "
        f"Do you want to create it using version [magenta]{version_id}[/magenta]?",
        default=True,
    )

    if not should_create:
        info(
            msg=f"Will not create instance [magenta]{instance_id}[/magenta].",
            emoji=":bulb:",
        )
        return

    _create_instance(
        cloud_app=cloud_app,
        app_id=app_id,
        version_id=version_id,
        instance_id=instance_id,
        now=now,
    )


def _update_instance(
    cloud_app: Application,
    app_id: str,
    version_id: str,
    instance_id: str,
) -> None:
    """
    Update an existing instance to use a new version.

    Parameters
    ----------
    cloud_app : Application
        The cloud application object to interact with Nextmv Cloud.
    app_id : str
        The application ID.
    version_id : str
        The version ID to link to the instance.
    instance_id : str
        The instance ID to update.
    """

    in_progress(f"Updating instance [magenta]{instance_id}[/magenta] to use version [magenta]{version_id}[/magenta]...")
    cloud_app.update_instance(id=instance_id, version_id=version_id)
    success(
        f"Instance [magenta]{instance_id}[/magenta] updated to use version [magenta]{version_id}[/magenta] "
        f"for application [magenta]{app_id}[/magenta]."
    )


def _create_instance(
    cloud_app: Application,
    app_id: str,
    version_id: str,
    instance_id: str,
    now: datetime,
) -> None:
    """
    Create a new instance linked to a specific version.

    Parameters
    ----------
    cloud_app : Application
        The cloud application object to interact with Nextmv Cloud.
    app_id : str
        The application ID.
    version_id : str
        The version ID to link to the new instance.
    instance_id : str
        The instance ID to create.
    now : datetime
        The current datetime, used for the instance description.
    """

    in_progress(f"Creating a new instance with ID [magenta]{instance_id}[/magenta]...")
    instance_description = f"Instance created automatically from push at {now.strftime('%Y-%m-%dT%H:%M:%SZ')}"
    instance = cloud_app.new_instance(
        version_id=version_id,
        id=instance_id,
        description=instance_description,
    )
    success(
        f"New instance [magenta]{instance.id}[/magenta] created using version [magenta]{version_id}[/magenta] "
        f"for application [magenta]{app_id}[/magenta]."
    )
