"""
This module defines the cloud scenario list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.actions.scenario import list_scenario_tests as _list_scenario_tests
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
            help="Saves the list of scenario tests to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    List all Nextmv Cloud scenario tests for an application.

    This command retrieves all scenario tests associated with the specified
    application.

    [bold][underline]Examples[/underline][/bold]

    - List all scenario tests for application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud scenario list --app-id hare-app[/dim]

    - List all scenario tests and save to a file.
        $ [dim]nextmv cloud scenario list --app-id hare-app --output scenario_tests.json[/dim]

    - List all scenario tests using a specific profile.
        $ [dim]nextmv cloud scenario list --app-id hare-app --profile prod[/dim]
    """

    client = Client(profile=profile)
    in_progress(msg="Listing scenario tests...")
    scenario_tests_dict = _list_scenario_tests(client, app_id)

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(scenario_tests_dict, f, indent=2)

        success(msg=f"Scenario tests list saved to [magenta]{output}[/magenta].")

        return

    print_json(scenario_tests_dict)
