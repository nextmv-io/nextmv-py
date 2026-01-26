"""
This module defines the cloud switchback update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption, SwitchbackTestIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def update(
    app_id: AppIDOption,
    switchback_test_id: SwitchbackTestIDOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Updated description of the switchback test.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Updated name of the switchback test.",
            metavar="NAME",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated switchback test information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Update a Nextmv Cloud switchback test.

    Update the name and/or description of a switchback test. Any fields not
    specified will remain unchanged.

    [bold][underline]Examples[/underline][/bold]

    - Update the name of a switchback test.
        $ [dim]nextmv cloud switchback update --app-id hare-app --switchback-test-id carrot-feast \\
            --name "Spring Carrot Harvest"[/dim]

    - Update the description of a switchback test.
        $ [dim]nextmv cloud switchback update --app-id hare-app --switchback-test-id bunny-hop-routes \\
            --description "Optimizing hop paths through the meadow"[/dim]

    - Update both name and description and save the result.
        $ [dim]nextmv cloud switchback update --app-id hare-app --switchback-test-id lettuce-delivery \\
            --name "Warren Lettuce Express" --description "Fast lettuce delivery to all burrows" \\
            --output updated-switchback-test.json[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)

    in_progress(msg="Updating switchback test...")
    switchback_test = cloud_app.update_switchback_test(
        switchback_test_id=switchback_test_id,
        name=name,
        description=description,
    )

    switchback_test_dict = switchback_test.to_dict()
    success(
        f"Switchback test [magenta]{switchback_test_id}[/magenta] updated successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(switchback_test_dict, f, indent=2)

        success(msg=f"Updated switchback test information saved to [magenta]{output}[/magenta].")

        return

    print_json(switchback_test_dict)
