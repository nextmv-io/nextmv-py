"""
This module defines the cloud secrets list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_cloud_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, DebugOption, NoPaginationOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def list(
    app_id: AppIDOption,
    no_pagination: NoPaginationOption = False,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the secrets collections list information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    _: DebugOption = False,
    profile: ProfileOption = None,
) -> None:
    """
    List all secrets collections of a Nextmv Cloud application.

    By default this command paginates the list of secrets, which means multiple
    API calls may be made to retrieve all secrets. You may use the
    --no-pagination option to disable pagination.

    [bold][underline]Examples[/underline][/bold]

    - List all secrets collections of application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud secrets list --app-id hare-app[/dim]

    - List all secrets collections using the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud secrets list --app-id hare-app --profile hare[/dim]

    - List all secrets collections and save the information to a [magenta]secrets.json[/magenta] file.
        $ [dim]nextmv cloud secrets list --app-id hare-app --output secrets.json[/dim]

    - List all secrets collections without pagination.
        $ [dim]nextmv cloud secrets list --app-id hare-app --no-pagination[/dim]
    """

    cloud_app, _ = build_cloud_app(app_id=app_id, profile=profile)
    in_progress(msg="Listing secrets collections...")
    collections = cloud_app.list_secrets_collections(no_pagination)
    collections_dicts = [collection.to_dict() for collection in collections]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(collections_dicts, f, indent=2)

        success(msg=f"Secrets collections list information saved to [magenta]{output}[/magenta].")

        return

    print_json(collections_dicts)
