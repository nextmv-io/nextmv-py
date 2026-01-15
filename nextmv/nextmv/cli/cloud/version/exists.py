"""
This module defines the cloud version exists command for the Nextmv CLI.
"""

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import error, in_progress, print_json
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
        $ [green]nextmv cloud version exists --app-id hare-app --version-id v1[/green]

    - Check if the version exists using the profile named [magenta]hare[/magenta].
        $ [green]nextmv cloud version exists --app-id hare-app --version-id v1 --profile hare[/green]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Checking if version exists...")

    try:
        ok = cloud_app.version_exists(version_id=version_id)
    except Exception as e:
        error(str(e))

    print_json({"exists": ok})
