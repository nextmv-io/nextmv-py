"""
This module defines the local app sync command for the Nextmv CLI.
"""

import os
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_cloud_app, build_local_app
from nextmv.cli.message import in_progress
from nextmv.cli.options import LocalAppIDOption, LocalAppSrcOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def sync(
    target_app_id: Annotated[
        str,
        typer.Option(
            "--target-app-id",
            "-t",
            help="The target Nextmv Cloud application ID to sync to.",
            envvar="NEXTMV_TARGET_APP_ID",
            metavar="TARGET_APP_ID",
        ),
    ],
    app_id: LocalAppIDOption = None,
    app_src: LocalAppSrcOption = None,
    instance_id: Annotated[
        str | None,
        typer.Option(
            "--instance-id",
            "-i",
            help="Optional Cloud instance ID if you want to associate the runs with a specific instance.",
            metavar="INSTANCE_ID",
        ),
    ] = None,
    run_ids: Annotated[
        list[str] | None,
        typer.Option(
            "--run-ids",
            "-r",
            help="List of run IDs to sync. All are used if not specified. Pass multiple run IDs by repeating the flag.",
            metavar="RUN_IDS",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Sync a local Nextmv application to the Nextmv Cloud.

    You may identify the app by using --app-src, or --app-id if it has been
    registered. If the app is not already registered, this command will
    register it. Using the --run-ids option allows you to specify a subset of
    runs to sync. By default, all runs are synced. You can also specify an
    --instance-id to associate the synced runs with a specific Cloud instance.

    [bold][underline]Examples[/underline][/bold]

    - Sync the registered local application with the ID [magenta]hare-app[/magenta] to the Cloud application
        with the ID [magenta]hare-cloud-app[/magenta], syncing all runs.
        $ [dim]nextmv local app sync --target-app-id hare-cloud-app --app-id hare-app[/dim]

    - Sync the local application at source path [magenta]./hare_app[/magenta] to the Cloud application
        with the ID [magenta]hare-cloud-app[/magenta], syncing only runs [magenta]run1, run2[/magenta].
        $ [dim]nextmv local app sync --target-app-id hare-cloud-app --app-src ./hare_app \\
            --run-ids run1 --run-ids run2[/dim]

    - Sync the registered local application with the ID [magenta]hare-app[/magenta] to the Cloud application
        with the ID [magenta]hare-cloud-app[/magenta], linking runs to instance [magenta]fluffy-inst[/magenta].
        $ [dim]nextmv local app sync --target-app-id hare-cloud-app --app-id hare-app --instance-id fluffy-inst[/dim]

    - Sync local applications using the profile named [magenta]hare[/magenta].
        $ [dim]nextmv local app sync --target-app-id hare-cloud-app --app-id hare-app --profile hare[/dim]
    """

    if (app_id is None or app_id == "") and (app_src is None or app_src == ""):
        app_src = "."

    if app_src is not None and app_src != "":
        app_src = os.path.abspath(app_src)

    local_app = build_local_app(app_src, app_id)
    in_progress(msg="Getting target application...")
    cloud_app = build_cloud_app(app_id=target_app_id, profile=profile)

    local_app.sync(
        target=cloud_app,
        run_ids=run_ids,
        instance_id=instance_id,
        verbose=True,
        rich_print=True,
    )
