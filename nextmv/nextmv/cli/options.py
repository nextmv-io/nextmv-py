"""
Shared CLI options for the Nextmv CLI.

This module defines reusable option types that can be imported
and used across all CLI commands.
"""

from typing import Annotated

import typer

# profile option - can be used in any command to specify which profile to use.
# Define it as follows in commands or callbacks, as necessary:
# profile: ProfileOption = None
ProfileOption = Annotated[
    str | None,
    typer.Option(
        "--profile",
        "-p",
        help="Profile to use for this action. Use [code]nextmv configuration[/code] to manage profiles.",
        envvar="NEXTMV_PROFILE",
        metavar="PROFILE_NAME",
    ),
]

# app_id option - can be used in any command that requires an application ID.
# Define it as follows in commands or callbacks, as necessary:
# app_id: AppIDOption
AppIDOption = Annotated[
    str,
    typer.Option(
        "--app-id",
        "-a",
        help="The Nextmv Cloud application ID to use for this action.",
        envvar="NEXTMV_APP_ID",
        metavar="APP_ID",
    ),
]

# run_id option - can be used in any command that requires a run ID.
# Define it as follows in commands or callbacks, as necessary:
# run_id: RunIDOption
RunIDOption = Annotated[
    str,
    typer.Option(
        "--run-id",
        "-r",
        help="The Nextmv Cloud run ID to use for this action.",
        envvar="NEXTMV_RUN_ID",
        metavar="RUN_ID",
    ),
]

# version_id option - can be used in any command that requires a version ID.
# Define it as follows in commands or callbacks, as necessary:
# version_id: VersionIDOption
VersionIDOption = Annotated[
    str,
    typer.Option(
        "--version-id",
        "-v",
        help="The Nextmv Cloud version ID to use for this action.",
        envvar="NEXTMV_VERSION_ID",
        metavar="VERSION_ID",
    ),
]

# instance_id option - can be used in any command that requires an instance ID.
# Define it as follows in commands or callbacks, as necessary:
# instance_id: InstanceIDOption
InstanceIDOption = Annotated[
    str,
    typer.Option(
        "--instance-id",
        "-i",
        help="The Nextmv Cloud instance ID to use for this action.",
        envvar="NEXTMV_INSTANCE_ID",
        metavar="INSTANCE_ID",
    ),
]

# secrets_collection_id option - can be used in any command that requires a secrets collection ID.
# Define it as follows in commands or callbacks, as necessary:
# secrets_collection_id: SecretsCollectionIDOption
SecretsCollectionIDOption = Annotated[
    str,
    typer.Option(
        "--secrets-collection-id",
        "-s",
        help="The Nextmv Cloud secrets collection ID to use for this action.",
        envvar="NEXTMV_SECRETS_COLLECTION_ID",
        metavar="SECRETS_COLLECTION_ID",
    ),
]
