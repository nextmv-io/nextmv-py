"""
This module defines the cloud instance list command for the Nextmv CLI.
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
            help="Saves the instance list information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    List all instances of a Nextmv Cloud application.

    [bold][underline]Examples[/underline][/bold]

    - List all instances of application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud instance list --app-id hare-app[/dim]

    - List all instances using the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud instance list --app-id hare-app --profile hare[/dim]

    - List all instances and save the information to a [magenta]instances.json[/magenta] file.
        $ [dim]nextmv cloud instance list --app-id hare-app --output instances.json[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Listing instances...")
    instances = cloud_app.list_instances()
    instances_dicts = [instance.to_dict() for instance in instances]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(instances_dicts, f, indent=2)

        success(msg=f"Instance list information saved to [magenta]{output}[/magenta].")

        return

    print_json(instances_dicts)
