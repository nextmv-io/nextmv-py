"""
This module defines the cloud scenario delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import info, success
from nextmv.cli.options import AppIDOption, ProfileOption, ScenarioTestIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    scenario_test_id: ScenarioTestIDOption,
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
    Deletes a Nextmv Cloud scenario test.

    This action is permanent and cannot be undone. The scenario test and all
    associated data will be deleted. Use the --yes flag to skip
    the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the scenario test with the ID [magenta]hop-analysis[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud scenario delete --app-id hare-app --scenario-test-id hop-analysis[/dim]

    - Delete the scenario test without confirmation prompt.
        $ [dim]nextmv cloud scenario delete --app-id hare-app --scenario-test-id carrot-routes --yes[/dim]
    """

    if not yes:
        confirm = get_confirmation(
            f"Are you sure you want to delete scenario test [magenta]{scenario_test_id}[/magenta] "
            f"from application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(f"Scenario test [magenta]{scenario_test_id}[/magenta] will not be deleted.")
            return

    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.delete_scenario_test(scenario_test_id=scenario_test_id)
    success(msg=f"Scenario test [magenta]{scenario_test_id}[/magenta] deleted.")
