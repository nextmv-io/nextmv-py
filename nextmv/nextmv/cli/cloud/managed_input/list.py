"""
This module defines the cloud managed-input list command for the Nextmv CLI.
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
            help="Saves the managed input list information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    List all managed inputs of a Nextmv Cloud application.

    [bold][underline]Examples[/underline][/bold]

    - List all managed inputs of application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud managed-input list --app-id hare-app[/dim]

    - List all managed inputs using the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud managed-input list --app-id hare-app --profile hare[/dim]

    - List all managed inputs and save the information to a [magenta]managed_inputs.json[/magenta] file.
        $ [dim]nextmv cloud managed-input list --app-id hare-app --output managed_inputs.json[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Listing managed inputs...")
    managed_inputs = cloud_app.list_managed_inputs()
    managed_inputs_dicts = [managed_input.to_dict() for managed_input in managed_inputs]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(managed_inputs_dicts, f, indent=2)

        success(msg=f"Managed input list information saved to [magenta]{output}[/magenta].")

        return

    print_json(managed_inputs_dicts)
