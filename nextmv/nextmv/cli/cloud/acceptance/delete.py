"""
This module defines the cloud acceptance delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import info, success
from nextmv.cli.options import AcceptanceTestIDOption, AppIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    acceptance_test_id: AcceptanceTestIDOption,
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
    Deletes a Nextmv Cloud acceptance test.

    This action is permanent and cannot be undone. The underlying batch
    experiment and associated data will also be deleted. Use the --yes flag to
    skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the acceptance test with the ID [magenta]test-cotton-tail[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud acceptance delete --app-id hare-app --acceptance-test-id test-cotton-tail[/dim]

    - Delete the acceptance test without confirmation prompt.
        $ [dim]nextmv cloud acceptance delete --app-id hare-app --acceptance-test-id test-cotton-tail --yes[/dim]
    """

    if not yes:
        confirm = get_confirmation(
            f"Are you sure you want to delete acceptance test [magenta]{acceptance_test_id}[/magenta] "
            f"from application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(f"Acceptance test [magenta]{acceptance_test_id}[/magenta] will not be deleted.")
            return

    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.delete_acceptance_test(acceptance_test_id=acceptance_test_id)
    success(
        f"Acceptance test [magenta]{acceptance_test_id}[/magenta] deleted successfully "
        f"from application [magenta]{app_id}[/magenta]."
    )
