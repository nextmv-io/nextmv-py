"""
This module defines the cloud secrets delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import info, success
from nextmv.cli.options import AppIDOption, ProfileOption, SecretsCollectionIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    secrets_collection_id: SecretsCollectionIDOption,
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
    Deletes a Nextmv Cloud secrets collection.

    This action is permanent and cannot be undone. Use the --yes
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the secrets collection with the ID [magenta]api-keys[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud secrets delete --app-id hare-app --secrets-collection-id api-keys[/dim]

    - Delete the secrets collection without confirmation prompt.
        $ [dim]nextmv cloud secrets delete --app-id hare-app --secrets-collection-id api-keys --yes[/dim]
    """

    if not yes:
        confirm = get_confirmation(
            f"Are you sure you want to delete secrets collection [magenta]{secrets_collection_id}[/magenta] "
            f"from application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(
                msg=f"Secrets collection [magenta]{secrets_collection_id}[/magenta] will not be deleted.",
                emoji=":bulb:",
            )
            return

    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.delete_secrets_collection(secrets_collection_id=secrets_collection_id)
    success(
        f"Secrets collection [magenta]{secrets_collection_id}[/magenta] deleted successfully "
        f"from application [magenta]{app_id}[/magenta]."
    )
