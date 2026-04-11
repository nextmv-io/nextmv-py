"""CLI-only workflows for the cloud secrets domain.

The ``secrets`` create and update commands accept repeatable ``--secrets``
flags whose values are JSON strings (either objects or arrays). The CLI
parses these into SDK ``Secret`` instances before calling the thin action.
That parsing logic lives here because it is a CLI-frontend concern: the
MCP side receives already-structured ``list[dict[str, str]]`` values
directly.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.actions.secrets import (
    create_secrets_collection,
    update_secrets_collection,
)
from nextmv.cli.framework.options import AppIdRequiredOption, SecretsCollectionIdOption
from nextmv.cli.message import enum_values, error, in_progress, print_json, success
from nextmv.cloud.client import Client
from nextmv.cloud.secrets import Secret, SecretType


def build_secrets(secrets: list[str]) -> list[Secret]:
    """Parse a list of JSON strings into ``Secret`` SDK instances.

    Each input string may be either a single JSON object (one secret) or
    a JSON array (multiple secrets). Each secret must have ``type``,
    ``location``, and ``value`` keys. Invalid inputs exit the CLI with a
    clear error message.
    """
    secrets_list: list[Secret] = []

    for secret_str in secrets:
        try:
            secret_data = json.loads(secret_str)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            error(f"Invalid secret format: [magenta]{secret_str}[/magenta]. Error: {e}")
            continue  # error() exits; continue here is defensive.

        if isinstance(secret_data, list):
            for ix, item in enumerate(secret_data):
                if (
                    item.get("type") is None
                    or item.get("location") is None
                    or item.get("value") is None
                ):
                    error(
                        f"Invalid secret format at index [magenta]{ix}[/magenta] in "
                        f"[magenta]{secret_str}[/magenta]. Each secret must have "
                        "[magenta]type[/magenta], [magenta]location[/magenta], "
                        "and [magenta]value[/magenta] fields."
                    )

                secrets_list.append(
                    Secret(
                        type=SecretType(item["type"]),
                        location=item["location"],
                        value=item["value"],
                    )
                )
        elif isinstance(secret_data, dict):
            if (
                secret_data.get("type") is None
                or secret_data.get("location") is None
                or secret_data.get("value") is None
            ):
                error(
                    f"Invalid secret format in [magenta]{secret_str}[/magenta]. "
                    "Each secret must have [magenta]type[/magenta], [magenta]location[/magenta], "
                    "and [magenta]value[/magenta] fields."
                )

            secrets_list.append(
                Secret(
                    type=SecretType(secret_data["type"]),
                    location=secret_data["location"],
                    value=secret_data["value"],
                )
            )
        else:
            error(
                f"Invalid secret format: [magenta]{secret_str}[/magenta]. "
                "Expected [magenta]json[/magenta] object or array."
            )

    return secrets_list


_SECRETS_HELP = (
    "Secrets to configure in the app. Data should be valid [magenta]json[/magenta]. "
    "Pass multiple secrets by repeating the flag, or providing a list of objects. "
    f"Allowed values for [magenta]type[/magenta] are: {enum_values(SecretType)}. "
    "Object format: [dim]{'type': type, 'location': location, 'value': value}[/dim]."
)


def run_create_secrets_collection(
    client: Client,
    app_id: AppIdRequiredOption,
    secrets: Annotated[
        list[str],
        typer.Option(
            "--secrets",
            "-e",
            help=_SECRETS_HELP,
            metavar="SECRETS",
        ),
    ],
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="An optional description for the secrets collection.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="A name for the secrets collection.",
            metavar="NAME",
        ),
    ] = None,
    secrets_collection_id: Annotated[
        str | None,
        typer.Option(
            "--secrets-collection-id",
            "-s",
            help="The ID to assign to the new secrets collection. If not provided, a random ID will be generated.",
            envvar="NEXTMV_SECRETS_COLLECTION_ID",
            metavar="SECRETS_COLLECTION_ID",
        ),
    ] = None,
) -> None:
    """Create a new Nextmv Cloud secrets collection.

    A secrets collection is a group of key-value pairs that can be used by
    your application instances during execution. Each collection can contain
    up to 20 secrets. Secrets are provided as JSON objects using the
    ``--secrets`` flag.

    Each secret must include three fields:

    * ``type``: Either ``env`` or ``file``, which determines how the secret
      is injected into the runtime.
    * ``location``: Where to place the secret. For ``env``, the environment
      variable name (e.g. ``BURROW_ENTRANCE``). For ``file``, the relative
      path from the execution directory (e.g. ``licenses/burrow.entr``).
    * ``value``: The secret value as text (limited to 1 KB).

    You can provide secrets in three ways:

    * A single secret as a JSON object.
    * Multiple secrets by repeating the ``--secrets`` flag.
    * Multiple secrets as a JSON array in a single ``--secrets`` flag.

    The ``--secrets-collection-id`` and ``--name`` are optional; if not
    provided, they will be automatically generated.
    """

    in_progress(msg="Creating secrets collection...")
    secrets_list = build_secrets(secrets)
    collection_dict = create_secrets_collection(
        client,
        app_id=app_id,
        secrets=secrets_list,
        secrets_collection_id=secrets_collection_id,
        name=name,
        description=description,
    )
    print_json(collection_dict)


def run_update_secrets_collection(
    client: Client,
    app_id: AppIdRequiredOption,
    secrets_collection_id: SecretsCollectionIdOption,
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
            help=(
                _SECRETS_HELP
                + " This will replace all existing secrets in the collection."
            ),
            metavar="SECRETS",
        ),
    ] = None,
) -> None:
    """Update a Nextmv Cloud secrets collection.

    You can update the name, description, and/or secrets of an existing
    secrets collection. When updating secrets, all existing secrets will
    be replaced with the new ones provided.

    Secrets follow the same format as in ``create``: either a single JSON
    object, the ``--secrets`` flag repeated, or a JSON array in a single
    ``--secrets`` flag.
    """

    from pathlib import Path

    if name is None and description is None and secrets is None:
        error("Provide at least one option to update: --name, --description, or --secrets.")

    secrets_list = build_secrets(secrets) if secrets is not None else None

    in_progress(msg="Updating secrets collection...")
    collection_dict = update_secrets_collection(
        client,
        app_id=app_id,
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
        Path(output).write_text(json.dumps(collection_dict, indent=2))
        success(
            f"Updated secrets collection information saved to [magenta]{output}[/magenta]."
        )
        return

    print_json(collection_dict)
