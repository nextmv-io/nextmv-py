"""
This module defines the cloud acceptance list command for the Nextmv CLI.
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
            help="Saves the list of acceptance tests to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    List all Nextmv Cloud acceptance tests for an application.

    This command retrieves all acceptance tests associated with the specified
    application.

    [bold][underline]Examples[/underline][/bold]

    - List all acceptance tests for application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud acceptance list --app-id hare-app[/dim]

    - List all acceptance tests and save to a file.
        $ [dim]nextmv cloud acceptance list --app-id hare-app --output tests.json[/dim]

    - List all acceptance tests using a specific profile.
        $ [dim]nextmv cloud acceptance list --app-id hare-app --profile prod[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Listing acceptance tests...")
    acceptance_tests = cloud_app.list_acceptance_tests()
    acceptance_tests_dict = [test.to_dict() for test in acceptance_tests]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(acceptance_tests_dict, f, indent=2)

        success(msg=f"Acceptance tests list saved to [magenta]{output}[/magenta].")
        return

    print_json(acceptance_tests_dict)
