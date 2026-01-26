"""
This module defines the cloud run get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption, RunIDOption
from nextmv.cloud.application import Application
from nextmv.output import OutputFormat
from nextmv.polling import PollingOptions, default_polling_options

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
    profile: ProfileOption = None,
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

    cloud_app = build_app(app_id=app_id, profile=profile)

    # Build the polling options.
    polling_options = default_polling_options()
    polling_options.max_duration = timeout

    handle_outputs(
        cloud_app=cloud_app,
        run_id=run_id,
        wait=wait,
        output=output,
        polling_options=polling_options,
        skip_wait_check=True,
    )


def handle_outputs(
    cloud_app: Application,
    run_id: str,
    wait: bool,
    output: str | None,
    polling_options: PollingOptions,
    skip_wait_check: bool = False,
) -> None:
    """
    Handle retrieving and outputting the results from a run.

    If ``wait`` is False and ``output`` is not specified, this function returns
    early without doing anything. Otherwise, results are retrieved using
    polling (since the run may not yet be complete) and output accordingly.

    The output behavior depends on the content type:

    - **JSON/TEXT**: If ``output`` is specified, writes to the given file path.
      Otherwise, prints to stdout.
    - **MULTI_FILE/CSV_ARCHIVE**: Downloads files to a directory. If ``output``
      is specified, uses that as the directory name. Otherwise, uses the
      ``run_id`` as the directory name.

    Parameters
    ----------
    cloud_app : Application
        The cloud application instance used to interact with the Nextmv Cloud
        API.
    run_id : str
        The unique identifier of the run to retrieve results for.
    wait : bool
        Whether to wait for the run to complete. If False and ``output`` is not
        specified, the function returns early without retrieving results.
    output : str | None
        The location to write the output. For JSON/TEXT formats, this is a file
        path. For MULTI_FILE/CSV_ARCHIVE formats, this is a directory path. If
        None, JSON/TEXT output is printed to stdout and MULTI_FILE/CSV_ARCHIVE
        output uses the ``run_id`` as the directory name.
    polling_options : PollingOptions
        Configuration options for polling behavior, including timeout and
        interval settings.
    skip_wait_check : bool, optional
        If True, skips the early return check when both `wait` is False and
        `output` is not specified. Default is False.
    """

    # If we don't need to wait, no output is specified, and we're not skipping
    # the wait check, return early.
    if not wait and (output is None or output == "") and not skip_wait_check:
        return

    # Get the run metadata to determine how to operate with the output.
    run_info = cloud_app.run_metadata(run_id=run_id)
    content_format = run_info.metadata.format.format_output.output_type

    # Build kwargs for the result retrieval.
    kwargs = {"run_id": run_id}

    # For MULTI_FILE and CSV_ARCHIVE, we need output_dir_path.
    if content_format not in {OutputFormat.JSON, OutputFormat.TEXT}:
        output_dir = f"{run_id}-output" if output is None or output == "" else output
        kwargs["output_dir_path"] = output_dir

    # Always poll for results since we can't guarantee the run is done.
    # If the run is already complete, polling returns immediately.
    in_progress(msg="Getting run results...")
    wait = wait or (output is not None and output != "")
    if wait:
        kwargs["polling_options"] = polling_options
        run_result = cloud_app.run_result_with_polling(**kwargs)
    else:
        run_result = cloud_app.run_result(**kwargs)

    # Handle the case where output is embedded directly in the result: json and text.
    if content_format in {OutputFormat.JSON, OutputFormat.TEXT}:
        if output is None or output == "":
            print_json(run_result.to_dict())
        else:
            with open(output, "w") as f:
                json.dump(run_result.to_dict(), f, indent=2)

            success(f"Run output written to [magenta]{output}[/magenta].")

        return

    # At this point, we know that the output is multi-file or csv-archive.
    result_dict = run_result.to_dict()
    if "output" in result_dict and run_result.metadata.run_is_finalized():
        del result_dict["output"]
        success(f"Run outputs downloaded to [magenta]{output_dir}[/magenta]. Here is the metadata.")
    else:
        success(
            f"Run is not finalized (status: [magenta]{run_result.metadata.status_v2.value}[/magenta]). "
            "Here is the metadata."
        )

    print_json(result_dict)
