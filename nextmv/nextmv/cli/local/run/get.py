"""
This module defines the cloud run get command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.options import AppIDOption, RunIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    app_id: AppIDOption,
    run_id: RunIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Waits for the run to complete and save the output to this location. "
            "A file or directory will be created depending on content format.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    timeout: Annotated[
        int,
        typer.Option(
            help="The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.",
            metavar="TIMEOUT_SECONDS",
        ),
    ] = -1,
    wait: Annotated[
        bool,
        typer.Option(
            "--wait",
            "-w",
            help="Wait for the run to complete. Run result is printed to [magenta]stdout[/magenta] for "
            "[magenta]json[/magenta], to a dir for [magenta]multi-file[/magenta]. "
            "Specify output location with --output.",
        ),
    ] = False,
) -> None:
    """
    Get the result (output) of a Nextmv Cloud application run.

    Use the --wait flag to wait for the run to complete, polling
    for results. Using the --output flag will also activate
    waiting, and allows you to specify a destination (file or dir) for the
    output, depending on the content type.

    [bold][underline]Examples[/underline][/bold]

    - Get the results of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud run get --app-id hare-app --run-id burrow-123[/dim]

    - Get the results of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Wait for the run to complete if necessary.
        $ [dim]nextmv cloud run get --app-id hare-app --run-id burrow-123 --wait[/dim]

    - Get the results of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. The app is a [magenta]json[/magenta] app.
      Save the results to a [magenta]results.json[/magenta] file.
        $ [dim]nextmv cloud run get --app-id hare-app --run-id burrow-123 --output results.json[/dim]

    - Get the results of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. The app is a [magenta]multi-file[/magenta] app.
      Save the results to the [magenta]results[/magenta] dir.
        $ [dim]nextmv cloud run get --app-id hare-app --run-id burrow-123 --output results[/dim]

    - Get the results of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Use the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud run get --app-id hare-app --run-id burrow-123 --profile hare[/dim]
    """

    # TODO: replace copied code with actual logic / connect to actual logic
