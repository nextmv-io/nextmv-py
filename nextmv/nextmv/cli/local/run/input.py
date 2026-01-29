"""
This module defines the cloud run input command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.options import AppIDOption, RunIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def input(
    app_id: AppIDOption,
    run_id: RunIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the input to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """
    Get the input of a Nextmv Cloud application run.

    By default, the input is fetched and printed to [magenta]stdout[/magenta].
    Use the --output flag to save the input to a file.

    [bold][underline]Examples[/underline][/bold]

    - Get the input of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Input is printed to [magenta]stdout[/magenta].
        $ [dim]nextmv cloud run input --app-id hare-app --run-id burrow-123[/dim]

    - Get the input of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Save the input to a [magenta]input.json[/magenta] file.
        $ [dim]nextmv cloud run input --app-id hare-app --run-id burrow-123 --output input.json[/dim]

    - Get the input of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Use the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud run input --app-id hare-app --run-id burrow-123 --profile hare[/dim]
    """

    # TODO: replace copied code with actual logic / connect to actual logic
