"""
This module defines the cloud scenario metadata command for the Nextmv CLI.
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
def metadata(
    app_id: AppIDOption,
    scenario_test_id: ScenarioTestIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the scenario test metadata to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get metadata for a Nextmv Cloud scenario test.

    This command retrieves metadata for a specific scenario test, including
    status, creation date, and other high-level information without the full
    run details.

    [bold][underline]Examples[/underline][/bold]

    - Get metadata for scenario test [magenta]bunny-warren-optimization[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud scenario metadata --app-id hare-app --scenario-test-id bunny-warren-optimization[/dim]

    - Get metadata and save to a file.
        $ [dim]nextmv cloud scenario metadata --app-id hare-app --scenario-test-id lettuce-delivery \\
            --output metadata.json[/dim]

    - Get metadata using a specific profile.
        $ [dim]nextmv cloud scenario metadata --app-id hare-app --scenario-test-id hop-schedule --profile prod[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Getting scenario test metadata...")
    scenario_metadata = cloud_app.scenario_test_metadata(scenario_test_id=scenario_test_id)
    scenario_metadata_dict = scenario_metadata.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(scenario_metadata_dict, f, indent=2)

        success(msg=f"Scenario test metadata saved to [magenta]{output}[/magenta].")

        return

    print_json(scenario_metadata_dict)
