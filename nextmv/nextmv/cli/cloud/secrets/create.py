"""
This module defines the cloud secrets create command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import enum_values, error, in_progress, print_json
from nextmv.cli.options import AppIDOption, ProfileOption
from nextmv.cloud.secrets import Secret, SecretType

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    app_id: AppIDOption,
    secrets: Annotated[
        list[str],
        typer.Option(
            "--secrets",
            "-e",
            help="Secrets to configure in the app. Data should be valid [magenta]json[/magenta]. "
            "Pass multiple secrets by repeating the flag, or providing a list of objects. "
            "Allowed values for [magenta]type[/magenta] are: "
            f"{enum_values(SecretType)}. "
            "Object format: [dim]{'type': type, 'location': location, 'value': value}[/dim].",
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
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Cloud secrets collection.

    A secrets collection is a group of key-value pairs that can be used by
    your application instances during execution. Each collection can contain
    up to 20 secrets. Secrets are provided as JSON objects using the
    --secrets flag.

    Each secret must include three fields:
    - [magenta]type[/magenta]: Either [magenta]env[/magenta] or [magenta]file[/magenta],
      which determines how the secret is injected into the runtime.
    - [magenta]location[/magenta]: Where to place the secret.
      - [magenta]env[/magenta]: the environment variable name. E.g.: [magenta]BURROW_ENTRANCE[/magenta].
      - [magenta]file[/magenta]: the relative path from the execution
        directory. E.g.: [magenta]licenses/burrow.entr[/magenta].
    - [magenta]value[/magenta]: The secret value as text (limited to 1 KB).

    You can provide secrets in three ways:
    - A single secret as a [magenta]json[/magenta] object.
    - Multiple secrets by repeating the --secrets flag.
    - Multiple secrets as a [magenta]json[/magenta] array in a single --secrets flag.

    The --secrets-collection-id and --name are optional.
    If not provided, they will be automatically generated.

    [bold][underline]Examples[/underline][/bold]

    - Create a secrets collection with a single environment variable secret.
        $ [dim]nextmv cloud secrets create --app-id hare-app \\
            --secrets '{"type": "env", "location": "API_KEY", "value": "secret-value"}'[/dim]

    - Create a secrets collection with multiple secrets by repeating the flag.
        $ [dim]nextmv cloud secrets create --app-id hare-app \\
            --secrets '{"type": "env", "location": "API_KEY", "value": "secret-value"}' \\
            --secrets '{"type": "env", "location": "DATABASE_URL", "value": "postgres://localhost"}'[/dim]

    - Create a secrets collection with multiple secrets in a single JSON array.
        $ [dim]nextmv cloud secrets create --app-id hare-app \\
            --secrets '[{"type": "env", "location": "DB_USER", "value": "admin"}, {...}]'[/dim]

    - Create a secrets collection with custom ID, name, and description.
        $ [dim]nextmv cloud secrets create --app-id hare-app \\
            --secrets-collection-id db-creds --name "Database Credentials" \\
            --description "Production database credentials" \\
            --secrets '{"type": "env", "location": "DB_USER", "value": "admin"}' \\
            --secrets '{"type": "env", "location": "DB_PASS", "value": "secure123"}'[/dim]

    - Create a secrets collection with file-based secrets.
        $ [dim]nextmv cloud secrets create --app-id hare-app \\
            --secrets-collection-id certs --name "Certificates" \\
            --secrets '{"type": "file", "location": "licenses/acme.lic", "value": "LICENSE_CONTENT_HERE"}'[/dim]

    - Mix environment and file-based secrets.
        $ [dim]nextmv cloud secrets create --app-id hare-app \\
            --secrets '{"type": "env", "location": "ACME_LICENSE_KEY", "value": "abc123"}' \\
            --secrets '{"type": "file", "location": "config/app.conf", "value": "server=prod\\nport=8080"}'[/dim]
    """

    cloud_app = build_app(app_id=app_id, profile=profile)
    in_progress(msg="Creating secrets collection...")

    # Build the secrets list from the CLI options
    secrets_list = build_secrets(secrets)

    collection = cloud_app.new_secrets_collection(
        secrets=secrets_list,
        id=secrets_collection_id,
        name=name,
        description=description,
    )
    print_json(collection.to_dict())


def build_secrets(secrets: list[str]) -> list[Secret]:
    """
    Builds the secrets list from the CLI option(s).

    Parameters
    ----------
    secrets : list[str]
        List of secrets provided via the CLI.

    Returns
    -------
    list[Secret]
        The built secrets list.
    """
    import json

    secrets_list = []

    for secret_str in secrets:
        try:
            secret_data = json.loads(secret_str)

            # Handle the case where the value is a list of secrets.
            if isinstance(secret_data, list):
                for ix, item in enumerate(secret_data):
                    if item.get("type") is None or item.get("location") is None or item.get("value") is None:
                        error(
                            f"Invalid secret format at index [magenta]{ix}[/magenta] in "
                            f"[magenta]{secret_str}[/magenta]. Each secret must have "
                            "[magenta]type[/magenta], [magenta]location[/magenta], "
                            "and [magenta]value[/magenta] fields."
                        )

                    secret = Secret(
                        type=SecretType(item["type"]),
                        location=item["location"],
                        value=item["value"],
                    )
                    secrets_list.append(secret)

            # Handle the case where the value is a single secret.
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

                secret = Secret(
                    type=SecretType(secret_data["type"]),
                    location=secret_data["location"],
                    value=secret_data["value"],
                )
                secrets_list.append(secret)

            else:
                error(
                    f"Invalid secret format: [magenta]{secret_str}[/magenta]. "
                    "Expected [magenta]json[/magenta] object or array."
                )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            error(f"Invalid secret format: [magenta]{secret_str}[/magenta]. Error: {e}")

    return secrets_list
