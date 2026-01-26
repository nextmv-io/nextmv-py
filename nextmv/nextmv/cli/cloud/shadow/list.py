"""
This module defines the cloud shadow list command for the Nextmv CLI.
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

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Listing shadow tests...")
    shadow_tests = cloud_app.list_shadow_tests()
    shadow_tests_dict = [test.to_dict() for test in shadow_tests]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(shadow_tests_dict, f, indent=2)

        success(msg=f"Shadow tests list saved to [magenta]{output}[/magenta].")

        return

    print_json(shadow_tests_dict)
