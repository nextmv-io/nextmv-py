"""
This module defines the cloud app exists command for the Nextmv CLI.
"""

import typer

from nextmv.cli.configuration.config import build_client
from nextmv.cli.message import in_progress, print_json
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.application import Application

# Set up subcommand application.
app = typer.Typer()


@app.command()
def exists(
    app_id: AppIDOption,
    profile: ProfileOption = None,
) -> None:
    """
    Check if a Nextmv Cloud application exists.

    This command is useful in scripting applications to verify the existence of
    a Nextmv Cloud application by its ID.

    [bold][underline]Examples[/underline][/bold]

    - Check if the application with the ID [magenta]hare-app[/magenta] exists.
        $ [dim]nextmv cloud app exists --app-id hare-app[/dim]

    - Check if the application with the ID [magenta]hare-app[/magenta] exists.
      Use the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud app exists --app-id hare-app --profile hare[/dim]
    """

    client = build_client(profile)
    in_progress(msg="Checking if application exists...")

    ok = Application.exists(
        client=client,
        id=app_id,
    )
    print_json({"exists": ok})
