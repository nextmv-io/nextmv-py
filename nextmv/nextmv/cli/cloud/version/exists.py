"""
This module defines the cloud version exists command for the Nextmv CLI.
"""

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, print_json
from nextmv.cli.options import AppIDOption, ProfileOption, VersionIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def exists(
    app_id: AppIDOption,
    version_id: VersionIDOption,
    profile: ProfileOption = None,
) -> None:
    """
    Check if a Nextmv Cloud application version exists.

    This command is useful in scripting applications to verify the existence of
    a Nextmv Cloud application version by its ID.

    [bold][underline]Examples[/underline][/bold]

    - Check if the version with the ID [magenta]v1[/magenta] exists in application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud version exists --app-id hare-app --version-id v1[/dim]

    - Check if the version exists using the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud version exists --app-id hare-app --version-id v1 --profile hare[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Checking if version exists...")
    ok = cloud_app.version_exists(version_id=version_id)
    print_json({"exists": ok})
