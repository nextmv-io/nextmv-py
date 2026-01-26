"""
This module defines the cloud switchback metadata command for the Nextmv CLI.
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
def metadata(
    app_id: AppIDOption,
    switchback_test_id: SwitchbackTestIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the switchback test metadata to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get metadata for a Nextmv Cloud switchback test.

    This command retrieves metadata for a specific switchback test, including
    status, creation date, and other high-level information without the full
    run details.

    [bold][underline]Examples[/underline][/bold]

    - Get metadata for switchback test [magenta]bunny-warren-optimization[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud switchback metadata --app-id hare-app \\
            --switchback-test-id bunny-warren-optimization[/dim]

    - Get metadata and save to a file.
        $ [dim]nextmv cloud switchback metadata --app-id hare-app --switchback-test-id lettuce-delivery \\
            --output metadata.json[/dim]

    - Get metadata using a specific profile.
        $ [dim]nextmv cloud switchback metadata --app-id hare-app --switchback-test-id hop-schedule \\
            --profile prod[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Getting switchback test metadata...")
    switchback_metadata = cloud_app.switchback_test_metadata(switchback_test_id=switchback_test_id)
    switchback_metadata_dict = switchback_metadata.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(switchback_metadata_dict, f, indent=2)

        success(msg=f"Switchback test metadata saved to [magenta]{output}[/magenta].")
        return

    print_json(switchback_metadata_dict)
