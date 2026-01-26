"""
This module defines the cloud shadow get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption, ShadowTestIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    app_id: AppIDOption,
    shadow_test_id: ShadowTestIDOption,
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
    Get a Nextmv Cloud shadow test, including its runs.

    [bold][underline]Examples[/underline][/bold]

    - Get the shadow test with ID [magenta]carrot-optimization[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud shadow get --app-id hare-app --shadow-test-id carrot-optimization[/dim]

    - Get the shadow test using a specific profile.
        $ [dim]nextmv cloud shadow get --app-id hare-app --shadow-test-id lettuce-routes --profile prod[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Getting shadow test...")
    shadow_test = cloud_app.shadow_test(shadow_test_id=shadow_test_id)

    shadow_test_dict = shadow_test.to_dict()

    # Handle output
    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(shadow_test_dict, f, indent=2)

        success(msg=f"Shadow test output saved to [magenta]{output}[/magenta].")

        return

    print_json(shadow_test_dict)
