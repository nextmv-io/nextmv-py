"""
This module defines the cloud shadow delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import info, success
from nextmv.cli.options import AppIDOption, ProfileOption, ShadowTestIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    shadow_test_id: ShadowTestIDOption,
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
    Deletes a Nextmv Cloud shadow test.

    This action is permanent and cannot be undone. The shadow test and all
    associated data, including runs, will be deleted. Use the --yes
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the shadow test with the ID [magenta]hop-analysis[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud shadow delete --app-id hare-app --shadow-test-id hop-analysis[/dim]

    - Delete the shadow test without confirmation prompt.
        $ [dim]nextmv cloud shadow delete --app-id hare-app --shadow-test-id carrot-routes --yes[/dim]
    """

    if not yes:
        confirm = get_confirmation(
            f"Are you sure you want to delete shadow test [magenta]{shadow_test_id}[/magenta] "
            f"from application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(f"Shadow test [magenta]{shadow_test_id}[/magenta] will not be deleted.")
            return

    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.delete_shadow_test(shadow_test_id=shadow_test_id)
    success(
        f"Shadow test [magenta]{shadow_test_id}[/magenta] deleted successfully "
        f"from application [magenta]{app_id}[/magenta]."
    )
