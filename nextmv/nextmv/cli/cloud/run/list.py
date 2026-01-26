"""
This module defines the cloud run list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import enum_values, in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.status import StatusV2

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
    status: Annotated[
        StatusV2 | None,
        typer.Option(
            "--status",
            "-s",
            help=f"Filter runs by their status. Allowed values are: {enum_values(StatusV2)}.",
            metavar="STATUS",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get the list of runs for a Nextmv Cloud application.

    By default, the list of runs is fetched and printed to [magenta]stdout[/magenta].
    Use the --output flag to save the list to a file.

    You can use the optional --status flag to filter runs by their status.

    [bold][underline]Examples[/underline][/bold]

    - Get the list of runs for an app with ID [magenta]hare-app[/magenta]. List is printed to [magenta]stdout[/magenta].
        $ [dim]nextmv cloud run list --app-id hare-app[/dim]

    - Get the list of runs for an app with ID [magenta]hare-app[/magenta]. Save the list to a
      [magenta]runs.json[/magenta] file.
        $ [dim]nextmv cloud run list --app-id hare-app --output runs.json[/dim]

    - Get the list of runs for an app with ID [magenta]hare-app[/magenta].
      Use the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud run list --app-id hare-app --profile hare[/dim]

    - Get the list of [magenta]queued[/magenta] runs for an app with ID [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud run list --app-id hare-app --status queued[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Listing app runs...")
    runs = cloud_app.list_runs(status=status)
    runs_dicts = [run.to_dict() for run in runs]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(runs_dicts, f, indent=2)

        success(msg=f"Run list saved to [magenta]{output}[/magenta].")

        return

    print_json(runs_dicts)
