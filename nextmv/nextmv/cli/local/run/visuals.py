"""
This module defines the cloud run metadata command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.options import AppIDOption, RunIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def metadata(
    app_id: AppIDOption,
    run_id: RunIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the metadata to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """
    Get the metadata of a Nextmv Cloud application run.

    By default, the metadata is fetched and printed to [magenta]stdout[/magenta].
    Use the --output flag to save the metadata to a file.

    [bold][underline]Examples[/underline][/bold]

    - Get the metadata of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Metadata is printed to [magenta]stdout[/magenta].
        $ [dim]nextmv cloud run metadata --app-id hare-app --run-id burrow-123[/dim]

    - Get the metadata of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Save the metadata to a [magenta]metadata.json[/magenta] file.
        $ [dim]nextmv cloud run metadata --app-id hare-app --run-id burrow-123 --output metadata.json[/dim]

    - Get the metadata of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Use the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud run metadata --app-id hare-app --run-id burrow-123 --profile hare[/dim]
    """

    # TODO: replace copied code with actual logic / connect to actual logic
