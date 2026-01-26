"""
This module defines the cloud managed-input get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ManagedInputIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    app_id: AppIDOption,
    managed_input_id: ManagedInputIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the managed input information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get a Nextmv Cloud application managed input.

    This command is useful to get the attributes of an existing Nextmv Cloud
    application managed input by its ID.

    [bold][underline]Examples[/underline][/bold]

    - Get the managed input with the ID [magenta]inp_123456789[/magenta] from application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud managed-input get --app-id hare-app --managed-input-id inp_123456789[/dim]

    - Get the managed input with the ID [magenta]inp_123456789[/magenta] and save the information to a
      [magenta]managed_input.json[/magenta] file.
        $ [dim]nextmv cloud managed-input get --app-id hare-app --managed-input-id inp_123456789 \
            --output managed_input.json[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Getting managed input...")
    managed_input = cloud_app.managed_input(managed_input_id=managed_input_id)
    managed_input_dict = managed_input.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(managed_input_dict, f, indent=2)

        success(msg=f"Managed input information saved to [magenta]{output}[/magenta].")

        return

    print_json(managed_input_dict)
