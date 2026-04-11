"""Cloud data command tree for the Nextmv CLI.

The ``upload`` command routes through ``_workflows.py`` because it
handles stdin piping, file/directory/tar packaging, and a custom
success message — none of which fit the framework's default JSON-emit
flow.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.cloud.data._workflows import run_upload_data

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Upload data for Nextmv Cloud application components.

    When data is too large (exceeds 5 MiB), or you are working with the
    multi-file content format, you can use this command to upload
    information to Nextmv Cloud. Requires a pre-signed upload URL, which
    can be obtained using ``nextmv cloud upload create``.
    """
    pass


UPLOAD_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Upload data from stdin for application [magenta]hare-app[/magenta].",
        "echo '{\"key\": \"value\"}' | nextmv cloud data upload \\\n"
        "    --app-id hare-app --upload-url <URL>",
    ),
    (
        "Upload data from a JSON file.",
        "nextmv cloud data upload --app-id hare-app --upload-url <URL> \\\n"
        "    --input data.json",
    ),
    (
        "Upload multi-file data from a directory.",
        "nextmv cloud data upload --app-id hare-app --upload-url <URL> \\\n"
        "    --input ./data_directory",
    ),
    (
        "Upload multi-file data from a [magenta].tar.gz[/magenta] file.",
        "nextmv cloud data upload --app-id hare-app --upload-url <URL> \\\n"
        "    --input data.tar.gz",
    ),
)


upload = cli.command(
    app,
    run_upload_data,
    name="upload",
    handles_own_output=True,
    examples=UPLOAD_EXAMPLES,
)
