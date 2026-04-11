"""CLI-only workflow for the cloud data upload command.

The ``data upload`` command supports three input sources: stdin (piped
JSON or text), a single file (JSON/text), and a directory or .tar.gz
file (multi-file). The workflow resolves the input into the correct
SDK keyword argument shape (``data=`` vs ``tar_file=``) before calling
the thin action.
"""

import json
import sys
import tarfile
from pathlib import Path
from typing import Annotated, Any

import typer

from nextmv.cli.actions.data import upload_data
from nextmv.cli.framework.options import AppIdRequiredOption
from nextmv.cli.message import error, in_progress, success
from nextmv.cloud import Application
from nextmv.cloud.client import Client


def run_upload_data(
    client: Client,
    app_id: AppIdRequiredOption,
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
            help=(
                "The input path to use. File or directory depending on content format. "
                "Uses [magenta]stdin[/magenta] if not defined. "
                "Can be a [magenta].tar.gz[/magenta] file for multi-file content format."
            ),
            metavar="INPUT_PATH",
        ),
    ] = None,
) -> None:
    """Upload data for Nextmv Cloud application components.

    When data is too large, or is not in a text-based content format,
    you can use this command to upload information for a Nextmv Cloud
    application. Data is used for starting new runs, tracking runs,
    performing experiments, and more.

    The ``--upload-url`` flag is required. Obtain a URL via
    ``nextmv cloud upload create``.

    The data input can be provided via stdin or the ``--input`` flag.
    When using ``--input``, the value can be:

    * A file path containing text or JSON data.
    * A directory path containing multi-file input data.
    * A path to a ``.tar.gz`` file containing tarred multi-file data.
    """

    stdin_input = sys.stdin.read().strip() if sys.stdin.isatty() is False else None
    if stdin_input is None and (input is None or input == ""):
        error("Input data must be provided via the --input flag or [magenta]stdin[/magenta].")

    cloud_app = Application(client=client, id=app_id)
    data_kwarg = _resolve_data_kwarg(stdin=stdin_input, input=input, cloud_app=cloud_app)

    in_progress(msg="Uploading data...")
    upload_data(client, app_id=app_id, upload_url=upload_url, **data_kwarg)
    success("Data uploaded successfully.")


def _resolve_data_kwarg(
    stdin: str | None,
    input: str | None,
    cloud_app: Application,
) -> dict[str, Any]:
    """Resolve the keyword argument (``data=`` or ``tar_file=``) for the
    underlying ``upload_data`` call.

    Handles stdin (JSON or text), single file, directory (tarred), and
    ``.tar.gz`` inputs.
    """

    if stdin is not None:
        try:
            input_data = json.loads(stdin)
        except json.JSONDecodeError:
            input_data = stdin
        return {"data": input_data}

    input_path = Path(input)  # type: ignore[arg-type]

    if input_path.is_file():
        if tarfile.is_tarfile(input_path):
            return {"tar_file": str(input_path)}
        return {"data": input_path.read_text()}

    if input_path.is_dir():
        tar_path = cloud_app._package_inputs(dir_path=str(input_path))
        return {"tar_file": tar_path}

    error(f"Input path [magenta]{input}[/magenta] does not exist.")
    return {}  # error() exits; unreachable.
