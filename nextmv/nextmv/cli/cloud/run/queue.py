"""
This module defines the cloud run queue command for the Nextmv CLI.
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
def queue(
    app_id: AppIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the runs queue information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    List current queued runs within the Nextmv Cloud application.

    [bold][underline]Examples[/underline][/bold]

    - List all queued runs of an application with ID [magenta]hare-app[/magenta].
        $ [green]nextmv cloud run queue --app-id hare-app[/green]

    - List all queued runs using the profile named [magenta]hare[/magenta].
        $ [green]nextmv cloud run queue --app-id hare-app --profile hare[/green]

    - List all queued runs and save the information to a [magenta]queue.json[/magenta] file.
        $ [green]nextmv cloud run queue --app-id hare-app --output queue.json[/green]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Getting runs queue...")
    queue = cloud_app.run_queue()
    queue_dict = queue.to_dict()

    if output is not None:
        with open(output, "w") as f:
            json.dump(queue_dict, f, indent=2)

        success(msg=f"Runs queue information saved to [magenta]{output}[/magenta].")

        return

    print_json(queue_dict)
