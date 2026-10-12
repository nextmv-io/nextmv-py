"""
This module defines the cloud secrets update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.cloud.secrets.create import build_secrets
from nextmv.cli.configuration.config import build_cloud_app
from nextmv.cli.message import enum_values, error, in_progress, print_json, success
from nextmv.cli.options import AppIDOption, DebugOption, ProfileOption, SecretsCollectionIDOption
from nextmv.cloud.secrets import SecretOperation, SecretOperationType, SecretType

# Set up subcommand application.
app = typer.Typer()


@app.command()
def update(
    app_id: AppIDOption,
    secrets_collection_id: SecretsCollectionIDOption,
    create: Annotated[
        list[str] | None,
        typer.Option(
            "--create",
            "-c",
            help="Secrets to add to the collection. Data should be valid [magenta]json[/magenta]. "
            "Pass multiple secrets by repeating the flag, or providing a list of objects. "
            "Allowed values for [magenta]type[/magenta] are: "
            f"{enum_values(SecretType)}. "
            "Object format: [dim]{'type': type, 'location': location, 'value': value}[/dim]. "
            "Fails if a secret with the same type and location already exists.",
            metavar="SECRETS",
        ),
    ] = None,
    delete: Annotated[
        list[str] | None,
        typer.Option(
            "--delete",
            "-x",
            help="Secrets to remove from the collection. Data should be valid [magenta]json[/magenta]. "
            "Pass multiple secrets by repeating the flag, or providing a list of objects. "
            "Allowed values for [magenta]type[/magenta] are: "
            f"{enum_values(SecretType)}. "
            "Object format: [dim]{'type': type, 'location': location}[/dim]. "
            "Secrets that do not exist are ignored.",
            metavar="SECRETS",
        ),
    ] = None,
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
            "This will replace all existing secrets in the collection. "
            "Cannot be combined with --create, --update, or --delete.",
            metavar="SECRETS",
        ),
    ] = None,
    update: Annotated[
        list[str] | None,
        typer.Option(
            "--update",
            "-t",
            help="Secrets whose value should be replaced. Data should be valid [magenta]json[/magenta]. "
            "Pass multiple secrets by repeating the flag, or providing a list of objects. "
            "Allowed values for [magenta]type[/magenta] are: "
            f"{enum_values(SecretType)}. "
            "Object format: [dim]{'type': type, 'location': location, 'value': value}[/dim]. "
            "Fails if no secret with the same type and location exists.",
            metavar="SECRETS",
        ),
    ] = None,
    _: DebugOption = False,
    profile: ProfileOption = None,
) -> None:
    """
    Update a Nextmv Cloud secrets collection.

    You can update the name and/or description of a secrets collection, and
    create, update, or delete individual secrets, without resending the
    values of the secrets you are not changing. Secrets are identified by
    their [magenta]type[/magenta] and [magenta]location[/magenta]. The
    changes are applied all together, or not at all.

    Alternatively, use --secrets to replace all the existing secrets in the
    collection with the ones provided.

    Secrets are provided as JSON objects, following the same format as the
    create command. You can provide secrets as:
    - A single secret as a JSON object
    - Multiple secrets by repeating the flag
    - Multiple secrets as a JSON array in a single flag

    [bold][underline]Examples[/underline][/bold]

    - Update the name of a secrets collection, keeping its secrets as they are.

        $ [dim]nextmv cloud secrets update --app-id hare-app \\
            --secrets-collection-id api-keys --name "Updated API Keys"[/dim]

    - Update both name and description.

        $ [dim]nextmv cloud secrets update --app-id hare-app \\
            --secrets-collection-id api-keys --name "Production API Keys" \\
            --description "API keys for production environment"[/dim]

    - Add a new secret to a collection.

        $ [dim]nextmv cloud secrets update --app-id hare-app \\
            --secrets-collection-id api-keys \\
            --create '{"type": "env", "location": "NEW_KEY", "value": "new-value"}'[/dim]

    - Rotate the value of an existing secret.

        $ [dim]nextmv cloud secrets update --app-id hare-app \\
            --secrets-collection-id api-keys \\
            --update '{"type": "env", "location": "API_KEY", "value": "rotated-value"}'[/dim]

    - Remove a secret from a collection.

        $ [dim]nextmv cloud secrets update --app-id hare-app \\
            --secrets-collection-id api-keys \\
            --delete '{"type": "env", "location": "OLD_KEY"}'[/dim]

    - Replace all secrets in a collection with new secrets.

        $ [dim]nextmv cloud secrets update --app-id hare-app \\
            --secrets-collection-id api-keys \\
            --secrets '{"type": "env", "location": "API_KEY", "value": "new-value"}' \\
            --secrets '{"type": "env", "location": "DATABASE_URL", "value": "postgres://newhost"}'[/dim]

    - Combine several changes and save the result.

        $ [dim]nextmv cloud secrets update --app-id hare-app \\
            --secrets-collection-id api-keys --description "Rotated keys" \\
            --update '{"type": "env", "location": "API_KEY", "value": "rotated-value"}' \\
            --delete '{"type": "env", "location": "OLD_KEY"}' \\
            --output updated.json[/dim]
    """

    has_operations = create is not None or update is not None or delete is not None
    if name is None and description is None and secrets is None and not has_operations:
        error(
            "Provide at least one option to update: --name, --description, --create, --update, --delete, or --secrets."
        )

    if secrets is not None and has_operations:
        error("--secrets cannot be combined with --create, --update, or --delete.")

    secrets_list = None
    if secrets is not None:
        secrets_list = build_secrets(secrets)

    operations = None
    if has_operations:
        operations = build_operations(create=create, update=update, delete=delete)

    cloud_app, _ = build_cloud_app(app_id=app_id, profile=profile)

    in_progress(msg="Updating secrets collection...")
    if secrets_list is not None:
        collection = cloud_app.update_secrets_collection(
            secrets_collection_id=secrets_collection_id,
            name=name,
            description=description,
            secrets=secrets_list,
        )
    else:
        collection = cloud_app.patch_secrets_collection(
            secrets_collection_id=secrets_collection_id,
            name=name,
            description=description,
            operations=operations,
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


def build_operations(
    create: list[str] | None,
    update: list[str] | None,
    delete: list[str] | None,
) -> list[SecretOperation]:
    """
    Builds the secret operations list from the CLI options.

    Parameters
    ----------
    create : list[str] | None
        Secrets to create, provided via the CLI.
    update : list[str] | None
        Secrets to update, provided via the CLI.
    delete : list[str] | None
        Secrets to delete, provided via the CLI.

    Returns
    -------
    list[SecretOperation]
        The built operations list.
    """

    operations = []
    for op, secrets in ((SecretOperationType.CREATE, create), (SecretOperationType.UPDATE, update)):
        if secrets is None:
            continue

        for secret in build_secrets(secrets):
            operations.append(
                SecretOperation(
                    op=op,
                    secret_type=secret.secret_type,
                    location=secret.location,
                    value=secret.value,
                )
            )

    if delete is not None:
        operations.extend(build_delete_operations(delete))

    return operations


def build_delete_operations(secrets: list[str]) -> list[SecretOperation]:
    """
    Builds the delete operations list from the CLI option(s).

    Parameters
    ----------
    secrets : list[str]
        List of secrets to delete provided via the CLI.

    Returns
    -------
    list[SecretOperation]
        The built delete operations list.
    """

    operations = []

    for secret_str in secrets:
        try:
            # NOTE: never echo the raw secret string back to the terminal - it
            # may contain a secret value. Reference the offending entry by
            # index only (CWE-522).
            secret_data = json.loads(secret_str)
            items = secret_data if isinstance(secret_data, list) else [secret_data]

            for ix, item in enumerate(items):
                if not isinstance(item, dict):
                    error("Invalid secret format. Expected a [magenta]json[/magenta] object or array.")

                if item.get("type") is None or item.get("location") is None:
                    error(
                        f"Invalid secret format at index [magenta]{ix}[/magenta]. "
                        "Each secret to delete must have [magenta]type[/magenta] and "
                        "[magenta]location[/magenta] fields."
                    )

                if item.get("value") is not None:
                    error(
                        f"Invalid secret format at index [magenta]{ix}[/magenta]. "
                        "Secrets to delete must not have a [magenta]value[/magenta] field."
                    )

                operations.append(
                    SecretOperation(
                        op=SecretOperationType.DELETE,
                        secret_type=SecretType(item["type"]),
                        location=item["location"],
                    )
                )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            error(f"Invalid secret format. Error: {e}")

    return operations
