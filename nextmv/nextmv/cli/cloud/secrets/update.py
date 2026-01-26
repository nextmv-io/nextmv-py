"""
This module defines the cloud secrets update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.cloud.secrets.create import build_secrets
from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import enum_values, error, print_json, success
from nextmv.cli.options import AppIDOption, ProfileOption, SecretsCollectionIDOption
from nextmv.cloud.secrets import SecretType

# Set up subcommand application.
app = typer.Typer()


@app.command()
def update(
    app_id: AppIDOption,
    secrets_collection_id: SecretsCollectionIDOption,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="A new description for the secrets collection.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="A new name for the secrets collection.",
            metavar="NAME",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-u",
            help="Saves the updated secrets collection information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    secrets: Annotated[
        list[str] | None,
        typer.Option(
            "--secrets",
            "-e",
            help="Secrets to configure in the app. Data should be valid [magenta]json[/magenta]. "
            "Pass multiple secrets by repeating the flag, or providing a list of objects. "
            "Allowed values for [magenta]type[/magenta] are: "
            f"{enum_values(SecretType)}. "
            "Object format: [dim]{'type': type, 'location': location, 'value': value}[/dim]. "
            "This will replace all existing secrets in the collection.",
            metavar="SECRETS",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Update a Nextmv Cloud secrets collection.

    You can update the name, description, and/or secrets of an existing
    secrets collection. When updating secrets, all existing secrets will be
    replaced with the new ones provided.

    Secrets are provided as JSON objects using the --secrets flag,
    following the same format as the create command. You can provide secrets as:
    - A single secret as a JSON object
    - Multiple secrets by repeating the --secrets flag
    - Multiple secrets as a JSON array in a single --secrets flag

    [bold][underline]Examples[/underline][/bold]

    - Update the name of a secrets collection.
        $ [dim]nextmv cloud secrets update --app-id hare-app \\
            --secrets-collection-id api-keys --name "Updated API Keys"[/dim]

    - Update the description of a secrets collection.
        $ [dim]nextmv cloud secrets update --app-id hare-app \\
            --secrets-collection-id api-keys \\
            --description "Updated collection of API keys"[/dim]

    - Update both name and description.
        $ [dim]nextmv cloud secrets update --app-id hare-app \\
            --secrets-collection-id api-keys --name "Production API Keys" \\
            --description "API keys for production environment"[/dim]

    - Replace all secrets in a collection with new secrets.
        $ [dim]nextmv cloud secrets update --app-id hare-app \\
            --secrets-collection-id api-keys \\
            --secrets '{"type": "env", "location": "API_KEY", "value": "new-value"}' \\
            --secrets '{"type": "env", "location": "DATABASE_URL", "value": "postgres://newhost"}'[/dim]

    - Replace all secrets with a JSON array.
        $ [dim]nextmv cloud secrets update --app-id hare-app \\
            --secrets-collection-id api-keys \\
            --secrets '[{"type": "env", "location": "API_KEY", "value": "new-value"}, {...}]'[/dim]

    - Update multiple attributes at once and save the result.
        $ [dim]nextmv cloud secrets update --app-id hare-app \\
            --secrets-collection-id api-keys --name "New Name" \\
            --description "New Description" \\
            --secrets '{"type": "env", "location": "NEW_KEY", "value": "new-value"}' \\
            --output updated.json[/dim]
    """

    if name is None and description is None and secrets is None:
        error("Provide at least one option to update: --name, --description, or --secrets.")

    cloud_app = build_app(app_id=app_id, profile=profile)

    # Build the secrets list if provided
    secrets_list = None
    if secrets is not None:
        secrets_list = build_secrets(secrets)

    collection = cloud_app.update_secrets_collection(
        secrets_collection_id=secrets_collection_id,
        name=name,
        description=description,
        secrets=secrets_list,
    )
    success(
        f"Secrets collection [magenta]{secrets_collection_id}[/magenta] updated successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(collection.to_dict(), f, indent=2)

        success(msg=f"Updated secrets collection information saved to [magenta]{output}[/magenta].")

        return

    print_json(collection.to_dict())
