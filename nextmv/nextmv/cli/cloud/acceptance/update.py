"""
This module defines the cloud acceptance update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AcceptanceTestIDOption, AppIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def update(
    app_id: AppIDOption,
    acceptance_test_id: AcceptanceTestIDOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Updated description of the acceptance test.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Updated name of the acceptance test.",
            metavar="NAME",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated acceptance test information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Update a Nextmv Cloud acceptance test.

    Update the name and/or description of an acceptance test. Any fields not
    specified will remain unchanged.

    [bold][underline]Examples[/underline][/bold]

    - Update the name of an acceptance test.
        $ [dim]nextmv cloud acceptance update --app-id hare-app \\
            --acceptance-test-id test-123 --name "Updated Test Name"[/dim]

    - Update the description of an acceptance test.
        $ [dim]nextmv cloud acceptance update --app-id hare-app \\
            --acceptance-test-id test-123 --description "Updated description"[/dim]

    - Update both name and description and save the result.
        $ [dim]nextmv cloud acceptance update --app-id hare-app \\
            --acceptance-test-id test-123 --name "New Name" \\
            --description "New description" --output updated-test.json[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)

    in_progress(msg="Updating acceptance test...")
    acceptance_test = cloud_app.update_acceptance_test(
        acceptance_test_id=acceptance_test_id,
        name=name,
        description=description,
    )
    success(
        f"Acceptance test [magenta]{acceptance_test_id}[/magenta] updated successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )

    acceptance_test_dict = acceptance_test.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(acceptance_test_dict, f, indent=2)

        success(msg=f"Updated acceptance test information saved to [magenta]{output}[/magenta].")
        return

    print_json(acceptance_test_dict)
