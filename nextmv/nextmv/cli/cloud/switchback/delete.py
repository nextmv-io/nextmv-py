"""
This module defines the cloud switchback delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import info, success
from nextmv.cli.options import AppIDOption, ProfileOption, SwitchbackTestIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    switchback_test_id: SwitchbackTestIDOption,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Agree to deletion confirmation prompt. Useful for non-interactive sessions.",
        ),
    ] = False,
    profile: ProfileOption = None,
) -> None:
    """
    Deletes a Nextmv Cloud switchback test.

    This action is permanent and cannot be undone. The switchback test and all
    associated data, including runs, will be deleted. Use the --yes
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the switchback test with the ID [magenta]hop-analysis[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud switchback delete --app-id hare-app --switchback-test-id hop-analysis[/dim]

    - Delete the switchback test without confirmation prompt.
        $ [dim]nextmv cloud switchback delete --app-id hare-app --switchback-test-id carrot-routes --yes[/dim]
    """

    if not yes:
        confirm = get_confirmation(
            f"Are you sure you want to delete switchback test [magenta]{switchback_test_id}[/magenta] "
            f"from application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(f"Switchback test [magenta]{switchback_test_id}[/magenta] will not be deleted.")
            return

    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.delete_switchback_test(switchback_test_id=switchback_test_id)
    success(
        f"Switchback test [magenta]{switchback_test_id}[/magenta] deleted successfully "
        f"from application [magenta]{app_id}[/magenta]."
    )
