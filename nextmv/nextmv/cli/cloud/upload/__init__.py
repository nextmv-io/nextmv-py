"""Cloud upload command tree for the Nextmv CLI.

Thin wrapper around ``create_upload_url`` plus a custom success message.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.upload import create_upload_url

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create temporary upload URLs for Nextmv Cloud applications.

    When data is too large, or you are working with multiple files, you
    can use upload URLs to upload data directly to Nextmv Cloud storage.
    """
    pass


CREATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Create an upload URL for application [magenta]hare-app[/magenta].",
        "nextmv cloud upload create --app-id hare-app",
    ),
    (
        "Create an upload URL using a specific profile.",
        "nextmv cloud upload create --app-id hare-app --profile hare",
    ),
)


create = cli.command(
    app,
    create_upload_url,
    name="create",
    progress="Creating upload URL...",
    examples=CREATE_EXAMPLES,
)
