"""
This module defines the cloud switchback list command for the Nextmv CLI.
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

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Listing switchback tests...")
    switchback_tests = cloud_app.list_switchback_tests()
    switchback_tests_dict = [test.to_dict() for test in switchback_tests]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(switchback_tests_dict, f, indent=2)

        success(msg=f"Switchback tests list saved to [magenta]{output}[/magenta].")

        return

    print_json(switchback_tests_dict)
