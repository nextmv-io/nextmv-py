"""
This module defines the cloud run queue command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_account
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def queue(
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
    List current queued runs within the Nextmv Cloud account (organization).

    [bold][underline]Examples[/underline][/bold]

    - List all queued runs.
        $ [green]nextmv cloud run queue[/green]

    - List all queued runs using the profile named [magenta]hare[/magenta].
        $ [green]nextmv cloud run queue --profile hare[/green]

    - List all queued runs and save the information to a [magenta]queue.json[/magenta] file.
        $ [green]nextmv cloud run queue --output queue.json[/green]
    """

    cloud_account = build_account(profile=profile)
    in_progress(msg="Getting runs queue...")
    queue = cloud_account.queue()
    queue_dict = queue.to_dict()

    if output is not None:
        with open(output, "w") as f:
            json.dump(queue_dict, f, indent=2)

        success(msg=f"Runs queue information saved to [magenta]{output}[/magenta].")

        return

    print_json(queue_dict)
