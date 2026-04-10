"""
This module defines the cloud secrets get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.actions.secrets import get_secrets_collection as _get_secrets_collection
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption, SecretsCollectionIDOption
from nextmv.cloud.client import Client

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    app_id: AppIDOption,
    secrets_collection_id: SecretsCollectionIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the secrets collection information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get a Nextmv Cloud secrets collection.

    This command is useful to get the attributes of an existing Nextmv Cloud
    secrets collection by its ID. :construction: [yellow bold]Warning:
    secret values will be included in the output.[/yellow bold]

    [bold][underline]Examples[/underline][/bold]

    - Get the secrets collection with the ID [magenta]api-keys[/magenta] from
      application [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud secrets get --app-id hare-app \\
        --secrets-collection-id api-keys[/dim]

    - Get the secrets collection with the ID [magenta]api-keys[/magenta] and
      save the information to a [magenta]secrets.json[/magenta] file.
        $ [dim]nextmv cloud secrets get --app-id hare-app \\
            --secrets-collection-id api-keys --output secrets.json[/dim]
    """

    client = Client(profile=profile)
    in_progress(msg="Getting secrets collection...")
    collection_dict = _get_secrets_collection(client, app_id=app_id, secrets_collection_id=secrets_collection_id)

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(collection_dict, f, indent=2)

        success(msg=f"Secrets collection information saved to [magenta]{output}[/magenta].")

        return

    print_json(collection_dict)
