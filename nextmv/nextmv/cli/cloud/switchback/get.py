"""
This module defines the cloud switchback get command for the Nextmv CLI.
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
def get(
    app_id: AppIDOption,
    switchback_test_id: SwitchbackTestIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the results to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get a Nextmv Cloud switchback test, including its runs.

    [bold][underline]Examples[/underline][/bold]

    - Get the switchback test with ID [magenta]carrot-optimization[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud switchback get --app-id hare-app --switchback-test-id carrot-optimization[/dim]

    - Get the switchback test using a specific profile.
        $ [dim]nextmv cloud switchback get --app-id hare-app --switchback-test-id lettuce-routes \\
            --profile prod[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Getting switchback test...")
    switchback_test = cloud_app.switchback_test(switchback_test_id=switchback_test_id)

    switchback_test_dict = switchback_test.to_dict()

    # Handle output
    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(switchback_test_dict, f, indent=2)

        success(msg=f"Switchback test output saved to [magenta]{output}[/magenta].")

        return

    print_json(switchback_test_dict)
