"""
This module defines the cloud data upload command for the Nextmv CLI.
"""

import json
import sys
import tarfile
from pathlib import Path
from typing import Annotated, Any

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import error, in_progress, success
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.application import Application

# Set up subcommand application.
app = typer.Typer()


@app.command()
def upload(
    app_id: AppIDOption,
    upload_url: Annotated[
        str,
        typer.Option(
            "--upload-url",
            "-u",
            help="Pre-signed URL for uploading the data.",
            metavar="UPLOAD_URL",
        ),
    ],
    input: Annotated[
        str | None,
        typer.Option(
            "--input",
            "-i",
            help="The input path to use. File or directory depending on content format. "
            "Uses [magenta]stdin[/magenta] if not defined. "
            "Can be a [magenta].tar.gz[/magenta] file for multi-file content format.",
            metavar="INPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Upload data for Nextmv Cloud application components.

    When data is too large, or is not in a text-based content format, you can
    use this command to upload information for a Nextmv Cloud application. Data
    is used for starting new runs, tracking runs, performing experiments, and
    more.

    The --upload-url flag is required to specify the pre-signed
    upload URL. It can be obtained using the [code]nextmv cloud upload
    create[/code] command. Use the [magenta].upload_url[/magenta] field from
    the command output.

    The data input should be given through [magenta]stdin[/magenta] or the
    --input flag. When using the --input flag, the value can be one of the
    following:

    - [yellow]<FILE_PATH>[/yellow]: path to a [magenta]file[/magenta] containing
      the data. Use with the [magenta]json[/magenta], and
      [magenta]text[/magenta] content formats.
    - [yellow]<DIR_PATH>[/yellow]: path to a [magenta]directory[/magenta]
      containing data files. Use with the [magenta]multi-file[/magenta]
      content format.
    - [yellow]<.tar.gz PATH>[/yellow]: path to a [magenta].tar.gz[/magenta] file
      containing tarred data files. Use with the [magenta]multi-file[/magenta]
      content format.

    [bold][underline]Examples[/underline][/bold]

    - Upload data from [magenta]stdin[/magenta] for application
      [magenta]hare-app[/magenta].
        $ [dim]echo '{"key": "value"}' | nextmv cloud data upload --app-id hare-app --upload-url <URL>[/dim]

    - Upload data from a [magenta]JSON[/magenta] file.
        $ [dim]nextmv cloud data upload --app-id hare-app --upload-url <URL> --input data.json[/dim]

    - Upload data from a [magenta]text[/magenta] file.
        $ [dim]nextmv cloud data upload --app-id hare-app --upload-url <URL> --input data.txt[/dim]

    - Upload [magenta]multi-file[/magenta] data from a directory.
        $ [dim]nextmv cloud data upload --app-id hare-app --upload-url <URL> --input ./data_directory[/dim]

    - Upload [magenta]multi-file[/magenta] data from a
      [magenta].tar.gz[/magenta] file.
        $ [dim]nextmv cloud data upload --app-id hare-app --upload-url <URL> --input data.tar.gz[/dim]

    - Upload data using a specific profile.
        $ [dim]nextmv cloud data upload --app-id hare-app --upload-url <URL> --input data.json \\
            --profile production[/dim]
    """

    # Validate that input is provided.
    stdin = sys.stdin.read().strip() if sys.stdin.isatty() is False else None
    if stdin is None and (input is None or input == ""):
        error("Input data must be provided via the --input flag or [magenta]stdin[/magenta].")

    cloud_app = build_app(app_id=app_id, profile=profile)
    data_kwarg = resolve_data_kwarg(
        stdin=stdin,
        input=input,
        cloud_app=cloud_app,
    )

    in_progress(msg="Uploading data...")
    cloud_app.upload_data(upload_url=upload_url, **data_kwarg)
    success(msg="Data uploaded successfully.")


def resolve_data_kwarg(stdin: str | None, input: str | None, cloud_app: Application) -> dict[str, Any]:
    """
    Gets the keyword argument related to the data that is needed for the
    upload. It handles stdin, file, and directory inputs.

    Parameters
    ----------
    stdin : str | None
        The stdin input data, if provided.
    input : str | None
        The input path, if provided.
    cloud_app : Application
        The Nextmv Cloud application instance.

    Returns
    -------
    dict[str, Any]
        The keyword argument with the resolved data.
    """

    if stdin is not None:
        # Handle the case where stdin is provided as JSON for a JSON app.
        try:
            input_data = json.loads(stdin)
        except json.JSONDecodeError:
            input_data = stdin

        return {"data": input_data}

    input_path = Path(input)

    # If the input is a file, we need to determine if it is a tar file or a
    # regular file. If it is a regular file, we need to read its content.
    if input_path.is_file():
        if tarfile.is_tarfile(input_path):
            return {"tar_file": str(input_path)}

        input_data = input_path.read_text()

        return {"data": input_data}

    # If the input is a directory, we need to tar the contents.
    if input_path.is_dir():
        tar_path = cloud_app._package_inputs(dir_path=str(input_path))

        return {"tar_file": tar_path}

    error(f"Input path [magenta]{input}[/magenta] does not exist.")
