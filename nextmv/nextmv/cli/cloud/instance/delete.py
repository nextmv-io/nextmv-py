"""
This module defines the cloud instance delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer
from rich.prompt import Confirm

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import info, success
from nextmv.cli.options import AppIDOption, InstanceIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    instance_id: InstanceIDOption,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Agree to deletion confirmation prompt. Useful for non-interactive sessions.",
        ),
    ] = False,
    profile: ProfileOption = None,
) -> None:
    """
    Deletes a Nextmv Cloud application instance.

    This action is permanent and cannot be undone. Use the [code]--yes[/code]
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the instance with the ID [magenta]prod[/magenta] from application [magenta]hare-app[/magenta].
        $ [green]nextmv cloud instance delete --app-id hare-app --instance-id prod[/green]

    - Delete the instance without confirmation prompt.
        $ [green]nextmv cloud instance delete --app-id hare-app --instance-id prod --yes[/green]
    """

    if not yes:
        confirm = Confirm.ask(
            f"Are you sure you want to delete instance [magenta]{instance_id}[/magenta] "
            f"from application [magenta]{app_id}[/magenta]? This action cannot be undone.",
            default=False,
        )

        if not confirm:
            info(msg=f"Instance [magenta]{instance_id}[/magenta] will not be deleted.", emoji=":bulb:")
            return

    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.delete_instance(instance_id=instance_id)
    success(
        f"Instance [magenta]{instance_id}[/magenta] deleted successfully from application [magenta]{app_id}[/magenta]."
    )
