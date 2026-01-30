"""
This module defines the cloud input-set delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import info, success
from nextmv.cli.options import AppIDOption, InputSetIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    input_set_id: InputSetIDOption,
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
    Deletes a Nextmv Cloud input set.

    This action is permanent and cannot be undone. The input set and all
    associated data will be deleted. Use the --yes flag to skip the
    confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the input set with the ID [magenta]hop-analysis[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud input-set delete --app-id hare-app --input-set-id hop-analysis[/dim]

    - Delete the input set without confirmation prompt.
        $ [dim]nextmv cloud input-set delete --app-id hare-app --input-set-id carrot-routes --yes[/dim]
    """

    if not yes:
        confirm = get_confirmation(
            f"Are you sure you want to delete input set [magenta]{input_set_id}[/magenta] "
            f"from application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(f"Input set [magenta]{input_set_id}[/magenta] will not be deleted.")
            return

    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.delete_input_set(input_set_id=input_set_id)
    success(
        f"Input set [magenta]{input_set_id}[/magenta] deleted successfully "
        f"from application [magenta]{app_id}[/magenta]."
    )
