"""
This module defines the local run metadata command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_local_app
from nextmv.cli.message import in_progress, print_json, success, warning
from nextmv.cli.options import DebugOption, LocalAppIDOption, LocalAppSrcOption, RunIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command(deprecated=True)
def metadata(
    run_id: RunIDOption,
    app_id: LocalAppIDOption = None,
    app_src: LocalAppSrcOption = ".",
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the metadata to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    _: DebugOption = False,
) -> None:
    """
    This command is deprecated, use [code]nextmv local run information[/code] instead.

    Get the metadata of a Nextmv local application run.

    You may identify the app by using --app-src, or --app-id if it has been
    registered. If the app is not already registered, this command will
    register it. By default, the metadata is fetched and printed to
    [magenta]stdout[/magenta]. Use the --output flag to save the metadata to a
    file.

    [bold][underline]Examples[/underline][/bold]

    - Get the metadata of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Metadata is printed to [magenta]stdout[/magenta].

        $ [dim]nextmv local run metadata --app-id hare-app --run-id burrow-123[/dim]

    - Get the metadata of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Save the metadata to a [magenta]metadata.json[/magenta] file.

        $ [dim]nextmv local run metadata --app-id hare-app --run-id burrow-123 --output metadata.json[/dim]

    - Get the metadata of a run with ID [magenta]burrow-123[/magenta], belonging to an app with ID
      [magenta]hare-app[/magenta]. Use the profile named [magenta]hare[/magenta].

        $ [dim]nextmv local run metadata --app-id hare-app --run-id burrow-123 --profile hare[/dim]
    """

    warning(
        "The [code]nextmv local run metadata[/code] command is deprecated and "
        "will be removed in the next major release. "
        "Please use the [code]nextmv local run information[/code] command instead."
    )

    local_app = build_local_app(app_src, app_id)
    in_progress(msg="Getting run metadata...")
    run_info = local_app.run_metadata(run_id)
    info_dict = run_info.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(info_dict, f, indent=2)

        success(msg=f"Run metadata saved to [magenta]{output}[/magenta].")

        return

    print_json(info_dict)
