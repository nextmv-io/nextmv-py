"""
This module defines the cloud switchback list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.actions.switchback import list_switchback_tests as _list_switchback_tests
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
            help="Saves the list of switchback tests to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    List all Nextmv Cloud switchback tests for an application.

    This command retrieves all switchback tests associated with the specified
    application.

    [bold][underline]Examples[/underline][/bold]

    - List all switchback tests for application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud switchback list --app-id hare-app[/dim]

    - List all switchback tests and save to a file.
        $ [dim]nextmv cloud switchback list --app-id hare-app --output tests.json[/dim]

    - List all switchback tests using a specific profile.
        $ [dim]nextmv cloud switchback list --app-id hare-app --profile prod[/dim]
    """

    client = Client(profile=profile)
    in_progress(msg="Listing switchback tests...")
    switchback_tests_dict = _list_switchback_tests(client, app_id)

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(switchback_tests_dict, f, indent=2)

        success(msg=f"Switchback tests list saved to [magenta]{output}[/magenta].")

        return

    print_json(switchback_tests_dict)
