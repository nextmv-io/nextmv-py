"""
This module defines the cloud run information command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_cloud_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, DebugOption, ProfileOption, RunIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def information(
    app_id: AppIDOption,
    run_id: RunIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    _: DebugOption = False,
    profile: ProfileOption = None,
) -> None:
    """
    Get the information of a Nextmv Cloud application run.

    By default, the information (including metadata) is fetched and printed to
    [magenta]stdout[/magenta]. Use the --output flag to save the information to
    a file.

    [bold][underline]Examples[/underline][/bold]

    - Get the information of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Information is printed to [magenta]stdout[/magenta].
        $ [dim]nextmv cloud run information --app-id hare-app --run-id burrow-123[/dim]

    - Get the information of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Save the information to a [magenta]information.json[/magenta] file.
        $ [dim]nextmv cloud run information --app-id hare-app --run-id burrow-123 --output information.json[/dim]

    - Get the information of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Use the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud run information --app-id hare-app --run-id burrow-123 --profile hare[/dim]
    """

    cloud_app, _ = build_cloud_app(app_id=app_id, profile=profile)
    in_progress(msg="Getting run information...")
    run_info = cloud_app.run_information(run_id)
    info_dict = run_info.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(info_dict, f, indent=2)

        success(msg=f"Run information saved to [magenta]{output}[/magenta].")

        return

    print_json(info_dict)
