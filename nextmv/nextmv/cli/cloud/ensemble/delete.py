"""
This module defines the cloud ensemble delete command for the Nextmv CLI.
"""

import typer

from nextmv.cli.configuration.config import build_cloud_app
from nextmv.cli.message import confirmation, info, success
from nextmv.cli.options import AppIDOption, DebugOption, EnsembleDefinitionIDOption, ProfileOption, YesOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    ensemble_definition_id: EnsembleDefinitionIDOption,
    yes: YesOption = False,
    _: DebugOption = False,
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
        confirm = confirmation(
            f"Are you sure you want to delete ensemble definition [magenta]{ensemble_definition_id}[/magenta] "
            f"from application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(f"Ensemble definition [magenta]{ensemble_definition_id}[/magenta] will not be deleted.")
            return

    cloud_app, _ = build_cloud_app(app_id=app_id, profile=profile)
    cloud_app.delete_ensemble_definition(ensemble_definition_id=ensemble_definition_id)
    success(
        f"Ensemble definition [magenta]{ensemble_definition_id}[/magenta] deleted successfully "
        f"from application [magenta]{app_id}[/magenta]."
    )
