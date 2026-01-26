"""
This module defines the cloud instance get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, InstanceIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    app_id: AppIDOption,
    instance_id: InstanceIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the instance information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get a Nextmv Cloud application instance.

    This command is useful to get the attributes of an existing Nextmv Cloud
    application instance by its ID.

    [bold][underline]Examples[/underline][/bold]

    - Get the instance with the ID [magenta]prod[/magenta] from application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud instance get --app-id hare-app --instance-id prod[/dim]

    - Get the instance with the ID [magenta]prod[/magenta] and save the information to a
      [magenta]instance.json[/magenta] file.
        $ [dim]nextmv cloud instance get --app-id hare-app --instance-id prod --output instance.json[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Getting instance...")
    instance = cloud_app.instance(instance_id=instance_id)
    instance_dict = instance.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(instance_dict, f, indent=2)

        success(msg=f"Instance information saved to [magenta]{output}[/magenta].")

        return

    print_json(instance_dict)
