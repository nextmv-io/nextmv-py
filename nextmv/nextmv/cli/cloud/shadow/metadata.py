"""
This module defines the cloud shadow metadata command for the Nextmv CLI.
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
def metadata(
    app_id: AppIDOption,
    shadow_test_id: ShadowTestIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the shadow test metadata to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get metadata for a Nextmv Cloud shadow test.

    This command retrieves metadata for a specific shadow test, including
    status, creation date, and other high-level information without the full
    run details.

    [bold][underline]Examples[/underline][/bold]

    - Get metadata for shadow test [magenta]bunny-warren-optimization[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud shadow metadata --app-id hare-app --shadow-test-id bunny-warren-optimization[/dim]

    - Get metadata and save to a file.
        $ [dim]nextmv cloud shadow metadata --app-id hare-app --shadow-test-id lettuce-delivery \\
            --output metadata.json[/dim]

    - Get metadata using a specific profile.
        $ [dim]nextmv cloud shadow metadata --app-id hare-app --shadow-test-id hop-schedule --profile prod[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Getting shadow test metadata...")
    shadow_metadata = cloud_app.shadow_test_metadata(shadow_test_id=shadow_test_id)
    shadow_metadata_dict = shadow_metadata.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(shadow_metadata_dict, f, indent=2)

        success(msg=f"Shadow test metadata saved to [magenta]{output}[/magenta].")
        return

    print_json(shadow_metadata_dict)
