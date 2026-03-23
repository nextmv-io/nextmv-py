"""
This module defines the cloud run delete command for the Nextmv CLI.
"""

import typer

from nextmv.cli.configuration.config import build_cloud_app
from nextmv.cli.message import confirmation, info, success
from nextmv.cli.options import AppIDOption, ProfileOption, RunIDOption, YesOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    run_id: RunIDOption,
    yes: YesOption = False,
    profile: ProfileOption = None,
) -> None:
    """
    Deletes a Nextmv Cloud application run.

    This action is permanent and cannot be undone. Use the --yes
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the run with ID [magenta]burrow-123[/magenta] belonging to an app with ID [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud run delete --app-id hare-app --run-id burrow-123[/dim]

    - Delete the run with ID [magenta]burrow-123[/magenta] belonging to an app with ID [magenta]hare-app[/magenta].
      Use the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud run delete --app-id hare-app --run-id burrow-123 --profile hare[/dim]
    """

    if not yes:
        confirm = confirmation(
            f"Are you sure you want to delete run [magenta]{run_id}[/magenta] from "
            f"application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(f"Run [magenta]{run_id}[/magenta] from application [magenta]{app_id}[/magenta] will not be deleted.")
            return

    cloud_app, _ = build_cloud_app(app_id=app_id, profile=profile)
    cloud_app.delete_run(run_id)
    success(f"Run [magenta]{run_id}[/magenta] from application [magenta]{app_id}[/magenta] deleted successfully.")
