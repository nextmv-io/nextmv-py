"""
This module defines the cloud run list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def list(
    app_id: AppIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the list of runs to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get the list of runs for a Nextmv Cloud application.

    By default, the list of runs is fetched and printed to [magenta]stdout[/magenta].
    Use the [code]--output[/code] flag to save the list to a file.

    [bold][underline]Examples[/underline][/bold]

    - Get the list of runs for an app with ID [magenta]hare-app[/magenta]. List is printed to [magenta]stdout[/magenta].
        $ [green]nextmv cloud run list --app-id hare-app[/green]

    - Get the list of runs for an app with ID [magenta]hare-app[/magenta]. Save the list to a
      [magenta]runs.json[/magenta] file.
        $ [green]nextmv cloud run list --app-id hare-app --output runs.json[/green]

    - Get the list of runs for an app with ID [magenta]hare-app[/magenta].
      Use the profile named [magenta]hare[/magenta].
        $ [green]nextmv cloud run list --app-id hare-app --profile hare[/green]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Listing app runs...")
    runs = cloud_app.list_runs()
    runs_dicts = [run.to_dict() for run in runs]

    if output is not None:
        with open(output, "w") as f:
            json.dump(runs_dicts, f, indent=2)

        success(msg=f"Run list saved to [magenta]{output}[/magenta].")

        return

    print_json(runs_dicts)
