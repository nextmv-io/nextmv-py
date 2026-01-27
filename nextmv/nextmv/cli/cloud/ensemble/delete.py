"""
This module defines the cloud ensemble delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import info, success
from nextmv.cli.options import AppIDOption, EnsembleDefinitionIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    ensemble_definition_id: EnsembleDefinitionIDOption,
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
    Deletes a Nextmv Cloud ensemble definition.

    This action is permanent and cannot be undone. Use the --yes
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the ensemble definition with the ID [magenta]prod-ensemble[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud ensemble delete --app-id hare-app --ensemble-definition-id prod-ensemble[/dim]

    - Delete the ensemble definition without confirmation prompt.
        $ [dim]nextmv cloud ensemble delete --app-id hare-app --ensemble-definition-id prod-ensemble --yes[/dim]
    """

    if not yes:
        confirm = get_confirmation(
            f"Are you sure you want to delete ensemble definition [magenta]{ensemble_definition_id}[/magenta] "
            f"from application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(
                msg=f"Ensemble definition [magenta]{ensemble_definition_id}[/magenta] will not be deleted.",
                emoji=":bulb:",
            )
            return

    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.delete_ensemble_definition(ensemble_definition_id=ensemble_definition_id)
    success(
        f"Ensemble definition [magenta]{ensemble_definition_id}[/magenta] deleted successfully "
        f"from application [magenta]{app_id}[/magenta]."
    )
