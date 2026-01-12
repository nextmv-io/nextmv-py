"""
This module defines the cloud run input command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import info, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption, RunIDOption
from nextmv.output import OutputFormat

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
    profile: ProfileOption = None,
) -> None:
    """
    Get the input of a Nextmv Cloud application run.

    By default, the input is fetched and printed to [magenta]stdout[/magenta].
    Use the [code]--output[/code] flag to save the input to a file.

    [bold][underline]Examples[/underline][/bold]

    - Get the input of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Input is printed to [magenta]stdout[/magenta].
        $ [green]nextmv cloud run input --app-id hare-app --run-id burrow-123[/green]

    - Get the input of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Save the input to a [magenta]input.json[/magenta] file.
        $ [green]nextmv cloud run input --app-id hare-app --run-id burrow-123 --output input.json[/green]

    - Get the input of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Use the profile named [magenta]hare[/magenta].
        $ [green]nextmv cloud run input --app-id hare-app --run-id burrow-123 --profile hare[/green]
    """

    cloud_app = build_app(app_id, profile)
    info(msg="Getting run input...", emoji=":hourglass_flowing_sand:")

    # First get the content type to check what we should do with the input,
    # based on its format.
    run_info = cloud_app.run_metadata(run_id)

    # If the input is multi-file, we need to provide an `output_dir_path` to
    # save the files to.
    if run_info.metadata.format.format_input.input_type not in {OutputFormat.JSON, OutputFormat.TEXT}:
        # If no output path is provided, use the run ID as the directory name.
        output = f"{run_id}-input" if output is None or output == "" else output
        cloud_app.run_input(run_id=run_id, output_dir_path=output)
        success(msg=f"Run input saved to [magenta]{output}[/magenta].")

        return

    # At this point, we know the input is JSON or text, so we can fetch it
    # normally. The method internally will take care of large inputs.
    run_input = cloud_app.run_input(run_id=run_id)

    # If an output path is provided, save the input to that file.
    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(run_input, f, indent=2)

        success(msg=f"Run input saved to [magenta]{output}[/magenta].")

        return

    # Otherwise, print the input to stdout.
    print_json(data=run_input)
