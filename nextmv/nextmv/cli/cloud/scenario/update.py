"""
This module defines the cloud scenario update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption, ScenarioTestIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def update(
    app_id: AppIDOption,
    scenario_test_id: ScenarioTestIDOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Updated description of the scenario test.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Updated name of the scenario test.",
            metavar="NAME",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated scenario test information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Update a Nextmv Cloud scenario test.

    Update the name and/or description of a scenario test. Any fields not
    specified will remain unchanged.

    [bold][underline]Examples[/underline][/bold]

    - Update the name of a scenario test.
        $ [dim]nextmv cloud scenario update --app-id hare-app --scenario-test-id carrot-feast \\
            --name "Spring Carrot Harvest"[/dim]

    - Update the description of a scenario test.
        $ [dim]nextmv cloud scenario update --app-id hare-app --scenario-test-id bunny-hop-routes \\
            --description "Optimizing hop paths through the meadow"[/dim]

    - Update both name and description and save the result.
        $ [dim]nextmv cloud scenario update --app-id hare-app --scenario-test-id lettuce-delivery \\
            --name "Warren Lettuce Express" --description "Fast lettuce delivery to all burrows" \\
            --output updated-scenario.json[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Updating scenario test...")
    scenario_info = cloud_app.update_scenario_test(
        scenario_test_id=scenario_test_id,
        name=name,
        description=description,
    )
    success(
        f"Scenario test [magenta]{scenario_test_id}[/magenta] updated successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
    scenario_info_dict = scenario_info.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(scenario_info_dict, f, indent=2)

        success(msg=f"Scenario test information saved to [magenta]{output}[/magenta].")
        return

    print_json(scenario_info_dict)
