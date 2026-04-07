"""
This module defines the cloud shadow list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.actions.shadow import list_shadow_tests as _list_shadow_tests
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.client import Client

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
            help="Saves the list of shadow tests to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    List all Nextmv Cloud shadow tests for an application.

    This command retrieves all shadow tests associated with the specified
    application.

    [bold][underline]Examples[/underline][/bold]

    - List all shadow tests for application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud shadow list --app-id hare-app[/dim]

    - List all shadow tests and save to a file.
        $ [dim]nextmv cloud shadow list --app-id hare-app --output tests.json[/dim]

    - List all shadow tests using a specific profile.
        $ [dim]nextmv cloud shadow list --app-id hare-app --profile prod[/dim]
    """

    client = Client(profile=profile)
    in_progress(msg="Listing shadow tests...")
    shadow_tests_dict = _list_shadow_tests(client, app_id)

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(shadow_tests_dict, f, indent=2)

        success(msg=f"Shadow tests list saved to [magenta]{output}[/magenta].")

        return

    print_json(shadow_tests_dict)
